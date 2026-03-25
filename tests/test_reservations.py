def test_post_reserve_bundle_success(test_client, customer_login_response, registered_bundle):
    token = customer_login_response["access_token"]
    reservation_response = test_client.post("reservations/1/reserve",
                                            headers={"Authorization": "Bearer " + token})
    reservation_response_data = reservation_response.json()
    assert reservation_response_data["message"] == "Reservation created successfully"
    assert reservation_response_data["reservation_id"] == 1
    assert reservation_response.status_code == 200

def test_post_reserve_bundle_when_no_bundle_exist_fail(test_client, customer_login_response, template_factory):
    template_factory()
    token = customer_login_response["access_token"]
    reservation_response = test_client.post("reservations/1/reserve",
                                            headers={"Authorization": "Bearer " + token})
    reservation_response_data = reservation_response.json()
    assert reservation_response_data["detail"] == "No bundle found for that template on the current day"
    assert reservation_response.status_code == 404
