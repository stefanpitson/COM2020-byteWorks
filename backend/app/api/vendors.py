from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Vendor

router = APIRouter()

@router.post("/", response_model=Vendor)
def create_vendor(vendor: Vendor, session: Session = Depends(get_session)):
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor

@router.get("/", response_model=List[Vendor])
def read_vendor(session: Session = Depends(get_session)):
    vendor = session.exec(select(Vendor)).all()
    return vendor
