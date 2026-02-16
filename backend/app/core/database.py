import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select
from app.models import Allergen

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

# connects to the db using the parts declared 
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # seeds the allergens on table creation
    seed_allergens()

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