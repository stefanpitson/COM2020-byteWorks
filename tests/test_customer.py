def test_get_profile_success(test_client, registered_customer):
    customer = registered_customer["customer_data"]
    login_response = test_client.post("/login", json={
        "email": customer["user"]["email"], 
        "password": customer["user"]["password"]
    })

    login_response_data = login_response.json()
    token = login_response_data["access_token"]
    profile_response = test_client.get(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token}
    )
    profile_response_data = profile_response.json()
    profile_name = profile_response_data["name"]
    profile_post_code = profile_response_data["post_code"]
    profile_customer_id = profile_response_data["customer_id"]

    assert profile_response.status_code == 200
    assert customer["customer"]["name"] == profile_name
    assert customer["customer"]["post_code"] == profile_post_code
    assert profile_customer_id > 0

def test_get_profile_wrong_role_fail(test_client ,registered_vendor):
    vendor = registered_vendor["vendor_data"]
    login_response = test_client.post("/login", json={
        "email": vendor["user"]["email"], 
        "password": vendor["user"]["password"]
    })

    login_response_data = login_response.json()
    token = login_response_data["access_token"]

    profile_response = test_client.get(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token}
    )

    assert profile_response.text == "{\"detail\":\"Not a customer account\"}"
    assert profile_response.status_code == 403

def test_get_profile_with_no_account_fail(test_client, registered_customer):
    '''Login, recieve JWT token, delete account (if that functiontionality is added), then attempt get profile'''

    # ...

    # assert profile_response.text == "{\"detail\":\"Profile not found\"}"
    # assert profile_response.status_code == 404
