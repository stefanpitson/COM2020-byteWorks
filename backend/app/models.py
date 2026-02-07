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
    photo: Optional[str]
    carbon_saved: int = Field(default=0)
    user: Optional[User] = Relationship(back_populates="vendor_profile")
    validated: bool = Field(default=False)


class Customer(SQLModel, table=True):
    customer_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="user.user_id")
    name:str
    post_code:str
    store_credit: int = Field(default=0)
    carbon_saved: int = Field(default=0)
    rating: Optional[int] = Field(default=None)

    user: Optional[User] = Relationship(back_populates="customer_profile")

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

    allergens: List["Allergen"] = Relationship( # for the linking table
        back_populates="templates",             # having this means we dont have to write join statements
        link_model=Allergen_Template
    )

class Allergen(SQLModel, table=True):
    allergen_id: Optional[int] = Field(default=None, primary_key=True)
    title: str 
    description: str

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
    consumer_id: Optional[int] = Field(default=None, foreign_key="customer.customer_id") 
    time_created: Time = Field(default_factory=lambda:datetime.now().time()) 

    code: Optional[int] = Field(default=None) #shouldn't have a default? 

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
    time: Time = Field(default_factory=lambda:datetime.now().time())
    precipitation: float = Field(default_factory=lambda:random()) # may want to change this 
    bundles_posted: int 
    bundles_reserved: int 
    no_shows: int 

class Forecast_Output(SQLModel, table=True):
    output_id: Optional[int] = Field(default=None, primary_key=True)
    vendor_id: Optional[int] = Field(default=None, foreign_key="vendor.vendor_id")
    template_id: Optional[int] = Field(default=None, foreign_key="template.template_id")
    date: Date = Field(default_factory=lambda:datetime.now().date())
    reservation_prediction: int 
    no_show_prediction: int 
    rationale:str 
    confidence:float 
