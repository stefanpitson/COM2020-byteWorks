from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from datetime import date, time

# schemas contains what the frontend will send and expect in return 

# profile reads 
# when we want to retrieve the user, the id is nice to have but the password mustn't be shared

class CustomerRead(BaseModel):
    customer_id: int
    name: str
    post_code: str
    store_credit: float

class VendorRead(BaseModel):
    vendor_id: int
    name: str
    street: str
    city: str
    post_code: str
    phone_number: str
    opening_hours: str
    photo: Optional[str]

# ___AUTH SCHEMAS___  

#login
class LoginRequest(BaseModel):
    email: str
    password: str

# information returned on log in
class LoginResponse(BaseModel):
    access_token: str # <--- access token for future authentication 
    token_type: str
    user: UserData
    class UserData(BaseModel):
        user_id: int
        email: str
        role: str

# sign up for customer
class CustomerSignupRequest(BaseModel):
    user: UserData
    class UserData(BaseModel):
        email: str
        password: str
        role: str

    customer: CustomerData
    class CustomerData(BaseModel):
        name: str
        post_code: str

# sign up for vendor 
class VendorSignupRequest(BaseModel):
    user: UserData
    class UserData(BaseModel):
        email: str
        password: str
        role: str
    vendor: VendorData
    class VendorData(BaseModel):
        name: str
        street: str
        city: str
        post_code: str
        phone_number: str
        opening_hours: str

#data for updating the customer 
# all are optional as only updated information is given
class CustomerUpdate(BaseModel):
    user: UserUpdateData
    class UserUpdateData(BaseModel):
        email: Optional[str] = None
        old_password : Optional[str] = None
        new_password : Optional[str] = None

    customer: CustomerUpdateData
    class CustomerUpdateData(BaseModel):
        name: Optional[str] = None
        post_code: Optional[str] = None

#data for updating the vendor 
class VendorUpdate(BaseModel):
    user: UserUpdateData

    class UserUpdateData(BaseModel):
        email: Optional[str] = None
        old_password : Optional[str] = None
        new_password : Optional[str] = None

    vendor: VendorUpdateData

    class VendorUpdateData(BaseModel):
        name: Optional[str] = None
        post_code: Optional[str] = None
        street: Optional[str] = None
        city: Optional[str] = None
        phone_number: Optional[str] = None
        opening_hours: Optional[str] = None    

# ___ TEMPLATES & BUNDLES ___

#templates
class TemplateCreate(BaseModel):
    title: str
    description: str
    estimated_value: float
    cost: float
    meat_percent: float
    carb_percent: float
    veg_percent: float
    # carbon save removed and now calculated
    weight: float
    is_vegan: bool
    is_vegetarian: bool
    # This is the key: the frontend sends a list of existing Allergen IDs
    allergen_titles: List[str] = []

# returns the information on each bundle
class TemplateRead(BaseModel):
    template_id: int
    title: str
    description: str
    cost: float
    meat_percent: float
    carb_percent: float
    veg_percent: float
    carbon_saved: float
    is_vegan: bool
    is_vegetarian: bool
    vendor: int
    photo: Optional[str]
    allergens: List["AllergenRead"] = []
    class AllergenRead(BaseModel):
        allergen_id: int
        title: str

# list of templates returned for a specific vendor
class TemplateList(BaseModel):
    total_count: int
    templates: List[TemplateRead]

# bundle create is small as all the detail is auto generated on back end or in template
class BundleCreate(BaseModel):
    template_id: int
    amount: int

#for viewing one bundle
class BundleRead(BaseModel):
    bundle_id: int
    template_id: int
    picked_up: bool 
    date: date
    time: time
    purchased_by: int | None

# for the customer view of a vendor page
class CustBundleList(BaseModel):
    total_count: int
    bundles: List[BundleData]
    class BundleData(BaseModel):
        template_id: int
        title: str
        estimated_value: float 
        cost: float 
        available_count: int

# for the vendor view of their bundles 
class VendBundleList(BaseModel):
    total_count:int
    bundles: List[BundleRead]
    class BundleData(BaseModel):
        bundle_id: int
        template_id: int
        picked_up: bool 
        date: date
        time: time
        purchased_by: int | None

class VendReservationRead(BaseModel):
    reservation_id : int
    bundle_id : int
    customer_id : int
    time_created : time
    status : str

class CustReservationRead(BaseModel):
    reservation_id : int
    bundle_id : int
    customer_id : int
    time_created : datetime
    code : int
    status : str

class CustReservationList(BaseModel):
    total_count:int
    bundles: List[CustReservationRead]

class VendReservationList(BaseModel):
    total_count:int
    bundles: List[VendReservationRead]
# get all stores
class VendorList(BaseModel):
    total_count:int
    vendors: List[VendorData]
    class VendorData(BaseModel):
        vendor_id: int
        name:str
        photo: str | None # may not have a photo
        post_code: str
        bundle_count: int
        has_vegan: bool
        has_vegetarian: bool

class PickupCode(BaseModel):
    pickup_code: int

class StreakRead(BaseModel):
    streak_id: int
    customer_id: int
    count: int
    started: date
    last: date
    ended:bool

