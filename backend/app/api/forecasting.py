from fastapi import APIRouter, Query, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.schema import ForecastChartResponse
from app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast import get_naive_forecast_chart
from datetime import date
from datetime import timedelta

router = APIRouter()

@router.get("/naive", response_model=ForecastChartResponse)
def naive_forecast(
    vendor_id: int = Query(...),
    # default to tomorrow 
    start_date: date = Query(None, description="First day of the target week"),
    session: Session = Depends(get_session) 
):
    if not start_date:
        start_date = date.today() + timedelta(days=1)

    # pass logic to dedicated function
    return get_naive_forecast_chart(session, vendor_id, start_date)