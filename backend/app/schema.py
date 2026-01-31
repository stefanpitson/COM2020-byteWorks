from pydantic import BaseModel
from app.models import UserBase, CustomerBase, VendorBase

# This file defines the class/object structure for passing between the front and backend 

# when creating a new user, we need the password, email, and role
class UserCreate(UserBase):
    password: str
    role: str

# when logging in a user, we need the password and email 
class UserLogin(UserBase):
    password: str

# when we want to retrieve the user, the id is nice to have but the password musnt be shared
class UserRead(UserBase):
    user_id:int
    role: str

# when we want to retrieve the user, the id is nice to have but the password musnt be shared
class CustomerRead(CustomerBase):
    customer_id:int

class VendorRead(VendorBase):
    vendor_id:int

# This is what the API actually expects to receive
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRead 

class LoginRequest(BaseModel):
    email: str
    password: str

class CustomerSignupRequest(BaseModel): # could be moved into auth.py
    user: UserCreate
    customer: CustomerBase

class VendorSignupRequest(BaseModel):
    user: UserCreate
    vendor: VendorBase