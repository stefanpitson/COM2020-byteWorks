from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Customer, User, Vendor, OpenHours
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.vendors import check_opening_hours
from app.schema import LoginResponse, LoginRequest, CustomerSignupRequest, VendorSignupRequest

router = APIRouter()

# this module handles the login and registering for users

@router.post("/login", response_model=LoginResponse, tags=["Auth"], summary="Main Log in for both vendors and customers.")
def login(
    credentials: LoginRequest, 
    session: Session = Depends(get_session)
    ):
    
    # get user from db 
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    # check credentials 
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(subject=user.user_id, role=user.role)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/register/customer", tags=["Auth","Customers"], summary="Create a new customer account")
def register_customer(
    data: CustomerSignupRequest, 
    session: Session = Depends(get_session)
    ):
    
    # checks email hasnt already been used
    if session.exec(select(User).where(User.email == data.user.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(data.user.password)
    
    # user creation happens in 2 steps, fist create a user
    new_user = User(
        email=data.user.email,
        password_hash=hashed_pw,
        role="customer"
    )
    
    try:
        # add user to db
        session.add(new_user)
        session.flush() # this sends sql to the db so the id can be generated but the transaction isnt committed or finished yet

        # now the obj is added to the db, so we can get its user id 
        new_customer = Customer(
            user_id = new_user.user_id,
            name = data.customer.name,
            post_code = data.customer.post_code,
        )

        session.add(new_customer)
        session.commit() 

        return {"message": "Customer account created successfully"}

    except Exception as e:
        session.rollback() # If anything fails, undo the User creation 
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register/vendor", tags=["Auth","Vendors"], summary="Create a new vendor account")
def register_vendor(
    data: VendorSignupRequest, 
    session: Session = Depends(get_session)
    ):
    
    if session.exec(select(User).where(User.email == data.user.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(data.user.password)
    
    # user creation happens in 2 steps, fist create a user
    new_user = User(
        email=data.user.email,
        password_hash=hashed_pw,
        role="vendor"
    )
    
    try:
        session.add(new_user)
        session.flush() # this sends sql to the db so the id can be generated but the transaction isnt committed or finished yet

        # now the obj is added to the db, so we can get its user id 
        new_vendor = Vendor(
            user_id = new_user.user_id,
            name = data.vendor.name,
            city =  data.vendor.city,
            street = data.vendor.street,
            phone_number = data.vendor.phone_number,
            post_code = data.vendor.post_code,
        )

        DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        DAY_NAMES_TO_INT = {"monday" : 0, "tuesday" : 1, "wednesday" : 2, "thursday" : 3, "friday" : 4, "saturday" : 5, "sunday": 6}
        for day_name in DAY_NAMES:
            if data.vendor.opening_hours[day_name]:
                if check_opening_hours(data.vendor.opening_hours[day_name]):
                    openHour = OpenHours(vendor_id = new_vendor.vendor_id, 
                                            day = DAY_NAMES_TO_INT[day_name], 
                                            openingHour = data.vendor.opening_hours[day_name][0],
                                            closingHour = data.vendor.opening_hours[day_name][1])
                    session.add(openHour)
                    # Commits later in the try statement
                else:
                    raise HTTPException(status_code = 403, detail = ("Incorrect opening hours for " + day_name))

        session.add(new_vendor)
        session.commit()

        return {"message": "Vendor account created successfully"}

    except Exception as e:
        session.rollback() # If anything fails, undo the Vendor creation
        raise HTTPException(status_code=500, detail=str(e))
