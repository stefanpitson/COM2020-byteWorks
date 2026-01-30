from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_db_and_tables
from app.api import customers, auth, vendors
from app.core.database import engine, create_db_and_tables 
from sqlmodel import SQLModel

# this function will handle the start up, and shut down of the app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # things written above yeild happen when the app starts 
    # like creating the db
    create_db_and_tables()
    yield
    # write shut down here

# starts fast api app 
app = FastAPI(lifespan=lifespan)

# for local run 
# NEEDS CHANGING FOR DEPLOYMENT 
origins = ["http://localhost:5173", "http://localhost:3000"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# allows all the other calls from the other files, like a import ____ 
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(vendors.router, prefix="/vendors", tags=["Vendors"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
# ADD NEW API MODULES HERE eg. bundles 
