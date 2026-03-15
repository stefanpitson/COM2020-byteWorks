from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select, func, case, and_
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select, func, case, and_
from app.core.database import get_session
from app.models import User, Bundle, Template, Reservation, Vendor, OpenHours
from app.schema import VendorRead, CustBundleList, VendorList, VendorUpdate, OpeningHoursRead
from app.api.deps import get_current_user
import uuid
import shutil
from datetime import datetime
from datetime import time
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

    vendor_id = current_user.vendor_profile.vendor_id

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
    
    if data.vendor.opening_hours != None:
        DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

        # If a day not included, then assume it is not to be changed
        for day_name in DAY_NAMES:
            if data.vendor.opening_hours[day_name]:
                if check_opening_hours(data.vendor.opening_hours[day_name]):
                    current_user.vendor_profile.opening_hours[day_name] = data.vendor.opening_hours[day_name]
                else:
                    raise HTTPException(status_code = 403, detail = ("Incorrect opening times for " + day_name))
                    

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

def check_opening_hours(
    possible_hours : List[str],
    ):
    if possible_hours:
        if len(possible_hours) == 2:
            newOpeningHour = possible_hours[0]
            newClosingHour = possible_hours[1]
            # Checks if either the opening and closing hour are the same and that they are both equal to either "allday" or "closed"
            # or checks if both the hours are numeric
            if (newOpeningHour == newClosingHour
                and (newOpeningHour == "closed" or newOpeningHour == "allday")): 
                    return True
            
            # Checks if not closed or all day, that both the times are within the 24hr clock system
            elif (newOpeningHour.isnumeric() and newClosingHour.isnumeric()):
                if (int(newOpeningHour) < int (newClosingHour)
                    and len(newOpeningHour) == 4 and newClosingHour == 4
                    and int(newOpeningHour[0:2]) >= 0 and int(newOpeningHour[0:2]) < 24
                    and int(newClosingHour[0:2]) >= 0 and int(newClosingHour[0:2]) < 24
                    and int(newOpeningHour[2:4]) >= 0 and int(newOpeningHour[2:4]) < 60
                    and int(newClosingHour[2:4]) >= 0 and int(newClosingHour[2:4]) < 60
                    ): 
                        return True


# get a list of bundles for the corresponding vendor
# for customer view at store page 
@router.get("/bundles/{vendor_id}",response_model=CustBundleList,tags=["Bundles"], summary="gets a list of simple details for a stores bundles")
def customer_list_bundles(
    vendor_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user) # keep this as it does some checks
    ):
        
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Not a vendor account")
        
    if not current_user.vendor_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

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

    try:
        session.add(current_user.vendor_profile)
        session.commit()
        return {"status": "success", "image_url": current_user.vendor_profile.photo}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        session.rollback() # If anything fails
        raise HTTPException(status_code=500, detail=str(e))
    
    
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

@router.get("/{vendor_id}/opening_hours", response_model = Dict[str, List[str]], tags=["Vendors"], summary = "Get the opening hours for a vendor")
def get_vendor_opening_hours(
    vendor_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Not a vendor account")
        
    if not current_user.vendor_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    vendor = session.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return vendor.opening_hours

@router.get("/{vendor_id}/is_open", response_model = bool, tags=["Vendors"], summary = "Check if a vendor is open")
def check_vendor_is_open(
    vendor_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    # Anyone should be able to run this so no need to check for current_user 
    
    vendor = session.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    current_day = datetime.now().strftime("%A").lower()
    current_time = datetime.now().time()
    is_open = False
    if vendor.opening_hours[current_day]:
        if vendor.opening_hours[current_day][0] == "allday":
            is_open = True
        if vendor.opening_hours[current_day][0] != "closed":
            if (time.fromisoformat(vendor.opening_hours[current_day][0][0:2] + ":" + vendor.opening_hours[current_day][0][2:4] + ":00") <= current_time
                and current_time < time.fromisoformat(vendor.opening_hours[current_day][1][0:2] + ":" + vendor.opening_hours[current_day][1][2:4] + ":00")):
                is_open = True
    
    return is_open