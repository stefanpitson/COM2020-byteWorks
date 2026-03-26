# TEST CONFIGURATION FILE FOR TESTS TO WORK

from dotenv import load_dotenv
load_dotenv(".env.test") # loads the test env variables, create this locally with SECRET_KEY and HASH_ALGORITHM to test

import pytest
from fastapi import FastAPI
from app.models import Report
from fastapi.testclient import TestClient

# Retrieves all the modules and functions
from app.api.auth import router as auth_router
from app.api.customers import router as customers_router
from app.api.templates import router as templates_router
from app.api.vendors import router as vendors_router
from app.api.bundles import router as bundles_router
from app.api.reports import router as reports_router
from app.api.reservations import router as reservations_router
from app.core.database import get_session
from app.core.security import get_password_hash
from app.models import User, Vendor, Customer, Allergen # UserBase no longer exists
from uploads.issue_reports_data import issue_data_pool
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


@pytest.fixture
def session(): # to make changes to db using session in test files
    with Session(test_engine) as session:
        yield session

@pytest.fixture(scope="session")
def app():
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(customers_router, prefix="/customers")
    app.include_router(vendors_router, prefix="/vendors")
    app.include_router(templates_router, prefix="/templates")
    app.include_router(bundles_router, prefix="/bundles")
    app.include_router(reports_router, prefix="/reports")
    app.include_router(reservations_router, prefix="/reservations")
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

@pytest.fixture(autouse=True)
def seed_allergens(setup_test_db):
    with Session(test_engine) as session:
        session.add_all([
            Allergen(title="dairy"),
            Allergen(title="milk"),
            Allergen(title="gluten"),
            Allergen(title="Celery"),
            Allergen(title="Gluten"),
            Allergen(title="Crustaceans"),
            Allergen(title="Eggs"),
            Allergen(title="Fish"),
            Allergen(title="Lupin"),
            Allergen(title="Milk"),
            Allergen(title="Molluscs"),
            Allergen(title="Mustard"),
            Allergen(title="Treenuts"),
            Allergen(title="Peanuts"),
            Allergen(title="Sesame"),
            Allergen(title="Soybean"),
            Allergen(title="Sulphur Dioxide"),
        ])
        session.commit()

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
            "post_code": "EX46BH",
            "phone_number": "44 020 1234 567",
            "opening_hours": "..",
            "photo": "https://www.fotor.com/blog/how-to-take-professional-photos/"
        }
    }

    response = test_client.post("/register/vendor", json=vendor_data)
    return {
        "vendor_data": vendor_data,
        "response": response,
    }

@pytest.fixture
def registered_vendor_2(test_client):
    vendor_data = {
        "user": {
            "email": "vendor2@exeter.ac.uk",
            "password": "vendorPassWORD123",
            "role": "vendor"
        },
        "vendor": {
            "name": "vendorer_2",
            "street": "12 Pennsylvania road",
            "city": "Exeter",
            "post_code": "EX46BH",
            "phone_number": "44 020 1234 567",
            "opening_hours": "..",
            "photo": "https://www.fotor.com/blog/how-to-take-professional-photos/"
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
            "password": "Customer123",
            "role": "customer"
        },
        "customer": {
            "name": "tester",
            "post_code": "SW1A1AA"
        }
    }
    response = test_client.post("/register/customer", json=customer_data)
    return {
        "customer_data": customer_data,
        "response": response,
    }

@pytest.fixture
def customer_login_response(test_client, registered_customer):
    default_user = registered_customer["customer_data"]["user"]

    class LoginResponse(dict):
        def __call__(self, email=None, password=None): # to accomodate both formats
            response = test_client.post(
                "/login",
                json={
                    "email": email or default_user["email"],
                    "password": password or default_user["password"],
                },
            )
            return response.json()

    initial_response = test_client.post(
        "/login",
        json={
            "email": default_user["email"],
            "password": default_user["password"],
        },
    )

    return LoginResponse(initial_response.json())

@pytest.fixture
def vendor_login_response(test_client, registered_vendor):
    vendor = registered_vendor["vendor_data"]
    response = test_client.post("/login", json={
        "email": vendor["user"]["email"],
        "password": vendor["user"]["password"]
    })
    return response.json()


@pytest.fixture
def vendor_login_response_2(test_client, registered_vendor_2):
    vendor = registered_vendor_2["vendor_data"]
    response = test_client.post("/login", json={
        "email": vendor["user"]["email"],
        "password": vendor["user"]["password"]
    })
    return response.json()

@pytest.fixture
def vendor_bundle_response(test_client, vendor_login_response):
    bundles_response = test_client.get(
        f"/bundles/{vendor_login_response["user"]["user_id"]}"
    )
    return bundles_response.json()

@pytest.fixture
def template_factory(test_client, vendor_login_response):
    default_token = vendor_login_response["access_token"]
    counter = {"count": 0}

    def create(title=None, login_response=None, token=None, **overrides):
        counter["count"] += 1
        base = {
            "title": title or f"template_{counter['count']}",
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "estimated_value": 10.0,
            "cost": 5.0,
            "meat_percent": 0.33,
            "carb_percent": 0.33,
            "veg_percent": 0.33,
            "weight": 1.0,
            "is_vegan": False,
            "is_vegetarian": False,
        }
        base.update(overrides)

        auth_token = token or (login_response or {}).get("access_token") or default_token
        
        response = test_client.post(
            "/templates",
            headers={"Authorization": "Bearer " + auth_token},
            json=base
        )
        return response
    
    return create

@pytest.fixture
def registered_bundle(test_client, vendor_login_response, template_factory):
    template_factory()
    template_factory()
    token = vendor_login_response["access_token"]
    bundle_response = test_client.post("/bundles/create",
        headers={"Authorization": "Bearer " + token},
        json={"template_id": 1,
              "amount": 5
        }
    )
    return bundle_response

@pytest.fixture
def customer_factory():
    def create(
        count=1
    ):
        customers = []
        with Session(test_engine) as session:
            for i in range(count):
                email = f"customer{i}@gmail.com"

                user = User(
                    email=email,
                    password_hash=get_password_hash(f"Customer{i}"),
                    role="customer",
                )
                session.add(user)
                session.flush()

                customer = Customer(
                    user_id=user.user_id,
                    name=f"Customer{i}",
                    post_code="EX1 2HU",
                )
                session.add(customer)
                session.flush()
                
                # Extract scalar values before session closes
                customers.append({
                    "user_id": user.user_id,
                    "customer_id": customer.customer_id,
                    "email": email,
                    "password": f"Customer{i}",
                    "name": f"Customer{i}",
                })

            session.commit()

        return customers

    return create

@pytest.fixture
def vendor_factory():
    def create(
        count=1
    ):
        vendors = []
        with Session(test_engine) as session:
            for i in range(count):
                vendor_user = User(
                    email=f"admin@vendor{i}.com",
                    password_hash=get_password_hash(f"Vendor{i}"),
                    role="vendor",
                )

                session.add(vendor_user)
                session.flush()

                open_hour = random.randint(7,12)
                close_hour = random.randint(17,23)

                vendor_account = Vendor(
                    user_id=vendor_user.user_id,
                    name=f"Vendor{i}",
                    street=f"{i} street",
                    city="Exeter",
                    post_code=f"EX{i%10} {i%10}{chr(open_hour+58)}{chr(close_hour+58)}",
                    phone_number= f"01392 {random.randint(200000, 499999)}",
                    opening_hours=f"{open_hour:02}:00-{close_hour}:00",# class of days
                    validated=True,
                    carbon_saved=0,
                )

                session.add(vendor_account)
                session.flush()
                
                # Extract scalar values before session closes
                vendors.append({
                    "user_id": vendor_user.user_id,
                    "vendor_id": vendor_account.vendor_id,
                    "email": f"admin@vendor{i}.com",
                    "password": f"Vendor{i}",
                    "name": f"Vendor{i}",
                })

            session.commit()
        return vendors
    return create

import random

@pytest.fixture
def seed_reports(customer_factory, vendor_factory, session):
    customer_list = customer_factory(10)
    vendor_list = vendor_factory(10)
    # seed_list = []

    def create(count=10):
        for i in range(count):
            category = random.choice(list(issue_data_pool.keys()))
            data = issue_data_pool[category]

            title = random.choice(data["titles"])
            subject = random.choice(data["A_subjects"])
            problem = random.choice(data["B_problems"])
            feedback = random.choice(data["C_feedback"])
            full_complaint = f"{subject} {problem}\n{feedback}"
            responded = random.choice([True, False])
            response = None
            chosen_vendor = random.choice(vendor_list)
            chosen_customer = random.choice(customer_list)

            if (responded):
                response = random.choice(data["vendor_responses"])

            seeded_report = Report(
            customer_id=chosen_customer["customer_id"],
            vendor_id=chosen_vendor["vendor_id"],
            title=title,
            complaint=(
                full_complaint 
            ),
            responded=responded,
            response=response,
            )
            # seed_list.append(seeded_report)
            session.add(seeded_report)
            session.flush()
        session.commit()

    return create

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