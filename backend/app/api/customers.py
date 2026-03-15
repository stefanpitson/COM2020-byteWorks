from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models import Customer, User, Streak, Badge, User_Badge
from app.schema import BadgeList, CustomerRead, CustomerUpdate, LeaderboardList, StreakRead, BadgeRead
from app.api.deps import get_current_user
from app.core.security import verify_password, get_password_hash
from ukpostcodeutils import validation
from typing import Optional, List

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

# get badges achieved by the customer. If the user is not a customer or does not have a customer profile, they should not have access to this endpoint and an error message should be given.
@router.get("/badges/owned", response_model=BadgeList, tags=["Customer", "Badges"], summary="Get the badges for the current customer")
def get_customer_owned_badges(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):


    if current_user.role != "customer":     #if the user is not a customer, they should not have access to this endpoint
        raise HTTPException(status_code=403, detail="Not a customer account")
        
    if not current_user.customer_profile:   #if the user does not have a customer profile, they should not have access to this endpoint
        raise HTTPException(status_code=404, detail="Profile not found")

    # gets all badges owned by the customer ,joins the Badge and User_Badge tables and filters for entries where the user_id matches the current user's id
    statement = (
        select(Badge)
        .join(Badge.users)
        .where(User.user_id == current_user.user_id)
    )

    badges = session.exec(statement).all()
    return {"total_count": len(badges), "badges": badges}

# get the badges not achieved by the customer. If the user is not a customer or does not have a customer profile, they should not have access to this endpoint and an error message should be given.
@router.get("/badges/unowned", response_model=BadgeList, tags=["Customer", "Badges"], summary="Get unowned badges for the current customer")
def get_customer_unowned_badges(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
    ):

    # if the user is not a customer, they should not have access to this endpoint
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Not a customer account")
        
    if not current_user.customer_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # gets all badge_ids the user already owns
    owned_subquery = (
        select(User_Badge.badge_id)
        .where(User_Badge.user_id == current_user.user_id)
    )

    # gets all badges where the badge is not owned by the customer, and it is a customer badge
    statement = (
        select(Badge)
        .where(Badge.user_role == "customer")               # only customer badges
        .where(Badge.badge_id.not_in(owned_subquery))       # exclude owned ones
    )
    
    badges = session.exec(statement).all()
    return {"total_count": len(badges), "badges": badges}

# return the leaderboard of customers sorted by food saved returns 10 or 11 entries depending on whether the current customer is in the top 10 or not. If the user is not a customer, they should not have access to this endpoint and an error message should be given.
@router.get("/leaderboard", response_model=LeaderboardList, tags=["Leaderboard"], summary="Get the food saved leaderboard")
def get_leaderboard(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    # checks if the current user is a customer, if not they shouldn't have access and returns an error
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers have a rank")
    
    # selects the top 10 customers by food saved
    statement = (select(Customer)
        .order_by(Customer.food_saved.desc())
        .limit(10)
    )
    top_ten = session.exec(statement).all()

    current_customer = current_user.customer_profile

    # simple boolean checking if any of the IDs in the top ten are the current customer's
    in_top_ten = any(c.customer_id == current_customer.customer_id for c in top_ten)

    # generates a list of the top ten customers with their rank, name+id, food saved and whether the entry is for the current customer (used for frontend display purposes)
    results = [
        {
            "customer_id": customer.customer_id,
            "rank": i + 1,
            "name": f"{customer.name}#{customer.customer_id}", #joins the customer's chosen name and their id to create a unique entry on the leaderboard e.g. Username#231
            "food_saved": customer.food_saved,
            "is_you": customer.customer_id == current_customer.customer_id
        }
        for i, customer in enumerate(top_ten)
    ]

    # if the customer isn't in the top ten for food saved, return a final entry with their id, name+id, rank (the num of people ahead of them) and food saved value
    if not in_top_ten:
        # counts the number of customers with more food
        rank_statement = select(func.count(Customer.customer_id)).where(
            Customer.food_saved > current_customer.food_saved
        )
        rank = session.exec(rank_statement).one() + 1

        # adds the current customer's id, rank, name and food saved to the end of the results list with is_you as true for frontend display purposes
        results.append({
            "customer_id": current_customer.customer_id,
            "rank": rank,
            "name": f"{current_customer.name}#{current_customer.customer_id}",
            "food_saved": current_customer.food_saved,
            "is_you": True
        })
    
    return LeaderboardList(total_count=len(results), entries=results)