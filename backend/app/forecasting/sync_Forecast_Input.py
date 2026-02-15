from sqlmodel import Session, select, func, case
from datetime import date, timedelta
from app.models import Forecast_Input, Bundle, Reservation, Template
from sqlmodel import Session
from app.core.database import engine


def sync_forecast_inputs(session: Session, vendor_id: int, days_back: int = 30):
    """
    for a given vendor we ensure the forecast input fields are correctly
    created for up to days_back days but will NOT overwrite entries if they already exists
    - Session = information about the database you are using
    - vendor_id = the id of thre vendors whos forecasy input you wish to update
    - days_back = the number of days back you wish to update
    :: in practice this function should be called for every vendor after their closing time
    """
    start_date = date.today() - timedelta(days=days_back)

    # build query with join Bundle -> Template -> Vendor (to filter vendor)
    # and left join Reservation to count reservations and no-shows
    stmt = (
        select(
            Bundle.date,
            Bundle.time,
            Bundle.template_id,
            func.count(Bundle.bundle_id).label("posted"),
            func.count(Reservation.reservation_id).label("reserved"),
            func.sum(
                case((Reservation.status == "no_show", 1), else_=0)
            ).label("no_shows")
        )
        .join(Template, Bundle.template_id == Template.template_id)
        .where(Template.vendor == vendor_id)  
        .where(Bundle.date >= start_date)
        .outerjoin(Reservation, Bundle.bundle_id == Reservation.bundle_id)
        .group_by(Bundle.date, Bundle.time, Bundle.template_id)
    )

    results = session.exec(stmt).all()

    for row in results:
        # check if the entry already exists
        existing = session.exec(
            select(Forecast_Input).where(
                Forecast_Input.vendor_id == vendor_id,
                Forecast_Input.template_id == row.template_id,
                Forecast_Input.date == row.date,
                Forecast_Input.time == row.time
            )
        ).first()

        data = {
            "vendor_id": vendor_id,
            "template_id": row.template_id,
            "date": row.date,
            "time": row.time,
            "bundles_posted": row.posted,
            "bundles_reserved": row.reserved,
            "no_shows": row.no_shows,
            "precipitation": -1.0  # placeholder as we dont yet know precipitation
        }

        if existing:
            # Update existing record
            for key, value in data.items():
                setattr(existing, key, value)
            session.add(existing)
        else:
            # new record
            new_entry = Forecast_Input(**data)
            session.add(new_entry)

    session.commit()
    return f"Synced {len(results)} forecast inputs for vendor {vendor_id}"



if __name__ == "__main__":
    
    with Session(engine) as session:
        result = sync_forecast_inputs(vendor_id=2, session=session, days_back=60)
        print(result)