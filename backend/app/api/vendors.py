from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import User
from app.schema import VendorRead
from app.api.deps import get_current_user
import uuid
import shutil

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
    