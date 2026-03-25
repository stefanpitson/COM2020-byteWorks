from sqlmodel import Session, select
from app.models import Forecast_Input, Forecast_Output, Template, Vendor
from app.core.database import engine
from datetime import date, timedelta, datetime, time
from app.forecasting.baseline_approaches.seasonal_naive.evaluate_seasonal_naive import get_naive_confidence_for_bundle_day
from typing import Optional, List
from app.schema import ForecastDatapoint, ForecastWeekData, ForecastDayData
import json



def update_or_create(
    session: Session,
    vendor_id: int,
    template_id: int,
    target_date: date,
    slot_start: time,
    slot_end: time,
    model_type: str,
    reservation_prediction: int,
    no_show_prediction: int,
    recommendation: str,
    rationale: str,
    confidence: float
) -> Forecast_Output:

    """
    The function takes in all parameters of a potential output forecast
    checks if the forecast already exists
    if the forecast does exist update it
    if the forecast does not exist then create it 
    return the new or updated forecast
    """
    # we only need to check the below fields to ensure uniqueness (or in this case verify a duplcate)
    stmnt = select(Forecast_Output).where(
        Forecast_Output.vendor_id == vendor_id,
        Forecast_Output.template_id == template_id,
        Forecast_Output.date == target_date,
        Forecast_Output.slot_start == slot_start,
        Forecast_Output.slot_end == slot_end,
        Forecast_Output.model_type == model_type,
    )

    # execute the statement
    existing = session.exec(stmnt).first()

    # assume None at forst -> this is what will be returned
    forecast = None

    #if there does exist a session
    if existing:
        # update the remaining fields
        existing.reservation_prediction = reservation_prediction
        existing.no_show_prediction = no_show_prediction
        existing.recommendation = recommendation
        existing.rationale = rationale
        existing.confidence = confidence
        forecast = existing

    else:
        # otherwise we create the specified output forecast from scratch with the parameters 
        forecast = Forecast_Output(
            vendor_id=vendor_id,
            template_id=template_id,
            date=target_date,
            slot_start=slot_start,
            slot_end=slot_end,
            model_type=model_type,
            reservation_prediction=reservation_prediction,
            no_show_prediction=no_show_prediction,
            recommendation=recommendation,
            rationale=rationale,
            confidence=confidence
        )

    # return the forecast
    session.add(forecast)
    return forecast



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

            #make a statement to represent the potential output forecast we want to make
            existing_statement = select(Forecast_Output).where(
                Forecast_Output.vendor_id == vendor_id,
                Forecast_Output.template_id == record.template_id,
                Forecast_Output.date == target_date,
                Forecast_Output.slot_start == record.slot_start,
                Forecast_Output.slot_end == record.slot_end,
                Forecast_Output.model_type == "seasonal_naive"
            )
            # execute the statement
            forecast_exists = session.exec(existing_statement).first()

            # if the presumed forecast above does exists in the DB already
            if forecast_exists:
                # we update the existing statement (it will likely already be up to date)
                forecast_exists.reservation_prediction = record.bundles_reserved
                forecast_exists.no_show_prediction = record.no_shows
                forecast_exists.confidence = get_naive_confidence_for_bundle_day(
                    vendor_id=vendor_id, 
                    template_id=record.template_id, 
                    target_date=target_date
                )
                # add the updated model
                session.add(forecast_exists)

            else:
                # in the case where no matching output forecast has been found
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

        # commit the session and return a descriptive string of the changes
        session.commit()
        return f"generated forecast for vendor: {vendor_id} on day: {target_date}"




# main function that the endpoint will call
def get_naive_forecast_chart(session: Session, vendor_id: int, target_start_date: Optional[date] = None) -> ForecastWeekData:
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

    day_map = {} # map in the form of day: dict[title:day forecast]

    # loop through the results 
    for record, title in results:
        if not record.slot_start or not record.slot_end:
            continue

        predicted_date = record.date + timedelta(days=7)   
        day_str = predicted_date.isoformat()    
        day_abbr = predicted_date.strftime("%a")
        
        # Ensure values are not None
        bundles_reserved = record.bundles_reserved or 0
        no_shows = record.no_shows or 0
        
        # calculate no show chance as no_show / no_show+predicted
        total = bundles_reserved + no_shows
        chance = round(no_shows / total, 3) if total > 0 else 0.0

        # create recomedation string before - specific to naive model
        recommendation = (
            f"Post {bundles_reserved} {title} bundles on {day_abbr} between {record.slot_start} and {record.slot_end}")
        # create rationale string before - specific to naive model
        rationale = (
            f"last {day_abbr} sold {bundles_reserved} {title} bundles, "
            f"therefore you will sell {bundles_reserved} this {day_abbr}"
        )

        # use the helper function for the upserting logic
        current_forecast = update_or_create(session=session, 
            vendor_id=vendor_id, 
            template_id=record.template_id, 
            target_date=predicted_date, 
            slot_start=record.slot_start, 
            slot_end=record.slot_end,
            model_type="seasonal_naive",
            reservation_prediction=bundles_reserved,
            no_show_prediction=no_shows,
            recommendation=recommendation,
            rationale=rationale,
            confidence=get_naive_confidence_for_bundle_day(vendor_id=vendor_id, template_id=record.template_id, target_date=predicted_date)
            )

        if day_str not in day_map:
            day_map[day_str] = {} # no data exists for this day

        day_bundles = day_map[day_str]
        if title not in day_bundles:
            # new aggregated datapoint for this bundle
            day_bundles[title] = {
                "bundle_name": title,
                "predicted_sales": 0,
                "predicted_no_show": 0,
                "chance_sum": 0.0,
                "confidence_sum": 0.0,
                "count": 0,
                "recommendations": [],
                "rationales": []
            }


        agg = day_bundles[title]
        agg["predicted_sales"] += bundles_reserved
        agg["predicted_no_show"] += no_shows
        agg["chance_sum"] += chance
        agg["confidence_sum"] += current_forecast.confidence
        agg["count"] += 1
        agg["recommendations"].append(recommendation)
        agg["rationales"].append(rationale)

    # we create day datapoints which contain unique datapoints in nested loop
    day_datapoints: List[ForecastDayData] = []
    for day_str in sorted(day_map.keys()):
        bundles: List[ForecastDatapoint] = []
        for agg in day_map[day_str].values():
            # Compute averages and build the forecast data point 
            avg_chance = agg["chance_sum"] / agg["count"]
            avg_confidence = agg["confidence_sum"] / agg["count"]
            dp = ForecastDatapoint(
                bundle_name=agg["bundle_name"],
                predicted_sales=agg["predicted_sales"],
                predicted_no_show=agg["predicted_no_show"],
                chance_of_no_show=max(round(avg_chance, 3), 0.05),
                confidence=round(avg_confidence, 3),
                recommendation=agg["recommendations"],   # list of strings
                rationale=agg["rationales"]               # list of strings
            )
            bundles.append(dp) # add the datapoints to the list
        day_datapoints.append(ForecastDayData(date=day_str, datapoints=bundles))

    session.commit()
    return ForecastWeekData(week_date=target_start_date.isoformat(), day_datapoints=day_datapoints) # ensure we add the data for the start of the week and all day data points

if __name__ == "__main__":
    today = date.today()
    target = today + timedelta(days=1)
    with Session(engine) as session:
        vendor_ids = session.exec(select(Vendor.vendor_id)).all()
        for vid in vendor_ids:
            result = get_naive_forecast_chart(session, vid, target)
            week_json = json.dumps(result.model_dump(), indent=2, default=str)
            for day in result.day_datapoints:
                print(f"\n Day: {day.date}")
                day_json = json.dumps(day.model_dump(), indent=2, default=str)
                print(day_json)
     


# to run inside backend
# python -m app.core.database
# python -m app.forecasting.database_creation.seed_test_data
# python -m app.forecasting.database_creation.generate_input_forecasts
# python -m app.forecasting.database_creation.previous_weather

# for seasonal naive
# python -m app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast

# for moving average
# python -m app.forecasting.baseline_approaches.moving_average.moving_average_forecast

# for linear regression
# python -m app.forecasting.linear_regression.linear_regression_forecast