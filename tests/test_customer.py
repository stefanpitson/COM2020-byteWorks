def test_get_profile_success(test_client):
    # Retrieving customer profile using a valid token
    test_email = "test2@exeter.ac.uk"
    test_password = "password456"
    test_name = "tester"
    test_post_code = "ab1 2cd"

    register_response = test_client.post("/register/customer", 
        json = {
            "user": {
                "email": test_email,
                "password": test_password,
                "role": "customer"
            },
            "customer": {
                "name": test_name,
                "post_code": test_post_code
            }
    })

    login_response = test_client.post("/login", json={
        "email": test_email, 
        "password": test_password
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
    assert test_name == profile_name
    assert test_post_code == profile_post_code
    assert profile_customer_id > 0

