# THIS SCRIPT MUST BE RUN FROM INSIDE BACKEND FOLDER  -> BECAUSE FUNCTION IMPORTS FROM FILES ONLY WORK FROM BACKEND FOLDER
# WITH COMMAND python -m pytest -v -s <FULL PATH TO TEST_AUTH.PY> -W ignore::DeprecationWarning
# CREATE A .env.test FILE INSIDE backend/ WITH SECRET_KEY and HASH_ALGORITHM PARAMETERS FOR TESTING
# CREATE A SECRET_KEY IN THE TERMINAL WITH COMMAND python -c "import secrets; print(secrets.token_urlsafe(32))" 
# HASH_ALGORITHM=256

# TESTS  FOLLOW Given-When-Then naming convention of tests

from dotenv import load_dotenv
load_dotenv(".env.test") # loads the test env variables, create this locally with SECRET_KEY and HASH_ALGORITHM to test

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Retrieves all the modules and functions
from app.api.auth import router
from app.core.database import get_session
from app.core.security import get_password_hash
from app.models import UserBase, User, Vendor, Customer
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

app = FastAPI()
app.include_router(router)
app.dependency_overrides[get_session] = get_test_session
testClient = TestClient(app=app, base_url="https://bytework.online/")


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

def test_register_login_success():
    test_email = "test2@exeter.ac.uk"
    test_password = "password456"

    register_response = testClient.post("/register/customer", 
        json = {
            "user": {
                "email": test_email,
                "password": test_password,
                "role": "customer"
            },
            "customer": {
                "name": "tester",
                "post_code": "ab1 2cd"
            }
    })

    login_response = testClient.post("/login", json={
        "email": test_email, 
        "password": test_password
    })

    login_response_data = login_response.json()


    assert register_response.status_code == 200
    assert register_response.text == "{\"message\":\"Customer account created successfully\"}"

    assert login_response_data["user"]["email"] == test_email
    assert login_response_data["user"]["role"] == "customer"
    assert login_response.status_code == 200


def test_login_fail():
    login_response = testClient.post("/login", json={
        "email": "test@exeter.ac.uk", 
        "password": "password456"
    })
    
    assert login_response.status_code == 401
    assert login_response.text == "{\"detail\":\"Incorrect email or password\"}"

def test_repeat_register_fail():
    test_email = "test2@exeter.ac.uk"
    test_password = "password456"

    register_response = testClient.post("/register/customer", 
        json = {
            "user": {
                "email": test_email,
                "password": test_password,
                "role": "customer"
            },
            "customer": {
                "name": "tester",
                "post_code": "ab1 2cd"
            }
    })
    register_response_2 = testClient.post("/register/customer", 
        json = {
            "user": {
                "email": test_email,
                "password": test_password,
                "role": "customer"
            },
            "customer": {
                "name": "tester",
                "post_code": "ab1 2cd"
            }
    })

    assert register_response.status_code == 200
    assert register_response.text == "{\"message\":\"Customer account created successfully\"}"

    assert register_response_2.status_code == 400
    assert register_response_2.text == "{\"detail\":\"Email already registered\"}"

