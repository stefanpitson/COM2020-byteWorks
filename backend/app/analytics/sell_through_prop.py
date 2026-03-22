from sqlmodel import Session, select
from app.models import Template, Bundle, Reservation, Vendor
from app.core.database import engine
from app.schema import week_sell_through_proportions, all_time_sell_through_proportions
from datetime import date, timedelta
from typing import Dict, Tuple




def proportions_last_week(session: Session, vendor_id: int) -> week_sell_through_proportions:

    """
    we calculate the last full weeks worth of bundles
    calculate the collected vs expired vs no shows
    return a dictionary of important summed stats and the start day of the week
    """

    day_today = date.today().weekday()
    start_date = date.today()-timedelta(days=(day_today+7))
    end_date = start_date + timedelta(days=6)

    relevant_bundles = session.exec(
        select(Bundle, Reservation.status)
        .join(Template, Bundle.template_id == Template.template_id)
        .where(Template.vendor == vendor_id)
        .where(Bundle.date.between(start_date, end_date))
        .outerjoin(Reservation, Bundle.bundle_id == Reservation.bundle_id)
    ).all()

    collected: int = 0
    no_shows: int = 0
    expired: int = 0

    for _, reservation in relevant_bundles:
        if reservation == 'no_show':
            no_shows += 1
        elif reservation == 'collected':
            collected += 1
        elif reservation is None:
            expired+=1

    total = no_shows + collected + expired

    if total == 0:
        return week_sell_through_proportions(
            num_collected=0,
            num_no_show=0,
            num_expired=0,
            week_start_date=start_date.isoformat()
        )   
    
    return week_sell_through_proportions(
            num_collected=collected,
            num_no_show=no_shows,
            num_expired=expired,
            week_start_date=start_date.isoformat()
        )
        




def proportions_all_time(session: Session, vendor_id: int) -> all_time_sell_through_proportions:

    """
    we select all relevant bundles and their reservation status with a join
    tally no show vs collected vs expired
    return the dictionary of proportions
    """

    relevant_bundles = session.exec(
        select(Bundle, Reservation.status)
        .join(Template, Bundle.template_id == Template.template_id)
        .where(Template.vendor == vendor_id)
        .outerjoin(Reservation, Bundle.bundle_id == Reservation.bundle_id)
    ).all()

    collected: int = 0
    no_shows: int = 0
    expired: int = 0

    for _, reservation in relevant_bundles:
        if reservation == 'no_show':
            no_shows += 1
        elif reservation == 'collected':
            collected += 1
        elif reservation is None:
            expired+=1

    total = no_shows + collected + expired

    if total == 0:
        return all_time_sell_through_proportions(
            num_collected=0,
            num_no_show=0,
            num_expired=0
        )   
    
    return all_time_sell_through_proportions(
            num_collected=collected,
            num_no_show=no_shows,
            num_expired=expired
        )


if __name__ == "__main__":

# python -m app.analytics.sell_through_prop

    with Session(engine) as session:
        vendor_ids = session.exec(select(Vendor.vendor_id)).all()
        for vid in vendor_ids:
            week = proportions_last_week(session, vid)
            all_time = proportions_all_time(session, vid)
            print(f"week: {week}\n\n\nall time: {all_time}")