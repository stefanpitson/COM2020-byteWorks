from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models import Template, Allergen, Bundle, Reservation, Customer, Vendor
from app.schema import ReservationRead
from app.api.deps import get_current_user
from datetime import datetime
from random import randint

router = APIRouter()

@router.post("/{template_id}/reserve", tags=["reservations"], summary="Create a reservation of a template if a bundle is available")
def create_reservation(
    template_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    # Ensures bundles of the correct template, made for that day and that haven't been purchased yet are selected
    statement = select(Bundle).where(Bundle.template_id == template_id 
                                     and Bundle.date == datetime.now().date() 
                                     and Bundle.purchased_by == None)
    
    # Picks the first of any suitable bundles that meet criteria
    bundle = session.exec(statement).first()

    # If no bundles left, return status error
    if not bundle:
        raise HTTPException(status_code=404, detail="No bundle found for that template on the current day")

    # Set that bundle to be bought by that customer so it cannot be bought by any other customer
    bundle.purchased_by = current_user.customer_profile.customer_id

    new_reservation = Reservation(bundle_id = bundle.bundle_id, 
                                  consumer_id = current_user.customer_profile.customer_id,
                                  code = randint(0,9999))

    # Update the bought bundle and add the new reservation
    session.add(bundle)
    session.add(new_reservation)
    session.commit()

    return {"message": "Bundle created successfully"}

@router.get("????????", response_model= ReservationRead, tags=["Reservation"], summary="Get one reservation details")
def get_reservation(
    reservation_id:int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    

    statement = select(Reservation).where(Reservation.reservation_id == reservation_id)
    reservation = session.exec(statement).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Gets the ID of the vendor that is responsible for the reservation
    statement = select(Template.vendor).where(Template.template_id == Bundle.template_id 
                                              and Bundle.bundle_id == reservation.bundle_id)

    reserveVendorID = session.exec(statement).first()

    # Checks if either the vendor that made the bundle that has the reservation or
    # the customer that created the reservation is trying to get the reservation
    if current_user.role == "vendor":  
        if current_user.vendor_profile.vendor_id != reserveVendorID:
            raise HTTPException(status_code=403, detail="Not the correct vendor")
    if current_user.role == "customer":
        if current_user.customer_profile.customer_id != reservation.consumer_id:
            raise HTTPException(status_code=403, detail = "Not correct customer")
    
    return reservation

@router.post("???", tags=["reservations"], summary="Cancel an already booked reservation")
def cancel_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    statement = select(Reservation).where(Reservation.reservation_id == reservation_id)
    reservation = session.exec(statement).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Gets the ID of the vendor that is responsible for the reservation
    statement = select(Template.vendor).where(Template.template_id == Bundle.template_id 
                                              and Bundle.bundle_id == reservation.bundle_id)

    reserveVendorID = session.exec(statement).first()

    # Checks if either the vendor that made the bundle that has the reservation or
    # the customer that created the reservation is trying to get the reservation
    if current_user.role == "vendor":  
        if current_user.vendor_profile.vendor_id != reserveVendorID:
            raise HTTPException(status_code=403, detail="Not the correct vendor")
    if current_user.role == "customer":
        if current_user.customer_profile.customer_id != reservation.consumer_id:
            raise HTTPException(status_code=403, detail = "Not correct customer")

    reservation.status = "cancelled"

    # cancel reservation by changing status
    # change bundle that was reserved "PurchasedBy" back to none
    # ensure that it is the vendor or the customer

    statement = select(Bundle).where(Bundle.template_id == reservation.bundle_id)
    bundle = session.exec(statement).first()

    bundle.purchased_by = None

    session.add(bundle)
    session.add(reservation)
    session.commit()

    return {"message": "Bundle created successfully"}

# need to do accept reservation (when they pick it up)
@router.post("???", tags=["reservations"], summary="Finalise a reservation")
def finalise_reservation(
    reservation_id: int,
    pickup_code : int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    statement = select(Reservation).where(Reservation.reservation_id == reservation_id)
    reservation = session.exec(statement).first()

    # Gets the ID of the vendor that is responsible for the reservation
    statement = select(Template.vendor).where(Template.template_id == Bundle.template_id 
                                              and Bundle.bundle_id == reservation.bundle_id)

    reserveVendorID = session.exec(statement).first()

    if current_user.role == "vendor":  
        if current_user.vendor_profile.vendor_id != reserveVendorID:
            raise HTTPException(status_code=403, detail="Not the correct vendor")
        
    statement = select(Customer).where(Customer.customer_id == reservation.consumer_id)
    customer = session.exec(statement).first()

    statement = select(Template.cost).where(Template.template_id == Bundle.template_id 
                                              and Bundle.bundle_id == reservation.bundle_id)
    cost = session.exec(statement).first()

    if pickup_code != reservation.code:
        raise HTTPException(status_code=403, detail="Customer does not the correct accepting code")

    if customer.store_credit < cost:
        raise HTTPException(status_code=403, detail="Customer does not have enough credit to purchase")

    statement = select(Template.carbon_saved).where(Template.template_id == Bundle.template_id 
                                              and Bundle.bundle_id == reservation.bundle_id)

    carbon_saved = session.exec(statement).first()

    reservation.status = "collected"
    customer.store_credit -= cost

    statement = select(Vendor).where(Vendor.vendor_id == current_user.vendor_profile.vendor_id)
    vendor = session.exec(statement).first()

    customer.carbon_saved += carbon_saved
    vendor.carbon_saved += carbon_saved

    session.add(reservation)
    session.add(customer)
    session.add(vendor)
    session.commit()




# need to do set no-show if they don't turn up 