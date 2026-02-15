import json


def test_get_profile_success(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.get(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token}
    )
    profile_response_data = profile_response.json()
    profile_name = profile_response_data["name"]
    profile_post_code = profile_response_data["post_code"]
    profile_customer_id = profile_response_data["customer_id"]

    assert customer["customer"]["name"] == profile_name
    assert customer["customer"]["post_code"] == profile_post_code
    assert profile_customer_id > 0
    assert profile_response.status_code == 200

def test_get_profile_wrong_role_fail(test_client, registered_vendor, vendor_login_response):
    vendor = registered_vendor["vendor_data"]
    token = vendor_login_response["access_token"]

    profile_response = test_client.get(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token}
    )

    profile_response_data = profile_response.json()
    assert profile_response_data["detail"] == "Not a customer account"
    assert profile_response.status_code == 403


def test_patch_profile_password_success(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": 
            {
                "old_password": customer["user"]["password"],
                "new_password": "myNewPassword123"
            },

            "customer": {}
        }
    )
    profile_response_data = profile_response.json()
    assert profile_response_data["message"] == "Customer updated successfully"
    assert profile_response.status_code == 200

def test_patch_profile_email_success(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": 
            {
                "email": "myNewEmail@exeter.ac.uk"
            },

            "customer": {}
        }
    )
    profile_response_data = profile_response.json()
    assert profile_response_data["message"] == "Customer updated successfully"
    assert profile_response.status_code == 200

def test_patch_profile_name_success(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": {},
            "customer": 
            {
                "name": "myNewName"
            }
        }
    )
    profile_response_data = profile_response.json()
    assert profile_response_data["message"] == "Customer updated successfully"
    assert profile_response.status_code == 200

def test_patch_profile_post_code_success(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": {},
            "customer": 
            {
                "post_code": "XY9 8WS"
            }
        }
    )
    profile_response_data = profile_response.json()
    assert profile_response_data["message"] == "Customer updated successfully"
    assert profile_response.status_code == 200


def test_patch_profile_missing_new_password_fail(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": 
            {
                "old_password": customer["user"]["password"]
            },

            "customer": {}
        }
    )
    profile_response_data = profile_response.json()
    assert profile_response_data["detail"] == "New password is missing"
    assert profile_response.status_code == 400
 
def test_patch_profile_missing_old_password_fail(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": 
            {
                "new_password": "myNewPassword123"
            },

            "customer": {}
        }
    )
    profile_response_data = profile_response.json()
    assert profile_response_data["detail"] == "Old password is required to change new password"
    assert profile_response.status_code == 400

def test_patch_profile_same_email_fail(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": 
            {
                "email": customer["user"]["email"]
            },
            "customer": {}
        }
    )
    profile_response_data = profile_response.json()
    assert profile_response_data["detail"] == "Email already registered"
    assert profile_response.status_code == 400

def test_patch_profile_same_name_fail(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": {},
            "customer": 
            {
                "name": customer["customer"]["name"]
            }
        }
    )
    profile_response_data = profile_response.json()
    assert profile_response_data["message"] == "Customer updated successfully"
    assert profile_response.status_code == 200

def test_patch_profile_same_post_code_fail(test_client, registered_customer, customer_login_response):
    customer = registered_customer["customer_data"]
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": {},
            "customer": 
            {
                "post_code": customer["customer"]["post_code"]
            }
        }
    )
    profile_response_data = profile_response.json()
    assert profile_response_data["message"] == "Customer updated successfully"
    assert profile_response.status_code == 200

# def test_get_profile_with_no_account_fail(test_client, registered_customer):
#     '''Login, recieve JWT token, delete account (if that functiontionality is added), then attempt get profile'''

#     # ...

#     # assert profile_response.text == "{\"detail\":\"Profile not found\"}"
#     # assert profile_response.status_code == 404
