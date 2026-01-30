from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class UserBase(SQLModel):
    email: str
    role: str

class CustomerBase(SQLModel):
    name: str
    post_code: str

class VendorBase(SQLModel):
    name: str
    street: str
    city: str
    post_code: str
    phone_number: str
    opening_hours: str # Should be JSON
    photo: str


class User(UserBase, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    password_hash:str

    vendor_profile: Optional["Vendor"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"uselist": False}
    )
    customer_profile: Optional["Customer"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"uselist": False}
    )

class Vendor(VendorBase, table=True):
    vendor_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="user.user_id")
    carbon_saved: int = Field(default=0)

    user: Optional[User] = Relationship(back_populates="vendor_profile")
    # validated: bool = Field(default=False)   DEBATED


class Customer(CustomerBase, table=True):
    customer_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="user.user_id")
    store_credit: int = Field(default=0)
    carbon_saved: int = Field(default=0)
    rating: Optional[int] = Field(default=None)

    user: Optional[User] = Relationship(back_populates="customer_profile")
