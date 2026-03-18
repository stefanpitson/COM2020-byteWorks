from sqlmodel import Session, select, func
from app.models import Forecast_Input, Forecast_Output, Template, Vendor
from app.core.database import engine
from datetime import date, timedelta
from typing import Optional, List
from app.schema import ForecastDatapoint, ForecastWeekData, ForecastDayData
from app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast import update_or_create
import json



def moving_avg_confidence_score(num_days: int, expected_max: int, avg: Optional[float], std: Optional[float]) -> float:
    """
    simple confidence fucntion that uses %of days we have data for as well as std/avg to determine a basic confidence score
    """
    if std is None:
        std = 0.0
    if avg is None:
        avg = 0.0

    # this is okay because the function call will never be reached unless a vendor has at least {context_window} days of data
    q = min(1.0, num_days / expected_max)  # this is a % of days we have data for  

    if avg <= 0:
        if std == 0:
            v = 0.8   
        else:
            v = 0.0

    else:
        cv = std / avg #covar
        v = max(0.0, 1.0 - float(cv))

    if num_days < 3: # threshold for minimum num days allowed
        v *= (num_days / 3)

    # weighting for both q and v -> amount of data is more important
    confidence = (q * 0.7) + (v * 0.3) # to be conservative
    return round(confidence, 3)






def generate_moving_average_forecast(
    session: Session,
    vendor_id: int,
    start_date: date,
    context_window: int = 28,  # e.g. we assume we want to consider the last 4 weeks of data for predicitions for the next x weeks  
    furthest_day: int = 7 # how long into the future we allow the model to predict -> will likely always be a week           
) -> List[Forecast_Output]:
    
    """
    generates the output forecast entities needed for furthest_day days into the future
    context_window is how long in the past we allow the model to see -> this can be tuned to produce the best results but is set to 4 weeks for now
    the list of generated forcast output is returned and can be used in a seperate function to generate forecast data points
    """

    forecast_outputs = []

    
    # for every day in the future
    for days in range(furthest_day):
        # we loop through all days from the start date to the limit num of days in the future
        target_day = start_date + timedelta(days=days)
        week_day = target_day.weekday()
        db_weekday = (week_day + 1) % 7 # convert to weekday the DB can understand 1, 2, 3 not 0, 1, 2

        # start and end of history to be searched for
        start_history = target_day - timedelta(days=context_window)
        end_history = min((target_day - timedelta(days=1)), date.today())


        statement = (
            select(
                Template.title,
                Forecast_Input.template_id, 
                Forecast_Input.slot_start,
                Forecast_Input.slot_end,
                func.avg(Forecast_Input.bundles_reserved).label('avg_reserved'), # assign aliases
                func.avg(Forecast_Input.no_shows).label('avg_no_shows'),
                func.stddev(Forecast_Input.bundles_reserved).label('std_reserved'), # needed for confidence
                func.count().label('num_days')  # count the number of occurences -> we can know e.g. only 2/14 days contain entries
            ).where(
                Forecast_Input.vendor_id == vendor_id,
                Forecast_Input.date.between(start_history, end_history), # filter between the history dates
                func.extract('dow', Forecast_Input.date) == db_weekday # dow - day of week -> ensure we use the correct day of week
            ).group_by( # 3 stage grouping
                Forecast_Input.template_id,
                Forecast_Input.slot_start,
                Forecast_Input.slot_end,
                Template.title # needed since we are selecting the template title
            ).join(Template, Forecast_Input.template_id == Template.template_id) # join on template so we can use title
        )

        # get results by executing statement
        averages_result = session.exec(statement=statement).all()

        for res in averages_result:

            # we now build the new forecast outputs using the helper function

            title = res.title if res.title is not None else "No title"

            # ensure that the below values are assigned a value as they may be None
            avg_reserved = res.avg_reserved if res.avg_reserved is not None else 0.0
            avg_no_shows = res.avg_no_shows if res.avg_no_shows is not None else 0.0

            # make string recommendation and rationale
            recommendation = f"Post {int(avg_reserved)} {title} bundles between {res.slot_start} and {res.slot_end} on {target_day.strftime('%A')} "

            rationale = f"Over the last {context_window} days, on average {avg_reserved:.2f} {title} bundles have been reserved"


            days_in_range = (end_history - start_history).days + 1
            expected_max = (days_in_range + 6) // 7
            confidence = round(moving_avg_confidence_score(num_days=int(res.num_days), expected_max=expected_max, avg=avg_reserved, std= res.std_reserved), 3)

            # use the helper function to update the output forecast or make it if it doesnt already exist
            forecast = update_or_create(
                session=session,
                vendor_id=vendor_id,
                template_id=res.template_id,
                target_date=target_day,
                slot_start=res.slot_start,
                slot_end=res.slot_end,
                model_type="moving_average",
                reservation_prediction=int(avg_reserved),
                no_show_prediction=int(avg_no_shows),
                recommendation=recommendation,
                rationale=rationale,
                confidence=confidence
            )

            forecast_outputs.append(forecast) # add to master list

    return forecast_outputs



# main function that the endpoint will call
def get_moving_average_forecast_chart(session: Session, vendor_id: int, start_date: date = date.today()+timedelta(days=1)) -> ForecastWeekData:
    """
    This function calls the helper generate_moving_average_forecast to create all output forecast entities that will be needed
    we go through the outputs needed list and systematically generate the forecast datapoints which are appended to make the final ForecastWeekData class
    """

    # gather outputs from the helper function
    outputs_needed: List[Forecast_Output] = generate_moving_average_forecast(session=session, vendor_id=vendor_id, start_date=start_date)

    # if there were no outputs produced - meaning the vendor does not have enough data return []
    if not outputs_needed:
        return ForecastWeekData(week_date=start_date.isoformat(), day_datapoints=[])

    # logic for making a dictionary mapping template id -> template title
    template_ids = list({o.template_id for o in outputs_needed if o.template_id})
    title_rows = session.exec(
        select(Template.template_id, Template.title).where(Template.template_id.in_(template_ids))).all()
    
    title_map = {row.template_id: row.title for row in title_rows}

    day_datapoints: List[ForecastDayData]  = [] # for adding all day datapoints in the loop to be processed before return

    map_total: dict[tuple[str, str], int] = {} # must hold all relevant date, name unique tuples so we can determine how to correctly average averaged fields like confidence

    # go through the forecast outputs
    for output in outputs_needed:
        date_d = output.date.isoformat()
        # calculate no show chance as no_show / no_show+predicted
        total = output.reservation_prediction + output.no_show_prediction
        chance_of_no_show = max((round(output.no_show_prediction / total, 3) if total > 0 else 0.0), 0.05)

        title = title_map.get(output.template_id, "Unknown") # use the dictionary to find the exact title from the template id

        index_day = next((i for i, day in enumerate(day_datapoints) if day.date == date_d), None)

        if index_day is not None: # if the day data point already exists
            day_to_add: List[ForecastDatapoint] = day_datapoints[index_day].datapoints
            index_point = next((i for i, point in enumerate(day_to_add) if point.bundle_name == title), None)
            if index_point is not None: #  there are duplicates - already exists
                agg_point: ForecastDatapoint = day_to_add[index_point]
                # must update it
                agg_point.chance_of_no_show += chance_of_no_show
                agg_point.confidence += output.confidence
                agg_point.predicted_sales += output.reservation_prediction
                agg_point.predicted_no_show += output.no_show_prediction
                agg_point.recommendation.append(output.recommendation)
                agg_point.rationale.append(output.rationale)

            else: # the day is the same but the bundle name does not already exist
                p = ForecastDatapoint(bundle_name = title,
                chance_of_no_show = chance_of_no_show,
                confidence = output.confidence,
                predicted_sales = output.reservation_prediction,
                predicted_no_show = output.no_show_prediction,
                recommendation= [output.recommendation],
                rationale = [output.rationale])

                day_datapoints[index_day].datapoints.append(p) # add the new datapoint to the appropriate date

        else: # the day datapoint does not yet exist we need to make a new day datapoint
            new_day = ForecastDayData(
                date=output.date.isoformat(),
                datapoints= [ForecastDatapoint(bundle_name = title,
                chance_of_no_show = chance_of_no_show,
                confidence = output.confidence,
                predicted_sales = output.reservation_prediction,
                predicted_no_show = output.no_show_prediction,
                recommendation= [output.recommendation],
                rationale = [output.rationale])]
            )
            day_datapoints.append(new_day)

        # add to the totals 
        map_total[(date_d, title)] = map_total.get((date_d, title), 0) + 1
     


    # at this point we should have all datapoints added and inside the day datapoints list BUT averages have not yet been averaged
    for day_da in day_datapoints:
        for p in day_da.datapoints:
            p.chance_of_no_show = round(p.chance_of_no_show / map_total.get((day_da.date, p.bundle_name), 1), 3)
            p.confidence = round(p.confidence / map_total.get((day_da.date, p.bundle_name), 1), 3)

    session.commit()

    # return the weekdatapoints object
    return ForecastWeekData(week_date=start_date.isoformat(), day_datapoints=day_datapoints)

    



if __name__ == "__main__":
    #python -m app.forecasting.baseline_approaches.moving_average.moving_average_forecast
    with Session(engine) as session:
        vendor_ids = session.exec(select(Vendor.vendor_id))
        for id in vendor_ids:
            result = get_moving_average_forecast_chart(session, id)
            week_json = json.dumps(result.model_dump(), indent=2, default=str)
            for day in result.day_datapoints:
                print(f"\n Day: {day.date}")
                day_json = json.dumps(day.model_dump(), indent=2, default=str)
                print(day_json)
         