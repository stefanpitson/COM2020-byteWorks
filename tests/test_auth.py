## All function parameters can be found within conftest.py
import pytest

def test_customer_register_success(test_client, registered_customer):
    '''Register a customer account with valid details'''
    register_response = registered_customer["response"]

    assert register_response.text == "{\"message\":\"Customer account created successfully\"}"
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

@pytest.mark.parametrize("input_value, expected", [
    ("InvalidEmail", True),
    ("InvalidEmail@",True),
    ("@InvalidEmail",True),
    ("a"*255 + "@example.com", True),
])
def test_invalid_email_register_fail(test_client, input_value, expected):    
    customer_data = {
        "user": {
            "email": "InvalidEmail",
            "password": "password456",
            "role": "customer"
        },
        "customer": {
            "name": "tester",
            "post_code": "ab1 2cd"
        }
    }
    register_response = test_client.post("/register/customer", json=customer_data)
    
    assert register_response.text == "{\"message\":\"Invalid email\"}"
    assert register_response.status_code == 400

def test_customer_login_fail(test_client):
    '''Login without an existing account'''

    login_response = test_client.post("/login", json={
        "email": "test@exeter.ac.uk", 
        "password": "password456"
    })
    
    assert login_response.status_code == 401
    assert login_response.text == "{\"detail\":\"Incorrect email or password\"}"

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

    assert register_response_1.status_code == 200
    assert register_response_1.text == "{\"message\":\"Customer account created successfully\"}"

    assert register_response_2.status_code == 400
    assert register_response_2.text == "{\"detail\":\"Email already registered\"}"


# VENDOR RELATED TESTS

def test_vendor_register_success(test_client, registered_vendor):
    register_response = registered_vendor["response"] 

    assert register_response.status_code == 200
    assert register_response.text == "{\"message\":\"Vendor account created successfully\"}"

def test_vendor_login_success(test_client, registered_vendor): # registered vendor is a fixture in conftest.py
    vendor = registered_vendor["vendor_data"]
    login_response = test_client.post("/login", json={
        "email": vendor["user"]["email"], 
        "password": vendor["user"]["password"]
    })

    login_response_data = login_response.json()

    assert login_response_data["user"]["email"] == vendor["user"]["email"]
    assert login_response_data["user"]["role"] == "vendor"
    assert login_response.status_code == 200


def test_vendor_login_success(test_client): # registered vendor is a fixture in conftest.py
    login_response = test_client.post("/login", json={
        "email": "vendor@exeter.ac.uk", 
        "password": "passwrod31"
    })

    assert login_response.status_code == 401
    assert login_response.text == "{\"detail\":\"Incorrect email or password\"}"

