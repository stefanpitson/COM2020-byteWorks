from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select 
from app.core.database import get_session
from app.api.deps import get_current_user
from app.models import Report
from app.schema import ReportCreate, ReportRead
import re # for regex

router = APIRouter()

@router.post("/create", tags=["Reports"], summary="create a report as a customer")
def create_report(
    data: ReportCreate,
    session: Session = Depends(get_session),
    current_user  = Depends(get_current_user)
    ):
    
    # checks 
    if current_user.role != "customer":
        raise HTTPException(status_code= 401, detail="must be a customer to create a report")
    
    title_regex = r"^(?=.{1,64}$)(.*?[a-zA-Z0-9]){5}.*$"
    if not re.search(title_regex,data.title):
        raise HTTPException(status_code=46, detail="title of an invalid length")
    
    complaint_regex = r'^(?=.{1,256}$)(.*?[a-zA-Z0-9]){32}.*$'
    if not re.search(complaint_regex, data.complaint):
        raise HTTPException(status_code=46, detail="complaint of an invalid length")
    
    
    # create new report 
    new_report = Report(customer_id= current_user.customer_profile.customer_id, 
                        vendor_id = data.vendor_id,
                        title=data.title,
                        complaint= data.complaint
                        )
    
    try:
        session.add(new_report)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return{"message": "Report created successfully", "report_id":new_report.report_id}



@router.get("/{report_id}", response_model=ReportRead, tags=["Report"], summary="read a report for both cust & vend")
def read_report(
    report_id:int,
    session: Session = Depends(get_session),
    current_user  = Depends(get_current_user)
    ):

    # get report 
    statement = select(Report).where(Report.report_id == report_id)
    report = session.exec(statement).first()

    # checks
    if current_user.role == "customer" and report.customer_id != current_user.customer_profile.customer_id:
        raise HTTPException(status_code=401, detail="you are not the correct customer for this report")
    
    if current_user.role == "vendor" and report.vendor_id != current_user.vendor_profile.vendor_id:
        raise HTTPException(status_code=401, detail="you are not the correct vendor for this report")
    
    #note admin can read all 

    return report

