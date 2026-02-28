from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import User, Streak
from app.schema import CustomerRead, CustomerUpdate, StreakRead, CreditTopUpDetails
from app.api.deps import get_current_user
from app.core.security import verify_password, get_password_hash
from ukpostcodeutils import validation
from typing import Optional
from datetime import datetime
import re

router = APIRouter()

@router.get("/profile", response_model= CustomerRead, tags=["Customers"], summary="Get the Customer Profile for the User logged in")
def get_customer_profile(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Not a customer account")
        
    if not current_user.customer_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return current_user.customer_profile

@router.patch("/profile", tags = ["Customers"], summary = "Updating the settings of customer's accounts")
def update_customer_profile(
    data: CustomerUpdate, 
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Not a customer account")
        
    if not current_user.customer_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    

    # User is already a customer 

    if data.user.email != None:
        # Ensures email has not already been used
        if session.exec(select(User).where(User.email == data.user.email)).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = data.user.email

    if data.customer.name != None:
        current_user.customer_profile.name = data.customer.name

    # Ensures both new and old password are inputted when trying to change password but does not provide an error 
    # if neither are inputted (e.g: password is not trying to be changed)
    if data.user.new_password != None and data.user.old_password != None:
        if verify_password(data.user.old_password, current_user.password_hash):
            current_user.password_hash = get_password_hash(data.user.new_password)
    if data.user.new_password != None and data.user.old_password == None:
        raise HTTPException(status_code=400, detail="Old password is required to change new password")
    if data.user.new_password == None and data.user.old_password != None:
        raise HTTPException(status_code=400, detail="New password is missing")
    
    if data.customer.post_code != None:
        parsed_postcode = (data.customer.post_code).upper().replace(" ","")
        if not validation.is_valid_postcode(parsed_postcode):
                    raise HTTPException(status_code=400, detail="Postcode is not valid")
        current_user.customer_profile.post_code = data.customer.post_code
    try:
        session.add(current_user)
        session.commit()
    except Exception as e:
        session.rollback() # If anything fails
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Customer updated successfully"}
    
# get customer streak 
@router.get("/streak", response_model=Optional[StreakRead], tags=["Customer","Streaks"], summary="Get the current streak")
def get_streak(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Not a customer account")
        
    if not current_user.customer_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # get the current streak: 
    statement = (
        select(
            Streak
        )
        .where(Streak.customer_id == current_user.customer_profile.customer_id)
        .where(Streak.ended.is_(False))
    )

    streak = session.exec(statement).first()
    return streak

@router.post("/addcredit", tags = ["Customer"], summary = "Add to customer's credit")
def add_credit_customer(
    card_details : CreditTopUpDetails,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    # Ensures user is a customer
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Not a customer account")
        
    if not current_user.customer_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Ensures all details are entered
    if card_details == None:
        raise HTTPException(status_code=404, detail="No card detail object passed in")
    
    if card_details.credit_top_up == None:
        raise HTTPException(status_code=404, detail="No credit top-up value entered")
    
    if card_details.first_line_address == None:
        raise HTTPException(status_code=404, detail="No first line address entered")
    
    if card_details.postcode == None:
        raise HTTPException(status_code=404, detail="No postcode entered")

    if card_details.name_on_card == None:
        raise HTTPException(status_code=404, detail="No name entered")
    
    if card_details.card_number == None:
        raise HTTPException(status_code=404, detail="No card number entered")
         
    if card_details.expiry_date == None:
        raise HTTPException(status_code=404, detail="No expiry date entered")
    
    if card_details.cvv == None:
        raise HTTPException(status_code=404, detail="No CVV entered")

    # Credit top up validation - ensures that the credit is within a valid range
    if card_details.credit_top_up < 5 or card_details.credit_top_up > 100:
        raise HTTPException(status_code=404, detail="Outside of the credit top-up range")
    
    # Postcode and Address validation - ensures the postcode is a real postcode and that 
    # the first line address is not empty
    parsed_postcode = (card_details.postcode).upper().replace(" ","")
    if not validation.is_valid_postcode(parsed_postcode):
        raise HTTPException(status_code=404, detail="Postcode is not valid")
    if card_details.first_line_address == "":
        raise HTTPException(status_code=404, detail="First line address is empty")
    
    # Name validation - ensures name is not empty
    if card_details.name_on_card == "":
        raise HTTPException(status_code=404, detail = "No name entered")
    
    # Expiry date validation - ensures the current month is either in or before the expiry date (cards expire at the end of the expiry month)
    current_date = datetime.now().date()
    if (card_details.expiry_date.year, card_details.expiry_date.month) < (current_date.year, current_date.month):
        raise HTTPException(status_code=404, detail = "Debit/Credit Card is expired")

    #CVV validation (ensures it is numeric and only 3 characters)
    if not card_details.cvv.isdigit():
        raise HTTPException(status_code=404, detail = "CVV should only include digits")
    if len(card_details.cvv) != 3:
        raise HTTPException(status_code=404, detail = "CVV is not three digits")
    
    
    # Card number validation
    card_number_verified = False

    # Visa or Mastercard Pattern ( they have 3 digit CVV's )
    # - VISA starts with 4 and can have 13, 16 or 19 digits
    # - Mastercard starts as a number between 51 and 55 or as a number between 2221 and 2720 and has 16 digits
    if re.compile(r"^4(\d{12})((\d{3}){0,2})$").match(card_details.card_number) or re.compile(r"^((5[1-5](\d{14}))|((2(2(2[1-9]|[3-9][0-9])|[3-6][0-9][0-9]|7([0-1][0-9]|20)))(\d{12}))$").match(card_details.card_number):
        card_number_verified = True
        if len(card_details.cvv) != 3:
            raise HTTPException(status_code=404, detail = "CVV should be three digits for Visa or Mastercard")

    # AMEX Pattern ( they have 4 digit CVV's )
    # - AMEX start with either 34 or 37 and have 15 digits in total
    if re.compile(r"(34|37)(\d{13})").match(card_details.card_number):
        card_number_verified = True
        if len(card_details.cvv) != 4:
            raise HTTPException(status_code=404, detail = "CVV should be four digits for American Express")

    if not card_number_verified:
        raise HTTPException(status_code = 404, detail = "Card number is not valid")

    # Luhn Algorithm is used below to validate that the card number is mathematically correct
    sum_total = 0
    should_double = True
    card_number_len = len(card_details.card_number)
    for index in range(card_number_len-2, -1, -1):
        if should_double:
            sum_total += 2 * int(card_details.card_number[index])
            should_double = False
        else:
            sum_total += int(card_details.card_number[index])
            should_double = True
    if (sum_total + int(card_details.card_number[card_number_len-1])) % 10 != 0:
        raise HTTPException(status_code = 404, detail = "Card number is not valid")

    # If all above is correct, then all the card information could be correct (we do not know for
    # sure as we are not querying a bank for actual details)
    current_user.customer_profile.store_credit += card_details.credit_top_up
    
    try:
        session.add(current_user)
        session.commit()
    except Exception as e:
        session.rollback() # If anything fails
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Credit added successfully"}
