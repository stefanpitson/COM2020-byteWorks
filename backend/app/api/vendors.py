from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models import User, Bundle, Template, Reservation
from app.schema import VendorRead, CustBundleList 
from app.api.deps import get_current_user
from datetime import datetime

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
        "available_count": row.available_count,
    }
    for row in rows
    ]


    if count ==0:
        return {
            "total_count":0,
            "templates":[]
        }

    return {
        "total_count":count,
        "bundles": templates
    }
