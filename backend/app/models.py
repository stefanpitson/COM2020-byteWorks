from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date as Date, time as Time, datetime
from random import random

# models establishes the object types for the database 


class User_Badge(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="user.user_id")
    badge_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="badge.badge_id")

class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    password_hash:str
    email:str
    role: str

    vendor_profile: Optional["Vendor"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"uselist": False}
    )
    customer_profile: Optional["Customer"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"uselist": False}
    )

    badges: List["Badge"] = Relationship( # for the linking table
        back_populates="users",             # having this means we dont have to write join statements
        link_model=User_Badge
    )

class Badge(SQLModel, table=True):
    badge_id: Optional[int] = Field(default=None, primary_key=True)
    title:str 
    description: str
    user_role:str = Field(default="user")

    users: List["User"] = Relationship( # for the linking table
        back_populates="badges",         # having this means we dont have to write join statements
        link_model=User_Badge
    )

class Vendor(SQLModel, table=True):
    vendor_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="user.user_id")
    name: str
    street: str
    city: str
    post_code: str
    phone_number: str
    opening_hours: str
    photo: Optional[str] = Field(default=None)
    total_revenue: float = Field(default=0.0) 
    carbon_saved: float = Field(default=0.0)
    food_saved: float = Field(default=0.0)
    user: Optional[User] = Relationship(back_populates="vendor_profile")
    validated: bool = Field(default=False)


class Customer(SQLModel, table=True):
    customer_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="user.user_id")
    name:str
    post_code:str
    store_credit: float = Field(default=100.0)
    carbon_saved: float = Field(default=0.0)
    rating: Optional[int] = Field(default=None)

    user: Optional[User] = Relationship(back_populates="customer_profile")

class Streak(SQLModel, table=True):
    streak_id: Optional[int] =Field(default=None, primary_key=True)
    customer_id: Optional[int] =Field(foreign_key="customer.customer_id")
    count: int = Field(default=0)
    started: Date
    last: Date
    ended: bool = Field(default=False)

class Allergen_Template(SQLModel,table=True): # linking table, has to come before the other entities 
    allergen_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="allergen.allergen_id")
    template_id: Optional[int] = Field(default = None, primary_key=True, foreign_key="template.template_id")

class Template(SQLModel, table=True):
    template_id: Optional[int] = Field(default=None, primary_key=True)
    title: str 
    description: str 
    estimated_value: float 
    cost: float 
    
    meat_percent: float
    carb_percent: float
    veg_percent: float
    carbon_saved: Optional[float]
    weight: float
    is_vegan: bool = Field(default=False)
    is_vegetarian: bool = Field(default=False)

    vendor: Optional[int] = Field(default=None,foreign_key="vendor.vendor_id")

    photo: Optional[str] = Field(default=None)

    allergens: List["Allergen"] = Relationship( # for the linking table
        back_populates="templates",             # having this means we dont have to write join statements
        link_model=Allergen_Template
    )

class Allergen(SQLModel, table=True):
    allergen_id: Optional[int] = Field(default=None, primary_key=True)
    title: str 

    templates: List["Template"] = Relationship( # for the linking table
        back_populates="allergens",             # having this means we dont have to write join statements
        link_model=Allergen_Template
    )


class Bundle(SQLModel, table=True):
    bundle_id: Optional[int] = Field(default=None, primary_key=True)
    template_id: Optional[int] = Field( default=None, foreign_key="template.template_id")
    picked_up: bool = Field(default= False)
    date: Date = Field(default_factory=lambda: datetime.now().date()) # basically tells the db to use this function to populate it
    time: Time = Field(default_factory=lambda: datetime.now().time())

    purchased_by: Optional[int] = Field(default=None, foreign_key="customer.customer_id")


class Reservation(SQLModel, table=True):
    reservation_id:Optional[int] = Field(default=None, primary_key=True)
    bundle_id: Optional[int] = Field(default=None, foreign_key="bundle.bundle_id")
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.customer_id") 
    time_created: datetime = Field(default_factory=datetime.now)

    # status either:
    # 'booked' - reservation made, not collected 
    # 'collected' - the customer collects 
    # 'no_show' - the customer is a no show (when booked and not cancelled and they didn't turn up)
    # 'cancelled' - the customer/vendor cancelled the booking (when booked and purposefully cancelled - different to no show)
    status: str = Field(default="booked") 

    code: Optional[int] = Field(default=None) #shouldn't have a default 

class Report(SQLModel, table=True):
    report_id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.customer_id")
    vendor_id: Optional[int] = Field(default=None, foreign_key="vendor.vendor_id")
    title: str
    complaint: str
    responded: bool = Field(default=False)
    response: Optional[str]

class Forecast_Input(SQLModel, table=True):
    record_id: Optional[int] = Field(default=None, primary_key=True)
    vendor_id: Optional[int] = Field(default=None, foreign_key="vendor.vendor_id")
    template_id: Optional[int] = Field(default=None, foreign_key="template.template_id")

    #time the bundles were posted, this should be able to grab from bundles table, but 
    # could have issues if there aren't any
    date: Date = Field(default_factory=lambda:datetime.now().date()) # basically tells the db to use this function to populate it
    slot_start: Time # this is the start of the 2 HOUR SLOT representing time POSTED
    slot_end: Time # this is the end of the 2 HOUR SLOT representing time POSTED
    discount: float = Field(default = 0.0) # number 0 - 1 indicating the level of discount from original price e.g. 0.3 = 30% discount
    precipitation: float = Field(default = -1.0)
    bundles_posted: int = Field(default = 0)
    bundles_reserved: int = Field(default = 0.0)
    no_shows: int = Field(default = 0.0)

class Forecast_Output(SQLModel, table=True):
    output_id: Optional[int] = Field(default=None, primary_key=True)
    vendor_id: Optional[int] = Field(default=None, foreign_key="vendor.vendor_id")
    template_id: Optional[int] = Field(default=None, foreign_key="template.template_id")
    date: Date = Field(default_factory=lambda:datetime.now().date()) # predcited day to sell
    slot_start: Time # this is the start of the 2 HOUR SLOT representing time predicted sale time
    slot_end: Time # this is the end of the 2 HOUR SLOT representing time predicted sale time
    model_type: str = Field(default = "seasonal_naive") # to show what model made the predicition since many different models could make the same forecast
    reservation_prediction: int # how many of these bundles will be sell
    no_show_prediction: int 
    recomendation: str
    rationale:str 
    confidence:float 
