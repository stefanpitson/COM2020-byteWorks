from sqlmodel import Session, select, func
from app.models import Template, Bundle, Vendor
from app.core.database import engine
from typing import Dict


def waste_proxy(session: Session, vendor_id: int) -> Dict[str, float]:
    """
    we calculate the estimated total waste avoided (in kg)
    and the average weight of a bundle
    """

    # calculate the total weight for all bundles and the average weight
    weight_metrics = session.exec(
        select(func.sum(Template.weight).label("total_weight"),
               func.avg(Template.weight).label("avg_weight"))
        .select_from(Bundle)
        .join(Template, Bundle.template_id == Template.template_id)
        .where(Template.vendor == vendor_id)).first()
   
    if weight_metrics is None: # check if no results were acquired 
        return {"total_waste_avoided": 0.0, "average_bundle_weight": 0.0}

    # return appropriate dictionary
    return {"total_waste_avoided": round(float(weight_metrics.total_weight), 3), "average_bundle_weight": round(float(weight_metrics.avg_weight), 3)}


if __name__ == "__main__":

    # python -m app.analytics.waste_proxy

    with Session(engine) as session:
        vendor_ids = session.exec(select(Vendor.vendor_id)).all()
        for vid in vendor_ids:
            proxy = waste_proxy(session, vid)
            print(f"proxy for vendor {vid}: {proxy}")