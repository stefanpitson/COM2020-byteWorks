from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import User
from app.schema import VendorRead, VendorUpdate
from app.api.deps import get_current_user
from app.core.security import verify_password, get_password_hash
from ukpostcodeutils import validation

router = APIRouter()

# pulls the vendor profile 
@router.get("/profile", response_model= VendorRead, tags=["Vendors"], summary="Get the Vendor Profile for the User logged in")
def get_vendor_profile(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Not a vendor account")
        
    if not current_user.vendor_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return current_user.vendor_profile

@router.patch("/profile")
def update_vendor_profile(
    data: VendorUpdate, 
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Not a vendor account")
        
    if not current_user.vendor_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # User is already a vendor 

    if data.user.email != None:
        if session.exec(select(User).where(User.email == data.user.email)).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = data.user.email

    if data.vendor.name != None:
        current_user.vendor_profile.name = data.vendor.name

    if data.user.newPassword != None and data.user.oldPassword != None:
        if verify_password(data.user.oldPassword, current_user.password_hash):
            current_user.password_hash = get_password_hash(data.user.newPassword)
    if data.user.newPassword == None and data.user.oldPassword != None:
        raise HTTPException(status_code=400, detail="Old password is required to change new password")
    if data.user.newPassword != None and data.user.oldPassword == None:
        raise HTTPException(status_code=400, detail="New password is missing")
    
    # Maybe will provide future validation if decided with frontend
    if data.vendor.street != None:
         current_user.vendor_profile.street = data.vendor.street

    if data.vendor.city != None:
         current_user.vendor_profile.city = data.vendor.city

    if data.vendor.post_code != None:
        parsed_postcode = (data.vendor.post_code).upper().replace(" ","")
        if not validation.is_valid_postcode(parsed_postcode):
                    raise HTTPException(status_code=400, detail="Postcode is not valid")
        current_user.vendor_profile.post_code = data.customer.post_code

    if data.vendor.phone_number != None:
         current_user.vendor_profile.phone_number = data.vendor.phone_number
    
    # May have to change when opening houts implementation is done properly
    if data.vendor.opening_hours != None:
         current_user.vendor_profile.opening_hours = data.vendor.opening_hours
    
    # May have to change when photo implementation is done properly
    if data.vendor.photo != None:
         current_user.vendor_profile.photo = data.vendor.photo

    session.add(current_user)
    session.commit()
    return {"message": "Customer updated successfully"}