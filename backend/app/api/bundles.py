from fastapi import APIRouter, Depends, HTTPException 
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models import Template, Allergen, Bundle, Reservation
from app.schema import BundleCreate, CustBundleList, BundleRead, VendBundleList
from app.api.deps import get_current_user
from app.core.time import timer

router = APIRouter()

# post a bundle 
@router.post("/create", tags=["bundles"], summary="Create an amount of bundles for a specified template")
def create_bundles(
    data: BundleCreate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Not a vendor account")
    
    # get the template
    template : Template = session.exec(select(Template).where(Template.template_id == data.template_id)).first()

    if not template: # no template
        raise HTTPException(status_code=400, detail="No corresponding template")
    if template.vendor != current_user.vendor_profile.vendor_id: # wrong vendor
        raise HTTPException(status_code=403, detail="You are not the vendor of the template")
    
    try:
        for i in range(data.amount):
            new_bundle = Bundle(
                template_id= template.template_id
                # all other attributes are auto generated
            )
            session.add(new_bundle)
        session.commit()
        return {"message": "Bundles created successfully"}
    except Exception as e:
        session.rollback() # If anything fails, undo the Vendor creation
        raise HTTPException(status_code=500, detail=str(e))
    
# read details on a specific bundle,
# vendor only as we dont want other customers to see who is other customers details?  
@router.get("/{bundle_id}", response_model=BundleRead, tags=["bundles"], summary="Get the info on a specific bundle listing, for Vendors only")
def bundle_read(
    bundle_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    statement = select(Bundle).where(Bundle.bundle_id == bundle_id)
    bundle = session.exec(statement).first()
    if not bundle:
        raise HTTPException(status_code=404, detail="Bundle not found")

    statement = select(Template.vendor).where(Template.template_id == Bundle.template_id)
    vendor = session.exec(statement).first()
    if vendor != current_user.vendor_profile.vendor_id:
        raise HTTPException(status_code=403, detail="Not corresponding vendor account")

    return bundle
    
# get bundles for store view 
@router.get("/mystore", response_model=VendBundleList, tags=["bundles"], summary="Gets a list of bundles that are current, and not picked up yet")
def vendor_list_bundles(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
        
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Not a vendor account")
    
    today = timer.date()
    #vendor = current_user.vendor_profile.vendor_id

    statement = (select(Bundle)
            .join(Reservation, Bundle.bundle_id == Reservation.bundle_id, isouter=True)
            .join(Template, Bundle.template_id == Template.template_id)
            .where(Template.vendor == current_user.vendor_profile.vendor_id)
            .where(Bundle.picked_up.is_(False))
            .where(Bundle.date == today)
            # .where(Reservation.status == "booked") do we want checks 
        )
    bundles = session.exec(statement).all()
    count = len(bundles)

    if count == 0:
        return {
            "total_count":0,
            "bundles":[]
        }

    return{
        "total_count":count,
        "bundles": bundles
    }
