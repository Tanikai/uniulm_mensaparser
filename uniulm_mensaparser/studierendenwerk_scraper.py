from bs4 import BeautifulSoup
import urllib.request  # @TODO: move to requests library
import re
from .models import Canteen, Plan, MaxmanagerRequest
import requests
from datetime import datetime, timedelta
from typing import List, Set
from html import unescape

"""
This module is used to get the links to the PDF files.
"""

BASE_URL = "https://studierendenwerk-ulm.de/essen-trinken/speiseplaene"
MAXMANAGER_URL = "https://sw-ulm-spl51.maxmanager.xyz/inc/ajax-php_konnektor.inc.php"


def get_current_canteen_urls(canteens: Set[Canteen]) -> List[Plan]:
    def ulm_filter(plan):
        return plan.canteen in canteens

    source = get_speiseplan_website()
    plans = scrape_pdf_links(source)  # parse legacy links

    plans = list(filter(ulm_filter, plans))

    plans += _get_canteens_with_updated_api(canteens)

    return plans


def _get_canteens_with_updated_api(canteens: Set[Canteen]) -> List[Plan]:
    result = []

    def _add_canteen(canteen: Canteen):
        today = datetime.now()
        next_week = today + timedelta(weeks=1)

        result.append(Plan(
            canteen=canteen,
            url="",
            week="KW" + today.strftime("%V"),
            meals=[],
            first_date=today
        ))

        result.append(Plan(
            canteen=canteen,
            url="",
            week="KW" + next_week.strftime("%V"),
            meals=[],
            first_date=next_week
        ))

    if Canteen.UL_UNI_Sued in canteens:
        _add_canteen(Canteen.UL_UNI_Sued)

    if Canteen.UL_UNI_West in canteens:
        _add_canteen(Canteen.UL_UNI_West)

    return result


def get_website(url: str) -> str:
    speiseplan_source = ""
    with urllib.request.urlopen(url) as response:
        speiseplan_source = response.read().decode("utf-8")
    return speiseplan_source


def get_speiseplan_website() -> str:
    """
    Loads the HTML source code of the speiseplan website.
    :return:
    """
    return get_website(BASE_URL)


def get_maxmanager_website(locId=1, date=datetime.now()) -> str:
    """
    Gets the HTML source code of the new Ulm University website.
    locId:
        1: Universität Süd
        2: Universität West
    :return:
    """

    form_data = MaxmanagerRequest()
    form_data.locId = locId
    form_data.date = date
    request_dict = form_data.generate_request_dictionary()
    resp = requests.post(f"{MAXMANAGER_URL}", data=request_dict)
    return unescape(resp.content.decode("utf-8"))


def scrape_pdf_links(source: str) -> List[Plan]:
    """
    Returns all PDF links of the Studierendenwerk Ulm website.
    :return:
    """
    soup = BeautifulSoup(source, "html.parser")

    links = soup.find_all("a")
    links = [link.attrs["href"] for link in links]
    links = list(filter(lambda link: link.endswith(".pdf") and "speise" in link, links))
    plans = []
    for a in links:
        try:
            plans.append(parse_pdf_name(a))
        except NotImplementedError:
            pass
        except Exception as e:
            print("Error while parsing href:", e)

    return plans


def scrape_maxmanager_pdf_links(source: str) -> List[Plan]:
    """
    For the canteen at Universität Süd, there is a new website for the canteen plan. As a temporary workaround, get the
    PDF urls from here.
    @TODO
    Instead of scraping the PDF file for Universität Süd, scrape the maxmanager HTML source code instead.
    alternatively, a client library for the the php endpoint at
        https://sw-ulm-spl51.maxmanager.xyz/inc/ajax-php_konnektor.inc.php
    could be implemented.

    :return:
    """
    soup = BeautifulSoup(source, "html.parser")
    links = soup.find_all("a", {"class": "downloadpdf"})

    href_set = set(map((lambda a: a["href"]), links))  # remove duplicates

    plans = []
    for href in href_set:
        try:
            plans.append(parse_maxmanager_pdf_name(href))
        except NotImplementedError:
            pass
        except Exception as e:
            print("Error while parsing href:", e)

    return plans


def parse_pdf_name(href: str) -> Plan:
    split_list = href.split("/")
    filename = split_list.pop()  # get last element of list -> filename
    filename = filename[:-4]  # remove .pdf
    file_attrs = re.split(r"\s+", filename)
    file_attrs.pop()  # monthly mensa plan

    p = Plan(
        canteen=Canteen.from_str(" ".join(file_attrs)),
        url=href,
        week=file_attrs.pop(),  # week in format KW**,
        meals=[]
    )

    return p


def parse_maxmanager_pdf_name(href: str) -> Plan:
    question_index = href.find(".pdf")
    cleaned_link = href[:question_index + 4]  # remove query parameter
    split_list = cleaned_link.split("/")
    filename = split_list.pop()[:-4]
    split_filename = filename.split("_")

    first_date = datetime.strptime(split_filename[1], "%Y-%m-%d")

    p = Plan(
        canteen=Canteen.from_str(split_filename[0].replace("-", " ")),
        url=cleaned_link,
        week="KW" + first_date.strftime("%V"),
        meals=[],
        first_date=first_date
    )

    return p
