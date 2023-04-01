from .adapter import SimpleAdapter2
from .pdf_parser import MensaParserIntf, DefaultMensaParser, MensaNordParser
from .models import Canteens, Meal
from .studierendenwerk_scraper import get_current_canteen_urls
import requests
import fitz


def parse_plan_from_url(pdf_url: str, parser: MensaParserIntf) -> [Meal]:
    with requests.get(pdf_url) as data:
        document = fitz.open("pdf", data.content)
        return parser.parse_plan(document[0])


def parse_plan_from_file(path: str, parser: MensaParserIntf):
    with fitz.open(filename=path, filetype="pdf") as document:
        return parser.parse_plan(document[0])


def create_parser(c: Canteens) -> MensaParserIntf:
    if c == Canteens.UL_UNI_Sued:
        return DefaultMensaParser(c)
    elif c == Canteens.UL_UNI_West:
        return DefaultMensaParser(c)
    elif c == Canteens.UL_UNI_Nord:
        return MensaNordParser(c)
    else:
        raise ValueError("unknown canteen")


def get_plans_for_canteens(canteens: {Canteens}, adapter_class=SimpleAdapter2) -> dict:
    plans = get_current_canteen_urls(canteens)
    for p in plans:
        parser = create_parser(p.canteen)
        p.meals = parse_plan_from_url(p.url, parser)

    adapter = adapter_class()
    converted = adapter.convert_plans(plans)
    return converted
