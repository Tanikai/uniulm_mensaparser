from .models import Canteen
from .adapter import SimpleAdapter2
from .mensaparser import get_plans_for_canteens

"""
Library API
"""


def get_plan(canteens=None, adapter_class=None):
    if canteens is None:
        canteens = {Canteen.UL_UNI_Sued, Canteen.UL_UNI_West, Canteen.UL_UNI_Nord}

    if adapter_class is None:
        adapter_class = SimpleAdapter2

    return get_plans_for_canteens(canteens, adapter_class)
