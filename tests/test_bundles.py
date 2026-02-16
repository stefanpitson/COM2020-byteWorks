from datetime import datetime, timedelta

from app.schema import VendorList

def test_create_bundle_success(test_client, vendor_login_response, template_factory):
    template_factory()
    token = vendor_login_response["access_token"]
    bundle_response = test_client.post("/bundles/create",
        headers={"Authorization": "Bearer " + token},
        json={"template_id": 1,
              "amount": 5
        }
    )
    bundle_response_data = bundle_response.json()
    assert bundle_response_data["message"] == "Bundles created successfully"
    assert bundle_response.status_code == 200

def test_create_bundle_with_invalid_role(test_client, template_factory, customer_login_response):
    template_factory()
    token = customer_login_response["access_token"]
    bundle_response = test_client.post("/bundles/create",
        headers={"Authorization": "Bearer " + token},
        json={"template_id": 1,
              "amount": 5
        }
    )
    bundle_response_data = bundle_response.json()
    assert bundle_response_data["detail"] == "Not a vendor account"
    assert bundle_response.status_code == 403

def test_create_bundle_without_template_role_fail(test_client, vendor_login_response):
    token = vendor_login_response["access_token"]
    bundle_response = test_client.post("/bundles/create",
        headers={"Authorization": "Bearer " + token},
        json={"template_id": 404,
              "amount": 5
        }
    )
    bundle_response_data = bundle_response.json()
    assert bundle_response_data["detail"] == "No corresponding template"
    assert bundle_response.status_code == 400



def test_create_bundle_with_template_of_an_other_vendor_role_fail(test_client, vendor_login_response, template_factory):
    token = vendor_login_response["access_token"]
    template_factory()
    vendor_data = {
        "user": {
            "email": "vendor2@exeter.ac.uk",
            "password": "password",
            "role": "vendor"
        },
        "vendor": {
            "name": "vendorer2",
            "street": "12 Pennsylvania road",
            "city": "Exeter",
            "post_code": "EX4 6BH",
            "phone_number": "44 020 1234 567",
            "opening_hours": "..",
            "photo": "https://www.fotor.com/blog/how-to-take-professional-photos/"
        }
    }

    register_response = test_client.post("/register/vendor", json=vendor_data)

    login_response = test_client.post("/login", json={
        "email": vendor_data["user"]["email"],
        "password": vendor_data["user"]["password"]
    })
    login_response_data = login_response.json()
    token_2 = login_response_data["access_token"]

    bundle_response = test_client.post("/bundles/create",
        headers={"Authorization": "Bearer " + token_2},
        json={"template_id": 1,
              "amount": 5
        }
    )



    bundle_response_data = bundle_response.json()
    assert bundle_response_data["detail"] == "You are not the vendor of the template"
    assert bundle_response.status_code == 403

def test_get_mystore_view_of_bundles_success(test_client, vendor_login_response, registered_bundle):
    token = vendor_login_response["access_token"]
    d = datetime.now()
    if d.month <= 9:
        month = f'0{d.month}'
    else:
        month = d.month
    if d.day <= 9:
        day = f'0{d.day}'
    else:
        day = d.day
    mystore_response = test_client.get("/bundles/mystore",
        headers={"Authorization": "Bearer " + token},               
    )
    mystore_response_data = mystore_response.json()
    assert mystore_response_data["total_count"] == 5
    i = 1
    for bundle in mystore_response_data["bundles"]:
        assert bundle["bundle_id"] == i
        i+=1
        assert bundle["template_id"] == 1
        assert bundle["picked_up"] == False
        assert bundle["date"] == f"{d.year}-{month}-{day}"
        # assert time
        assert bundle["purchased_by"] == None
    assert mystore_response.status_code == 200

def test_get_mystore_view_with_no_bundles_success(test_client, vendor_login_response):
    token = vendor_login_response["access_token"]
    mystore_response = test_client.get("/bundles/mystore",
        headers={"Authorization": "Bearer " + token},               
    )
    mystore_response_data = mystore_response.json()
    assert mystore_response_data["total_count"] == 0
    assert mystore_response_data["bundles"] == []
    assert mystore_response.status_code == 200

def test_get_mystore_view_of_bundles_with_invalid_role_fail(test_client, customer_login_response):
    token = customer_login_response["access_token"]
    mystore_response = test_client.get("/bundles/mystore",
        headers={"Authorization": "Bearer " + token},               
    )
    mystore_response_data = mystore_response.json()
    assert mystore_response_data["detail"] == "Not a vendor account"
    assert mystore_response.status_code == 403

def test_get_bundle_success(test_client, vendor_login_response, registered_bundle):
    token = vendor_login_response["access_token"]
    bundle_response = test_client.get("/bundles/1",
        headers={"Authorization": "Bearer " + token},               
    )
    bundle_response_data = bundle_response.json()

    bundle_time = datetime.combine(
        datetime.today(),
        datetime.strptime(bundle_response_data["time"], "%H:%M:%S.%f").time()

    )
    now = datetime.now()
    latency = timedelta(seconds=2)
    assert bundle_response_data["bundle_id"] == 1
    assert bundle_response_data["template_id"] == 1
    assert bundle_response_data["picked_up"] == False
    assert bundle_response_data["date"] == str(datetime.now().date())
    assert bundle_response_data["date"] == str(datetime.now().date())
    assert now - latency <= bundle_time <= now + latency
    assert bundle_response_data["purchased_by"] == None
    assert bundle_response.status_code == 200

def test_get_non_existent_bundle_fail(test_client, vendor_login_response):
    token = vendor_login_response["access_token"]
    bundle_response = test_client.get("/bundles/404",
        headers={"Authorization": "Bearer " + token},               
    )
    bundle_response_data = bundle_response.json()
    assert bundle_response_data["detail"] == "Bundle not found"
    assert bundle_response.status_code == 404

def test_get_bundle_as_wrong_vendor_role_fail(test_client, vendor_login_response_2, registered_bundle):
    token = vendor_login_response_2["access_token"]
    bundle_response = test_client.get("/bundles/1",
        headers={"Authorization": "Bearer " + token},               
    )
    bundle_response_data = bundle_response.json()
    assert bundle_response_data["detail"] == "Not corresponding vendor account"
    assert bundle_response.status_code == 403
