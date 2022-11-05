from .adapter import SimpleAdapter
from .pdf_parser import MensaParser
from .speiseplan_website_parser import get_speiseplan, Canteens

"""
Library API
"""


def get_current_plans(adapter_class=SimpleAdapter) -> dict:
    return get_plans_for_canteens({Canteens.UL_UNI_Sued}, adapter_class)

def get_plans_for_canteens(canteens: {Canteens}, adapter_class=SimpleAdapter) -> dict:
    plans = get_speiseplan(canteens)
    try:
        for p in plans:
            p["parsed"] = parse_from_url(p["url"])

        adapter = adapter_class()
        converted = adapter.convert_plans(plans)
        return converted
    except Exception as e:
        pass


def parse_from_url(url: str) -> dict:
    mp = MensaParser()
    try:
        return mp.parse_plan_from_url(url)
    except Exception as e:
        print(f"Exception occurred with {url}: {e}")


def parse_from_file(path: str) -> dict:
    mp = MensaParser()
    return mp.parse_plan_from_file(path)
