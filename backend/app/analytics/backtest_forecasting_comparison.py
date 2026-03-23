from sqlmodel import Session, select, func
from app.models import Forecast_Input, Forecast_Output, Vendor
from app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast import get_naive_forecast_chart
from app.forecasting.baseline_approaches.moving_average.moving_average_forecast import get_moving_average_forecast_chart
from app.forecasting.linear_regression.linear_regression_forecast import get_linear_regression_forecast_chart
from datetime import date, timedelta
from typing import Dict
import numpy as np
from app.core.database import engine


def backtest_models(session: Session, vendor_id: int, test_start: date, test_end: date) -> Dict[str, Dict[str, float]]:
    """
    This function uses all 3 models to calculate the necessary output forecasts for a given help out test period
    back testing is then used to compare the Forecast_Output entities to the actual Forecast_Input entities 
    an MAE and r2 score is calculated for both no show and reservation predictions which is averaged
    a final MAE and r2 score is calculated for each model
    """

    current = test_start # we call our get model chart functions to generate all output forecasts needed for the relevant dates
    while current <= test_end:

        get_naive_forecast_chart(session, vendor_id, target_start_date=current)

        get_moving_average_forecast_chart(session, vendor_id, start_date=current)

        get_linear_regression_forecast_chart(session, vendor_id, start_date=current, days_ahead=1)
        current += timedelta(days=1)

    actuals = {}
    stmt = select(Forecast_Input).where(
        Forecast_Input.vendor_id == vendor_id,
        Forecast_Input.date.between(test_start, test_end)
    )
    for actual in session.exec(stmt):
        key = (actual.template_id, actual.date, actual.slot_start, actual.slot_end)
        actuals[key] = (actual.bundles_reserved, actual.no_shows)

  
    results = {}
    for model_type in ['seasonal_naive', 'moving_average', 'linear_regression']:

        forecasts = session.exec( # get all relevant forecasts
            select(Forecast_Output).where(
                Forecast_Output.vendor_id == vendor_id,
                Forecast_Output.model_type == model_type,
                Forecast_Output.date.between(test_start, test_end)
            )
        ).all()

        res_errors = []
        res_actuals = []
        ns_errors = []
        ns_actuals = []

        # for each forecast we append metrics to list to be averaged later
        for f in forecasts:
            key = (f.template_id, f.date, f.slot_start, f.slot_end)
            if key in actuals:
                act_res, act_ns = actuals[key]
                res_errors.append(f.reservation_prediction - act_res)
                res_actuals.append(act_res)
                ns_errors.append(f.no_show_prediction - act_ns)
                ns_actuals.append(act_ns)

        # if the re or ns list is empty then return nan values for this model
        if not res_errors or not ns_errors:
            results[model_type] = {'avg_mae': float('nan'), 'avg_r2': float('nan')}
            continue

        # get the mean and var of reservations made
        res_mae = np.mean(np.abs(res_errors))
        res_var = np.sum(np.square(res_actuals - np.mean(res_actuals)))
        if res_var == 0:
            res_r2 = np.nan
        else:
            res_r2 = 1 - np.sum(np.square(res_errors)) / res_var

        # get the mae and var of no shows
        ns_mae = np.mean(np.abs(ns_errors))
        ns_var = np.sum(np.square(ns_actuals - np.mean(ns_actuals)))
        if ns_var == 0:
            ns_r2 = np.nan
        else:
            ns_r2 = 1 - np.sum(np.square(ns_errors)) / ns_var

        # average the two metrics
        avg_mae = (res_mae + ns_mae) / 2
        avg_r2 = (res_r2 + ns_r2) / 2

        results[model_type] = {'avg_mae': avg_mae, 'avg_r2': avg_r2}

    return results


if __name__ == "__main__":
    pass

# Test period: 2026-03-08 to 2026-03-21

# seasonal_naive: avg MAE = 1.946, avg R² = -1.564 (based on 24 vendors)
# moving_average: avg MAE = 1.806, avg R² = -0.780 (based on 25 vendors)
# linear_regression: avg MAE = 1.537, avg R² = -0.213 (based on 25 vendors)