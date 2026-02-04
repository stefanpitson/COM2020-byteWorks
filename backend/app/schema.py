from pydantic import BaseModel

# schemas contains what the frontend will send and expect in return 

# profile reads
# when we want to retrieve the user, the id is nice to have but the password musnt be shared

class CustomerRead(BaseModel):
    customer_id: int
    name: str
    post_code: str

class VendorRead(BaseModel):
    vendor_id: int
    name: str
    street: str
    city: str
    post_code: str
    phone_number: str
    opening_hours: str
    photo: str


# ___AUTH SCHEMAS___  

#login
class LoginRequest(BaseModel):
    email: str
    password: str

# This is what the API actually expects to receive
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserData
     # Nested class to keep the JSON structure
    class UserData(BaseModel):
        user_id: int
        email: str
        role: str

# sign up 
class CustomerSignupRequest(BaseModel):
    user: UserData
    # Nested class to keep the JSON structure
    class UserData(BaseModel):
        email: str
        password: str
        role: str

    customer: CustomerData
    # Nested class to keep the JSON structure
    class CustomerData(BaseModel):
        name: str
        post_code: str


class VendorSignupRequest(BaseModel):
    user: UserData
    # Nested class to keep the JSON structure
    class UserData(BaseModel):
        email: str
        password: str
        role: str

    vendor: VendorData
    # Nested class to keep the JSON structure
    class VendorData(BaseModel):
        name: str
        street: str
        city: str
        post_code: str
        phone_number: str
        opening_hours: str
        photo: str
    
# more to come vvv 