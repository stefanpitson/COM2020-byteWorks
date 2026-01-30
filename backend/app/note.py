from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship, JSON, Column

# ==========================================
# 1. BASE MODELS (Shared Interfaces)
# These prevent you from typing the same fields twice.
# ==========================================

class UserBase(SQLModel):
    email: str
    role: str = "customer" # "customer" or "seller"

class VendorBase(SQLModel):
    name: str
    street: str
    city: str
    postCode: str
    phone_number: str
    validated: bool = False
    carbon_saved: int = 0
    photo: Optional[str] = None
    # We use sa_column to tell the DB to store this strictly as JSON
    opening_hours: Dict = Field(default={}, sa_column=Column(JSON))

class CustomerBase(SQLModel):
    name: str
    postCode: str
    store_credit: int = 0
    carbon_saved: int = 0
    rating: int = 5

# ==========================================
# 2. DATABASE TABLES (table=True)
# These represent your actual PostgreSQL tables.
# ==========================================

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str # Only the User table stores the password!
    
    # RELATIONSHIPS
    # These let you access user.vendor or user.customer in Python
    # 'sa_relationship_kwargs' ensures if you delete a User, the profile is deleted too
    vendor_profile: Optional["Vendor"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"uselist": False}
    )
    customer_profile: Optional["Customer"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"uselist": False}
    )

class Vendor(VendorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # FOREIGN KEY: This links this specific Vendor to a specific User
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    # Back link to access vendor.user
    user: Optional[User] = Relationship(back_populates="vendor_profile")

class Customer(CustomerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # FOREIGN KEY
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    user: Optional[User] = Relationship(back_populates="customer_profile")

# ==========================================
# 3. API SCHEMAS (table=False)
# These are used for Request bodies and Responses
# ==========================================

# -- CREATE SCHEMAS (What React sends to Python) --

class UserCreate(UserBase):
    password: str # Plain text password from frontend

class VendorCreate(VendorBase):
    pass # Inherits all fields from VendorBase

# -- READ SCHEMAS (What Python sends to React) --

# When we send a user back, we DO NOT want to include the password
class UserRead(UserBase):
    id: int

# A special schema that includes the User info inside the Vendor info
class VendorReadWithUser(VendorBase):
    id: int
    user: UserRead # Nested object!