from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import User
from app.schema import CustomerRead, CustomerUpdate
from app.api.deps import get_current_user
from app.core.security import verify_password, get_password_hash

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

@router.patch("/profile")
def update_customer_profile(
    data: CustomerUpdate, 
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    # User is already a customer 

    if data.email != None:
        # Ensures email has not already been used
        if session.exec(select(User).where(User.email == data.email)).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = data.email

    if data.name != None:
        current_user.customer_profile.name = data.name

    # Ensures both new and old password are inputted when trying to change password but does not provide an error 
    # if neither are inputted (e.g: password is not trying to be changed)
    if data.newPassword != None and data.oldPassword != None:
        if verify_password(data.oldPassword, current_user.password_hash):
            current_user.password_hash = get_password_hash(data.newPassword)
    if data.newPassword != None and data.oldPassword == None:
        raise HTTPException(status_code=400, detail="Old password is required to change new password")
    if data.newPassword == None and data.oldPassword != None:
        raise HTTPException(status_code=400, detail="New password is missing")
    
    if data.post_code != None:
        current_user.customer_profile.post_code = data.post_code

    session.add(current_user)
    session.commit()
    return {"message": "Customer updated successfully"}
    
