from sqlmodel import select
from app.models import User, Customer, Streak, Badge, User_Badge
from datetime import datetime, timedelta
import pytest

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

def test_patch_profile_email_success(test_client, customer_login_response):
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

def test_patch_profile_name_success(test_client, customer_login_response):
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

def test_patch_profile_post_code_success(test_client, customer_login_response):
    token = customer_login_response["access_token"]
    profile_response = test_client.patch(
        "/customers/profile",
        headers={"Authorization": "Bearer " + token},
        json=
        {
            "user": {},
            "customer": 
            {
                "post_code": "SW1A 1AA"
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
 
def test_patch_profile_missing_old_password_fail(test_client, customer_login_response):
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

def test_get_streak_of_zero_success(test_client, customer_login_response):
    token = customer_login_response["access_token"]
    streak_response = test_client.get("/customers/streak",
                                      headers={"Authorization": "Bearer " + token}
                                      )
    streak_response_data = streak_response.json()
    assert streak_response_data == None
    assert streak_response.status_code == 200

def test_get_streak_success(test_client, registered_customer, session, customer_login_response):
    email = registered_customer["customer_data"]["user"]["email"] # grab customers email
    user = session.exec(select(User).where(User.email == email)).first() # grab user record
    customer = session.exec(select(Customer).where(Customer.user_id == user.user_id)).first() # grab customer record

    started = datetime.now().date() - timedelta(days=10)
    last = datetime.now().date() - timedelta(days=1)

    streak = Streak(
        customer_id=customer.customer_id,
        started=started,
        last=last,
        count=10,
        ended=False,
    )  # seeded customer with streak of 10
    session.add(streak)
    session.commit()
    session.refresh(streak)

    token = customer_login_response["access_token"]
    streak_response = test_client.get("/customers/streak",
                                      headers={"Authorization": "Bearer " + token}
                                      )
    
    streak_response_data = streak_response.json()
    assert streak_response_data == {'streak_id': 1, 'customer_id': 1, 'count': 10, 'started': started.isoformat(), 'last': last.isoformat(), 'ended': False}
    assert streak_response.status_code == 200

def test_post_add_credit_using_mastercard_success(test_client, customer_login_response):
    token = customer_login_response["access_token"]
    credit_response = test_client.post("/customers/addcredit",
                     headers={"Authorization": "Bearer " + token},
                     json={"credit_top_up": 15.0,
                           "first_line_address": "15 Sidwell Street",
                           "postcode": "EX4 6NN",
                           "name_on_card": "Joe Andrews",
                           "card_number": "5555555555554444",
                           "expiry_date": "2026-10-31",
                           "cvv": "123"})
    credit_response_data = credit_response.json()
    
    assert credit_response_data == {'message': 'Credit added successfully'}
    assert credit_response.status_code == 200

def test_post_add_credit_using_visa_success(test_client, customer_login_response):
    token = customer_login_response["access_token"]
    credit_response = test_client.post("/customers/addcredit",
                     headers={"Authorization": "Bearer " + token},
                     json={"credit_top_up": 15.0,
                           "first_line_address": "15 Sidwell Street",
                           "postcode": "EX4 6NN",
                           "name_on_card": "Joe Andrews",
                           "card_number": "4111111111111111",
                           "expiry_date": "2026-10-31",
                           "cvv": "123"})
    credit_response_data = credit_response.json()
    assert credit_response_data == {'message': 'Credit added successfully'}
    assert credit_response.status_code == 200


def test_post_add_credit_using_amex_success(test_client, customer_login_response):
    token = customer_login_response["access_token"]
    credit_response = test_client.post("/customers/addcredit",
                     headers={"Authorization": "Bearer " + token},
                     json={"credit_top_up": 15.0,
                           "first_line_address": "15 Sidwell Street",
                           "postcode": "EX4 6NN",
                           "name_on_card": "Joe Andrews",
                           "card_number": "378282246310005",
                           "expiry_date": "2026-10-31",
                           "cvv": "1234"})
    credit_response_data = credit_response.json()
    assert credit_response_data == {'message': 'Credit added successfully'}
    assert credit_response.status_code == 200


@pytest.mark.parametrize("payload,expected_detail,expected_status", [
    # Invalid credit sizes
    ({"credit_top_up": 3.0, "first_line_address": "15 Sidwell Street", "postcode": "EX4 6NN", "name_on_card": "Joe Andrews", "card_number": "5555555555554444", "expiry_date": "2026-10-31", "cvv": "123"}, "Outside of the credit top-up range", 404),
    ({"credit_top_up": 150.0, "first_line_address": "15 Sidwell Street", "postcode": "EX4 6NN", "name_on_card": "Joe Andrews", "card_number": "5555555555554444", "expiry_date": "2026-10-31", "cvv": "123"}, "Outside of the credit top-up range", 404),
    # Invalid postcode
    ({"credit_top_up": 15.0, "first_line_address": "15 Sidwell Street", "postcode": "INVALID", "name_on_card": "Joe Andrews", "card_number": "5555555555554444", "expiry_date": "2026-10-31", "cvv": "123"}, "Postcode is not valid", 404),
    # Empty first line address
    ({"credit_top_up": 15.0, "first_line_address": "", "postcode": "EX4 6NN", "name_on_card": "Joe Andrews", "card_number": "5555555555554444", "expiry_date": "2026-10-31", "cvv": "123"}, "First line address is empty", 404),
    # Empty name
    ({"credit_top_up": 15.0, "first_line_address": "15 Sidwell Street", "postcode": "EX4 6NN", "name_on_card": "", "card_number": "5555555555554444", "expiry_date": "2026-10-31", "cvv": "123"}, "No name entered", 404),
    # Expired card
    ({"credit_top_up": 15.0, "first_line_address": "15 Sidwell Street", "postcode": "EX4 6NN", "name_on_card": "Joe Andrews", "card_number": "5555555555554444", "expiry_date": "2020-10-31", "cvv": "123"}, "Debit/Credit Card is expired", 404),
    # Invalid CVV 
    ({"credit_top_up": 15.0, "first_line_address": "15 Sidwell Street", "postcode": "EX4 6NN", "name_on_card": "Joe Andrews", "card_number": "5555555555554444", "expiry_date": "2026-10-31", "cvv": "ABC"}, "CVV should only include digits", 404),
    # Invalid card number format
    ({"credit_top_up": 15.0, "first_line_address": "15 Sidwell Street", "postcode": "EX4 6NN", "name_on_card": "Joe Andrews", "card_number": "1234567890123456", "expiry_date": "2026-10-31", "cvv": "123"}, "Card number is not valid", 404),
    # Wrong CVV length for Mastercard (needs 3)
    ({"credit_top_up": 15.0, "first_line_address": "15 Sidwell Street", "postcode": "EX4 6NN", "name_on_card": "Joe Andrews", "card_number": "5555555555554444", "expiry_date": "2026-10-31", "cvv": "1234"}, "CVV should be three digits for Visa or Mastercard", 404),
    # Wrong CVV length for AMEX (needs 4)
    ({"credit_top_up": 15.0, "first_line_address": "15 Sidwell Street", "postcode": "EX4 6NN", "name_on_card": "Joe Andrews", "card_number": "378282246310005", "expiry_date": "2026-10-31", "cvv": "123"}, "CVV should be four digits for American Express", 404),
], ids=[
    "credit_top_up_too_low",
    "credit_top_up_too_high",
    "invalid_postcode",
    "empty_first_line_address",
    "empty_name_on_card",
    "expired_card",
    "non_numeric_cvv",
    "invalid_card_number_format",
    "wrong_cvv_length_mastercard",
    "wrong_cvv_length_amex",
])
def test_post_add_credit_with_invalid_or_missing_fields_fail(test_client, customer_login_response, payload, expected_detail, expected_status):
    token = customer_login_response["access_token"]
    credit_response = test_client.post("/customers/addcredit",
                     headers={"Authorization": "Bearer " + token},
                     json=payload)
    credit_response_data = credit_response.json()
    assert credit_response_data["detail"] == expected_detail
    assert credit_response.status_code == expected_status

def test_get_badges_owned_with_zero_badges_success(test_client, customer_login_response):
    token = customer_login_response["access_token"]
    badges_response = test_client.get("/customers/badges/owned",
                                      headers={"authorization":"Bearer "+token})
    badges_response_data = badges_response.json()
    assert badges_response_data == {'total_count': 0, 'badges': []}
    assert badges_response.status_code == 200

def test_get_badges_owned_with_multiple_badges_success(test_client, registered_customer, session, customer_login_response):
    email = registered_customer["customer_data"]["user"]["email"] # grab customers email
    user = session.exec(select(User).where(User.email == email)).first() # grab user record

    badge = Badge(
        title="Saved 10 Meals",
        description="Awarded for saving 10 meals",
        user_role="customer",
        metric="food_saved",
        threshold=10,
    )

    session.add(badge)
    session.commit()
    session.refresh(badge)

    user_badge = User_Badge(user_id=user.user_id, badge_id=badge.badge_id)

    session.add(user_badge)
    session.commit()

    token = customer_login_response["access_token"]
    badges_response = test_client.get("/customers/badges/owned",
                                      headers={"authorization":"Bearer "+token})
    badges_response_data = badges_response.json()

    assert badges_response_data["total_count"] == 1
    assert len(badges_response_data["badges"]) == 1
    assert badges_response.status_code == 200

