from .adapter import PlanAdapter
from .html_parser import HtmlMensaParser
from .pdf_parser import MensaParserIntf, DefaultMensaParser, MensaNordParser
from .models import Canteen, Meal, Plan
from .studierendenwerk_scraper import get_current_pdf_urls, get_maxmanager_website
import requests
import fitz
from typing import List, Set, Type
from datetime import datetime, timedelta

from .utils import date_format_iso


def get_plans_for_canteens(
    canteens: Set[Canteen], adapter_class: Type[PlanAdapter]
) -> dict:
    """
    This is the main function to get mensa plans.
    """
    plans: List[Plan] = get_current_pdf_urls(canteens)

    def parseplan(plan: Plan) -> Plan:
        if plan.canteen in {Canteen.UL_UNI_Sued, Canteen.UL_UNI_West}:
            return parse_maxmanager_plan(plan)
        else:
            parser = create_parser(plan.canteen)
            plan.meals = parse_plan_from_url(plan.url, parser)
            plan.opened_days = parser.get_opened_days()
            return plan

    plans = list(map(parseplan, plans))
    adapter = adapter_class()
    converted = adapter.convert_plans(plans)
    return converted


def parse_plan_from_url(pdf_url: str, parser: MensaParserIntf) -> [Meal]:
    with requests.get(pdf_url) as data:
        document = fitz.open("pdf", data.content)
        return parser.parse_plan(document[0])


def parse_plan_from_file(path: str, parser: MensaParserIntf) -> [Meal]:
    with fitz.open(filename=path, filetype="pdf") as document:
        return parser.parse_plan(document[0])


def create_parser(c: Canteen) -> MensaParserIntf:
    if c == Canteen.UL_UNI_Sued:
        return DefaultMensaParser(c)
    elif c == Canteen.UL_UNI_West:
        return DefaultMensaParser(c)
    elif c == Canteen.UL_UNI_Nord:
        return MensaNordParser(c)
    else:
        raise ValueError("unknown canteen")


def parse_maxmanager_plan(plan: Plan) -> Plan:
    weekdates = _get_weekdates(plan.first_date)

    meals = []
    for date in weekdates:
        datemeals = get_meals_for_date(date, plan.canteen)
        if len(datemeals) == 0:
            plan.opened_days[date_format_iso(date)] = False
        if len(datemeals) > 0:
            meals += datemeals
            plan.opened_days[date_format_iso(date)] = True

    plan.meals = meals

    return plan


def get_meals_for_date(date: datetime, canteen: Canteen) -> List[Meal]:
    p = HtmlMensaParser()
    source = get_maxmanager_website(canteen.get_maxmanager_id(), date)
    return p.parse_plan(source, date, canteen)


def _get_weekdates(date: datetime) -> List[datetime]:
    start_of_current_week = date - timedelta(days=date.weekday())
    current_weekdates = [start_of_current_week + timedelta(days=i) for i in range(5)]

    return current_weekdates
