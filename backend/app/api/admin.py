from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select 
from app.core.database import get_session, engine
from app.core.security import get_password_hash
from app.models import Vendor, User, Customer
from app.schema import AdminVendorList, AllUsers
from app.api.deps import get_current_user


router = APIRouter()

# user functions

@router.delete("/users/{user_id}", tags=["Admin"], summary="Delete a user account")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
    ):

    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail = "Cannot delete your own admin account.")

    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Must be an admin to delete accounts.")
    
    statement = select(User).where(User.user_id == user_id)
    user = session.exec(statement).first()

    if not user: 
        raise HTTPException(status_code=404, detail="User not found.")

    try:
        if user.role == "vendor":
            statement = select(Vendor).where(Vendor.vendor_id == user.vendor_profile.vendor_id)
            vendor = session.exec(statement).first()
            session.delete(vendor)

        elif user.role == "customer":
            statement = select(Customer).where(Customer.customer_id == user.customer_profile.customer_id)
            customer = session.exec(statement).first()
            session.delete(customer)
            
        session.delete(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return {"message":f"user {user_id} deleted successfully"}

# vendor functions 

@router.get("/vendors", response_model=AdminVendorList, tags=["Admin","Vendors"], summary="Get list of vendors to be verified")
def get_vendors(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
    ):

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
    return { "message": f"Vendor {vendor_id} validated"}
# delete vendor bundles and templates -- do this in bundles / templates 

# viewing all the reports uses the same endpoints as normal 

def create_admin():
    with Session(engine) as session:
        statement = select(User).where(User.email == "admin@byte.com")
        existing = session.exec(statement).first()

        if existing:
            print("admin already exists")
            return
        
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
    

@router.get("/users", response_model=AllUsers, tags=["Admin"], summary="Get all users for the admin view")
def get_all_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
    ):

    if current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Must be an admin to view all accounts.")
    
    users = session.exec(select(User)).all()

    trunked = [
        {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role
        } for user in users
    ]

    return { "total_count":len(trunked), "users":trunked }
