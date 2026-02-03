# import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib") # removing warning for readability
# # warnings currently not ignored

from dotenv import load_dotenv
load_dotenv(".env.test") # loads the test env variables

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.auth import router
from app.core.database import get_session
from app.core.security import get_password_hash
from app.models import UserBase, User, Vendor, Customer
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine, Session


TEST_DATABASE_URL = "sqlite://" 
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
    """Create tables before each test and drop after"""
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def test_user():
    with Session(test_engine) as session:
        test_user = User(
            email="test@exeter.ac.uk",
            password_hash=get_password_hash("password123"),
            role="customer"
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        return test_user

def test_login_success(test_user):
    response = testClient.post("/login", json={
        "email": "test@exeter.ac.uk", 
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    print(data)

