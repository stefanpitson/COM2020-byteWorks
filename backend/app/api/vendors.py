from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select, func, case
from app.core.database import get_session
from app.models import User, Bundle, Template, Reservation, Vendor
from app.schema import VendorRead, CustBundleList, VendorList
from app.api.deps import get_current_user
import uuid
import shutil
from datetime import datetime

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
            "templates":[]
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
    current_user.vendor_profile.photo = f"static/{unique_filename}"

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
            func.count(Bundle.bundle_id).label("bundle_count"),
            func.max(Template.isVegan).label("has_vegan"),
            func.max(Template.isVegetarian).label("has_veg")
        )
        .join(Template,Template.vendor == Vendor.vendor_id)
        .join(Bundle, Bundle.template_id == Template.template_id)
        .join(Reservation, Bundle.bundle_id == Reservation.bundle_id, isouter=True)
        .where(Template.vendor == Vendor.vendor_id)
        .where(Bundle.picked_up.is_(False))
        .where(Reservation.bundle_id.is_(None)) # this means there is no reservation for the bundle
        .where(Bundle.date == today) # only fresh bundles 
        .group_by(Vendor.name, # count the 
                Vendor.post_code,
                Vendor.photo 
                )
    )

    rows = session.exec(statement).all()
    count = len(rows)

    vendors = [
    {
        "name": row.name,
        "photo": row.photo,
        "post_code":row.post_code,
        "bundle_count":row.bundle_count,
        "has_vegan": row.has_vegan,
        "has_vegetarian": row. has_vegetarian
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

