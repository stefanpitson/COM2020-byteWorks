from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select, func, case, and_
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select, func, case, and_
from app.core.database import get_session
from app.models import User, Bundle, Template, Reservation, Vendor
from app.schema import VendorRead, CustBundleList, VendorList, VendorUpdate
from app.models import User, Bundle, Template, Reservation, Vendor
from app.schema import VendorRead, CustBundleList, VendorList, VendorUpdate
from app.api.deps import get_current_user
import uuid
import shutil
from datetime import datetime
import uuid
import shutil
from datetime import datetime
from app.core.security import verify_password, get_password_hash
from ukpostcodeutils import validation

router = APIRouter()

# Gets the vendor profile 
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

@router.patch("/profile", tags = ["Vendors"], summary = "Updating the settings of the vendors accounts")
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

    try:
        session.add(current_user)
        session.commit()
    except Exception as e:
        session.rollback() # If anything fails
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Customer updated successfully"}

# get a list of bundles for the corresponding vendor
# for customer view at store page 
@router.get("/bundles/{vendor_id}",response_model=CustBundleList,tags=["bundles"], summary="gets a list of simple details for a stores bundles")
def customer_list_bundles(
    vendor_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user) # keep this as it does some checks
    ):
    
        
    if current_user.role == "vendor" and vendor_id != current_user.vendor_profile.vendor_id:
        return HTTPException(status_code=403, detail="Not the correct vendor")

    today = datetime.now().date()

    # get templates
    # this statement may not show as functioning but it does seem to work  
    statement = (
        select(
            Template.template_id,
            Template.title,
            Template.estimated_value,
            Template.cost,
            func.count(Bundle.bundle_id).label("available_count")
        )
        # join bundles to templates 
        .join(Bundle, Template.template_id == Bundle.template_id) 
        # left join reservations to bundles
        .join(Reservation, Bundle.bundle_id == Reservation.bundle_id, isouter=True)
        .where(Template.vendor == vendor_id)
        .where(Bundle.picked_up.is_(False))
        .where(Reservation.bundle_id.is_(None)) # this means there is no reservation for the bundle
        .where(Bundle.date == today) # only fresh bundles 
        .group_by(Template.template_id,  # count up the total for each template
                  Template.title, 
                  Template.estimated_value, 
                  Template.cost 
                  )
    )

    rows = session.exec(statement).all()
    count = len(rows)

    templates = [
    {
        "template_id": row.template_id,
        "title": row.title,
        "estimated_value": row.estimated_value,
        "cost": row.cost,
        "available_count": row.available_count
    }
    for row in rows # this loops through and converts the rows into the json format expected 
    ]               # like saying [x*2 for x in range(10)]


    if count ==0:
        return {
            "total_count":0,
            "bundles":[]
        }

    return {
        "total_count":count,
        "bundles": templates
    }

@router.post("/upload-image", tags=["Vendors"], summary="Post an image to be stored on the server and set it to be the Vendor photo")
async def upload_image(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
    ):
    # If the image is malformed, throw a 400 error
    if not image.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_extension = image.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = f"uploads/{unique_filename}"

    # Copy the file information to the /uploads folder
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User is not a vendor")
    
    # Set the vendor photo to the saved filepath
    current_user.vendor_profile.photo = f"/static/{unique_filename}"

    session.add(current_user.vendor_profile)
    session.commit()
    
    return {"status": "success", "image_url": current_user.vendor_profile.photo}
    
@router.get("", response_model= VendorList, tags=["Vendors"],summary="Gets all the Vendors for Customer View")
def get_all_vendors(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    today = datetime.now().date()
    # get all vendors 
    statement = ( 
        select(
            Vendor.vendor_id,
            Vendor.name,
            Vendor.photo,
            Vendor.post_code,
            func.count(case((
                and_( # count all the correct bundles 
                        Bundle.picked_up.is_(False),
                        Reservation.bundle_id.is_(None),
                        Bundle.date == today
                    ),
                    Bundle.bundle_id
            ))).label("bundle_count"),
            func.count(case((Template.is_vegan == True, Bundle.bundle_id))).label("has_vegan"),
            func.count(case((Template.is_vegetarian == True, Bundle.bundle_id))).label("has_vegetarian")
        )
        .outerjoin(Template,Template.vendor == Vendor.vendor_id)
        .outerjoin(Bundle, Bundle.template_id == Template.template_id)
        .outerjoin(Reservation, Bundle.bundle_id == Reservation.bundle_id)
        .group_by(
                Vendor.vendor_id,
                Vendor.name, # count the number of bundles per vendor
                Vendor.post_code,
                Vendor.photo 
                )
    )

    rows = session.exec(statement).all()
    count = len(rows)

    vendors = [
    {
        "vendor_id": row.vendor_id,
        "name": row.name,
        "photo": row.photo,
        "post_code":row.post_code,
        "bundle_count":row.bundle_count,
        "has_vegan": bool(row.has_vegan),
        "has_vegetarian": bool(row.has_vegetarian)
    }
    for row in rows # this loops through and converts the rows into the json format expected 
    ]  

    if count ==0:
        return {
            "total_count":0,
            "vendors":[]
        }

    return {
        "total_count":count,
        "vendors":vendors
    }

@router.get("/{vendor_id}", response_model=VendorRead, tags=["Vendors"], summary="Get a specific vendor's public profile")
def get_vendor_public_profile(
    vendor_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    vendor = session.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

