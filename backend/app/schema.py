from pydantic import BaseModel
from app.models import UserBase, CustomerBase, VendorBase

# when creating a new user, we need the password, email, and role
class UserCreate(UserBase):
    password: str

# when logging in a user, we need the password, email, but role can be blank
class UserLogin(UserBase):
    password: str

# when we want to retrieve the user, the id is nice to have but the password musnt be shared
class UserRead(UserBase):
    user_id:int


# when we want to retrieve the user, the id is nice to have but the password musnt be shared
class CustomerRead(CustomerBase):
    customer_id:int

class VendorRead(VendorBase):
    vendor_id:int

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRead 

class LoginRequest(BaseModel):
    email: str
    password: str

# --- Part B: The Composite Schemas (The "Envelope") ---
# This is what the API actually expects to receive
class CustomerSignupRequest(BaseModel):
    user: UserCreate
    customer: CustomerBase

class VendorSignupRequest(BaseModel):
    user: UserCreate
    vendor: VendorBase