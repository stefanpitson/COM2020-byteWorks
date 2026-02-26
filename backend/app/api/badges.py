from sqlmodel import Session, select
from app.core.database import get_session
from app.models import User, Badge, Customer


# This handles the logic for awarding badges to users. Called whenever a reservation is completed
def customer_verify_and_give_badges(user: User, session: Session):

    if user.role != "customer":
        print("User is not a customer, cannot award badges")
        return
    
    if not user.customer_profile:
        print("User does not have a customer profile, cannot award badges")
        return

    statement = select(Badge).where(Badge.user_role == user.role)
    badges = session.exec(statement).all()

    for badge in badges:
        if badge.metric == "carbon_saved":
            value = user.customer_profile.carbon_saved
        
        elif badge.metric == "food_saved":
            value = user.customer_profile.food_saved
        
        elif badge.metric == "streak_count":
            value = user.customer_profile.streak_count
        
        
        
        else:
            print(f"Unknown badge metric: {badge.metric}")
            continue
