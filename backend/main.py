from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_db_and_tables
from app.api import customers, auth, vendors
from app.core.database import engine, create_db_and_tables 
from sqlmodel import SQLModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(vendors.router, prefix="/vendors", tags=["Vendors"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

