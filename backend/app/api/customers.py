from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import User
from app.schema import CustomerRead, CustomerUpdate
from app.api.deps import get_current_user
from app.core.security import verify_password, get_password_hash
from ukpostcodeutils import validation

router = APIRouter()

@router.get("/profile", response_model= CustomerRead, tags=["Customers"], summary="Get the Customer Profile for the User logged in")
def get_customer_profile(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Not a customer account")
        
    if not current_user.customer_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return current_user.customer_profile

@router.patch("/profile", tags = ["Customers"], summary = "Updating the settings of customer's accounts")
def update_customer_profile(
    data: CustomerUpdate, 
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Not a customer account")
        
    if not current_user.customer_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    

    # User is already a customer 

    if data.user.email != None:
        # Ensures email has not already been used
        if session.exec(select(User).where(User.email == data.user.email)).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = data.user.email

    if data.customer.name != None:
        current_user.customer_profile.name = data.customer.name

    # Ensures both new and old password are inputted when trying to change password but does not provide an error 
    # if neither are inputted (e.g: password is not trying to be changed)
    if data.user.new_password != None and data.user.old_password != None:
        if verify_password(data.user.old_password, current_user.password_hash):
            current_user.password_hash = get_password_hash(data.user.new_password)
    if data.user.new_password != None and data.user.old_password == None:
        raise HTTPException(status_code=400, detail="Old password is required to change new password")
    if data.user.new_password == None and data.user.old_password != None:
        raise HTTPException(status_code=400, detail="New password is missing")
    
    if data.customer.post_code != None:
        parsed_postcode = (data.customer.post_code).upper().replace(" ","")
        if not validation.is_valid_postcode(parsed_postcode):
                    raise HTTPException(status_code=400, detail="Postcode is not valid")
        current_user.customer_profile.post_code = data.customer.post_code
    try:
        session.add(current_user)
        session.commit()
    except Exception as e:
        session.rollback() # If anything fails
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Customer updated successfully"}
    
