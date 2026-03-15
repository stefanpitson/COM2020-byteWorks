from fastapi import APIRouter, Query, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.api.deps import get_current_user
from app.schema import ForecastWeekData
from app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast import get_naive_forecast_chart
from app.forecasting.baseline_approaches.moving_average.moving_average_forecast import get_moving_average_forecast_chart
from app.forecasting.linear_regression.linear_regression_forecast import get_linear_regression_forecast_chart
from datetime import date, timedelta
import logging
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError

# all forecasting functions that need to be called will be of the form: get_{model name}_forecast_chart

# log errors produced
logger = logging.getLogger(__name__)

# more descriptive router with forecasting prefix added
router = APIRouter(prefix="/forecast", tags=["Forecasting"])

# changed to post for now as modifies the db
@router.post("/naive", response_model=ForecastWeekData)
def naive_forecast(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session) 
):
    
    """
    endpoint for the naive baseline
    this endpoint requires the current user and session as parameters
    the start date defaults to tomorrow -> providing a 7 day forecast starting tomorrow 
    the forecasting function is attempted to be called with exception handling integrated
    """

    # if the vendor does not exist or has been incorrectly recieved: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
        
    vendor_id = current_user.vendor_profile.vendor_id

    start_date = date.today() + timedelta(days=1) # the default start date is set to tomrrow for baseline forcasts as they can only predict a week into the future

    try:
        # pass logic to dedicated function
        forecast_response = get_naive_forecast_chart(session, vendor_id, start_date)
        return forecast_response
    
    # use the logger to log the exceptions made
    except SQLAlchemyError:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception:
        logger.exception("error in forecast generation")
        raise HTTPException(status_code=500, detail="internal server error")
    




# endpoint for moving average baseline
@router.post("/moving-average", response_model=ForecastWeekData)
def moving_average_forecast(
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session) 
):
    
    """
    endpoint for the naive-moving average baseline
    this endpoint requires the current user and session as parameters
    the start date defaults to tomorrow -> providing a 7 day forecast starting tomorrow 
    the forecasting function is attempted to be called with exception handling integrated
    """
    
    # if the vendor does not exist or has been incorrectly recieved: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
    
    vendor_id = current_user.vendor_profile.vendor_id

    start_date = date.today() + timedelta(days=1) # the default start date is set to tomrrow for baseline forcasts as they can only predict a week into the future

    try:
        forecast_response = get_moving_average_forecast_chart(session=session, vendor_id=vendor_id, start_date=start_date)
        return forecast_response
    
    # catch exceptions: status 500: somwthing wrong on the server level
    except SQLAlchemyError:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception:
        logger.exception("error in forecast generation")
        raise HTTPException(status_code=500, detail="internal server error")




# endpoint for advanced forecasting - linear regression
@router.post("/linear-regression", response_model=ForecastWeekData)
def linear_regression_forecast(
    # default to tomorrow 
    start_date: Optional[date] = Query(None, description="First day of the target week"),
    days_ahead: Optional[int] = Query(None, description="the number of days from start date when the forecast should end -> (Optional) defaults to 7 days"),
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session) 
):
    
    """
    endpoint for the linear regression forecasting system
    this endpoint requires the current user and session as parameters
    start date is optional and defaults to tomorrow -> providing a 7 day forecast starting tomorrow
    due to the nature of linear regression forecasts for future dates e.g. 2 weeks ahead can be predicted but is currenty deafult as 7 days
    the linear regression forecasting function is attempted to be called with exception handling integrated
    """

    
    # if the vendor does not exist or has been incorrectly recieved: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
    
    vendor_id = current_user.vendor_profile.vendor_id

    if start_date is None:
        start_date = date.today() + timedelta(days=1)

    if days_ahead is None:
        days_ahead = 7

    # the max future date that can be predicted is 14 days into the future -> otherwise the accuracy is not reliable -> most likely 7 day forecasts from today will be requested
    last_forecast_day = start_date + timedelta(days=days_ahead - 1)
    if last_forecast_day > date.today() + timedelta(days=14):
        raise HTTPException(
            status_code=400,
            detail= f"linear regression forecast cannot predict more than 14 days in the future, date: {start_date + timedelta(days=days_ahead)} is too far in the future."
        )
    
    # start date cant be in the past
    if start_date < date.today():
        raise HTTPException(status_code=400, detail="Start date cannot be in the past")

    try:
        forecast_response = get_linear_regression_forecast_chart(session=session, vendor_id=vendor_id, start_date=start_date, days_ahead=days_ahead)
        return forecast_response
    
    # catch exceptions: status 500: somwthing wrong on the server level
    except SQLAlchemyError:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception:
        logger.exception("error in forecast generation")
        raise HTTPException(status_code=500, detail="internal server error")