from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import User
from app.schema import VendorRead
from app.api.deps import get_current_user

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