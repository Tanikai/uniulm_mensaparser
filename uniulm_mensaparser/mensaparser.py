from .adapter import SimpleAdapter
from .pdf_parser import MensaParserIntf
from .models import Canteens
from .studierendenwerk_scraper import get_plan_urls
import requests
import fitz


def parse_plan_from_url(pdf_url: str, parser: MensaParserIntf):
    with requests.get(pdf_url) as data:
        document = fitz.open("pdf", data.content)
        return parser.parse_plan(document[0])


def parse_plan_from_file(path: str, parser: MensaParserIntf):
    with fitz.open(filename=path, filetype="pdf") as document:
        return parser.parse_plan(document[0])


def get_plans_for_canteens(canteens: {Canteens}, adapter_class=SimpleAdapter) -> dict:
    plans = get_plan_urls(canteens)
    # try:
    for p in plans:
        p["parsed"] = parse_plan_from_url(p["url"])
        # add metadata to meals
        week = int(p["week"][2:])
        canteen = p["mensa"]
        for m in p["parsed"]["adapter_meals"]:
            m.week_number = week
            m.canteen = canteen

    adapter = adapter_class()
    converted = adapter.convert_plans(plans)
    return converted
