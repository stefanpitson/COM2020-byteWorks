def test_get_profile_success(test_client, registered_vendor, vendor_login_response):
    vendor = registered_vendor["vendor_data"]
    token = vendor_login_response["access_token"]
    profile_response = test_client.get(
        "/vendors/profile",
        headers={"Authorization": "Bearer " + token}
    )
    profile_response_data = profile_response.json()
    profile_name = profile_response_data["name"]
    profile_post_code = profile_response_data["post_code"]
    profile_vendor_id = profile_response_data["vendor_id"]

    assert vendor["vendor"]["name"] == profile_name
    assert vendor["vendor"]["post_code"] == profile_post_code
    assert profile_vendor_id > 0
    assert profile_response.status_code == 200

def test_get_profile_wrong_role_fail(test_client, customer_login_response):
    token = customer_login_response["access_token"]
    profile_response = test_client.get(
        "/vendors/profile",
        headers={"Authorization": "Bearer " + token}
    )

    profile_response_data = profile_response.json()
    assert profile_response_data["detail"] == "Not a vendor account"
    assert profile_response.status_code == 403
