from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Customer, User, Vendor
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schema import LoginResponse, LoginRequest, CustomerSignupRequest, VendorSignupRequest

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, session: Session = Depends(get_session)):
    
    # 1. Fetch the user by Email
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    # 2. Verify the Password
    # If user is None OR password check returns False, fail.
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # 3. Create the JWT
    # We pass the User ID as the subject, and the Role for frontend routing
    access_token = create_access_token(subject=user.user_id, role=user.role)

    # 4. Return the data
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/register/customer")
def register_customer(
    data: CustomerSignupRequest, 
    session: Session = Depends(get_session)
    ):
    
    if session.exec(select(User).where(User.email == data.user.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 1. Hash the password using Argon2
    hashed_pw = get_password_hash(data.user.password)
    
    # 2. Create the User object with the HASH, not the plain password
    new_user = User(
        email=data.user.email,
        password_hash=hashed_pw, # <--- Storing the hash
        role=data.user.role
    )
    
    try:
        session.add(new_user)
        session.flush() # this sends sql to the db so the id can be generated but the transaction isnt committed or finished yet

        new_customer = Customer(
            user_id = new_user.user_id,
            name = data.customer.name,
            post_code = data.customer.post_code,
        )

        session.add(new_customer)
        session.commit()

        return {"message": "Customer account created successfully"}

    except Exception as e:
        session.rollback() # If anything fails, undo the User creation too
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register/vendor")
def register_vendor(
    data: VendorSignupRequest, 
    session: Session = Depends(get_session)
    ):
    
    if session.exec(select(User).where(User.email == data.user.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 1. Hash the password using Argon2
    hashed_pw = get_password_hash(data.user.password)
    
    # 2. Create the User object with the HASH, not the plain password
    new_user = User(
        email=data.user.email,
        password_hash=hashed_pw, # <--- Storing the hash
        role=data.user.role
    )
    
    try:
        session.add(new_user)
        session.flush() # this sends sql to the db so the id can be generated but the transaction isnt committed or finished yet

        new_vendor = Vendor(
            user_id = new_user.user_id,
            name = data.vendor.name,
            city =  data.vendor.city,
            street = data.vendor.street,
            phone_number = data.vendor.phone_number,
            opening_hours = data.vendor.opening_hours,
            # validated: bool,
            photo = data.vendor.photo,
            post_code = data.vendor.post_code,
        )

        session.add(new_vendor)
        session.commit()

        return {"message": "Vendor account created successfully"}

    except Exception as e:
        session.rollback() # If anything fails, undo the User creation too
        raise HTTPException(status_code=500, detail=str(e))
