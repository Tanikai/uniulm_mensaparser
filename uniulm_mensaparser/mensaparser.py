import asyncio

from .adapter import PlanAdapter
from .html_parser import HtmlMensaParser
from .models import Canteen, Meal, Plan
from .studierendenwerk_scraper import get_maxmanager_weekly_plans, get_maxmanager_website
from typing import List, Set, Type
from datetime import datetime, timedelta
import aiohttp

from .utils import date_format_iso


async def get_meals_for_canteens(canteens: Set[Canteen]) -> List[Plan]:
    """
    This is the main function to get mensa plans.
    """
    async with aiohttp.ClientSession() as session:
        # TODO: Plan object should be refactored
        plans: List[Plan] = get_maxmanager_weekly_plans(canteens)

        async def _parse_plan(plan: Plan) -> Plan:
            return await parse_maxmanager_plan(session, plan)

        tasks: List[asyncio.Task] = []
        for p in plans:
            tasks.append(asyncio.create_task(_parse_plan(p)))

        results = await asyncio.gather(*tasks)
    return results


def format_meals(meals: List[Plan], adapter_class: Type[PlanAdapter]):
    adapter = adapter_class()
    converted = adapter.convert_plans(meals)
    return converted

async def parse_maxmanager_plan(session: aiohttp.ClientSession, plan: Plan) -> Plan:
    """
    Parses the current canteen plan from the MaxManager CMS endpoint.
    Args:
        session: The session which should be used to issue HTTP requests.
        plan: Information about the canteen, weekdays, and opened days

    Returns: Plan from argument with updated values

    """
    weekdates = _get_weekdates(plan.first_date)

    meals = []
    for date in weekdates:
        datemeals = await get_meals_for_date(session, date, plan.canteen)
        if len(datemeals) == 0:
            plan.opened_days[date_format_iso(date)] = False
        if len(datemeals) > 0:
            meals += datemeals
            plan.opened_days[date_format_iso(date)] = True

    plan.meals = meals

    return plan


async def get_meals_for_date(
    session: aiohttp.ClientSession, date: datetime, canteen: Canteen
) -> List[Meal]:
    p = HtmlMensaParser()
    source = await get_maxmanager_website(session, canteen.get_maxmanager_id(), date)
    return p.parse_plan(source, date, canteen)


def _get_weekdates(date: datetime) -> List[datetime]:
    start_of_current_week = date - timedelta(days=date.weekday())
    current_weekdates = [start_of_current_week + timedelta(days=i) for i in range(5)]

    return current_weekdates
