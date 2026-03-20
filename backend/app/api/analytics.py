from fastapi import APIRouter, Query, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.api.deps import get_current_user
from datetime import date, timedelta
import logging
from typing import Optional, Dict, Tuple, List
from sqlalchemy.exc import SQLAlchemyError
from app.analytics.sell_through_prop import proportions_all_time, proportions_last_week
from app.analytics.waste_proxy import waste_proxy
from app.analytics.pricing_effectiveness import pricing_effectiveness
from app.schema import discount_coordinate, discount_coordinate_data

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
        logger.exception("error in analytic generation")
        raise HTTPException(status_code=500, detail="internal server error")
    


@router.get("/waste_proxy")
def get_waste_proxy(current_user = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    endpoint to call the function waste_proxy
    this function returns a dictionary in the form: {"total_waste_avoided": x, "average_bundle_weight": y}
    """

    # if the vendor does not exist or has been incorrectly received: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
        
    vendor_id = current_user.vendor_profile.vendor_id # get the vendor id from current user

    try: # attempt to extract info from the function for the current vendor
        waste: Dict[str, float] = waste_proxy(session, vendor_id)

        return waste
    
    # use the logger to log the exceptions made
    except SQLAlchemyError:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception: # generic exception to catch all other exceptions
        logger.exception("error in analytic generation")
        raise HTTPException(status_code=500, detail="internal server error")
    


@router.get("/pricing_effectiveness", response_model=discount_coordinate_data)
def get_pricing_effectiveness(current_user = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    endpoint that calls the function pricing_effectiveness
    this return a list of custom classes to represent the datapoints
    intended to made into a scatter plot on the front end
    the front end should display a not enough data message if [] is returned
    """

    # if the vendor does not exist or has been incorrectly received: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
        
    vendor_id = current_user.vendor_profile.vendor_id # get the vendor id from current user

    try:
        # call and return result of plots
        plots: discount_coordinate_data = pricing_effectiveness(session, vendor_id, days_back=42)
        return plots
    
    # use the logger to log the exceptions made
    except SQLAlchemyError:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception: # generic exception to catch all other exceptions
        logger.exception("error in analytic generation")
        raise HTTPException(status_code=500, detail="internal server error")