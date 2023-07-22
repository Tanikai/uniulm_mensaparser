from .models import Canteen
from .adapter import SimpleAdapter2, PlanAdapter
from .mensaparser import get_plans_for_canteens
from typing import Set

"""
Library API
"""


def get_plan(canteens: Set[Canteen] = None, adapter_class: PlanAdapter = None) -> dict:
    """
    Returns the Ulm University canteen plan for this and next week.
    Args:
        canteens: Selected canteens
        adapter_class: Formatter for plan output

    Returns: Formatted canteen plan

    """
    if canteens is None:
        canteens = {Canteen.UL_UNI_Sued, Canteen.UL_UNI_West, Canteen.UL_UNI_Nord}

    if adapter_class is None:
        adapter_class = SimpleAdapter2

    return get_plans_for_canteens(canteens, adapter_class)
