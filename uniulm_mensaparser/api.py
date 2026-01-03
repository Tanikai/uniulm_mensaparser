import asyncio
from typing import Set, Type

from .adapter import PlanAdapter, SimpleAdapter2
from .mensaparser import format_meals, get_meals_for_canteens
from .models import Canteen, MultiCanteenPlan

"""
Library API
"""


def get_plan(
    canteens: Set[Canteen] = None, adapter_class: Type[PlanAdapter] = None
) -> dict:
    """
    Returns the Ulm University canteen plan for this and next week.
    Args:
        canteens: Selected canteens
        adapter_class: Formatter for plan output

    Returns: Formatted canteen plan

    """
    return get_plan_by_language("de", canteens, adapter_class)


def get_plan_by_language(
    language: str = "de",
    canteens: Set[Canteen] = None,
    adapter_class: Type[PlanAdapter] = None,
) -> dict:
    """
    Returns the Ulm University canteen plan for this and next week in the
    given language.
    Args:
        language: Language of canteen plan, possible values: "de" | "en"
        canteens: Selected canteens
        adapter_class: Formatter for plan output

    Returns: Formatted canteen plan in given langauge

    """
    if canteens is None:
        canteens = {Canteen.UL_UNI_Sued, Canteen.UL_UNI_West}

    multi_canteen_plan = get_unformatted_plan(canteens, language)

    if adapter_class is None:
        adapter_class = SimpleAdapter2

    return format_meals(multi_canteen_plan, adapter_class)


def get_unformatted_plan(
    canteens: Set[Canteen] = None, language: str = "de"
) -> MultiCanteenPlan:
    if canteens is None:
        canteens = {Canteen.UL_UNI_Sued, Canteen.UL_UNI_West}

    return asyncio.run(get_meals_for_canteens(canteens, language))
