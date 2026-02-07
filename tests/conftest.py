# TEST CONFIGURATION FILE FOR TESTS TO WORK

from dotenv import load_dotenv
load_dotenv(".env.test") # loads the test env variables, create this locally with SECRET_KEY and HASH_ALGORITHM to test

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Retrieves all the modules and functions
from app.api.auth import router as auth_router
from app.api.customers import router as customers_router
from app.core.database import get_session
from app.core.security import get_password_hash
from app.models import User, Vendor, Customer # UserBase no longer exists
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine, Session


TEST_DATABASE_URL = "sqlite://"  # local database for testing
test_engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

def get_test_session():
    with Session(test_engine) as session:
        yield session

@pytest.fixture(scope="session")
def app():
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(customers_router, prefix="/customers")
    app.dependency_overrides[get_session] = get_test_session
    return app

@pytest.fixture(scope="session")
def test_client(app):
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    SQLModel.metadata.create_all(test_engine) # setup local test database
    yield # tests run at this point
    SQLModel.metadata.drop_all(test_engine) # destroy local test database


# FUNCTION FOR CREATING EXISTING USERS IN THE DATABASE DIRECTLY
# test_user() must then be passed into the test function
# @pytest.fixture
# def test_user():
#     with Session(test_engine) as session:
#         test_user = User(
#             email="test@exeter.ac.uk",
#             password_hash=get_password_hash("password123"),
#             role="customer"
#         )
#         session.add(test_user)
#         session.commit()
#         session.refresh(test_user)
#         return test_user