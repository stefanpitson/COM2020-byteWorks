def test_post_create_report_success(test_client, customer_login_response, registered_vendor):
    token = customer_login_response["access_token"]
    report_response = test_client.post("/reports/create",
                                       headers={"Authorization": "Bearer "+token},
                                       json={
                                            "vendor_id": 1,
                                            "title": "Food not as expected",
                                            "complaint":"When I arrived my chicken sandwhich contained no chicken!"
                                       })
    report_response_data = report_response.json()
    assert report_response_data == {'message': 'Report created successfully', 'report_id': 1}
    assert report_response.status_code == 200

def test_post_create_report_with_title_of_invalid_length_fail(test_client, customer_login_response, registered_vendor):
    token = customer_login_response["access_token"]
    report_response = test_client.post("/reports/create",
                                       headers={"Authorization": "Bearer "+token},
                                       json={
                                            "vendor_id": 1,
                                            "title": "A"*65,
                                            "complaint":"When I arrived my chicken sandwhich contained no chicken!"
                                       })
    report_response_data = report_response.json()
    assert report_response_data == {'detail': 'Title of an invalid length.'}
    assert report_response.status_code == 422

def test_post_create_report_with_complaint_of_invalid_length_fail(test_client, customer_login_response, registered_vendor):
    token = customer_login_response["access_token"]
    report_response = test_client.post("/reports/create",
                                       headers={"Authorization": "Bearer "+token},
                                       json={
                                            "vendor_id": 1,
                                            "title": "Vendor was rude",
                                            "complaint":"A"*1025
                                       })
    report_response_data = report_response.json()
    assert report_response_data == {'detail': 'Complaint of an invalid length.'}
    assert report_response.status_code == 422