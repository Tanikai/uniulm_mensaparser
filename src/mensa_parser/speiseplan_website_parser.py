import sys

from bs4 import BeautifulSoup
import urllib.request
from enum import Enum
import re
from . import pdf_parser
from json import dumps


class UniversityMensa(Enum):
    UL_UNI_Sued = 1,
    UL_UNI_Nord = 2,
    UL_UNI_Helmholtz = 3,
    UL_UNI_West = 4

    def __str__(self):
        return ''

    @staticmethod
    def from_str(label: str):
        l = label.lower().strip()  # all smallercase and trim whitespace
        if "ul uni mensa süd" in l:
            return UniversityMensa.UL_UNI_Sued
        elif "ul uni nord" in l:
            return UniversityMensa.UL_UNI_Nord
        elif "ul uni helmholtz" in l:
            return UniversityMensa.UL_UNI_Helmholtz
        elif "ul uni west" in l:
            return UniversityMensa.UL_UNI_West
        else:
            raise NotImplementedError


BASE_URL = "https://studierendenwerk-ulm.de/essen-trinken/speiseplaene"


def get_speiseplan() -> []:
    def ulm_filter(url):
        if url["mensa"] == UniversityMensa.UL_UNI_Sued:
            return True
        # if url["mensa"] == UniversityMensa.UL_UNI_West:
        #     return True
        return False

    plans = get_links()
    plans = list(filter(ulm_filter, plans))
    for link in plans:
        link["parsed"] = parse_speiseplan(link["url"])

    return plans


def parse_speiseplan(url: str) -> dict:
    mp = pdf_parser.MensaParser()
    try:
        return mp.parse_plan_from_url(url)
    except Exception as e:
        print(f"Exception occurred with {url}: {e}")


def fs_et_adapter(plans: []) -> dict:
    result = {"weeks": []}

    for p in plans:
        pass


def simple_adapter(plans: []) -> dict:
    result = {}

    for p in plans:
        mensa_name = p["mensa"].name.lower()
        if mensa_name not in result:
            result[mensa_name] = {}
        mensa_dict = result[mensa_name]
        for day in p["parsed"]["weekdays"]:
            day_dict = p["parsed"]["weekdays"][day]
            date = day_dict["date"]

            if date not in mensa_dict:
                mensa_dict[date] = []

            meals = day_dict["meals"]
            for meal_category in day_dict["meals"]:
                if meal_category == "extra":
                    continue  # skip extra category for the time being

                current_meal = meals[meal_category]
                if (not "name" in current_meal) or \
                        (not "prices" in current_meal):
                    continue
                out = {
                    "name": current_meal["name"],
                    "category": pdf_parser.MealCategory.pretty_print(
                        meal_category),
                    "prices": dict(current_meal["prices"]),
                }
                mensa_dict[date].append(out)

    return result


def get_speiseplan_website() -> str:
    """
    Loads the
    :return:
    """
    speiseplan_source = ""
    with urllib.request.urlopen(BASE_URL) as response:
        speiseplan_source = response.read().decode("utf-8")
    return speiseplan_source


def get_links() -> []:
    source = get_speiseplan_website()
    soup = BeautifulSoup(source, "html.parser")

    links = soup.find_all("a", string="hier")

    plans = []
    for a in links:
        try:
            plans.append(parse_href(a["href"]))
        except NotImplementedError as e:
            break
        except Exception as e:
            pass

    return plans


def parse_href(href: str) -> dict:
    plan = {"url": href}
    split_list = href.split("/")
    filename = split_list.pop()  # get last element of list -> filename
    filename = filename[:-4]  # remove .pdf
    file_attrs = re.split('\s+', filename)
    file_attrs.pop()  # monthly mensa plan
    plan["week"] = file_attrs.pop()  # week in format KW**
    plan["mensa"] = UniversityMensa.from_str(" ".join(file_attrs))
    return plan


if __name__ == "__main__":
    plans = get_speiseplan()
    formatted = fs_et_adapter(plans)

    if len(sys.argv) >= 2:
        with open(sys.argv[1], "w") as f:
            f.write(dumps(formatted))
    else:  # no argument
        with open("./out/mensaplan.json", "w") as f:
            f.write(dumps(formatted))
