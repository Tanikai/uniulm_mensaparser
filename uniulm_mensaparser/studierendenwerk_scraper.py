from .models import MaxmanagerRequest
from datetime import date
import aiohttp

"""
This module is used to get the links to the PDF files.
"""

BASE_URL = "https://studierendenwerk-ulm.de/essen-trinken/speiseplaene"
MAXMANAGER_URL = "https://sw-ulm-spl51.maxmanager.xyz/inc/ajax-php_konnektor.inc.php"


async def get_maxmanager_website(
        session: aiohttp.ClientSession, loc_id: int = 1, plan_date: date = date.today(), lang: str = "de"
) -> str:
    """
    Returns the HTML canteen plan for the selected canteen and date.
    Args:
        lang: "de" | "en"
        session:
        loc_id:
            1: Universität Süd
            2: Universität West
        plan_date: Date for plan

    Returns: HTML source code of date
    """

    form_data = MaxmanagerRequest()
    form_data.locId = loc_id
    form_data.date = plan_date
    form_data.lang = lang
    request_dict = form_data.generate_request_dictionary()
    async with session.post(MAXMANAGER_URL, data=request_dict) as resp:
        data = await resp.text()
        return data
