import os
from dotenv import load_dotenv # Import this
from typing import List, Optional
from fastapi import FastAPI, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.middleware.cors import CORSMiddleware


# --- 1. LOAD SECRETS ---
load_dotenv() # This loads the variables from .env

# Get the URL from the environment variable
# If it's missing, the app will crash (which is good, so you know it's missing)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables")

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- 2. DATA MODELS ---
# This class defines what our data looks like in Python AND the Database
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

# --- 3. APP CONFIGURATION ---
app = FastAPI()

# Allow React to talk to this backend
origins = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run this when the server starts to create the table if it doesn't exist
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- 4. API ENDPOINTS ---

@app.post("/users/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/", response_model=List[User])
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users
