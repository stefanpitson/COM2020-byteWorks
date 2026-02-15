import random
from datetime import datetime, timedelta, date, time
from sqlmodel import Session, create_engine, select
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session
from app.core.database import engine


# Import your actual models (adjust the path to your models module)
from app.models import (
    User, Vendor, Customer, Template, Bundle, Reservation,
    # Allergen, Allergen_Template  # if needed, uncomment
)

# -------------------- CONFIGURATION --------------------

VENDOR_NAME = "Good Food Market"
TEMPLATES = [
    {"title": "Vegan Bowl", "description": "Hearty plant-based bowl",
     "estimated_value": 8.50, "cost": 3.20, "meat_percent": 0, "carb_percent": 40,
     "veg_percent": 60, "carbon_saved": 1.2, "weight": 0.5,
     "is_vegan": True, "is_vegetarian": True, "popularity": 0.8},  # popularity factor for reservation rate
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

CUSTOMERS = [
    {"name": "Alice", "post_code": "SW1A 1AA"},
    {"name": "Bob", "post_code": "E1 6QL"},
    {"name": "Carol", "post_code": "M1 1AE"},
    {"name": "David", "post_code": "B2 4QA"},
    {"name": "Eve", "post_code": "G1 2FF"},
]

# Time slots per week: (day_of_week, hour, minute, demand_factor)
# demand_factor multiplies the base reservation probability
TIME_SLOTS = [
    (0, 17, 0, 0.7),   # Monday 5pm (lower demand)
    (2, 12, 0, 1.0),   # Wednesday 12pm (medium)
    (4, 18, 0, 1.5),   # Friday 6pm (higher demand)
]

WEEKS_OF_HISTORY = 6
START_DATE = date.today() - timedelta(weeks=WEEKS_OF_HISTORY)

# Base ranges
POSTED_RANGE = (15, 35)           # bundles posted per batch (per template)
BASE_RESERVATION_RATE = (0.5, 0.9) # proportion reserved, adjusted by template popularity and day factor
NO_SHOW_RATE = (0.05, 0.2)        # proportion of reserved that become no-shows

# -------------------------------------------------------

def seed():
    with Session(engine) as session:
        # 1. Create vendor user and vendor
        vendor_user = User(
            password_hash="hashed_placeholder",
            email="vendor@goodfood.com",
            role="vendor"
        )
        session.add(vendor_user)
        session.flush()

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
        print(f"Created vendor {vendor.name} with ID {vendor.vendor_id}")

        # 2. Create customers
        customer_ids = []
        for c in CUSTOMERS:
            user = User(
                password_hash="hashed_placeholder",
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
        print(f"Created {len(customer_ids)} customers")

        # 3. Create templates (store popularity factor for later use)
        template_records = []
        for t in TEMPLATES:
            popularity = t['popularity']
            # Remove the extra key before creating Template object
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
        print(f"Created {len(template_records)} templates")

        # 4. Generate historical bundles and reservations
        total_bundles = 0
        total_reservations = 0

        for week in range(WEEKS_OF_HISTORY):
            week_start = START_DATE + timedelta(weeks=week)
            for dow, hour, minute, demand_factor in TIME_SLOTS:
                slot_date = week_start + timedelta(days=dow)
                if slot_date > date.today():
                    continue  # skip future dates (shouldn't happen given START_DATE)
                slot_time = time(hour, minute)

                for template in template_records:
                    template_id = template["id"]
                    popularity = template["popularity"]

                    # Number of bundles posted in this batch
                    posted = random.randint(*POSTED_RANGE)

                    # Base reservation probability, then adjusted
                    base_rate = random.uniform(*BASE_RESERVATION_RATE)
                    # Cap at 0.95 to avoid overshoot
                    reservation_rate = min(base_rate * popularity * demand_factor, 0.95)
                    reserved = int(posted * reservation_rate)

                    # No-show rate
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

                    total_bundles += posted

                    # Decide which bundles are reserved
                    if reserved > 0:
                        reserved_bundle_ids = random.sample(bundle_ids, reserved)
                        # Choose which of those become no-shows
                        no_show_bundle_ids = random.sample(reserved_bundle_ids, no_shows) if no_shows > 0 else []

                        for b_id in reserved_bundle_ids:
                            cust_id = random.choice(customer_ids)
                            # Update bundle
                            stmt = select(Bundle).where(Bundle.bundle_id == b_id)
                            bundle = session.exec(stmt).one()
                            bundle.purchased_by = cust_id

                            # Determine status
                            status = 'no_show' if b_id in no_show_bundle_ids else 'collected'

                            # Create reservation
                            reservation = Reservation(
                                bundle_id=b_id,
                                customer_id=cust_id,
                                time_created=datetime.now().time(),  # placeholder
                                status=status,
                                code=random.randint(100000, 999999)
                            )
                            session.add(reservation)
                            total_reservations += 1

                            if status == 'collected':
                                bundle.picked_up = True
                            # else no_show remains picked_up=False

                    # Bundles not reserved remain as is (expired)

        session.commit()
        print(f"Seeding complete. Created {total_bundles} bundles and {total_reservations} reservations.")

if __name__ == "__main__":
    seed()