from sqlmodel import Session, select, func
from app.models import Forecast_Input, Forecast_Output, Template, Vendor
from app.core.database import engine
from datetime import date, timedelta, time
from app.forecasting.database_creation.previous_weather import get_future_weather
from typing import Optional, List, Tuple
from app.schema import ForecastDatapoint, ForecastWeekData, ForecastDayData
import pandas as pd
from app.forecasting.linear_regression.preprocessing import get_vendors_performance, get_rolling_avg_field
from app.forecasting.baseline_approaches.seasonal_naive.seasonal_naive_forecast import update_or_create
import joblib
import json
import os



def compute_std_var(session: Session, vendor_id: int, template_id: int, field: str, slot_start: time, slot_end: time, weeks_back: int = 6) -> Tuple[int, float]:
    """
    This function is a helper to be called for calculating the credibility of a particular prediction based on previous performance
    This is template vendor, time slot and field specific
    a tuple containing (count, standard deviation) is returned
    weeks_back: must be the same as in get_rolling_avg_field to ensure consistency
    """

    if not hasattr(Forecast_Input, field):
        raise AttributeError(f"{field} is not a valid field within ForecastInput")

    history_start = date.today() - timedelta(weeks=weeks_back)

    history_end = date.today() - timedelta(days=1)

    # we want to select the number of overall records over the past N weeks for this slot and template and field since high count = increased confidence
    statement = select(
        func.count().label('cnt'),
        func.stddev_samp(getattr(Forecast_Input, field)).label('std') # get the standard deviation -> varaince
    ).where(
        Forecast_Input.vendor_id == vendor_id,
        Forecast_Input.template_id == template_id,
        Forecast_Input.slot_start == slot_start,
        Forecast_Input.slot_end == slot_end,
        Forecast_Input.date.between(history_start, history_end)
    )

    result = session.exec(statement).first()

    # we calculate correct count and standard deviation values including a fallback
    if result is None or result.cnt == 0:
        return (0, 0.0)

    count = result.cnt 

    std = float(result.std) if result.std else 0.0

    return (count, std)




def get_active_slots(session: Session, vendor_id: int, weeks_back: int = 6) -> list[Tuple[int, time, time, int]]:
    """
    for a given vendor we will compute all unique (template id, slot start, slot end, day of week) instances
    this is to determine the domain for which to generate the traing data - else we would be forcing the model to make predictions for extrememly unlikely scenarios
    """
    # start date generated as days_back days back from today
    start_date = date.today()-timedelta(weeks=weeks_back)

    # create the statement to select all uniqie and releveant statements
    statement = select(Forecast_Input.template_id,
        Forecast_Input.slot_start,
        Forecast_Input.slot_end,
        func.extract('dow', Forecast_Input.date).label("dow")
        ).where(Forecast_Input.vendor_id == vendor_id,
        Forecast_Input.date >= start_date
        ).distinct()
    
    results = session.exec(statement).all() # exec statement

    unique_slots: list[Tuple[int, time, time, int]] = [] 
    
    # pythin time is needed here which is 0: monday , 2: tuesday .... sunday: 6
    for res in results:
        p_dow = (int(res.dow)-1)%7
        unique_slots.append((res.template_id, res.slot_start, res.slot_end, p_dow))

    return unique_slots



def precompute_rolling_averages(session, vendor_id, slots, cutoff_date):
    """
    slots: list of (template_id, slot_start, slot_end, dow)
    we must precompute a cache of rolling averages for a vendor using the helper
    cache in the form [(tmpl, s_start, s_end, dow)] = (avg_res, avg_ns)
    """
    rolling_cache = {}
    for tmpl, s_start, s_end, dow in slots:
        avg_res = get_rolling_avg_field(session, vendor_id, s_start, s_end, # reuse helper functions
                                        'bundles_reserved', date_ow=cutoff_date)
        avg_ns = get_rolling_avg_field(session, vendor_id, s_start, s_end,
                                       'no_shows', date_ow=cutoff_date)
        rolling_cache[(tmpl, s_start, s_end, dow)] = (avg_res, avg_ns) # for each unique vendor-time slot instance we assign the key tuple: average reserved, average no showa
    return rolling_cache






def predict_for_slot(session: Session, vendor_id: int, vendor_stats, rolling_cache, target_date, template_id, slot_start, slot_end,
                     discount=0.0, model_dir: str = "app/forecasting/linear_regression/models") -> Tuple[int, int]:
    
    """
    function designed to predict the bundles posted and no shows for a particular fututre time slot
    we use the model weights saved in model dir to perform inference
    helper functions are used to create a comprehensive input data point used to generate a prediction
    discount is assumed as 0 but this should ideally be inputted by the vendor for a given bundle to massively increase accuracy
    bundles reserved prediction and no shows predictions are generated
    """

    if not os.path.exists(model_dir):
        raise FileNotFoundError("the model dir does not exist")
    
    # load the models using joblib
    model_res = joblib.load(os.path.join(model_dir, "ridge_reserved.pkl"))
    model_ns = joblib.load(os.path.join(model_dir, "ridge_no_show.pkl"))
    feature_names = joblib.load(os.path.join(model_dir, "feature_names.pkl"))


    # use helper to get the unique (template id, slot start, slot end, day of week) instances
    vendor_aggr = vendor_stats.get(vendor_id, {})

    # use the precomputed averages for the specific emplate_id, slot_start, slot_end, target_date
    avg_res, avg_ns = rolling_cache.get((template_id, slot_start, slot_end, target_date.weekday()), (0.0, 0.0))

    # build the input data point
    raw = {
        'vendor_avg_reserved': vendor_aggr.get('avg_reserved', 0.0),
        'vendor_avg_no_show': vendor_aggr.get('avg_no_show', 0.0),
        'vendor_total_records': vendor_aggr.get('total_records', 0),
        'vendor_avg_discount': vendor_aggr.get('avg_discount', 0.0),
        'template_id': template_id,
        'day_of_week': target_date.weekday(),
        'month': target_date.month,
        'slot_start_hour': slot_start.hour,
        'slot_end_hour': slot_end.hour,
        'discount': discount,
        'precipitation': get_future_weather(session=session, vendor_id=vendor_id, date_t=target_date),
        'trend': (target_date - date(2020,1,1)).days,
        'is_weekend': 1 if target_date.weekday() >= 5 else 0, # flag is designed to capture the effect of weekends
        'avg_reserved_last_4w': avg_res,
        'avg_no_shows_last_4w': avg_ns,
    }

    # one hot encoding for model input
    df = pd.DataFrame([raw])
    cat_cols = ['template_id', 'day_of_week', 'month']
    df_encoded = pd.get_dummies(df, columns=cat_cols)

    # Align with training feature names 
    for col in feature_names:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_encoded = df_encoded[feature_names]

    # make predicitions woth both models
    pred_res = int(round(model_res.predict(df_encoded)[0]))
    pred_ns = int(round(model_ns.predict(df_encoded)[0]))
    return pred_res, pred_ns # return preds





def generate_linear_regression_forecast(session: Session, vendor_id: int, start_date: date = date.today()+timedelta(days=1), days_ahead: int = 7, model_dir: str = "app/forecasting/linear_regression/models") -> List[Forecast_Output]:
    
    """
    start_date: generate output forecasts from this date 
    days_ahead: how many days into the future we want to generate forecasts for
    This function will add a number of forecast outputs to the DB and return them to be used for the endpoint function under this one
    """

    # when we gather the vendor statistics we should gather data up untill yesterday
    cutoff = date.today() - timedelta(days=1)
    vendor_stats = get_vendors_performance(session, up_to=cutoff, weeks_history=4)

    # use our helper function to get the active slots for a vendor
    active_slots = get_active_slots(session, vendor_id)

    # precompute rolling averages for these combos
    rolling_cache = precompute_rolling_averages(session, vendor_id, active_slots, cutoff)

    # we make a title map that maps all template ids to their title to the can be retireved
    template_ids = {t for (t, _, _, _) in active_slots}
    title_map = {}
    if template_ids:
        rows = session.exec(select(Template.template_id, Template.title).where(Template.template_id.in_(template_ids))).all()
        title_map = {row.template_id: row.title for row in rows}

    # build a dictionary of template id: discount
    discount_map = {}
    if template_ids:
        templates = session.exec(
            select(Template.template_id, Template.estimated_value, Template.cost)
            .where(Template.template_id.in_(template_ids))
        ).all()
        for t in templates:
            if t.estimated_value > 0:
                discount = (t.estimated_value - t.cost) / t.estimated_value
            else:
                discount = 0.0
            discount_map[t.template_id] = discount

    # check that the file exists if not assign default confidence
    metrics_path = os.path.join(model_dir, "metrics.pkl")
    if os.path.exists(metrics_path):
        metrics = joblib.load(metrics_path)
    else:
        metrics = {'reserved_mae': 2.0}


    # gather forecast outputs once made to be returned
    forecast_outputs = []
    for days in range(days_ahead):

        target = start_date + timedelta(days=days)
      
        relevant_slots = [(t, s, e) for (t, s, e, d) in active_slots if d == target.weekday()]

        for tmpl, s_start, s_end in relevant_slots:

            title = title_map.get(tmpl, "Unknown") # set the title to unknow in case it is not able to be retrieved properly

            discount_val = discount_map.get(tmpl, 0.0) # use out map the get the relevant discount for this template id
            pred_res, pred_ns = predict_for_slot(session, vendor_id, vendor_stats, rolling_cache, target, tmpl, s_start, s_end, discount=discount_val)

            # create the reccomendation and rationale fields
            recommendation = f"Post {int(pred_res)} {title} bundles between {s_start} and {s_end} on {target.strftime('%A')} "
            rationale = "Based on historical data and our most advanced model."

            # use the helper function to compute the std and total bundles for this particular template and vendor for default 4 weeks back
            count_res, std_res = compute_std_var(session, vendor_id, tmpl, 'bundles_reserved', s_start, s_end)

            base_conf = 1 / (1 + metrics.get('reserved_mae', 2)) 
          
            count_factor = min(1.0, count_res / 10)

            avg_res = rolling_cache.get((tmpl, s_start, s_end, target.weekday()), (0.0, 0.0))[0]
            if avg_res > 0:
                cv = std_res / avg_res            
                var_factor = max(0.1, 1.0 - min(cv, 2.0) / 2.0)   
            else:
                var_factor = 0.5 if std_res == 0 else 0.2 # baseline 0.2 confidence if there is no data 

            confidence = round((max(base_conf, 0.5) + count_factor + var_factor)/3.0, 3) # main confidence calculation 

            # use the helper function again to create the forecast output entity
            forecast = update_or_create(
                session=session,
                vendor_id=vendor_id,
                template_id=tmpl,
                target_date=target,
                slot_start=s_start,
                slot_end=s_end,
                model_type="linear_regression",
                reservation_prediction=pred_res,
                no_show_prediction=pred_ns,
                recommendation=recommendation,
                rationale=rationale,
                confidence=confidence
            )
            forecast_outputs.append(forecast)

    return forecast_outputs





def get_linear_regression_forecast_chart(session: Session, vendor_id: int, start_date: date = date.today()+timedelta(days=1), days_ahead: int = 7) -> ForecastWeekData:
    """
    This function calls the helper generate_linear_regression_forecast to create all output forecast entities that will be needed
    we go through the outputs needed list and systematically generate the forecast datapoints which are appended to make the final ForecastWeekData class
    """

    # gather outputs from the helper function
    outputs_needed: List[Forecast_Output] = generate_linear_regression_forecast(session=session, vendor_id=vendor_id, start_date=start_date, days_ahead=days_ahead)

    # if there were no outputs produced - meaning the vendor does not have enough data return []
    if not outputs_needed:
        return ForecastWeekData(week_date=start_date.isoformat(), day_datapoints = [])

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
        title = title_map.get(output.template_id, "Unknown") # use the dictionary to find the exact title from the template id
        
        # calculate no show chance as no_show / no_show+predicted
        total = output.reservation_prediction + output.no_show_prediction
        chance_of_no_show = max((round(output.no_show_prediction / total, 3) if total > 0 else 0.0), 0.05)

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

    #python -m app.forecasting.linear_regression.linear_regression_forecast

    with Session(engine) as session:
        vendor_ids = session.exec(select(Vendor.vendor_id))
        for id in vendor_ids:
            result = get_linear_regression_forecast_chart(session, vendor_id=id)
            week_json = json.dumps(result.model_dump(), indent=2, default=str)
            for day in result.day_datapoints:
                print(f"\n Day: {day.date}")
                day_json = json.dumps(day.model_dump(), indent=2, default=str)
                print(day_json)
        
        

       
            

        

