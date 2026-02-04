from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query 
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Customer, User, Vendor, Template, Allergen
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schema import TemplateCreate, TemplateList, TemplateRead
from app.api.deps import get_current_user

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

    if session.exec(select(Template).where(Template.name == data.name and Template.vendor == current_user.vendor_profile.vendor_id)).first():
        raise HTTPException(status_code=400, detail="Template already registered")
    

    new_template = Template(
        title = data.title,
        description = data.description,
        estimated_value = data.estimated_value,
        cost = data.price,

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
    
@router.get("/templates/{template_id}", response_model= TemplateRead)
def get_template(
    template_id:int,
    session: Session = Depends(get_session)
):
    statement = select(Template).where(Template.template_id == template_id)
    template = session.exec(statement).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template