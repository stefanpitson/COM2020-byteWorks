from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.core.database import get_session, engine
from app.core.security import get_password_hash
from app.models import Template, Allergen, Bundle, Reservation, Customer, Vendor, Streak, User
from app.schema import VendorList
from app.api.deps import get_current_user


router = APIRouter()

# user functions

@router.delete("/users/{user_id}", tags=["Admin"], summary="delete a user account")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
    ):

    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="must be an admin to delete accounts")
    
    statement = select(User).where(User.user_id == user_id)
    user = session.exec(statement).first()

    if not user: 
        raise HTTPException(status_code=404, detail="user not found")

    try:
        if user.role == "vendor":
            statement = select(Vendor).where(Vendor.vendor_id == user.vendor_profile.vendor_id)
            vendor = session.exec(statement).first()
            session.delete(vendor)
        # we dont need to delete customer profiles
        session.delete(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return {"message":f"user {user_id} deleted successfully"}

# vendor functions 

@router.get("/vendors", tags=["Admin","Vendors"], summary="Get list of vendors to be verified")
def get_vendors(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
    )-> VendorList:

    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="must be an admin to view uncertified vendors")
    
    statement = select(Vendor).where(Vendor.validated == False)
    vendors = session.exec(statement).all()

    return {
        "total_count": len(vendors),
        "vendors":vendors
    }

@router.patch("/vendor/validate/{vendor_id}", tags=["Admin","Vendors"], summary="valdiate a vendor as an admin")
def validate_vendor(
    vendor_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
    ):

    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="must be an admin to validate vendors")
    
    statement = select(Vendor).where(Vendor.vendor_id == vendor_id)
    vendor = session.exec(statement).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    if vendor.validated:
        raise HTTPException(status_code=400, detail="vendor is already validated")
    
    vendor.validated = True
    try:
        session.add(vendor)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# delete vendor bundles and templates -- do this in bundles / templates 

# viewing all the reports uses the same endpoints as normal 

def create_admin():
    with Session(engine) as session:
        admin = User(email = "admin@byte.com", password_hash= get_password_hash("adminPass"), role ="admin")
        try:
            session.add(admin)
            session.commit()
            print("admin added successfully")
        except Exception as e:
            session.rollback()
            print(f"error: {str(e)}")

if __name__ == "__main__":
    # create an admin account 
   create_admin()
    