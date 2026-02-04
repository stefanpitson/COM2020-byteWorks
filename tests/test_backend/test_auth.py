# THIS SCRIPT MUST BE RUN FROM INSIDE BACKEND FOLDER  -> BECAUSE FUNCTION IMPORTS FROM FILES ONLY WORK FROM BACKEND FOLDER
# WITH COMMAND python -m pytest -v -s <FULL PATH TO TEST_AUTH.PY>
# CREATE A .env.test FILE INSIDE backend/ WITH SECRET_KEY and HASH_ALGORITHM parameters for testing

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
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


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

def test_register_success():
    register_response = testClient.post("/customer/signup", 
        json = {
            "email": "test2@exeter.ac.uk",
            "password": "password456",
            "name": "tester",
    })
    assert register_response.status_code == 200
    print(register_response.text)

    login_response = testClient.post("/login", json={
        "email": "test2@exeter.ac.uk", 
        "password": "password456"
    })
    
    assert login_response.status_code == 200



# def test_login_success():
#     response = testClient.post("/login", json={
#         "email": "test@exeter.ac.uk", 
#         "password": "password456"
#     })
    
#     assert response.status_code == 200
#     data = response.json()
#     print(data)

