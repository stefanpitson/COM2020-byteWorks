from datetime import date, timedelta
from sqlmodel import Session, select
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pgeocode
import pandas as pd
from app.core.database import engine
from app.models import Forecast_Input, Vendor


# cache api result since we call multiple times
_cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
_retry_session = retry(_cache_session, retries=5, backoff_factor=0.2)
_openmeteo = openmeteo_requests.Client(session=_retry_session)


def get_vendor_coordinates(postcode: str) -> tuple:
    """Get lat/lon for a UK postcode"""
    nomi = pgeocode.Nominatim('GB')
    result = nomi.query_postal_code(postcode)
    
    if pd.isna(result.latitude):
        return None, None  
    
    return float(result.latitude), float(result.longitude)




def update_weather_for_vendor(
    session: Session,
    vendor_id: int,
    days_back: int = 60,
    training_mode: bool = False
) -> str:
    
    """
    for a partiular vendor the function goes back days_back days to update real life weather using their location
    days_back: how many days back we should update weather for -> default weather is -1.0
    if previous weather exists for an input forecasst then the precipitation will be overwritten
    training_mode: if true then we introduce random noise into the data by adding precip = -1.0 to ensure the trained model learns how "unknow" precip records look
    if training mode is not active then all relevant precip fields will be updated unless the API call fails (default -1.0)
    """

    vendor = session.get(Vendor, vendor_id)
    if not vendor:
        return f"Vendor with ID {vendor_id} not found."

    postcode = vendor.post_code
    if not postcode:
        return f"Vendor {vendor_id} has no postcode."
    
    # logic to work out the longditude and latutude
    latitude, longitude = get_vendor_coordinates(postcode)

    # check if the postcode was found
    if longitude is None or latitude is None:
        return f"could not find the postcode: {postcode} -- exiting..."

    # since precipitation is only added 3-5 after, we only add this measurement to 5-day-old forecast inputs
    cutoff_actuals = date.today() - timedelta(days=5)
    min_date = date.today() - timedelta(days=days_back)

    # find relevant records where precipitation hasnt been set 
    records = session.exec(
        select(Forecast_Input).where(
            Forecast_Input.vendor_id == vendor_id,
            Forecast_Input.date <= cutoff_actuals,
            Forecast_Input.date >= min_date,
            Forecast_Input.precipitation == -1.0
        )
    ).all()

    # return descriptive error message
    if not records:
        return f"No eligible forecast inputs for vendor {vendor_id}."

    # Group by date to avoid repeated API calls
    dates = {r.date for r in records}
    updated = 0
    failed = []

    for target_date in dates:
        # wrap this in a try except block to graceful handle api faliure
        try: 

            # call api
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": target_date.isoformat(),
                "end_date": target_date.isoformat(),
                "daily": "precipitation_sum",
                "timezone": "Europe/London"
            }
            # extract the precipitation for that day
            responses = _openmeteo.weather_api(url, params=params)
            daily = responses[0].Daily()
            precip = float(daily.Variables(0).ValuesAsNumpy()[0])

            # Update all records for this date
            if training_mode: # IMPORTANT -- if training mode is enabled then it is simulated that 5% of all weather flags are undetermined (-1.0) for whatever reason e.g. failed API call
                for i, record in enumerate(records):
                    if record.date == target_date and i % 20 != 0:
                        record.precipitation = precip
                        updated += 1

            else: 
                for i, record in enumerate(records):
                    if record.date == target_date:
                        record.precipitation = precip
                        updated += 1


        except Exception as e:
            print(f"Failed weather report for {target_date}: {e}")
            failed.append(target_date)
            continue

    session.commit()

    # check if the api call failed for one or more dates
    if failed:
        return f"failed on {len(failed)} days"
    else:
        return f"Updated weather for {updated} records."

        


def get_future_weather(session: Session, vendor_id: int, date_t: date) -> float:

    vendor = session.get(Vendor, vendor_id)

    if not vendor:
        print(f"Vendor with ID {vendor_id} not found.")
        return-1.0

    postcode = vendor.post_code
    if not postcode:
        print(f"Vendor {vendor_id} has no postcode.")
        return -1.0
    
    # logic to work out the longditude and latutude
    latitude, longitude = get_vendor_coordinates(postcode)

    # check if the postcode was found
    if longitude is None or latitude is None:
        print(f"could not find the postcode: {postcode}")
        return -1.0

    today = date.today()

    if date_t <= today: # if the call is for the past we need to use a differne url

        # call api
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date_t.isoformat(),
            "end_date": date_t.isoformat(),
            "daily": "precipitation_sum",
            "timezone": "Europe/London"
        }    

        try:
            responses = _openmeteo.weather_api(url, params=params)
            if not responses:
                return -1.0
            daily = responses[0].Daily()
            # For archive API, the time array is reliable
            time_array = pd.to_datetime(daily.Time(), unit='s', utc=True).date
            indices = [i for i, d in enumerate(time_array) if d == date_t]
            if not indices:
                return -1.0
            idx = indices[0]
            precip = float(daily.Variables(0).ValuesAsNumpy()[idx])
            return precip
        except Exception as e:
            print(f"Failed weather report for {date_t}: {e}")
            return -1.0
        
    else: # if we are predicting the forecast

        days_ahead = (date_t - today).days
        if days_ahead > 16:
            print(f"Requested date {date_t} is more than 16 days ahead")
            return -1.0

        # if we try to predict the future weather - max 16 days
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": days_ahead + 1,
            "daily": "precipitation_sum",
            "timezone": "Europe/London"
        }

        try:
            responses = _openmeteo.weather_api(url, params=params)
            if not responses:
                return -1.0
            daily = responses[0].Daily()
           
            precip_array = daily.Variables(0).ValuesAsNumpy()
          
            precip = float(precip_array[days_ahead]) # extract precipitation
            return precip
        
        # if the api call failed
        except Exception as e:
            print(f"Failed weather report for {date_t}: {e}")
            return -1.0







if __name__ == "__main__":
    with  Session(engine) as session:
        vendor_ids = session.exec(select(Vendor.vendor_id))
        for id in vendor_ids:
            update_weather_for_vendor(session, vendor_id=id, days_back=45)
            