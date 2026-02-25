from fastapi import APIRouter, Query, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.api.deps import get_current_user
from app.schema import ForecastWeekData
from app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast import get_naive_forecast_chart
from datetime import date
from datetime import timedelta

router = APIRouter()

@router.get("/naive", response_model=ForecastWeekData)
def naive_forecast(
    # default to tomorrow 
    start_date: date = Query(None, description="First day of the target week"),
    current_user = Depends(get_current_user),
    session: Session = Depends(get_session) 
):
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="User has no vendor profile associated")
        
    vendor_id = current_user.vendor_profile.vendor_id
    if not start_date:
        start_date = date.today() + timedelta(days=1)

    try:
        # pass logic to dedicated function
        forecastResponse = get_naive_forecast_chart(session, vendor_id, start_date)
        return forecastResponse
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Forecasting Error: {str(e)}")