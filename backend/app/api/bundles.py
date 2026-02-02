from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Customer, User, Vendor, Template
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schema import TemplateCreate, TemplateList, VendorTemplates
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
        price = data.price,
        carbon_saved = data.carbon_saved,
        vendor = current_user.vendor_profile.vendor_id
    )
    
    try:
        session.add(new_template)
        session.commit()
        
        return {"message": "Template created successfully"}
            
    except Exception as e:
        session.rollback() # If anything fails, undo the Vendor creation
        raise HTTPException(status_code=500, detail=str(e))
    
# get a list of templates 
@router.get("/templates", response_model = TemplateList)
def get_list_of_templates(
    # doesnt need verification? as anyone can see the templates?
    data: VendorTemplates,
    session: Session = Depends(get_session)
    ):
    
    statement = select(Template).where(Template.vendor == data.vendor_id)
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
    
