from datetime import date, timedelta
from sqlmodel import Session, select
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pgeocode
import pandas as pd
from app.core.database import engine
from app.models import Forecast_Input, Vendor


def get_vendor_coordinates(postcode: str) -> tuple:
    """Get lat/lon for a UK postcode"""
    nomi = pgeocode.Nominatim('GB')
    result = nomi.query_postal_code(postcode)
    
    if pd.isna(result.latitude):
        return None, None  
    
    return float(result.latitude), float(result.longitude)




def update_weather_for_vendor(
    vendor_id: int,
    days_back: int = 60
) -> str:
    
        
    with Session(engine) as session:

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


        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

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
                responses = openmeteo.weather_api(url, params=params)
                daily = responses[0].Daily()
                precip = float(daily.Variables(0).ValuesAsNumpy()[0])

                # Update all records for this date
                for record in records:
                    if record.date == target_date:
                        record.precipitation = precip
                        session.add(record)
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

        



if __name__ == "__main__":
    result = update_weather_for_vendor(vendor_id=1, days_back=60)
    print(result)