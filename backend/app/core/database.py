import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

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

# connects to the db using the parts declared 
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# used on all api calls using the db 
def get_session():
    with Session(engine) as session:
        yield session

# drops all tables
def reset_db():
    print("Dropping all tables")
    SQLModel.metadata.drop_all(engine)
    create_db_and_tables()

if __name__ == "__main__":
    reset_db()