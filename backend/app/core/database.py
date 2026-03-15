import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select
from app.models import Allergen, Badge

# Main functions relating to database functionality

# Running this file *SHOULD will drop all tables, allowing a reset when attributes for functions change 

# GLOBAL
# the code outside the functions will run once on start up when the file is imported (typically create_db_and_tables)

load_dotenv()

# get db from env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables")

engine = create_engine(DATABASE_URL, echo=True)

DEFAULT_ALLERGENS = [
    "Celery", "Gluten", "Crustaceans", "Eggs", "Fish", "Lupin", 
    "Milk", "Molluscs", "Mustard", "Treenuts", "Peanuts", 
    "Sesame", "Soybean", "Sulphur Dioxide"
]

def seed_allergens():
    with Session(engine) as session:
        # Check if we already have allergens in the DB
        statement = select(Allergen)
        existing_allergens = session.exec(statement).first()

        if not existing_allergens:
            print("Seeding default allergens...")
            for name in DEFAULT_ALLERGENS:
                allergen = Allergen(title=name)
                session.add(allergen)
            session.commit()
            print("Allergens successfully seeded.")

DEFAULT_BADGES = [
    {"title": "Streak Beginner", "description": "Reach a 3 day streak", "metric": "streak_count", "threshold": 3, "user_role": "customer"},
    {"title": "Streak Intermediate", "description": "Reach a 7 day streak", "metric": "streak_count", "threshold": 7, "user_role": "customer"},
    {"title": "Streak Pro", "description": "Reach a 14 day streak", "metric": "streak_count", "threshold": 14, "user_role": "customer"},
    {"title": "Streak Master", "description": "Reach a 30 day streak", "metric": "streak_count", "threshold": 30, "user_role": "customer"},
    {"title": "Waste Saver", "description": "Save 1kg of food", "metric": "food_saved", "threshold": 1, "user_role": "customer"},
    {"title": "Waste Soldier", "description": "Save 5kg of food", "metric": "food_saved", "threshold": 5, "user_role": "customer"},
    {"title": "Waste Warrior", "description": "Save 10kg of food", "metric": "food_saved", "threshold": 10, "user_role": "customer"},
    {"title": "Waste Pro", "description": "Save 20kg of food", "metric": "food_saved", "threshold": 20, "user_role": "customer"},
    {"title": "Local Helper", "description": "Buy 1 bundle", "metric": "bundles_saved", "threshold": 1, "user_role": "customer"},
    {"title": "Local Pro", "description": "Buy 5 bundles", "metric": "bundles_saved", "threshold": 5, "user_role": "customer"},
    {"title": "Local Hero", "description": "Buy 10 bundles", "metric": "bundles_saved", "threshold": 10, "user_role": "customer"},
    {"title": "Local Legend", "description": "Buy 20 bundles", "metric": "bundles_saved", "threshold": 20, "user_role": "customer"},
    {"title": "Carbon Cutter", "description": "Save 5kg of carbon", "metric": "carbon_saved", "threshold": 5, "user_role": "customer"},
    {"title": "Carbon Champion", "description": "Save 15kg of carbon", "metric": "carbon_saved", "threshold": 15, "user_role": "customer"},
    {"title": "Carbon Conqueror", "description": "Save 25kg of carbon", "metric": "carbon_saved", "threshold": 25, "user_role": "customer"},
    {"title": "Carbon Royal", "description": "Save 50kg of carbon", "metric": "carbon_saved", "threshold": 50, "user_role": "customer"},
    {"title": "Money Saver", "description": "Save £10", "metric": "money_saved", "threshold": 10, "user_role": "customer"},
    {"title": "Money Master", "description": "Save £25", "metric": "money_saved", "threshold": 25, "user_role": "customer"},
    {"title": "Money Mogul", "description": "Save £50", "metric": "money_saved", "threshold": 50, "user_role": "customer"},
    {"title": "Money Royal", "description": "Save £100", "metric": "money_saved", "threshold": 100, "user_role": "customer"},
]

# seeds the badges defined above in the database if they do not already exist.
def seed_badges():
    with Session(engine) as session:
        # check if we already have badges in the DB
        statement = select(Badge)
        existing_badges = session.exec(statement).first()

        if not existing_badges: # if there are no existing badges, seed the default badges defined above
            print("Seeding default badges...")
            for badge_data in DEFAULT_BADGES:
                badge = Badge(**badge_data)
                session.add(badge)
            session.commit()
            print("Badges successfully seeded.")

# connects to the db using the parts declared 
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # seeds the allergens on table creation
    seed_allergens()
    seed_badges()

# used on all api calls using the db 
def get_session():
    with Session(engine) as session:
        yield session

# drops all tables
def reset_db():
    from app.models import User, Customer, Vendor
    print("Dropping all tables")
    SQLModel.metadata.drop_all(engine)
    print("Creating new tables")
    SQLModel.metadata.create_all(engine)
    
if __name__ == "__main__":
    reset_db()