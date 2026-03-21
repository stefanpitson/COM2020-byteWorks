from sqlmodel import Session, select, func
from app.models import Forecast_Input, Forecast_Output, Template, Vendor
from app.core.database import engine
from datetime import date, timedelta
from typing import Optional, List
from app.schema import ForecastDatapoint, ForecastWeekData, ForecastDayData
from app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast import get_naive_forecast_chart
from app.forecasting.baseline_approaches.moving_average.moving_average_forecast import generate_moving_average_forecast
from app.forecasting.linear_regression.linear_regression_forecast import generate_linear_regression_forecast

