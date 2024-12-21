import asyncio

from .adapter import PlanAdapter
from .html_parser import HtmlMensaParser
from .models import Canteen, Meal, MultiCanteenPlan, DailyCanteenMeals
from .studierendenwerk_scraper import get_maxmanager_website
from typing import List, Set, Type, Tuple
from datetime import datetime, date
import aiohttp

from .utils import get_weekdates_this_and_next_week, date_format_iso


async def get_meals_for_canteens(canteens: Set[Canteen]) -> MultiCanteenPlan:
    """

    Args:
        canteens: Canteens to fetch meals from.

    Returns: Tuple of List of meals and List of fetched & parsed dates.

    """
    async with aiohttp.ClientSession() as session:
        # TODO: Plan object should be refactored

        # get today's date
        today = datetime.now()
        # get weekdates from this week and next week
        dates = get_weekdates_this_and_next_week(today)

        tasks: List[asyncio.Task] = []

        async def get_meals_by_canteen(c: Canteen):
            return c, await get_meals_per_canteen(session, dates, c)

        for canteen in canteens:
            tasks.append(asyncio.create_task(get_meals_by_canteen(canteen)))

        results: List[Tuple[Canteen, DailyCanteenMeals]] = await asyncio.gather(*tasks)

    return dict(results)


async def get_meals_per_canteen(session, dates: List[datetime], canteen: Canteen) -> DailyCanteenMeals:
    tasks: List[asyncio.Task] = []

    async def get_meal_by_date(d: date):
        return d, await get_meals_for_date(session, d, canteen)

    for d in dates:
        tasks.append(asyncio.create_task(get_meal_by_date(d)))

    results: List[Tuple[date, List[Meal]]] = await asyncio.gather(*tasks)
    return dict(results)


def format_meals(canteen_plans: MultiCanteenPlan, adapter_class: Type[PlanAdapter]):
    adapter = adapter_class()
    converted = adapter.convert_plans(canteen_plans)
    return converted


async def get_meals_for_date(
        session: aiohttp.ClientSession, plan_date: date, canteen: Canteen
) -> List[Meal]:
    """
    This function is used to fetch and parse a single day from the specified canteen.
    Args:
        session:
        plan_date:
        canteen:

    Returns:

    """
    p = HtmlMensaParser()
    source = await get_maxmanager_website(session, canteen.get_maxmanager_id(), plan_date)
    return p.parse_plan(source, plan_date, canteen)
