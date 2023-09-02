from bs4 import BeautifulSoup
import re
from .models import Canteen, Plan, MaxmanagerRequest
from datetime import datetime, timedelta
from typing import List, Set
from html import unescape
import aiohttp

from .utils import fetch

"""
This module is used to get the links to the PDF files.
"""

BASE_URL = "https://studierendenwerk-ulm.de/essen-trinken/speiseplaene"
MAXMANAGER_URL = "https://sw-ulm-spl51.maxmanager.xyz/inc/ajax-php_konnektor.inc.php"


async def get_current_pdf_urls(
    session: aiohttp.ClientSession, canteens: Set[Canteen]
) -> List[Plan]:
    def ulm_filter(plan):
        return plan.canteen in canteens

    source = await fetch(session, BASE_URL)
    plans: List[Plan] = _scrape_legacy_pdf_urls(source)  # parse legacy links

    plans = list(filter(ulm_filter, plans))

    plans += _get_canteens_with_updated_api(canteens)

    return plans


def _get_canteens_with_updated_api(canteens: Set[Canteen]) -> List[Plan]:
    """
    Adds empty plans for the current and next week.
    Args:
        canteens: Selected Ulm University canteens

    Returns: Empty canteen plan objects with unparsed meals

    """
    result = []

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

    if Canteen.UL_UNI_Sued in canteens:
        _add_canteen(Canteen.UL_UNI_Sued)

    if Canteen.UL_UNI_West in canteens:
        _add_canteen(Canteen.UL_UNI_West)

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


def _scrape_legacy_pdf_urls(source: str) -> List[Plan]:
    """
    Returns all available Canteen plans from the legacy Studierendenwerk Ulm website.
    Args:
        source: HTML source code

    Returns: Empty canteen plan objects with unparsed meals
    """
    soup = BeautifulSoup(source, "html.parser")

    links = soup.find_all("a")
    links = [link.attrs["href"] for link in links]
    links = list(filter(lambda link: link.endswith(".pdf") and "speise" in link, links))
    plans = []
    for a in links:
        try:
            plans.append(_parse_legacy_pdf_name(a))
        except NotImplementedError:
            pass
        except Exception as e:
            print("Error while parsing href:", e)

    return plans


def _parse_legacy_pdf_name(href: str) -> Plan:
    split_list = href.split("/")
    filename = split_list.pop()  # get last element of list -> filename
    filename = filename[:-4]  # remove .pdf
    file_attrs = re.split(r"\s+", filename)
    file_attrs.pop()  # monthly mensa plan

    p = Plan(
        canteen=Canteen.from_str(" ".join(file_attrs)),
        url=href,
        week=file_attrs.pop(),  # week in format KW**,
        meals=[],
    )

    return p


def _scrape_maxmanager_pdf_urls(source: str) -> List[Plan]:
    """
    Returns the PDF urls from the bottom of a MaxManager canteen plan.
    Args:
        source: HTML Source Code

    Returns: Empty canteen plan objects with unparsed meals
    """
    soup = BeautifulSoup(source, "html.parser")
    links = soup.find_all("a", {"class": "downloadpdf"})

    href_set = set(map((lambda a: a["href"]), links))  # remove duplicates

    plans = []
    for href in href_set:
        try:
            plans.append(_parse_maxmanager_pdf_name(href))
        except NotImplementedError:
            pass
        except Exception as e:
            print("Error while parsing href:", e)

    return plans


def _parse_maxmanager_pdf_name(href: str) -> Plan:
    question_index = href.find(".pdf")
    cleaned_link = href[: question_index + 4]  # remove query parameter
    split_list = cleaned_link.split("/")
    filename = split_list.pop()[:-4]
    split_filename = filename.split("_")

    first_date = datetime.strptime(split_filename[1], "%Y-%m-%d")

    p = Plan(
        canteen=Canteen.from_str(split_filename[0].replace("-", " ")),
        url=cleaned_link,
        week="KW" + first_date.strftime("%V"),
        meals=[],
        first_date=first_date,
    )

    return p
