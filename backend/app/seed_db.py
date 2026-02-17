from sqlmodel import Session, SQLModel
from app.core.database import engine
from app.core.security import get_password_hash
from app.models import User, Vendor, Customer, Template, Bundle, Reservation
from datetime import datetime, timedelta

def seed_database():
    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        vendor1_user = User(
            email="admin@tesco.com",
            password_hash=get_password_hash("tesco123"),
            role="vendor",
        )
        vendor2_user = User(
            email="admin@greggs.com",
            password_hash=get_password_hash("greggs123"),
            role="vendor",
        )
        customer1_user = User(
            email="bob@gmail.com",
            password_hash=get_password_hash("bob123"),
            role="customer",
        )
        customer2_user = User(
            email="alice@gmail.com",
            password_hash=get_password_hash("alice123"),
            role="customer",
        )

        session.add_all([vendor1_user, vendor2_user, customer1_user, customer2_user])
        session.commit()
        session.refresh(vendor1_user)
        session.refresh(vendor2_user)
        session.refresh(customer1_user)
        session.refresh(customer2_user)

        vendor1 = Vendor(
            user_id=vendor1_user.user_id,
            name="Tesco Express",
            street="74 Sidwell Street",
            city="Exeter",
            post_code="EX4 6PH",
            phone_number="01392 111222",
            opening_hours="08:00-22:00",
            photo="/static/tesco.png",
            validated=True,
            carbon_saved=150,
        )
        vendor2 = Vendor(
            user_id=vendor2_user.user_id,
            name="Greggs",
            street="12 High Street",
            city="Exeter",
            post_code="EX4 3AT",
            phone_number="01392 333444",
            opening_hours="07:00-18:00",
            photo="/static/greggs.png",
            validated=True,
            carbon_saved=220,
        )

        session.add_all([vendor1, vendor2])
        session.commit()
        session.refresh(vendor1)
        session.refresh(vendor2)

        customer1 = Customer(
            user_id=customer1_user.user_id,
            name="Joe Andrews",
            post_code="EX1 2JA",
            carbon_saved=35,
            store_credit=10,
        )
        customer2 = Customer(
            user_id=customer2_user.user_id,
            name="Alice Brown",
            post_code="EX2 4QP",
            carbon_saved=22,
            store_credit=5,
        )

        session.add_all([customer1, customer2])
        session.commit()
        session.refresh(customer1)
        session.refresh(customer2)

        template1 = Template(
            title="Pastries Box",
            description="Assorted croissants and cinnamon buns",
            estimated_value=12.0,
            cost=4.0,
            meat_percent=0.0,
            carb_percent=1.0,
            veg_percent=0.0,
            carbon_saved=0.8,
            weight=0.5,
            is_vegan=False,
            is_vegetarian=True,
            vendor=vendor1.vendor_id,
            photo="/static/cinnabuns.jpg",
        )
        template2 = Template(
            title="Mixed Sandwich Pack",
            description="Chicken, ham, and veggie sandwiches",
            estimated_value=10.0,
            cost=3.5,
            meat_percent=0.4,
            carb_percent=0.4,
            veg_percent=0.2,
            carbon_saved=1.2,
            weight=0.6,
            is_vegan=False,
            is_vegetarian=False,
            vendor=vendor1.vendor_id,
            photo="/static/sandwiches.jpg",
        )
        template3 = Template(
            title="Fresh Salad Bowl",
            description="Mixed greens with dressing",
            estimated_value=8.0,
            cost=3.0,
            meat_percent=0.0,
            carb_percent=0.1,
            veg_percent=0.9,
            carbon_saved=0.5,
            weight=0.4,
            is_vegan=True,
            is_vegetarian=True,
            vendor=vendor1.vendor_id,
            photo="/static/saladbowl.jpg",
        )
        template4 = Template(
            title="Coffee & Muffin Bundle",
            description="Freshly baked muffin with coffee",
            estimated_value=6.0,
            cost=2.5,
            meat_percent=0.0,
            carb_percent=0.8,
            veg_percent=0.2,
            carbon_saved=0.4,
            weight=0.3,
            is_vegan=False,
            is_vegetarian=True,
            vendor=vendor2.vendor_id,
            photo="/static/coffeemuffin.jpg",
        )
        template5 = Template(
            title="Artisan Bread Loaf",
            description="Day-old sourdough loaf",
            estimated_value=5.0,
            cost=2.0,
            meat_percent=0.0,
            carb_percent=1.0,
            veg_percent=0.0,
            carbon_saved=0.6,
            weight=0.8,
            is_vegan=True,
            is_vegetarian=True,
            vendor=vendor2.vendor_id,
            photo="/static/bread.jpg",
        )

        session.add_all([template1, template2, template3, template4, template5])
        session.commit()
        session.refresh(template1)
        session.refresh(template2)
        session.refresh(template3)
        session.refresh(template4)
        session.refresh(template5)

        today = datetime.now().date()
        # More bundles posted on busy days (Fri/Sat), fewer on Mon/Tue
        day_multipliers = {
            0: 2,  # Monday
            1: 2,  
            2: 3,  
            3: 4,  
            4: 6,  
            5: 4,  
            6: 3   # Sunday
        }
        
        bundles_created = []
        reservation_code = 1000
        
        for week in range(4):
            for day in range(7):
                bundle_date = today - timedelta(days=(28 - (week * 7 + day)))
                day_of_week = bundle_date.weekday()
                bundle_count = day_multipliers[day_of_week]
                
                for i in range(bundle_count):
                    
                    if day_of_week == 4:  # Friday
                        if i < bundle_count * 0.6:  
                            template = template2
                        elif i < bundle_count * 0.8:
                            template = template1  
                        else:
                            template = template3  
                    
                    elif day_of_week == 6: 
                        if i < bundle_count * 0.5:
                            template = template1  
                        elif i < bundle_count * 0.7:
                            template = template4 
                        else:
                            template = template5 
                    
                    elif day_of_week in [2, 3]:
                        if i < bundle_count * 0.4:
                            template = template3  
                        elif i < bundle_count * 0.7:
                            template = template2 
                        else:
                            template = template1
                    
                    # OTHER DAYS
                    else:
                        if i % 3 == 0:
                            template = template2  
                        elif i % 3 == 1:
                            template = template1
                        else:
                            template = template4
                    
                    gets_reserved = (i < bundle_count * 0.8)
                    
                    if gets_reserved:
                        rand = (i + day + week) % 10
                        if rand < 7:
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
                    
                    bundle = Bundle(
                        template_id=template.template_id,
                        date=bundle_date,
                        picked_up=picked_up
                    )
                    session.add(bundle)
                    session.flush()
                    bundles_created.append(bundle)
                    
                    if gets_reserved:
                        customer = customer1 if i % 2 == 0 else customer2
                        reservation = Reservation(
                            bundle_id=bundle.bundle_id,
                            customer_id=customer.customer_id,
                            status=status,
                            code=reservation_code
                        )
                        session.add(reservation)
                        reservation_code += 1
        
        for i in range(4):
            template = [template1, template2, template4, template5][i]
            bundle = Bundle(template_id=template.template_id, date=today)
            session.add(bundle)
            session.flush()
            
            if i < 2:
                reservation = Reservation(
                    bundle_id=bundle.bundle_id,
                    customer_id=customer1.customer_id if i == 0 else customer2.customer_id,
                    status="booked",
                    code=reservation_code
                )
                session.add(reservation)
                reservation_code += 1
        
        session.commit()

    print("Database seeded")

if __name__ == '__main__':
    seed_database()