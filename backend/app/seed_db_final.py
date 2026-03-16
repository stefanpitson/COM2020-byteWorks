from sqlmodel import Session, SQLModel, select
from app.core.database import engine, seed_allergens
from app.core.security import get_password_hash
from app.models import User, Vendor, Customer, Template, Bundle, Reservation, Streak, Allergen
from datetime import datetime, timedelta, time as dt_time
import random
import copy
import shutil
from pathlib import Path

from uploads.vendors_data import vendors # vendor info
from app.forecasting.database_creation.generate_input_forecasts import sync_forecast_inputs

def seed_database():

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    seed_allergens()

    vendors_runtime = copy.deepcopy(vendors)  # so as to keep the original dictionary
    customer_names = ["alice", "bob", "charlie", "david", "eve", "frank", "grace", "hannah", "irene", "jack"]
    customer_list = []

    with Session(engine) as session:
        allergen_lookup = {
            allergen.title: allergen
            for allergen in session.exec(select(Allergen)).all()
        }

        for i in range(len(customer_names)):
            user = User(
                email=f"{customer_names[i]}@gmail.com",
                password_hash=get_password_hash(f"{customer_names[i]}123"),
                role="customer",
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            customer = Customer(
                user_id=user.user_id,
                name=customer_names[i],
                post_code="EX4 6TJ",
                carbon_saved=0,
                store_credit=800,
            )
            customer_list.append(customer)
            session.add(customer)
            session.commit()
            session.refresh(customer)

        reservation_code = 1000

        for vendor, info in vendors_runtime.items():
            # VENDOR CREATION
            vendor_user = User(
                email=f"admin@{vendor.lower().replace(' ', '')}.com",
                password_hash=get_password_hash(f"{vendor.lower().replace(' ', '')}123"),
                role="vendor",
            )

            session.add(vendor_user)
            session.commit()
            session.refresh(vendor_user)

            open_hour = (random.randint(7,12))
            close_hour = random.randint(17,23)
            vendor_account = Vendor(
                user_id=vendor_user.user_id,
                name=vendor,
                street=info["street"],
                city="Exeter",
                post_code=info["postcode"],
                phone_number= f"01392 {random.randint(200000, 499999)}",
                opening_hours=f"{open_hour:02}:00-{close_hour}:00",# class of days
                photo=f"/static/seed-data/logo_images/{vendor.lower().replace(' ','')}.png",
                validated=True,
                carbon_saved=0,
            )

            session.add(vendor_account)
            session.commit()
            session.refresh(vendor_account)


            # TEMPLATE CREATION
            template_list = [] 
            for template in info["templates"]: 
                estimated_value = round(random.uniform(5.0, 15.0),2)
                discount = round(random.uniform(0.4,1.0),2) # could be up to 60% off

                template_register = Template(
                    title=template["name"],
                    description=template["description"],
                    estimated_value=estimated_value,
                    cost=estimated_value*discount,
                    meat_percent=template["meat_percent"],
                    carb_percent=template["carb_percent"],
                    veg_percent=template["veg_percent"],
                    carbon_saved=template["carbon_saved"],
                    weight=template["weight"],
                    is_vegan=template["is_vegan"],
                    is_vegetarian=template["is_vegetarian"],
                    vendor=vendor_account.vendor_id,
                    photo=f"/static/seed-data/template_images/{template['name'].lower().replace(' ','')}.jpg",
                )

                template_register.allergens = [
                    allergen_lookup[title]
                    for title in template['allergens']
                    if title in allergen_lookup
                ]
                session.add(template_register)
                session.commit()
                session.refresh(template_register)

                template_list.append(template_register)

            total_bundles_sold_per_week = random.randint(2,15) # total bundles a week for a specific vendor
            distribution = 1.0
            popularity_list = []

            for i in range(len(template_list)): # assign a popularity for each template
                popularity = random.uniform(0.0, distribution)
                if ((1 - (template_list[i].cost / template_list[i].estimated_value)) > 0.4):
                    popularity *= 1.2 # more popular with higher discount

                popularity = min(popularity, distribution)

                distribution = distribution - popularity
                popularity_list.append(popularity)
            bundles_created = []
            
            today = datetime.now().date()

            # 6 WEEKS OF SEEDED DATA
            for i in range(len(template_list)):

                # for this template, num bundles will be sold depending on its popularity and total bundles sold in a week
                num_bundle = int(round(popularity_list[i] * total_bundles_sold_per_week))
                day = random.randint(0, 6)
                bundle_hour = random.randint(open_hour, close_hour - 1)

                for week in range(6): 
                    if num_bundle > 1: # add small variance if bigger than 1, rudimentary variance
                        num_bundle = num_bundle + random.randint(-1,1)

                    bundle_date = today - timedelta(days=(42 - (week * 7 + day)))
                    day_of_week = bundle_date.weekday()
                    
                    # distribute status of bundle reservation
                    for j in range(num_bundle):
                        gets_reserved = (j < (num_bundle) * 0.8) # 80 percent chance to be reserved
                        if gets_reserved:
                            rand = random.randint(0,9)
                            if rand < 7: # 70% collected
                                status = "collected"
                                picked_up = True
                            elif rand < 9: 
                                status = "no_show"
                                picked_up = False
                            else:
                                status = "cancelled"
                                picked_up = False
                        else:
                            status = None
                            picked_up = False

                        bundle_time = dt_time(bundle_hour, random.randint(0, 59))
                        bundle = Bundle(
                            template_id=template_list[i].template_id,
                            date=bundle_date,
                            time=bundle_time,
                            picked_up=picked_up
                        )
                        session.add(bundle)
                        session.flush()
                        bundles_created.append(bundle)

                        if gets_reserved:
                            template_obj = template_list[i]
                            eligible_customers = [
                                c for c in customer_list if c.store_credit >= template_obj.cost
                            ]
                            if not eligible_customers:
                                continue
                            customer = random.choice(eligible_customers)

                            # Simulate real reservation wallet behaviour.
                            customer.store_credit -= template_obj.cost
                            if status == "cancelled":
                                # Cancellation should release the bundle and restore wallet credit.
                                customer.store_credit += template_obj.cost
                                bundle.purchased_by = None
                            else:
                                bundle.purchased_by = customer.customer_id

                            # reservation time is same day as bundle, with up to two hour difference
                            reservation_hour = min(bundle_hour + random.randint(0, 2), close_hour - 1)
                            reservation_dt = datetime(
                                bundle_date.year, bundle_date.month, bundle_date.day,
                                reservation_hour, random.randint(0, 59)
                            )
                            reservation = Reservation(
                                bundle_id=bundle.bundle_id,
                                customer_id=customer.customer_id,
                                status=status,
                                code=reservation_code,
                                time_created=reservation_dt,
                            )
                            session.add(reservation)
                            reservation_code += 1

                            if status == "collected":
                                # calculating analytics manually
                                carbon_saved = template_obj.carbon_saved or 0.0
                                vendor_account.total_revenue += template_obj.cost
                                vendor_account.food_saved += template_obj.weight
                                vendor_account.carbon_saved += carbon_saved
                                customer.carbon_saved += carbon_saved

            # sync forecast inputs
            session.flush()
            sync_forecast_inputs(session, vendor_id=vendor_account.vendor_id, days_back=60)

            # current bundles available today
            for i in range(len(template_list)):
                num_today = max(1, int(round(popularity_list[i] * total_bundles_sold_per_week)))
                template_post_hour = random.randint(open_hour, max(open_hour, close_hour - 1))

                for j in range(num_today):
                    bundle_hour = template_post_hour
                    bundle = Bundle(
                        template_id=template_list[i].template_id,
                        date=today,
                        time=dt_time(bundle_hour, random.randint(0, 59)),
                        picked_up=False
                    )
                    session.add(bundle)
                    session.flush()

                    # use the same reservation-rate pattern as historical seeded data
                    if j < num_today * 0.8:
                        template_obj = template_list[i]
                        eligible_customers = [
                            c for c in customer_list if c.store_credit >= template_obj.cost
                        ]
                        if not eligible_customers:
                            continue
                        customer = random.choice(eligible_customers)

                        reservation_hour = min(bundle_hour + random.randint(0, 1), close_hour - 1)
                        reservation_dt = datetime(
                            today.year, today.month, today.day,
                            reservation_hour, random.randint(0, 59)
                        )
                        # keep some reservations active today so vendors can see pending pickups
                        rand = (i + j) % 10
                        if rand < 5:
                            today_status = "booked"
                            bundle.picked_up = False
                        elif rand < 8:
                            today_status = "collected"
                            bundle.picked_up = True
                        elif rand < 9:
                            today_status = "no_show"
                            bundle.picked_up = False
                        else:
                            today_status = "cancelled"
                            bundle.picked_up = False

                        # Simulate real reservation wallet behaviour.
                        customer.store_credit -= template_obj.cost
                        if today_status == "cancelled":
                            # Cancellation should release the bundle and restore wallet credit.
                            customer.store_credit += template_obj.cost
                            bundle.purchased_by = None
                        else:
                            bundle.purchased_by = customer.customer_id

                        reservation = Reservation(
                            bundle_id=bundle.bundle_id,
                            customer_id=customer.customer_id,
                            status=today_status,
                            code=reservation_code,
                            time_created=reservation_dt,
                        )
                        session.add(reservation)
                        reservation_code += 1

                        if today_status == "collected":
                            carbon_saved = template_obj.carbon_saved or 0.0
                            vendor_account.total_revenue += template_obj.cost
                            vendor_account.food_saved += template_obj.weight
                            vendor_account.carbon_saved += carbon_saved
                            customer.carbon_saved += carbon_saved

        # set streaks for each customer based on their historical collected reservations, must be done manually
        for customer in customer_list:
            collected_dates = session.exec(
                select(Bundle.date)
                .join(Reservation, Bundle.bundle_id == Reservation.bundle_id)
                .where(Reservation.customer_id == customer.customer_id)
                .where(Reservation.status == "collected")
                .order_by(Bundle.date)
            ).all()

            if not collected_dates:
                continue

            current_streak = None
            for col_date in collected_dates:
                if current_streak is None:
                    current_streak = Streak(
                        customer_id=customer.customer_id,
                        started=col_date,
                        last=col_date,
                        count=1,
                        ended=False,
                    )
                    session.add(current_streak)
                    session.flush()
                else:
                    if col_date == current_streak.last:
                        continue 
                    # if date of subsequent reservation was within 7 days, add to streak
                    elif col_date <= current_streak.last + timedelta(days=7):
                        current_streak.count += 1
                        current_streak.last = col_date
                        session.add(current_streak)
                    else:
                        # end first streak, set new streak to 1
                        current_streak.ended = True
                        session.add(current_streak)
                        current_streak = Streak(
                            customer_id=customer.customer_id,
                            started=col_date,
                            last=col_date,
                            count=1,
                            ended=False,
                        )
                        session.add(current_streak)
                        session.flush()

            # if its been more than 7 days since the last reservation then end streak
            if current_streak and current_streak.last + timedelta(days=7) < today:
                current_streak.ended = True
                session.add(current_streak)

        session.commit()

    print("Database seeded")

if __name__ == '__main__':
    seed_database()