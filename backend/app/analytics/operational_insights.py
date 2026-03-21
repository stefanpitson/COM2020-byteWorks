from sqlmodel import Session, select, func
from app.models import Forecast_Input, Vendor, Template
from app.core.database import engine
from app.forecasting.database_creation.generate_input_forecasts import sync_forecast_inputs
from app.schema import post_window_datapoint, post_windows_data, popular_bundle_datapoint, popular_bundle_data
from typing import List
from datetime import date, timedelta, time
import json


def get_posting_windows(session: Session, vendor_id: int, days_back: int = 42) -> post_windows_data:
    """
    identify the most popular posting windows of a vendor regardless of bundle type
    for a set of time slots identify the weekly average over the last days_back days for a vendor
    package results into custom datapoint to be returned
    """

    sync_forecast_inputs(session, vendor_id, days_back)

    end_date = date.today() - timedelta(days=1)

    start_date = end_date - timedelta(days=days_back) 

    statement = select(func.avg(Forecast_Input.bundles_reserved - Forecast_Input.no_shows).label("avg_sold"), 
            Forecast_Input.slot_start, 
            Forecast_Input.slot_end
        ).where(Forecast_Input.vendor_id == vendor_id,
            Forecast_Input.date.between(start_date, end_date)
        ).group_by(Forecast_Input.slot_start, 
            Forecast_Input.slot_end
        ).order_by(Forecast_Input.slot_start)

    result = session.exec(statement).all()

    if not result: # if we didnt get any result we return empty data
        return post_windows_data(top_post_window="", window_datapoints=[])
    
    post_datapoints: List[post_window_datapoint] = [] # append all post datapoint to a list 
    
    for avg_sold, start, end in result:
        if end < time(6): 
            continue
        new_datapoint = post_window_datapoint(
            posting_timeslot=f"{start} - {end}",
            weekly_average=int(round((avg_sold*7), 0))
        )
        post_datapoints.append(new_datapoint)

    # post datapoints may be empty
    if not post_datapoints:
        return post_windows_data(top_post_window="", window_datapoints=[])

    # get the timeslot where the most bundles have been sold
    best_datapoint = max(post_datapoints, key=lambda p: p.weekly_average)

    best_window = best_datapoint.posting_timeslot

    return post_windows_data(top_post_window=best_window, window_datapoints=post_datapoints)
    


def get_bestselling_bundle_titles(session: Session, vendor_id: int, days_back: int = 42) -> popular_bundle_data:
    """
    data intended to be returned to fronted and display the top 3 best selling bundle titles
    we gather the weekly average of each bundle sold over the last days_back days
    use custom datapoints to return the result
    """

    sync_forecast_inputs(session, vendor_id, days_back)

    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=days_back) 
    total_days = (end_date - start_date).days + 1

    statement = select(
        Template.title,
        func.sum(Forecast_Input.bundles_reserved - Forecast_Input.no_shows).label('total_sold')
    ).join(
        Template, Forecast_Input.template_id == Template.template_id
    ).where(
        Forecast_Input.vendor_id == vendor_id,
        Forecast_Input.date.between(start_date, end_date)
    ).group_by(Template.title)
    
    result = session.exec(statement).all()

    if not result:
        return popular_bundle_data(top_bundle="", bundle_datapoints=[])
    
    datapoints = []
    for title, total_sold in result:
        daily_avg = total_sold / total_days
        weekly_avg = int(round(daily_avg * 7))
        datapoints.append(popular_bundle_datapoint(
            bundle_title=title,
            weekly_average=weekly_avg
        ))

    if not datapoints:
        return popular_bundle_data(top_bundle="", bundle_datapoints=[])

    # sort and find the best datapoints - top 3
    datapoints.sort(key=lambda p: p.weekly_average, reverse=True)
    top_three = datapoints[:3]
    top_bundle = top_three[0].bundle_title if top_three else ""

    # return the data item
    return popular_bundle_data(top_bundle=top_bundle, bundle_datapoints=top_three)


if __name__ == "__main__":

    # python -m app.analytics.operational_insights

    with Session(engine) as session:
        vendor_ids = session.exec(select(Vendor.vendor_id)).all()
        for vid in vendor_ids:
            try:
                result = get_posting_windows(session=session, vendor_id=vid)
                print("Posting windows:")
                print(json.dumps(result.model_dump(), indent=2, default=str))
            except Exception as e:
                print(f"Error in posting windows: {e}")

         