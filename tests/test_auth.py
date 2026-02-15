## All function parameters can be found within conftest.py
import pytest

def test_customer_register_success(test_client, registered_customer):
    '''Register a customer account with valid details'''
    register_response = registered_customer["response"]
    register_response_data = register_response.json()

    assert register_response_data["message"] == "Customer account created successfully"
    assert register_response.status_code == 200

def test_customer_login_success(test_client, registered_customer):
    '''Login with a registered account'''
    customer = registered_customer["customer_data"]

    login_response = test_client.post("/login", json={
        "email": customer["user"]["email"], 
        "password": customer["user"]["password"]
    })

    login_response_data = login_response.json()

    assert login_response_data["user"]["email"] == customer["user"]["email"]
    assert login_response_data["user"]["role"] == "customer"
    assert login_response.status_code == 200

@pytest.mark.parametrize("input_value", [
    (""),
    ("InvalidEmail"),
    ("InvalidEmail@"),
    ("@InvalidEmail"),
    ("a"*255 + "@example.com"),
])
def test_invalid_email_register_fail(test_client, input_value):    
    customer_data = {
        "user": {
            "email": input_value,
            "password": "password456",
            "role": "customer"
        },
        "customer": {
            "name": "tester",
            "post_code": "ab1 2cd"
        }
    }
    register_response = test_client.post("/register/customer", json=customer_data)
    register_response_data = register_response.json()
    
    assert register_response_data["message"] == "Invalid email"
    assert register_response.status_code == 400

def test_customer_login_fail(test_client):
    '''Login without an existing account'''

    login_response = test_client.post("/login", json={
        "email": "test@exeter.ac.uk", 
        "password": "password456"
    })
    login_response_data = login_response.json()
    
    assert login_response_data["detail"] == "Incorrect email or password"
    assert login_response.status_code == 401

def test_customer_repeat_register_fail(test_client, registered_customer):
    '''Register user with same details twice'''

    register_response_1 = registered_customer["response"]

    test_email = "test2@exeter.ac.uk"
    test_password = "password456"

    register_response_2 = test_client.post("/register/customer", 
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
    register_response_data_1 = register_response_1.json()
    register_response_data_2 = register_response_2.json()

    assert register_response_data_1["message"] == "Customer account created successfully"
    assert register_response_1.status_code == 200

    assert register_response_data_2["detail"] == "Email already registered"
    assert register_response_2.status_code == 400


# VENDOR RELATED TESTS

def test_vendor_register_success(test_client, registered_vendor):
    register_response = registered_vendor["response"]
    register_response_data = register_response.json()
    assert register_response_data["message"] == "Vendor account created successfully"
    assert register_response.status_code == 200

def test_vendor_login_success(test_client, registered_vendor):
    vendor = registered_vendor["vendor_data"]
    login_response = test_client.post("/login", json={
        "email": vendor["user"]["email"], 
        "password": vendor["user"]["password"]
    })

    login_response_data = login_response.json()

    assert login_response_data["user"]["email"] == vendor["user"]["email"]
    assert login_response_data["user"]["role"] == "vendor"
    assert login_response_data["user"]["user_id"] > 0
    assert login_response.status_code == 200


def test_vendor_login_fail(test_client):
    login_response = test_client.post("/login", json={
        "email": "vendor@exeter.ac.uk", 
        "password": "passwrod31"
    })
    login_response_data = login_response.json()

    assert login_response_data["detail"] == "Incorrect email or password"
    assert login_response.status_code == 401

