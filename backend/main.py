from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_db_and_tables
from app.api import customers, auth, vendors, bundles, templates
from app.core.database import engine, create_db_and_tables 
from sqlmodel import SQLModel
import os

# this function will handle the start up, and shut down of the app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # things written above yield happen when the app starts 
    # like creating the db
    create_db_and_tables()
    yield
    # write shut down here

# starts fast api app 
app = FastAPI(lifespan=lifespan)

# for local run 
# NEEDS CHANGING FOR DEPLOYMENT? 
origins = ["http://localhost:5173", "http://localhost:3000", "https://bytework.online"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# passes on requests to the correct corresponding file
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(vendors.router, prefix="/vendors", tags=["Vendors"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(templates.router, prefix="/templates", tags=["Templates"])
app.include_router(bundles.router, prefix="/bundles", tags=["Bundles"])
# ADD NEW API ROUTES HERE eg. bundles 
