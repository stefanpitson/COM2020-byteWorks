from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models import Template, Allergen, Bundle, Reservation, Customer, Vendor, Streak, User
from app.schema import VendReservationRead, CustReservationRead, CustReservationList, VendReservationList, PickupCode
from app.api.deps import get_current_user
from datetime import datetime, timedelta, date
from random import randint

router = APIRouter()

@router.post("/{template_id}/reserve", tags=["Reservations"], summary="Create a reservation of a template if a bundle is available")
def create_reservation(
    template_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    # Ensures bundles of the correct template, made for that day and that haven't been purchased yet are selected
    statement = (select(Bundle).where(Bundle.template_id == template_id, 
                                     Bundle.date == datetime.now().date(), 
                                     Bundle.purchased_by == None))
    
    # Picks the first of any suitable bundles that meet criteria
    bundle = session.exec(statement).first()

    # If no bundles left, return status error
    if not bundle:
        raise HTTPException(status_code=404, detail="No bundle found for that template on the current day")

    # Set that bundle to be bought by that customer so it cannot be bought by any other customer
    bundle.purchased_by = current_user.customer_profile.customer_id

    new_reservation = Reservation(bundle_id = bundle.bundle_id, 
                                  customer_id = current_user.customer_profile.customer_id,
                                  code = randint(0,9999))
    
            
    statement = select(Customer).where(Customer.customer_id == new_reservation.customer_id)
    customer = session.exec(statement).first()

    statement = select(Template).where(Template.template_id == template_id)
    template = session.exec(statement).first()
    
    if customer.store_credit < template.cost:
        raise HTTPException(status_code=403, detail="Customer does not have enough credit to purchase")
    customer.store_credit -= template.cost
    

    # Update the bought bundle and add the new reservation
    try:
        session.add(bundle)
        session.add(new_reservation)
        session.commit()
    except Exception as e:
        session.rollback() # If anything fails
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Reservation created successfully", "reservation_id":new_reservation.reservation_id}

    

@router.get("/{reservation_id}/vendor", response_model= VendReservationRead, tags=["Reservations"], summary="Get one reservation details")
def get_reservation_vendor(
    reservation_id:int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    

    statement = select(Reservation).where(Reservation.reservation_id == reservation_id)
    reservation = session.exec(statement).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Gets the ID of the vendor that is responsible for the reservation
    statement = select(Template.vendor).where(Template.template_id == Bundle.template_id, 
                                               Bundle.bundle_id == reservation.bundle_id)

    reserveVendorID = session.exec(statement).first()

    # Checks if the vendor that made the bundle that has the reservation is trying to get the reservation
    if current_user.role == "vendor":  
        if current_user.vendor_profile.vendor_id != reserveVendorID:
            raise HTTPException(status_code=403, detail="Not the correct vendor")
    
    return VendReservationRead(reservation_id = reservation_id, 
                                   bundle_id = reservation.bundle_id, 
                                   customer_id = reservation.customer_id,
                                   time_created = reservation.time_created,
                                   status = reservation.status)

@router.get("/{reservation_id}/customer", response_model= CustReservationRead, tags=["Reservations"], summary="Get one reservation details")
def get_reservation_customer(
    reservation_id:int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    
    statement = select(Reservation).where(Reservation.reservation_id == reservation_id)
    reservation = session.exec(statement).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Ensures only the customer that created the reservation can access it
    if current_user.role == "customer":
        if current_user.customer_profile.customer_id != reservation.customer_id:
            raise HTTPException(status_code=403, detail = "Not correct customer")
    
    return CustReservationRead(reservation_id = reservation_id, 
                                   bundle_id = reservation.bundle_id, 
                                   customer_id = reservation.customer_id,
                                   time_created = reservation.time_created,
                                   code = reservation.code,
                                   status = reservation.status)

@router.get("/customer", response_model= CustReservationList, tags=["Reservations"], summary="Get one reservation details")
def get_list_of_reservations_customer(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    
    # Ensures only the customers can call this
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail = "Not customer")

    statement = select(Reservation).where(Reservation.customer_id == current_user.customer_profile.customer_id)
    reservations = session.exec(statement).all()

    count = len(reservations)

    customer_reservations = []

    for reservation in reservations:
        customer_reservations.append(CustReservationRead(reservation_id = reservation.reservation_id, 
                                   bundle_id = reservation.bundle_id, 
                                   customer_id = reservation.customer_id,
                                   time_created = reservation.time_created,
                                   code = reservation.code,
                                   status = reservation.status))
    
    return{
        "total_count":count,
        "bundles": customer_reservations
    }

@router.get("/vendor", response_model= VendReservationList, tags=["Reservations"], summary="Get one reservation details")
def get_list_of_reservations_vendor(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    
    # Ensures only the vendors can call this
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail = "Not vendor")

    statement = select(Reservation).where(Template.vendor == current_user.vendor_profile.vendor_id, 
                                          Reservation.bundle_id == Bundle.bundle_id,
                                          Bundle.template_id == Template.template_id)
    reservations = session.exec(statement).all()

    count = len(reservations)

    vendor_reservations = []

    for reservation in reservations:
        vendor_reservations.append(VendReservationRead(reservation_id = reservation.reservation_id, 
                                   bundle_id = reservation.bundle_id, 
                                   customer_id = reservation.customer_id,
                                   time_created = reservation.time_created,
                                   status = reservation.status))
    
    return{
        "total_count":count,
        "bundles": vendor_reservations
    }

@router.post("/{reservation_id}/cancel", tags=["Reservations"], summary="Cancel an already booked reservation")
def cancel_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    statement = select(Reservation).where(Reservation.reservation_id == reservation_id)
    reservation = session.exec(statement).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    
    if reservation.status == "cancelled":
        raise HTTPException(status_code=404, detail="Reservation already cancelled")

    # Gets the ID of the vendor that is responsible for the reservation
    statement = select(Template.vendor).where(Template.template_id == Bundle.template_id, 
                                              Bundle.bundle_id == reservation.bundle_id)

    reserveVendorID = session.exec(statement).first()

    # Checks if either the vendor that made the bundle that has the reservation or
    # the customer that created the reservation is trying to get the reservation
    if current_user.role == "vendor":  
        if current_user.vendor_profile.vendor_id != reserveVendorID:
            raise HTTPException(status_code=403, detail="Not the correct vendor")
    if current_user.role == "customer":
        if current_user.customer_profile.customer_id != reservation.customer_id:
            raise HTTPException(status_code=403, detail = "Not correct customer")

    reservation.status = "cancelled"

    statement = select(Customer).where(Customer.customer_id == reservation.customer_id)
    customer = session.exec(statement).first()
    
    statement = select(Template.cost).where(Bundle.template_id == Template.template_id, 
                                     Bundle.bundle_id == reservation.bundle_id,
                                     reservation.reservation_id == reservation_id)
    cost = session.exec(statement).first()

    customer.store_credit += cost

    statement = select(Bundle).where(Bundle.bundle_id == reservation.bundle_id)
    bundle = session.exec(statement).first()

    bundle.purchased_by = None
    try:
        session.add(bundle)
        session.add(reservation)
        session.add(customer)
        session.commit()
    except Exception as e:
        session.rollback() # If anything fails
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Reservation cancelled successfully"}

# need to do accept reservation (when they pick it up)
@router.post("/{reservation_id}/check", tags=["Reservations"], summary="Finalise a reservation")
def finalise_reservation(
    reservation_id: int,
    pickup_code_obj : PickupCode,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    if pickup_code_obj == None:
        raise HTTPException(status_code=404, detail="No pickup code object")
    
    if pickup_code_obj.pickup_code == None:
        raise HTTPException(status_code=404, detail="No pick up code sent in the object")


    pickup_code = pickup_code_obj.pickup_code

    statement = select(Reservation).where(Reservation.reservation_id == reservation_id)
    reservation = session.exec(statement).first()

    # Gets the ID of the vendor that is responsible for the reservation
    statement = select(Template.vendor).where(Template.template_id == Bundle.template_id,
                                              Bundle.bundle_id == reservation.bundle_id)

    reserveVendorID = session.exec(statement).first()

    if current_user.role == "vendor":  
        if current_user.vendor_profile.vendor_id != reserveVendorID:
            raise HTTPException(status_code=403, detail="Not the correct vendor")
        
    statement = select(Customer).where(Customer.customer_id == reservation.customer_id)
    customer = session.exec(statement).first()

    statement = select(Template.cost).where(Template.template_id == Bundle.template_id,
                                            Bundle.bundle_id == reservation.bundle_id)

    if pickup_code != reservation.code:
        raise HTTPException(status_code=403, detail="Customer does not have the correct accepting code")

    statement = select(Template.carbon_saved).where(Template.template_id == Bundle.template_id,
                                                    Bundle.bundle_id == reservation.bundle_id)

    carbon_saved = session.exec(statement).first()

    reservation.status = "collected"

    statement = select(Vendor).where(Vendor.vendor_id == current_user.vendor_profile.vendor_id)
    vendor = session.exec(statement).first()

    customer.carbon_saved += carbon_saved
    vendor.carbon_saved += carbon_saved
    try:
        increment_streak(session,customer)
        session.add(reservation)
        session.add(customer)
        session.add(vendor)
        session.commit()
    except Exception as e:
        session.rollback() # If anything fails
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Reservation accepted successfully"}

#logic for incrementing or making a new streak 
def increment_streak(session: Session, customer):
    # check if they have a streak
    statement = (select(Streak)
                 .where(Streak.customer_id == customer.customer_id)
                 .where(Streak.ended.is_(False))
                 )
    streak = session.exec(statement).first()
    try:
        if streak != None:
            # check date 
            if streak.last == datetime.now().date():
                return # streak is not adjusted if last was same day

            last = streak.last + timedelta(days=7)
            if last >= datetime.now().date(): # streak is in date
                streak.count +=1
                streak.last = datetime.now().date()
                session.add(streak)
                session.commit()
                return
            
            else: # streak is out of date
                streak.ended = True
                session.add(streak)
    
        # create new streak
        new_streak = Streak(
            customer_id=customer.customer_id,
            started= datetime.now().date(),
            last= datetime.now().date(),
            count = 1
        )

        session.add(new_streak)
        session.commit()
        return
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# need to do set no-show if they don't turn up 
