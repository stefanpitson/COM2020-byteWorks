from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models import Template, Allergen, Bundle, Reservation
from app.schema import TemplateCreate, TemplateList, TemplateRead, ReservationRead
from app.api.deps import get_current_user
from datetime import datetime
from random import randint

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
    
    percents = data.meat_percent + data.carb_percent + data.veg_percent\
    
    if percents > 1.05 or percents < 0.90:
        raise HTTPException(status_code=400, detail="Percentages do not add up to 100")


    # calculating the bundle carbon 
    meat_carbon = data.weight * (data.meat_percent) *12.4 # see backend chat
    carb_carbon = data.weight * (data.carb_percent) *1 
    veg_carbon = data.weight * ( data.meat_percent) *0.2 

    calc_carbon_saved = meat_carbon +carb_carbon +veg_carbon
    
    new_template = Template(
        title = data.title,
        description = data.description,
        estimated_value = data.estimated_value,
        cost = data.cost,

        meat_percent = data.meat_percent,
        carb_percent = data.carb_percent,
        veg_percent = data.veg_percent,
        carbon_saved = calc_carbon_saved,
        weight= data.weight,
        is_vegan = data.is_vegan,
        is_vegetarian = data.is_vegetarian,

        vendor = current_user.vendor_profile.vendor_id
    )

    # for the allergens it is a bit more complex, we need to get 
    if data.allergen_titles:
        statement = select(Allergen).where(Allergen.title.in_(data.allergen_titles))
        allergens = session.exec(statement).all()
        
        # check they match 
        if len(allergens) != len(data.allergen_titles):
            raise HTTPException(status_code=400, detail="One or more Allergen titles are invalid")

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
    
# gets the count of how many bundles there are for a template
# expected use when getting a displaying full bundle/template information 
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
    template_id: int,
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

    customer.carbon_saved += carbon_saved
    vendor.carbon_saved += carbon_saved






# need to do set no-show if they don't turn up 