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
from app.analytics.operational_insights import get_bestselling_bundle_titles, get_posting_windows
from app.schema import discount_coordinate_data, popular_bundle_data, post_windows_data, waste_proxy_data, week_sell_through_proportions, all_time_sell_through_proportions, combined_sell_through_data

# log errors produced
logger = logging.getLogger(__name__)

# more descriptive router with forecasting prefix added
router = APIRouter()

@router.get("/sell_through_proportions", response_model=combined_sell_through_data)
def get_sell_through_proportions(current_user = Depends(get_current_user), session: Session = Depends(get_session)):

    """
    endpoint for returning a data for sell through
    weekly sell through proportions are in the form: class {num_collected: int, num_no_show: int, num_expired: int, week_start_date: str}
    all time sell through proportions are in the form: class {num_collected: int, num_no_show: int, num_expired: int}
    the returned object (combined_sell_through_data) combines the above 2 classes for a full scope of recent and all time sell through
    """

    # if the vendor does not exist or has been incorrectly received: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
        
    vendor_id = current_user.vendor_profile.vendor_id

    try:
        # attempt to call the functions we use for different sell through
        last_week: week_sell_through_proportions = proportions_last_week(session=session, vendor_id=vendor_id)
        all_time: all_time_sell_through_proportions = proportions_all_time(session=session, vendor_id=vendor_id)
        combined: combined_sell_through_data = combined_sell_through_data(weekly_proportions=last_week, all_time_proportions=all_time)

        return combined

    # use the logger to log the exceptions made
    except SQLAlchemyError:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception: # generic exception to catch all other exceptions
        logger.exception("error in analytic generation")
        raise HTTPException(status_code=500, detail="internal server error")
    


@router.get("/waste_proxy", response_model=waste_proxy_data)
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
        waste: waste_proxy_data = waste_proxy(session, vendor_id)
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



@router.post("/posting_windows", response_model=post_windows_data)
def get_post_window_data(current_user = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Endpoint for frontend to call that returns the necessary datapoints for a bar chart
    function get_posting_windows is called returning a class to represent datapoints
    x axis = time slots from 06:00 onwards
    y axis = the weekly average number of all bundles sold in that timeslot
    title: most popular posting times
    subtitle: your most popular timeslot is xx:yy:zz - xx:yy:zz
    """
    # if the vendor does not exist or has been incorrectly received: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
        
    vendor_id = current_user.vendor_profile.vendor_id # get the vendor id from current user

    try:
        # call and return result of datapoints
        points: post_windows_data = get_posting_windows(session=session, vendor_id=vendor_id, days_back=42)
        return points
    
    # use the logger to log the exceptions made
    except SQLAlchemyError:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception: # generic exception to catch all other exceptions
        logger.exception("error in analytic generation")
        raise HTTPException(status_code=500, detail="internal server error")
    


@router.post("/bestsellers", response_model=popular_bundle_data)
def get_popular_bundle_data(current_user = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    endpoint to be called for making a bar chart to identify the top 3 most popular bundles by title
    x axis: bundle title
    y axis: weekly average sold 
    title: best selling bundles
    subtitle: you best selling bundle is {x}_bundle
    """
    # if the vendor does not exist or has been incorrectly received: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
        
    vendor_id = current_user.vendor_profile.vendor_id # get the vendor id from current user

    try:
        # call and return result of datapoints
        points: popular_bundle_data = get_bestselling_bundle_titles(session=session, vendor_id=vendor_id, days_back=42)
        return points
    
    # use the logger to log the exceptions made
    except SQLAlchemyError:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception: # generic exception to catch all other exceptions
        logger.exception("error in analytic generation")
        raise HTTPException(status_code=500, detail="internal server error")