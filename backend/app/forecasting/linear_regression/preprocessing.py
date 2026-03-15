from sqlmodel import Session, select, func
from app.models import Forecast_Input
from datetime import date, timedelta, time
from typing import Optional
import pandas as pd


def get_vendors_performance(session: Session, up_to: Optional[date], weeks_history: int = 4) -> dict[int:dict]:
    """
    We return a dictionary of 4 important vendor metrics
    this is to quantify overall performance for the last N weeks
    akin to an "elo score" but with more values to capture complex relationships
    up_to = the maximum date we want to compute a vendors history up to
    weeks_history = how many weeks back from up_to we want to go back
    {r.vendor_id: {
        'avg_reserved': r.avg_reserved,
        'avg_no_show': r.avg_no_show,
        'total_records': r.total_records,
        'avg_discount': r.avg_discount
    }
    """

    # if no date way provided 
    if up_to is None:
        up_to = date.today() - timedelta(days=1)

    back_date = up_to-timedelta(weeks=weeks_history)

    # extract all forecast input records that exists and claculate relevant averages
    statement = select(Forecast_Input.vendor_id,
        func.avg(Forecast_Input.bundles_reserved).label("avg_reserved"),
        func.avg(Forecast_Input.no_shows).label("avg_no_show"),
        func.count().label("total_records"),
        func.avg(Forecast_Input.discount).label("avg_discount")
        ).where(Forecast_Input.date.between(back_date, up_to)).group_by(Forecast_Input.vendor_id)
    
    result = session.exec(statement).all()

    # make the result into dictionary format
    dict_form = {r.vendor_id: 
                {'avg_reserved': r.avg_reserved, 'avg_no_show': r.avg_no_show,'total_records' : r.total_records, 'avg_discount': r.avg_discount}
                for r in result}

    return dict_form




def get_rolling_avg_field(session: Session, vendor_id: int, slot_start: time, slot_end: time, field: str, date_ow: Optional[date] = None, weeks_back = 4) -> float:
    """
    for a given vendor we compute the average of a particular field for weeks_back weeks in the past
    this is likely to be used for e.g. avg no_shows and avg bundles_reserved
    the function is slot and day of week specifific so uses similar functionality to get moving average functions
    """

    if date_ow is None:
        date_ow = date.today() - timedelta(days=1)

    if not hasattr(Forecast_Input, field):
        raise AttributeError(f"{field} is not a valid field within ForecastInput")

    # set the range of dates
    start_date = date_ow-timedelta(weeks=weeks_back)
    end_date = date_ow

    week_day = (date_ow.weekday()+1)%7   #day of the week we are targeting

    # this statement should extract averages for field from weeks back up to today
    statement = select(func.avg(getattr(Forecast_Input, field))).where(
        Forecast_Input.vendor_id==vendor_id,
        Forecast_Input.slot_start == slot_start,
        Forecast_Input.slot_end == slot_end,
        Forecast_Input.date.between(start_date, end_date),
        func.extract('dow', Forecast_Input.date) == week_day
    )

    result = session.exec(statement).first()

    # check to see if the result is empty which may happen if the vendor has no data
    return float(result) if result is not None else 0.0
    
  

def extract_features_for_record(session: Session, record: Forecast_Input, vendor_stats_cache: dict) -> dict:
    """
    use a cache dictionary so that heavy computation can be avoided and does not become redundent
    this is important as the db grows
    """
    cutoff = record.date - timedelta(days=1) 

    # get vendor‑level aggregates for this cutoff date 
    vendor_stats = vendor_stats_cache.get(cutoff, {}).get(record.vendor_id, {})

    # basic features that will be used as input for training data - training both reservation predictor model and no_shows predictor model
    features = {
        'vendor_avg_reserved': vendor_stats.get('avg_reserved', 0.0),
        'vendor_avg_no_show': vendor_stats.get('avg_no_show', 0.0),
        'vendor_total_records': vendor_stats.get('total_records', 0),
        'vendor_avg_discount': vendor_stats.get('avg_discount', 0.0),
        'template_id': record.template_id,
        'day_of_week': record.date.weekday(),
        'month': record.date.month,
        'slot_start_hour': record.slot_start.hour,
        'slot_end_hour': record.slot_end.hour,
        'discount': record.discount,
        'precipitation': record.precipitation,
        'trend': (record.date - date(2020, 1, 1)).days,
        'is_weekend': 1 if record.date.weekday() >= 5 else 0, # 1 for weekend or 0 for weekday
        'avg_reserved_last_4w': get_rolling_avg_field( # use the helper fucntiond defined above
            session, record.vendor_id, record.slot_start, record.slot_end,
            'bundles_reserved', date_ow=cutoff, weeks_back=4
        ),
        'avg_no_shows_last_4w': get_rolling_avg_field( # use the helper fucntiond defined above
            session, record.vendor_id, record.slot_start, record.slot_end,
            'no_shows', date_ow=cutoff, weeks_back=4
        ),
    }


    return features



def create_train_data(session: Session) -> pd.DataFrame:
    """
    here we make the cache used in extract_features_for_record
    the training data is built as a list of dictinaries where ground truth labels are added
    the list of dicts is convedted into a PD dataframe for ML use and efficiency when training
    """
    # get all input forecasts
    all_recs = session.exec(select(Forecast_Input)).all()

    # make a set containing all unique dates that exists in the dataset
    cutoff_dates = {r.date - timedelta(days=1) for r in all_recs}
    vendor_stats_cache = {}

    # for all the cutoff dates populate the cache to give us cutoff_date: vendor performance
    for cd in cutoff_dates:
        vendor_stats_cache[cd] = get_vendors_performance(session, up_to=cd, weeks_history=4)
    
    # for all the records we go through and add the ground truth labels to the dict leaving us with a list of dicts containing the training data 
    rows = []
    for rec in all_recs:
        feat = extract_features_for_record(session, rec, vendor_stats_cache)
        feat['target_reserved'] = rec.bundles_reserved
        feat['target_no_show'] = rec.no_shows
        rows.append(feat)
    
    df = pd.DataFrame(rows)
    return df




def prepare_X_y(df: pd.DataFrame):
    """
    takes in the output of the above function
    critically seperate train and test data -> the same dataset can be used for both models
    one hot encode 'template_id', 'day_of_week', 'month'
    """
    # Separate features and targets
    feature_cols = [col for col in df.columns if not col.startswith('target_')]
    X = df[feature_cols]
    y_res = df['target_reserved'] # one colum for each seperate prediction
    y_ns = df['target_no_show']
    
    # one hot encode categoricals since discrete values cant be used
    cat_cols = ['template_id', 'day_of_week', 'month']
    X_encoded = pd.get_dummies(X, columns=cat_cols, drop_first=False) # pd function for OHE
    
    # retunr feature names for inference later to preserve training order
    feature_names = X_encoded.columns.tolist()
    return X_encoded, y_res, y_ns, feature_names




if __name__ == "__main__":
    pass