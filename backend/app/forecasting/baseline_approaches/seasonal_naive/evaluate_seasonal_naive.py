from datetime import date, timedelta
from sqlmodel import Session, select
from app.models import Forecast_Input
from app.core.database import engine

def get_naive_confidence_for_bundle_day(vendor_id: int,template_id: int,target_date: date,weeks_history: int = 4) -> float:
    """
    for a vendor and date we should calculate how confident we are for this day of the week and bundle
    This will return confidence reflecting confidence in number of bundles predicted to sell only
    """
    day_of_week = target_date.strftime("%A")
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(weeks=weeks_history) + timedelta(days=1)

    errors = []      
    actuals = []     

    with Session(engine) as session:
        current = start_date
        while current <= end_date:
            # calculate the days that are of the same day of the week as target_date
            if current.strftime("%A") != day_of_week:
                current += timedelta(days=1)
                continue

            # the data for the current day
            current_records = session.exec(
                select(Forecast_Input).where(
                    Forecast_Input.vendor_id == vendor_id,
                    Forecast_Input.template_id == template_id,
                    Forecast_Input.date == current
                )
            ).all()

            # data from the same day a week earlier so we can compare them
            past_date = current - timedelta(days=7)
            past_records = session.exec(
                select(Forecast_Input).where(
                    Forecast_Input.vendor_id == vendor_id,
                    Forecast_Input.template_id == template_id,
                    Forecast_Input.date == past_date
                )
            ).all()

            # lookup for past records
            past_dict = {}
            for rec in past_records:
                key = (rec.slot_start, rec.slot_end)
                past_dict[key] = rec.bundles_reserved

            # using the lookup table calculate how close the predicted vs actual is
            for cur in current_records:
                key = (cur.slot_start, cur.slot_end)
                if key in past_dict:
                    past_res = past_dict[key]
                    errors.append(abs(cur.bundles_reserved - past_res))
                    actuals.append(cur.bundles_reserved)

            current += timedelta(days=1) # increment our date and continue

    if not errors or not actuals:
        # there isnt enough data so the confidence is neutral
        return 0.5

    # confidnece calculation
    mae = sum(errors) / len(errors)
    avg_actual = sum(actuals) / len(actuals)

    if avg_actual > 0:
        confidence = max(0.0, 1.0 - (mae / avg_actual))
    else:
        confidence = 1.0 if mae == 0 else 0.0

    return round(confidence, 3) # round the result to a 3dp float


if __name__ == "__main__":
    result = get_naive_confidence_for_bundle_day(vendor_id=1, template_id=2, target_date=date.today())
    print(result)


#inside backend
# run with:  python -m app.forecasting.baseline_approaches.seasonal_naive.evaluate_seasonal_naive