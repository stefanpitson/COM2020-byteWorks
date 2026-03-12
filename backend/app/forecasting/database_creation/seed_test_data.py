import random
from datetime import datetime, timedelta, date, time
from sqlmodel import Session, select
from app.core.database import engine
from app.core.security import get_password_hash
from app.models import (
    User, Vendor, Customer, Template, Bundle, Reservation
)


# make a vendor name and templates here to be used later on
VENDOR_NAME = "Good Food Market"
TEMPLATES = [
    {"title": "Vegan Bowl", "description": "Hearty plant-based bowl",
     "estimated_value": 8.50, "cost": 3.20, "meat_percent": 0, "carb_percent": 40,
     "veg_percent": 60, "carbon_saved": 1.2, "weight": 0.5,
     "is_vegan": True, "is_vegetarian": True, "popularity": 0.8},
    {"title": "Sandwich Combo", "description": "Sandwich, crisps, drink",
     "estimated_value": 6.00, "cost": 2.50, "meat_percent": 30, "carb_percent": 50,
     "veg_percent": 20, "carbon_saved": 0.8, "weight": 0.4,
     "is_vegan": False, "is_vegetarian": False, "popularity": 0.9},
    {"title": "Salad Box", "description": "Fresh salad with dressing",
     "estimated_value": 5.50, "cost": 2.00, "meat_percent": 0, "carb_percent": 20,
     "veg_percent": 80, "carbon_saved": 0.5, "weight": 0.3,
     "is_vegan": True, "is_vegetarian": True, "popularity": 0.6},
    {"title": "Soup & Bread", "description": "Homemade soup with roll",
     "estimated_value": 4.50, "cost": 1.80, "meat_percent": 0, "carb_percent": 60,
     "veg_percent": 40, "carbon_saved": 0.6, "weight": 0.6,
     "is_vegan": False, "is_vegetarian": True, "popularity": 0.7},
    {"title": "Dessert Pack", "description": "Two sweet treats",
     "estimated_value": 5.00, "cost": 2.20, "meat_percent": 0, "carb_percent": 80,
     "veg_percent": 20, "carbon_saved": 0.4, "weight": 0.3,
     "is_vegan": False, "is_vegetarian": True, "popularity": 0.5},
]

# create the customers ti be used later
CUSTOMERS = [
    {"name": "Alice", "post_code": "SW1A 1AA"},
    {"name": "Bob", "post_code": "E1 6QL"},
    {"name": "Carol", "post_code": "M1 1AE"},
    {"name": "David", "post_code": "B2 4QA"},
    {"name": "Eve", "post_code": "G1 2FF"},
]

# create time slots per week
TIME_SLOTS = [
    (0, 17, 0, 0.7),  
    (2, 12, 0, 1.0),   
    (4, 18, 0, 1.5),   
]

# possible ranges/ rates
POSTED_RANGE = (15, 35)
BASE_RESERVATION_RATE = (0.5, 0.9)
NO_SHOW_RATE = (0.05, 0.2)



def seed(weeks_of_history: int = 6):
    """
    we seed the database (specified in the .emv file) witn weeks_of_history weeks of data 
    ranges are defined externally -> an arbitrary amount of histroy may be created
    Only 1 vendor
    """
    start_date = date.today() - timedelta(weeks=weeks_of_history)

    with Session(engine) as session: # used the session from the url defined in .env
        # make a vendor amd user entities to represent vendor
        vendor_user = User(
            password_hash=get_password_hash("vendorpass"),
            email="vendor@goodfood.com",
            role="vendor"
        )
        session.add(vendor_user)
        session.flush()

        # vendor entity
        vendor = Vendor(
            user_id=vendor_user.user_id,
            name=VENDOR_NAME,
            street="123 High Street",
            city="London",
            post_code="EC1A 1BB",
            phone_number="020 1234 5678",
            opening_hours="Mon-Fri 9am-6pm",
            validated=True
        )
        session.add(vendor)
        session.flush()

        # make customers and users to represent customers with semi realistic credentials
        customer_ids = []
        for c in CUSTOMERS:
            user = User(
                password_hash=get_password_hash("customerpass"),
                email=c["name"].lower() + "@example.com",
                role="customer"
            )
            session.add(user)
            session.flush()
            customer = Customer(
                user_id=user.user_id,
                name=c["name"],
                post_code=c["post_code"],
                store_credit=0,
                carbon_saved=0
            )
            session.add(customer)
            session.flush()
            customer_ids.append(customer.customer_id)

        # make the temolates based on information defined at the top
        template_records = []
        for t in TEMPLATES:
            popularity = t['popularity']
            template_data = {k: v for k, v in t.items() if k != "popularity"}
            template = Template(
                **template_data,
                vendor=vendor.vendor_id
            )
            session.add(template)
            session.flush()
            template_records.append({
                "id": template.template_id,
                "popularity": popularity
            })


        # we go through all the weeks in the predefined history
        for week in range(weeks_of_history):
            # set the week start
            week_start = start_date + timedelta(weeks=week)
            for dow, hour, minute, demand_factor in TIME_SLOTS:
                slot_date = week_start + timedelta(days=dow)
                if slot_date > date.today(): # scip slot dates in the future
                    continue
                slot_time = time(hour, minute)

                # go through template records which have now been creates
                for template in template_records:
                    template_id = template["id"]
                    popularity = template["popularity"]

                    # random number of bundles posted in this batch based on predefined range
                    posted = random.randint(*POSTED_RANGE)

                    # set the reserved rate to calculate how many reservations
                    base_rate = random.uniform(*BASE_RESERVATION_RATE)
                    reservation_rate = min(base_rate * popularity * demand_factor, 0.95)
                    reserved = int(posted * reservation_rate)

                    # no-show rate is defined similarly
                    no_show_rate = random.uniform(*NO_SHOW_RATE)
                    no_shows = int(reserved * no_show_rate) if reserved > 0 else 0

                    # Create bundles
                    bundle_ids = []
                    for _ in range(posted):
                        bundle = Bundle(
                            template_id=template_id,
                            picked_up=False,
                            date=slot_date,
                            time=slot_time,
                            purchased_by=None
                        )
                        session.add(bundle)
                        session.flush()
                        bundle_ids.append(bundle.bundle_id)


                    # set reserved bundles and handle no‑shows
                    if reserved > 0:
                        reserved_bundle_ids = random.sample(bundle_ids, reserved)
                        no_show_bundle_ids = random.sample(reserved_bundle_ids, no_shows) if no_shows > 0 else []

                        for b_id in reserved_bundle_ids:
                            cust_id = random.choice(customer_ids)
                            # Update the bundle
                            stmt = select(Bundle).where(Bundle.bundle_id == b_id)
                            bundle = session.exec(stmt).one()
                            bundle.purchased_by = cust_id

                            status = 'no_show' if b_id in no_show_bundle_ids else 'collected'
                            # create the reservation entity
                            reservation = Reservation(
                                bundle_id=b_id,
                                customer_id=cust_id,
                                time_created=datetime.now(),
                                status=status,
                                code=random.randint(1000, 9999) # accept small risk of collision just for seeded dataset. IRL collisions handled
                            )
                            session.add(reservation)

                            if status == 'collected':
                                bundle.picked_up = True

        session.commit()


if __name__ == "__main__":
    seed()