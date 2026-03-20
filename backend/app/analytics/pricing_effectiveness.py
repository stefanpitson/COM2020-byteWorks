from sqlmodel import Session, select
from app.models import Forecast_Input, Vendor
from app.core.database import engine
from app.forecasting.database_creation.generate_input_forecasts import sync_forecast_inputs
from typing import Tuple, List



def pricing_effectiveness(session: Session, vendor_id: int, days_back = 42) -> List[Tuple[float, float]]:
    """
    we want to return coordinates for a scatter plot with
    x axis: discount
    y axis: sold vs posted as a fraction
    """

    sync_forecast_inputs(session, vendor_id, days_back)

    statement = select(
        Forecast_Input.discount, Forecast_Input.bundles_posted, Forecast_Input.bundles_reserved, Forecast_Input.no_shows
    ).where(Forecast_Input.vendor_id == vendor_id)

    result = session.exec(statement).all()

    if not result:
        return []
    
    acc = {} # discount: (sell through, total)
    
    for discount, posted, reserved, no_shows in result:
        if posted == 0:
            sell_t = 0
        else:
            sell_t = (reserved-no_shows)/posted

        if acc.get(discount) is not None:
            acc[discount][0] += sell_t
            acc[discount][1] += 1
        else:
            acc[discount] = [sell_t, 1]

    coords: List[Tuple[float, float]] = [(round(discount, 2), round((sell_through/total), 2)) for discount, (sell_through, total) in acc.items()]

    return coords




if __name__ == "__main__":

    # python -m app.analytics.pricing_effectiveness

    with Session(engine) as session:
        vendor_ids = session.exec(select(Vendor.vendor_id)).all()
        for vid in vendor_ids:
            effect = pricing_effectiveness(session, vid)
            print(f"effect for vendor {vid}: {effect}")

    

        