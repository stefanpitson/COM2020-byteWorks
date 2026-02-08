# TEST CONFIGURATION FILE FOR TESTS TO WORK

from dotenv import load_dotenv
load_dotenv(".env.test") # loads the test env variables, create this locally with SECRET_KEY and HASH_ALGORITHM to test

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Retrieves all the modules and functions
from app.api.auth import router as auth_router
from app.api.customers import router as customers_router
from app.api.vendors import router as vendors_router
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
    app.include_router(vendors_router, prefix="/vendors")
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


@pytest.fixture
def registered_vendor(test_client):
    vendor_data = {
        "user": {
            "email": "vendor@exeter.ac.uk",
            "password": "vendorPassWORD123",
            "role": "vendor"
        },
        "vendor": {
            "name": "vendorer",
            "street": "12 Pennsylvania road",
            "city": "Exeter",
            "post_code": "EX4 6BH",
            "phone_number": "44 020 1234 567",
            "opening_hours": "..",
            "photo": ".."
        }
    }

    response = test_client.post("/register/vendor", json=vendor_data)
    return {
        "vendor_data": vendor_data,
        "response": response,
    }

@pytest.fixture
def registered_customer(test_client):
    customer_data = {
        "user": {
            "email": "test2@exeter.ac.uk",
            "password": "password456",
            "role": "customer"
        },
        "customer": {
            "name": "tester",
            "post_code": "ab1 2cd"
        }
    }
    response = test_client.post("/register/customer", json=customer_data)
    return {
        "customer_data": customer_data,
        "response": response,
    }



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