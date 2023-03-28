from .adapter import SimpleAdapter
from .pdf_parser import MensaParser
from .models import Meal, Canteens
from .studierendenwerk_scraper import get_plan_urls



def get_plans_for_canteens(canteens: {Canteens}, adapter_class=SimpleAdapter) -> dict:
    plans = get_plan_urls(canteens)
    # try:
    for p in plans:
        p["parsed"] = parse_from_url(p["url"])
        # add metadata to meals
        week = int(p["week"][2:])
        canteen = p["mensa"]
        for m in p["parsed"]["adapter_meals"]:
            m.week_number = week
            m.canteen = canteen

    adapter = adapter_class()
    converted = adapter.convert_plans(plans)
    return converted
