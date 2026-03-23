from sqlmodel import Session, select
from app.models import Forecast_Input, Vendor
from app.core.database import engine
from app.forecasting.database_creation.generate_input_forecasts import sync_forecast_inputs
from typing import List
from app.schema import discount_coordinate, discount_coordinate_data



def pricing_effectiveness(session: Session, vendor_id: int, days_back = 42) -> discount_coordinate_data:
    """
    we want to return coordinates for a scatter plot with
    x axis: discount
    y axis: sold vs posted as a fraction
    this is represented as custom classes defined in schema
    """

    sync_forecast_inputs(session, vendor_id, days_back)

    statement = select(
        Forecast_Input.discount, Forecast_Input.bundles_posted, Forecast_Input.bundles_reserved, Forecast_Input.no_shows
    ).where(Forecast_Input.vendor_id == vendor_id)

    result = session.exec(statement).all()

    if not result:
        return discount_coordinate_data(coordinates=[])
    
    acc = {} # discount: (sell through, total)
    
    for discount, posted, reserved, no_shows in result:
        if posted == 0:
            continue
        
        rounded_discount = round(discount, 2) 
        sell_t = (reserved - no_shows) / posted

        if rounded_discount in acc:
            acc[rounded_discount][0] += sell_t
            acc[rounded_discount][1] += 1
        else:
            acc[rounded_discount] = [sell_t, 1]

            
    coordinates: List[discount_coordinate] = []

    for discount, (sell_through, total) in acc.items():

        coordinate = discount_coordinate(discount=round(discount, 2), sell_through=round((sell_through/total), 2))

        coordinates.append(coordinate)

    coordinates.sort(key=lambda d: d.discount)

    return discount_coordinate_data(coordinates=coordinates)



if __name__ == "__main__":

    # python -m app.analytics.pricing_effectiveness

    with Session(engine) as session:
        vendor_ids = session.exec(select(Vendor.vendor_id)).all()
        for vid in vendor_ids:
            effect = pricing_effectiveness(session, vid)
            print(f"\n\neffect for vendor {vid}: {effect}\n\n\n")

    

        