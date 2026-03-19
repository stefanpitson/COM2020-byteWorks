from fastapi import APIRouter, Query, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.api.deps import get_current_user
from datetime import date, timedelta
import logging
from typing import Optional, Dict
from sqlalchemy.exc import SQLAlchemyError
from app.analytics.sell_through_prop import proportions_all_time, proportions_last_week

# log errors produced
logger = logging.getLogger(__name__)

# more descriptive router with forecasting prefix added
router = APIRouter()

@router.get("/sell_through_proportions")
def get_sell_through_proportions(current_user = Depends(get_current_user), session: Session = Depends(get_session)):

    """
    endpoint for returning a dictionary of sell through
    dictionary 1 form {"collected": x, "no_show": y, "expired": z, "week_start_date": some_date}
    dictionary 2 form {"collected": x, "no_show": y, "expired": z}
    we return a single dictionary 3 in the form {"weekly_proportions": dictionary 1, "all_time_proportions": dictionary 2}
    """

    # if the vendor does not exist or has been incorrectly received: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
        
    vendor_id = current_user.vendor_profile.vendor_id

    try:
        # attempt to call the functions we use for different sell through
        last_week: Dict = proportions_last_week(session=session, vendor_id=vendor_id)
        all_time: Dict[str, float] = proportions_all_time(session=session, vendor_id=vendor_id)

        return {"weekly_proportions": last_week, "all_time_proportions": all_time}

    # use the logger to log the exceptions made
    except SQLAlchemyError:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception: # generic exception to catch all other exceptions
        logger.exception("error in forecast generation")
        raise HTTPException(status_code=500, detail="internal server error")