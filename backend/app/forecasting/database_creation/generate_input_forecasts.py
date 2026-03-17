from sqlmodel import Session, select, func
from datetime import date, timedelta, time
from collections import defaultdict
from app.models import Forecast_Input, Bundle, Reservation, Template
from app.core.database import engine

def get_slot_from_time(t: time) -> tuple[time, time]:
    """Return (slot_start, slot_end) for the 2-hour slot - helper function"""
    hour = t.hour
    slot_start_hour = (hour // 2) * 2
    slot_end_hour = slot_start_hour + 2
    if slot_end_hour == 24:
        slot_end_hour = 0
    return time(slot_start_hour, 0, 0), time(slot_end_hour, 0, 0)



def sync_forecast_inputs(session: Session, vendor_id: int, days_back: int = 30):
    """
    for any vendor we should ensure that days_back days is up to date i.e. forecast input entities have been
    made from all relevent database entities
    this would ideally be called at the end of every day after the vendors closing time to ensure the database is up to date
    """
    # work out the date function is called
    start_date = date.today() - timedelta(days=days_back)

    # collect all relevant bundles for this vendor, along with their reservation status
    bundles = session.exec(
        select(Bundle, Reservation.status)
        .join(Template, Bundle.template_id == Template.template_id)
        .where(Template.vendor == vendor_id)
        .where(Bundle.date >= start_date)
        .outerjoin(Reservation, Bundle.bundle_id == Reservation.bundle_id)
    ).all()  

    # funxction to group by (date, slot_start, slot_end, template_id)
    groups = defaultdict(lambda: {"posted": 0, "reserved": 0, "no_shows": 0})

    for bundle, status in bundles:
        slot_start, slot_end = get_slot_from_time(bundle.time)
        key = (bundle.date, slot_start, slot_end, bundle.template_id)

        groups[key]["posted"] += 1
        if status is not None:          # bundle has a reservation
            groups[key]["reserved"] += 1
            if status == "no_show":
                groups[key]["no_shows"] += 1
        

    # For each group, get the template to compute discount
    template_cache = {}  # cache template_id sinve will be needed to calculate dicount
    for key, agg in groups.items():
        rec_date, slot_start, slot_end, template_id = key  

        # Get or compute discount for this template
        if template_id not in template_cache:
            template = session.get(Template, template_id)
            if template:
                discount = (template.estimated_value - template.cost) / template.estimated_value
                template_cache[template_id] = discount
            else:
                template_cache[template_id] = 0.0

        discount = template_cache[template_id]

        # Prepare data for upsert
        data = {
            "vendor_id": vendor_id,
            "template_id": template_id,
            "date": rec_date,
            "slot_start": slot_start,
            "slot_end": slot_end,
            "discount": discount,
            "precipitation": -1.0,
            "bundles_posted": agg["posted"],
            "bundles_reserved": agg["reserved"],
            "no_shows": agg["no_shows"],
        }

        # Check if a record already exists with these exact keys
        existing = session.exec(
            select(Forecast_Input).where(
                Forecast_Input.vendor_id == vendor_id,
                Forecast_Input.template_id == template_id,
                Forecast_Input.date == rec_date,
                Forecast_Input.slot_start == slot_start,
                Forecast_Input.slot_end == slot_end,
            )
        ).first()

        if existing:
            # Update all fields (except primary key)
            for field, value in data.items():
                setattr(existing, field, value)
            session.add(existing)
        else:
            session.add(Forecast_Input(**data))

    session.commit()

if __name__ == "__main__":
    with Session(engine) as session:
        sync_forecast_inputs(vendor_id=1, session=session, days_back=60)