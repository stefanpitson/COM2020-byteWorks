from datetime import date, timedelta
from sqlmodel import Session, select
from app.models import Forecast_Input, Forecast_Output, Template
from app.core.database import engine



def generate_naive_forecast(vendor_id: int, target_date: date) -> str:
    """
    Creates a naive forecast by looking at
    performance exactly 7 days prior to target_date.
    """
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
            return f"No historical data found for vendor {vendor_id} on {historical_date}. No forecasts generated."

        for record in historical_data:
            # generate the output forecast based on our naive calculations
            new_forecast = Forecast_Output(
                vendor_id=vendor_id,
                template_id=record.template_id,
                date=target_date,
                slot_start=record.slot_start,
                slot_end=record.slot_end,
                reservation_prediction=record.bundles_reserved,
                no_show_prediction=record.no_shows,
                model_type="seasonal_naive",
                rationale=f"we assume {target_date} will sell a similar number of bundles as {historical_date} given {record.bundles_reserved} bundles are posted",
                confidence=0.50  
            )
            session.add(new_forecast)

        session.commit()
       





def get_naive_forecast_chart(
    session: Session,
    vendor_id: int,
    target_start_date: date
) -> dict:
    historical_start = target_start_date - timedelta(days=7)
    historical_end = historical_start + timedelta(days=6)

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

    results = session.exec(stmt).all()
    datapoints = []

    for record, title in results:
        predicted_date = record.date + timedelta(days=7)
        day_abbr = predicted_date.strftime("%a")
        slot_str = record.slot_start.strftime("%H:%M")
        bundle_name = f"{day_abbr} {slot_str}: {title}"
        historical_day_abbr = record.date.strftime("%a")   # for the recommendation

        # prevent duplicates
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

        if existing:
            existing.reservation_prediction = record.bundles_reserved
            existing.no_show_prediction = record.no_shows
            existing.rationale = f"Based on actual data from {record.date} (same day last week)."
            existing.confidence = 0.5
            session.add(existing)
        else:
            forecast = Forecast_Output(
                vendor_id=vendor_id,
                template_id=record.template_id,
                date=predicted_date,
                slot_start=record.slot_start,
                slot_end=record.slot_end,
                reservation_prediction=record.bundles_reserved,
                no_show_prediction=record.no_shows,
                model_type="seasonal_naive",
                rationale=f"Based on actual data from {record.date} (same day last week).",
                confidence=0.5
            )
            session.add(forecast)

        # Simple recommendation 
        recommendation = f"Post {record.bundles_reserved} bundles based on last {historical_day_abbr}."

        datapoints.append({
            "bundle_name": bundle_name,
            "predicted": record.bundles_reserved,
            "no_show": record.no_shows,
            "posted": record.bundles_posted,
            "recommendation": recommendation
        })

    session.commit()


    return {
        "data": {
            "week_data": [
                {
                    "week_date": target_start_date.isoformat(),
                    "datapoints": datapoints
                }
            ]
        }
    }


if __name__ == "__main__":

    vendor_id = 1
    
    today = date.today()
    target = today + timedelta(days=1)  

    print(f"Generating forecasts for week starting {target}")
    with Session(engine) as session:
        result = get_naive_forecast_chart(session, vendor_id, target)

        import json
        print(json.dumps(result, indent=2, default=str))