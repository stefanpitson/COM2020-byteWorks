from tempfile import template
from turtle import title
import pytest

def test_create_template_without_allergies_success(test_client, vendor_login_response):
    token = vendor_login_response["access_token"]
    template_response = test_client.post(f"/templates",
        headers={"Authorization": "Bearer " + token},
        json={
            "title": "test_title",
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam aliquet pretium leo, in eleifend enim tristique mollis. Etiam ac mattis sem. Nunc massa mi, faucibus id facilisis id, euismod et ante. Mauris viverra dapibus dui at gravida. In ut lacus semper, imperdiet lectus quis, tincidunt sapien. Donec pretium eros quis sem placerat, vel scelerisque elit ultrices.",
            "estimated_value": 5.0,
            "cost": 10.0,
            "meat_percent": 0.2,
            "carb_percent": 0.7,
            "veg_percent": 0.1,
            "weight": 1.0,
            "is_vegan": False,
            "is_vegetarian": False,
            # no allergens
        }                 
    )
    template_response_data = template_response.json()
    assert template_response_data["message"] == 'Template created successfully'
    assert template_response_data["template_id"] == 1
    assert template_response.status_code == 200

def test_create_template_with_valid_allergies_success(test_client, vendor_login_response):
    token = vendor_login_response["access_token"]
    template_response = test_client.post(f"/templates",
        headers={"Authorization": "Bearer " + token},
        json={
            "title": "test_title",
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam aliquet pretium leo, in eleifend enim tristique mollis. Etiam ac mattis sem. Nunc massa mi, faucibus id facilisis id, euismod et ante. Mauris viverra dapibus dui at gravida. In ut lacus semper, imperdiet lectus quis, tincidunt sapien. Donec pretium eros quis sem placerat, vel scelerisque elit ultrices.",
            "estimated_value": 5.0,
            "cost": 10.0,
            "meat_percent": 0.2,
            "carb_percent": 0.7,
            "veg_percent": 0.1,
            "weight": 1.0,
            "is_vegan": False,
            "is_vegetarian": False,
            "allergen_titles": ["dairy", "gluten"]
        }                 
    )
    template_response_data = template_response.json()
    assert template_response_data["message"] == 'Template created successfully'
    assert template_response_data["template_id"] == 1
    assert template_response.status_code == 200

@pytest.mark.parametrize("input_value", [
    (["dairy", "FalseAllergy"]),
    (["FalseAllergy"]),
    ([""]),
], ids=["One valid allergy, one invalid allergy", "One invalid allergy", "Empty"])
def test_create_template_with_invalid_allergies_fail(test_client, vendor_login_response, input_value):
    token = vendor_login_response["access_token"]
    template_response = test_client.post(f"/templates",
        headers={"Authorization": "Bearer " + token},
        json={
            "title": "test_title",
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam aliquet pretium leo, in eleifend enim tristique mollis. Etiam ac mattis sem. Nunc massa mi, faucibus id facilisis id, euismod et ante. Mauris viverra dapibus dui at gravida. In ut lacus semper, imperdiet lectus quis, tincidunt sapien. Donec pretium eros quis sem placerat, vel scelerisque elit ultrices.",
            "estimated_value": 5.0,
            "cost": 10.0,
            "meat_percent": 0.2,
            "carb_percent": 0.7,
            "veg_percent": 0.1,
            "weight": 1.0,
            "is_vegan": False,
            "is_vegetarian": False,
            "allergen_titles": input_value
        }                 
    )
    template_response_data = template_response.json()
    assert template_response_data["detail"] == 'One or more Allergen titles are invalid'
    assert template_response.status_code == 400

def test_create_template_wrong_role_fail(test_client, customer_login_response):
    token = customer_login_response["access_token"]
    template_response = test_client.post(f"/templates",
        headers={"Authorization": "Bearer " + token},
        json={
            "title": "test_title",
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam aliquet pretium leo, in eleifend enim tristique mollis. Etiam ac mattis sem. Nunc massa mi, faucibus id facilisis id, euismod et ante. Mauris viverra dapibus dui at gravida. In ut lacus semper, imperdiet lectus quis, tincidunt sapien. Donec pretium eros quis sem placerat, vel scelerisque elit ultrices.",
            "estimated_value": 5.0,
            "cost": 10.0,
            "meat_percent": 0.2,
            "carb_percent": 0.7,
            "veg_percent": 0.1,
            "weight": 1.0,
            "is_vegan": False,
            "is_vegetarian": False,
            # no allergens
        }                 
    )
    template_response_data = template_response.json()
    assert template_response_data["detail"] == 'Not a vendor account'
    assert template_response.status_code == 403

def test_create_same_template_twice_fail(template_factory):
    template_response = template_factory(title="template_1")
    template_response_2 = template_factory(title="template_1")
    template_response_data = template_response.json()
    template_response_data_2 =  template_response_2.json()

    assert template_response_data["message"] == 'Template created successfully'
    assert template_response_data["template_id"] == 1
    assert template_response.status_code == 200

    assert template_response_data_2["detail"] == 'Template already registered'
    assert template_response_2.status_code == 400

def test_create_template_with_invalid_percentages(test_client, vendor_login_response):
   token = vendor_login_response["access_token"]
   template_response = test_client.post(f"/templates",
        headers={"Authorization": "Bearer " + token},
        json={
            "title": "test_title",
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam aliquet pretium leo, in eleifend enim tristique mollis. Etiam ac mattis sem. Nunc massa mi, faucibus id facilisis id, euismod et ante. Mauris viverra dapibus dui at gravida. In ut lacus semper, imperdiet lectus quis, tincidunt sapien. Donec pretium eros quis sem placerat, vel scelerisque elit ultrices.",
            "estimated_value": 5.0,
            "cost": 10.0,
            "meat_percent": 0.2,
            "carb_percent": 0.7,
            "veg_percent": 0.6,
            "weight": 1.0,
            "is_vegan": False,
            "is_vegetarian": False,
            # no allergens
        }                 
    )
   template_response_data = template_response.json()
   assert template_response_data["detail"] == "Percentages do not add up to 1"
   assert template_response.status_code == 400

def test_get_template_success(test_client, vendor_login_response, template_factory):
    token = vendor_login_response["access_token"]
    template_factory()
    template_response = test_client.get("/templates/1", headers={"Authorization": "Bearer " + token})
    template_response_data = template_response.json()
    assert template_response_data["title"] == "template_1"
    assert template_response_data["description"] == "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    assert template_response_data["cost"] == 5.0
    assert template_response_data["meat_percent"] == 0.33
    assert template_response_data["carb_percent"] == 0.33
    assert template_response_data["veg_percent"] == 0.33
    assert template_response_data["is_vegan"] == False
    assert template_response_data["is_vegetarian"] == False

def test_get_template_that_does_not_exist_fail(test_client, vendor_login_response):
    token = vendor_login_response["access_token"]
    template_response = test_client.get("/templates/404", headers={"Authorization": "Bearer " + token})
    template_response_data = template_response.json()
    assert template_response_data["detail"] == "Template not found"
    assert template_response.status_code == 404


# parametrize this
def test_get_list_of_templates_from_a_vendor_success(test_client, vendor_login_response, template_factory):
    for i in range(10):
        t = template_factory()

    token = vendor_login_response["access_token"]
    templates_list_response = test_client.get("/templates/vendor/1", headers={"Authorization": "Bearer " + token})
    templates_list_response_data = templates_list_response.json()
    assert templates_list_response_data["total_count"] == 10
    i = 1
    for template in templates_list_response_data["templates"]:
        assert template["template_id"] == i
        assert template["title"] == f"template_{i}"
        i+=1

def test_get_list_of_templates_of_a_wrong_vendor_fail(test_client, vendor_login_response):
    token = vendor_login_response["access_token"]
    templates_list_response = test_client.get("/templates/vendor/2", headers={"Authorization": "Bearer " + token})
    templates_list_response_data = templates_list_response.json()
    assert templates_list_response_data["detail"] == "Not the correct vendor"
    assert templates_list_response.status_code == 403

# def test_get_number_of_bundles_for_a_template_success(test_client):
#     return