def test_register_login_success(test_client):
    test_email = "test2@exeter.ac.uk"
    test_password = "password456"

    register_response = test_client.post("/register/customer", 
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

    login_response = test_client.post("/login", json={
        "email": test_email, 
        "password": test_password
    })

    login_response_data = login_response.json()


    assert register_response.status_code == 200
    assert register_response.text == "{\"message\":\"Customer account created successfully\"}"

    assert login_response_data["user"]["email"] == test_email
    assert login_response_data["user"]["role"] == "customer"
    assert login_response.status_code == 200


def test_login_fail(test_client):
    login_response = test_client.post("/login", json={
        "email": "test@exeter.ac.uk", 
        "password": "password456"
    })
    
    assert login_response.status_code == 401
    assert login_response.text == "{\"detail\":\"Incorrect email or password\"}"

def test_repeat_register_fail(test_client):
    test_email = "test2@exeter.ac.uk"
    test_password = "password456"

    register_response = test_client.post("/register/customer", 
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

    assert register_response.status_code == 200
    assert register_response.text == "{\"message\":\"Customer account created successfully\"}"

    assert register_response_2.status_code == 400
    assert register_response_2.text == "{\"detail\":\"Email already registered\"}"

# VENDOR RELATED TESTS


