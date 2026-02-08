from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models import Template, Allergen, Bundle, Reservation
from app.schema import TemplateCreate, TemplateList, TemplateRead 
from app.api.deps import get_current_user
from datetime import datetime

router = APIRouter()

# for creating a new template
@router.post("", tags=["Templates"], summary="Create a new template to be used")
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
@router.get("/{template_id}", response_model= TemplateRead, tags=["Templates"], summary="Get one templates details")
def get_template(
    template_id:int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user) # conducts basic security checks even though the variable isn't used
):
    statement = select(Template).where(Template.template_id == template_id)
    template = session.exec(statement).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template

    
# get a list of templates 
@router.get("/vendor/{vendor_id}", response_model = TemplateList, tags=["Templates"], summary="Get a list of template details for a specific vendor")
def get_list_of_templates(
    # doesn't need verification? as anyone can see the templates?
    vendor_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user) # conducts basic security checks even though the variable isn't used
    ):
    
    if current_user.role == "vendor" and vendor_id != current_user.vendor_profile.vendor_id:
        return HTTPException(status_code=403, detail="Not the correct vendor")

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
    
@router.get("/count/{template_id}", response_model = int, tags=["Template"], summary="Get the count of available bundles for a specified template.")
def count_bundles(
    template_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user) # conducts basic security checks even though the variable isn't used
    ):
    
    today = datetime.now().date()

    statement = (
        select(
            func.count(Bundle.bundle_id).label("available_count")
        )
        .where(Bundle.template_id == template_id)
        # left join reservations to bundles
        .join(Reservation, Bundle.bundle_id == Reservation.bundle_id, isouter=True)
        .where(Bundle.picked_up.is_(False))
        .where(Reservation.bundle_id.is_(None)) # this means there is no reservation for the bundle
        .where(Bundle.date == today) # only fresh bundles 
        .group_by(Bundle.template_id) # count template 
    )

    count = session.exec(statement).one_or_none()
    return count 
