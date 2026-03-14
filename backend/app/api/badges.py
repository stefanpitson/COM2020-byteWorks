from http.client import HTTPException

from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Customer, Streak, Badge


# This handles the logic for awarding badges to users. Called whenever a reservation is completed
def customer_verify_and_give_badges(customer: Customer, session: Session):

    statement = select(Badge).where(Badge.user_role == customer.role)
    badges = session.exec(statement).all()

    try:
        for badge in badges:
            if badge.metric == "carbon_saved":
                value = customer.customer_profile.carbon_saved
            
            elif badge.metric == "food_saved":
                value = customer.customer_profile.food_saved
            
            elif badge.metric == "streak_count":
                statement = (
                    select(Streak.count)
                    .where(Streak.customer_id == customer.customer_profile.customer_id)
                    .where(Streak.ended.is_(False))
                )
                value = session.exec(statement).first() or 0

            else:
                continue

            if value >= badge.threshold:
                if badge not in customer.badges:
                    customer.badges.append(badge)
                    session.add(customer)

        session.commit()

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

