from bs4 import BeautifulSoup
import urllib.request
import re
from enum import Enum
from .models import Canteens

"""
This module is used to get the links to the PDF files.
"""



BASE_URL = "https://studierendenwerk-ulm.de/essen-trinken/speiseplaene"


def get_plan_urls(canteens: {Canteens}) -> []:
    def ulm_filter(url):
        return url["mensa"] in canteens

    plans = get_pdf_links()
    plans = list(filter(ulm_filter, plans))
    return plans


def get_speiseplan_website() -> str:
    """
    Loads the HTML source code of the speiseplan website.
    :return:
    """
    speiseplan_source = ""
    with urllib.request.urlopen(BASE_URL) as response:
        speiseplan_source = response.read().decode("utf-8")
    return speiseplan_source


def get_pdf_links() -> []:
    """
    Returns all PDF links of the Studierendenwerk Ulm website.
    :return:
    """
    source = get_speiseplan_website()
    soup = BeautifulSoup(source, "html.parser")

    links = soup.find_all("a", string="hier")

    plans = []
    for a in links:
        try:
            plans.append(parse_pdf_name(a["href"]))
        except NotImplementedError as e:
            pass
        except Exception as e:
            pass

    return plans


def parse_pdf_name(href: str) -> dict:
    plan = {"url": href}
    split_list = href.split("/")
    filename = split_list.pop()  # get last element of list -> filename
    filename = filename[:-4]  # remove .pdf
    file_attrs = re.split('\s+', filename)
    file_attrs.pop()  # monthly mensa plan
    plan["week"] = file_attrs.pop()  # week in format KW**
    plan["mensa"] = Canteens.from_str(" ".join(file_attrs))
    return plan
