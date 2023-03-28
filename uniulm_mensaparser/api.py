from .models import Canteens
from .adapter import SimpleAdapter
from .mensaparser import get_plans_for_canteens

"""
Library API
"""


def get_plan(canteens={}, adapter_class=None):
    c = canteens
    if c == {}:
        c = {Canteens.UL_UNI_Sued}

    if adapter_class is None:
        adapter_class = SimpleAdapter

    return get_plans_for_canteens(c, adapter_class)

