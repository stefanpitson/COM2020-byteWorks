def test_get_profile_success(test_client, registered_vendor):
    vendor = registered_vendor["vendor_data"]
    login_response = test_client.post("/login", json={
        "email": vendor["user"]["email"], 
        "password": vendor["user"]["password"]
    })
    login_response_data = login_response.json()
    token = login_response_data["access_token"]
    profile_response = test_client.get(
        "/vendors/profile",
        headers={"Authorization": "Bearer " + token}
    )
    profile_response_data = profile_response.json()
    profile_name = profile_response_data["name"]
    profile_post_code = profile_response_data["post_code"]
    profile_vendor_id = profile_response_data["vendor_id"]

    assert profile_response.status_code == 200
    assert vendor["vendor"]["name"] == profile_name
    assert vendor["vendor"]["post_code"] == profile_post_code
    assert profile_vendor_id > 0

def test_get_profile_wrong_role_fail(test_client ,registered_customer):
    customer = registered_customer["customer_data"]
    login_response = test_client.post("/login", json={
        "email": customer["user"]["email"], 
        "password": customer["user"]["password"]
    })

    login_response_data = login_response.json()
    token = login_response_data["access_token"]

    profile_response = test_client.get(
        "/vendors/profile",
        headers={"Authorization": "Bearer " + token}
    )

    assert profile_response.text == "{\"detail\":\"Not a vendor account\"}"
    assert profile_response.status_code == 403

# def test_get_profile_with_no_account_fail(test_client, registered_vendor):
#     '''Login, recieve JWT token, delete account (if that functiontionality is added), then attempt get profile'''

#     # ...

#     # assert profile_response.text == "{\"detail\":\"Profile not found\"}"
#     # assert profile_response.status_code == 404
