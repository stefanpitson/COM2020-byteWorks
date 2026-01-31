from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import User
from app.schema import CustomerRead
from app.api.deps import get_current_user


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

