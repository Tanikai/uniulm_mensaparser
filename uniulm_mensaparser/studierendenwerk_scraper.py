from .models import Canteen, Plan, MaxmanagerRequest
from datetime import datetime, timedelta
from typing import List, Set
import aiohttp

"""
This module is used to get the links to the PDF files.
"""

BASE_URL = "https://studierendenwerk-ulm.de/essen-trinken/speiseplaene"
MAXMANAGER_URL = "https://sw-ulm-spl51.maxmanager.xyz/inc/ajax-php_konnektor.inc.php"


def get_maxmanager_weekly_plans(canteens: Set[Canteen]) -> List[Plan]:
    """
    Adds empty plans for the current and next week.
    Args:
        canteens: Selected Ulm University canteens

    Returns: Empty canteen plan objects with unparsed meals

    """
    result: List[Plan] = []

    def _add_canteen(canteen: Canteen):
        today = datetime.now()
        next_week = today + timedelta(weeks=1)

        result.append(
            Plan(
                canteen=canteen,
                url="",
                week="KW" + today.strftime("%V"),
                meals=[],
                first_date=today,
            )
        )

        result.append(
            Plan(
                canteen=canteen,
                url="",
                week="KW" + next_week.strftime("%V"),
                meals=[],
                first_date=next_week,
            )
        )

    for c in canteens:
        _add_canteen(c)

    return result


async def get_maxmanager_website(
    session: aiohttp.ClientSession, locId: int = 1, date: datetime = datetime.now()
) -> str:
    """
    Returns the HTML canteen plan for the selected canteen and date.
    Args:
        locId:
            1: Universität Süd
            2: Universität West
        date: Date for plan

    Returns: HTML source code of date
    """

    form_data = MaxmanagerRequest()
    form_data.locId = locId
    form_data.date = date
    request_dict = form_data.generate_request_dictionary()
    async with session.post(MAXMANAGER_URL, data=request_dict) as resp:
        data = await resp.text()
        return data
