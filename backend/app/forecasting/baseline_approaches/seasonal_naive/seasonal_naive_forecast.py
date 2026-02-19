from datetime import date, timedelta
from sqlmodel import Session, select
from app.models import Forecast_Input, Forecast_Output, Template
from app.core.database import engine
from datetime import date, timedelta, datetime
from app.forecasting.baseline_approaches.seasonal_naive.evaluate_seasonal_naive import get_naive_confidence_for_bundle_day
from typing import Optional


def generate_naive_forecast(vendor_id: int, target_date: Optional[date] = None) -> str:
    """
    Creates a naive forecast by looking at
    performance exactly 7 days prior to target_date.
    This then creates an output entity for a given week
    """
    if target_date is None:
        target_date = date.today() + timedelta(days=1)

    with Session(engine) as session:
        # look back one week
        historical_date = target_date - timedelta(days=7)

        # get all inputs from that day for this vendor
        statement = select(Forecast_Input).where(
            Forecast_Input.vendor_id == vendor_id,
            Forecast_Input.date == historical_date
        )
        historical_data = session.exec(statement).all()

        if not historical_data:
            return f"No historical data found for vendor {vendor_id} on {historical_date}."

        for record in historical_data:
            # create the forecast output
            new_forecast = Forecast_Output(
                vendor_id=vendor_id,
                template_id=record.template_id,
                date=target_date,
                slot_start=record.slot_start,
                slot_end=record.slot_end,
                reservation_prediction=record.bundles_reserved,
                no_show_prediction=record.no_shows,
                model_type="seasonal_naive",
                recommendation=f"Post {record.bundles_reserved} bundles on {target_date.strftime('%a')}",
                rationale=f"we assume {target_date} will sell a similar number of bundles as {historical_date} given {record.bundles_reserved} bundles are posted",
                confidence=get_naive_confidence_for_bundle_day(vendor_id=vendor_id, template_id=record.template_id, target_date=target_date)
            )
            session.add(new_forecast)

        session.commit()
       





def get_naive_forecast_chart(session: Session, vendor_id: int, target_start_date: Optional[date] = None) -> dict:
    """
    for a vendor create the output forecast entities using the seasonal naive model
    for a particular week starting on tartget_start_date
    return: in object json format the forcast for a particular format
    """

    if target_start_date is None:
        target_start_date = date.today() + timedelta(days=1)


    # set the start date as a week before the target date to allow for easier calculations
    historical_start = target_start_date - timedelta(days=7)
    historical_end = historical_start + timedelta(days=6)

    # generate a statement to gather relevant information needed for the calculation
    stmt = (
        select(Forecast_Input, Template.title)
        .join(Template, Forecast_Input.template_id == Template.template_id)
        .where(
            Forecast_Input.vendor_id == vendor_id,
            Forecast_Input.date >= historical_start,
            Forecast_Input.date <= historical_end
        )
        .order_by(Forecast_Input.date, Forecast_Input.slot_start, Template.title)
    )

    # execute the statement
    results = session.exec(stmt).all()
    datapoints = []

    # loop through the results 
    for record, title in results:
        if not record.slot_start or not record.slot_end:
            continue

        predicted_date = record.date + timedelta(days=7)
        day_name = predicted_date.strftime("%A")        
        day_abbr = predicted_date.strftime("%a")
        
        # Ensure values are not None
        bundles_reserved = record.bundles_reserved or 0
        no_shows = record.no_shows or 0
        
        # calculate no show chance as no_show / no_show+predicted
        total_reserved_and_no_show = bundles_reserved + no_shows
        chance_of_no_show = (
            round(no_shows / total_reserved_and_no_show, 3)
            if total_reserved_and_no_show > 0 else 0.0
        ) 

        
        # Subtract one hour from slot_start for the recommendation for helpful preperaton time
        rec_start = (datetime.combine(date.today(), record.slot_start) - timedelta(hours=1)).time()
        rec_start_str = rec_start.strftime("%H:%M")

        # create recomedation string before - specific to naive model
        recommendation = (
            f"Post {bundles_reserved} {title} bundles on {day_abbr} "
            f"by {rec_start_str}"
        )
        # create rationale string before - specific to naive model
        rationale = (
            f"last {day_abbr} sold {bundles_reserved} {title} bundles, "
            f"therefore you will sell {bundles_reserved} this {day_abbr}"
        )

        # Upsert forecast output - avoid duplicates
        existing = session.exec(
            select(Forecast_Output).where(
                Forecast_Output.vendor_id == vendor_id,
                Forecast_Output.template_id == record.template_id,
                Forecast_Output.date == predicted_date,
                Forecast_Output.slot_start == record.slot_start,
                Forecast_Output.slot_end == record.slot_end,
                Forecast_Output.model_type == "seasonal_naive"
            )
        ).first()

        current_forecast = None
        # in the case there already existse the forecast we are tying to make
        if existing:
            existing.reservation_prediction = bundles_reserved
            existing.no_show_prediction = no_shows
            existing.recommendation = recommendation
            existing.rationale = rationale
            existing.confidence = get_naive_confidence_for_bundle_day(vendor_id=vendor_id, template_id=record.template_id, target_date=existing.date)
            session.add(existing)
            current_forecast = existing
        else:
            current_forecast = Forecast_Output(
                vendor_id=vendor_id,
                template_id=record.template_id,
                date=predicted_date,
                slot_start=record.slot_start,
                slot_end=record.slot_end,
                reservation_prediction=bundles_reserved,
                no_show_prediction=no_shows,
                model_type="seasonal_naive",
                recommendation=recommendation,
                rationale=rationale,
                confidence=get_naive_confidence_for_bundle_day(vendor_id=vendor_id, template_id=record.template_id, target_date=predicted_date)
            )
            session.add(current_forecast)

        # build data to be sent to frontend
        datapoints.append({
            "bundle_name": title,                 
            "predicted_sales": bundles_reserved,
            "chance_of_no_show": chance_of_no_show,
            "day": day_name,
            "start_time": record.slot_start.isoformat(),
            "end_time": record.slot_end.isoformat(),
            "no_show": no_shows,
            "confidence": current_forecast.confidence,
            "recommendation": recommendation,
            "rationale": rationale
        })

    session.commit()

    return {
        "week_data": [
            {
                "week_date": target_start_date.isoformat(),
                "datapoints": datapoints
            }
        ]
    }
if __name__ == "__main__":
    today = date.today()
    target = today + timedelta(days=1)

    print(f"Generating forecasts for week starting {target}")
    with Session(engine) as session:
        result = get_naive_forecast_chart(session, 1, target)
        import json
        print(json.dumps(result, indent=2, default=str))


# to run inside backend
# python -m app.forecasting.database_creation.seed_test_data
# python -m app.forecasting.database_creation.generate_input_forecasts
# python -m app.forecasting.database_creation.previous_weather
# python -m app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast