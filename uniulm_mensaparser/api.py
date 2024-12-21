from .models import Canteen
from .adapter import SimpleAdapter2, PlanAdapter
from .mensaparser import get_meals_for_canteens, format_meals
from typing import Set, Type, Tuple, List
from .models import MultiCanteenPlan
from datetime import datetime
import asyncio

"""
Library API
"""


def get_plan(canteens: Set[Canteen] = None, adapter_class: Type[PlanAdapter] = None) -> dict:
    """
    Returns the Ulm University canteen plan for this and next week.
    Args:
        canteens: Selected canteens
        adapter_class: Formatter for plan output

    Returns: Formatted canteen plan

    """

    if canteens is None:
        canteens = {Canteen.UL_UNI_Sued, Canteen.UL_UNI_West}

    multi_canteen_plan = get_unformatted_plan(canteens)

    if adapter_class is None:
        adapter_class = SimpleAdapter2

    return format_meals(multi_canteen_plan, adapter_class)


def get_unformatted_plan(canteens: Set[Canteen] = None) -> MultiCanteenPlan:
    if canteens is None:
        canteens = {Canteen.UL_UNI_Sued, Canteen.UL_UNI_West}

    return asyncio.run(get_meals_for_canteens(canteens))
