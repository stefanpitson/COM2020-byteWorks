from fastapi import APIRouter, Query, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.api.deps import get_current_user
from app.schema import ForecastWeekData
from app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast import get_naive_forecast_chart
from app.forecasting.baseline_approaches.moving_average.moving_average_forecast import get_moving_average_forecast_chart
from datetime import date
from datetime import timedelta
from fastapi import HTTPException
import logging
from sqlalchemy.exc import SQLAlchemyError

# all forecasting functions that need to be called will be of the form: get_{model name}_forecast_chart

# log errors produced
logger = logging.getLogger(__name__)

# more descriptive router with forecasting prefix added
router = APIRouter(prefix="/forecast", tags=["Forecasting"])

# changed to post for now as modifies the db
@router.post("/naive", response_model=ForecastWeekData)
def naive_forecast(
    # default to tomorrow 
    start_date: date = Query(None, description="First day of the target week"),
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session) 
):
    
    """
    eendpoint for the naive baseline
    this endpoint requires the current user and session as parameters
    start date is optional and defaults to tomorrow -> providing a 7 day forecast starting tomorrow
    although it is unlikely, target dates cannot be more than 7 days in the future or no forecasts will have been generated
    the forecasting function is attempted to be called with exception handling integrated
    """

    # if the vendor does not exist or has been incorrectly recieved: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
        
    vendor_id = current_user.vendor_profile.vendor_id
    if not start_date:
        start_date = date.today() + timedelta(days=1)

    if start_date > date.today()+timedelta(days=7):
        raise HTTPException(
            status_code=400,
            detail= f"Seasonal naive forecast cannot predict more than 7 days in the future, requested start date: {start_date} is too far in the future."
        )

    # the date cannot be in the past
    if start_date < date.today():
        raise HTTPException(status_code=400, detail="Start date cannot be in the past")

    try:
        # pass logic to dedicated function
        forecast_response = get_naive_forecast_chart(session, vendor_id, start_date)
        return forecast_response
    
    # use the logger to log the exceptions made
    except SQLAlchemyError as s:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception as e:
        logger.exception("error in forecast generation")
        raise HTTPException(status_code=500, detail="internal server error")
    




# endpoint for moving average baseline
@router.post("/moving-average", response_model=ForecastWeekData)
def moving_average_forecast(
    # default to tomorrow 
    start_date: date = Query(None, description="First day of the target week"),
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session) 
):
    
    """
    endpoint for the naive moving average baseline
    this endpoint requires the current user and session as parameters
    start date is optional and defaults to tomorrow -> providing a 7 day forecast starting tomorrow
    although it is unlikely, target dates cannot be more than 7 days in the future or no forecasts will have been generated
    the forecasting function is attempted to be called with exception handling integrated
    """
    
    # if the vendor does not exist or has been incorrectly recieved: 400 code: client send bad request
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
    
    vendor_id = current_user.vendor_profile.vendor_id

    if not start_date:
        start_date = date.today() + timedelta(days=1)

    # devs can change this to predict longer in the future inside the function generate_moving_average_forecast in dir backend.app.forecasting.baseline_approaches.moving_average.moving_average_forecast.py
    if start_date > date.today()+timedelta(days=7):
        raise HTTPException(
            status_code=400,
            detail= f"moving average forecast cannot predict more than 7 days in the future, requested start date: {start_date} is too far in the future."
        )
    
    # start date cant be in the past
    if start_date < date.today():
        raise HTTPException(status_code=400, detail="Start date cannot be in the past")

    try:
        forecast_response = get_moving_average_forecast_chart(session=session, vendor_id=vendor_id, start_date=start_date)
        return forecast_response
    
    # catch exceptions: status 500: somwthing wrong on the server level
    except SQLAlchemyError as s:
        logger.exception("error when loading database")
        raise HTTPException(status_code=500, detail="Data Base error")
    
    except Exception as e:
        logger.exception("error in forecast generation")
        raise HTTPException(status_code=500, detail="internal server error")


