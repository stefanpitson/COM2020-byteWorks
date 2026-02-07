from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query 
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models import Template, Allergen, Bundle, Reservation
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schema import TemplateCreate, TemplateList, TemplateRead, BundleCreate, CustBundleList, BundleRead
from app.api.deps import get_current_user
#from sqlalchemy import func
from datetime import date as Date, time as Time, datetime

router = APIRouter()

# for creating a new template
@router.post("/templates")
def create_template(
    data: TemplateCreate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Not a vendor account")

    if session.exec(select(Template).where(Template.title == data.title and Template.vendor == current_user.vendor_profile.vendor_id)).first():
        raise HTTPException(status_code=400, detail="Template already registered")
    
    new_template = Template(
        title = data.title,
        description = data.description,
        estimated_value = data.estimated_value,
        cost = data.cost,

        meat_percent = data.meat_percent,
        carb_percent = data.carb_percent,
        veg_percent = data.veg_percent,
        carbon_saved = data.carbon_saved,
        weight= data.weight,
        is_vegan = data.is_vegan,
        is_vegetarian = data.is_vegetarian,

        vendor = current_user.vendor_profile.vendor_id
    )

    # for the allergens it is a bit more complex, we need to get 
    if data.allergen_ids:
        statement = select(Allergen).where(Allergen.allergen_id.in_(data.allergen_ids))
        allergens = session.exec(statement).all()
        
        # check they match 
        if len(allergens) != len(data.allergen_ids):
            raise HTTPException(status_code=400, detail="One or more Allergen IDs are invalid")

        # adds the allergen ids to the template 
        new_template.allergens = allergens
    
    try:
        session.add(new_template)
        session.commit()
        
        return {"message": "Template created successfully", "template_id":new_template.template_id}
            
    except Exception as e:
        session.rollback() # If anything fails, undo the Vendor creation
        raise HTTPException(status_code=500, detail=str(e))
    
# get a specific template
@router.get("/templates/{template_id}", response_model= TemplateRead)
def get_template(
    template_id:int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    statement = select(Template).where(Template.template_id == template_id)
    template = session.exec(statement).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template

    
# get a list of templates 
@router.get("/templates/{vendor_id}", response_model = TemplateList)
def get_list_of_templates(
    # doesn't need verification? as anyone can see the templates?
    vendor_id: int,
    session: Session = Depends(get_session)
    ):
    
    statement = select(Template).where(Template.vendor == vendor_id)
    templates = session.exec(statement).all()
    
    # if empty send this
    if not templates:
        return {
            "templates":[],
            "total_count":0
        }
        
    count = len(templates) 
    # else return items 
    return {
        "templates": templates,
        "total_count":count
    }
    

# post a bundle 
@router.post("/create")
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
    
# who should be able to see the raw info on one bundle? 
# lets say just the vendor
@router.get("/bundle/{bundle_id}", response_model=BundleRead)
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
    

# get a list of bundles for the corresponding vendor
# for customer view at store page 
@router.get("/{vendor_id}",response_model=CustBundleList)
def customer_list_bundles(
    vendor_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    
    today = datetime.now().date()

    # get templates
    # tricky statement 
    # may have issues 
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

# get bundles for store view
@router.get("/mystore")
def vendor_list_bundles(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
        
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Not a vendor account")
    
    today = datetime.now().date()
    vendor = current_user.vendor_profile.vendor_id

    statement = (select(Bundle)
            .join(Reservation, Bundle.bundle_id == Reservation.bundle_id, isouter=True)
            .join(Template, Bundle.template_id == Template.template_id)
            .where(Template.vendor == vendor)
            .where(Bundle.picked_up.is_(False))
            .where(Bundle.date == today)
            # .where(Reservation.status == "booked") do we want checks
        )
    bundles = session.exec(statement).all()
    count = len(bundles)

    if count ==0:
        return {
            "total_count":0,
            "templates":[]
        }

    return{
        "total_count":count,
        "bundles": bundles
    }
