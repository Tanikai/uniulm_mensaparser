import re

from bs4 import BeautifulSoup, Tag, NavigableString
from uniulm_mensaparser.models import Meal, MealCategory, Canteen
from typing import List, Tuple
from dataclasses import dataclass

from datetime import datetime

from uniulm_mensaparser.pdf_parser import build_meal_name
from uniulm_mensaparser.utils import date_format_iso


@dataclass
class SoupMealCategory:
    headerDiv: Tag
    mealDivs: List[Tag]


class HtmlMensaParser:
    def __init__(self):
        pass

    # Gets the source of a day and parses it into meals.
    def parse_plan(self, source: str, date: datetime, canteen: Canteen) -> List[Meal]:
        soup = BeautifulSoup(source, "html.parser")
        meals: List[Meal] = []

        no_meals = soup.find("div", {"class": "nodata"})

        if no_meals is not None:
            return []

        meal_container: Tag = soup.div

        categories: List[SoupMealCategory] = self._split_categories(
            meal_container.findChildren("div", recursive=False)
        )
        for cat in categories:
            meals += self._parse_category(cat)

        year, week_number, _ = date.isocalendar()
        for m in meals:
            # name and
            # category is already set
            m.date = date_format_iso(date)
            m.week_number = week_number
            # prices for students, employees, others is already set
            m.canteen = canteen
            # allergy and type is already set

        return meals

    def _split_categories(self, meal_categories: List[Tag]) -> List[SoupMealCategory]:
        result: List[SoupMealCategory] = []

        while len(meal_categories) > 0:
            category_div = meal_categories.pop(0)
            if "gruppenkopf" not in category_div.attrs["class"]:
                raise Exception("invalid input")
            meal_divs = []

            while (
                len(meal_categories) > 0
                and "gruppenkopf" not in meal_categories[0].attrs["class"]
            ):
                meal_divs.append(meal_categories.pop(0))

            result.append(
                SoupMealCategory(
                    headerDiv=category_div,
                    mealDivs=meal_divs,
                )
            )

        return result

    def _parse_category(self, category: SoupMealCategory) -> List[Meal]:
        """
        Parses a single meal from the day.
        Args:
            category: The souped div from the HTML document.

        Returns:

        """
        meal_category = MealCategory.from_str(
            str(category.headerDiv.find("div", {"class": "gruppenname"}).contents[0])
        )

        meals = []

        for mealDiv in category.mealDivs:
            # Parse allergy information
            allergy = mealDiv.attrs["lang"]
            allergy_ids = set(allergy.split(","))

            # Get meal string
            meal_block = mealDiv.find(
                "div", {"class": "visible-xs-block"}
            )  # first block due to
            fltl_divs = meal_block.findAll("div", {"class": "fltl"})

            meal_info = fltl_divs[1]
            meal_name_parts = list(
                filter(
                    lambda child: isinstance(child, NavigableString), meal_info.contents
                )
            )

            # Clean up and concatenate partial strings of meal name
            meal_name = build_meal_name(meal_name_parts)

            # Get meal type (vegetarian, vegan, ...) -> there can be multiple meal types per meal
            meal_type = ""
            meal_types = []
            meal_type_icons = mealDiv.findAll("img", {"class": "icon", "title": re.compile("^(?:(?!BIO).)*$")}) # not bio
            print(meal_type_icons)
            if meal_type_icons is not None and not len(meal_type_icons) == 0:
                meal_type = meal_type_icons[0].attrs["title"]
                meal_types = list(map(lambda icon: icon.attrs["title"], meal_type_icons))

            price_div = meal_block.find("span", {"class": "preisgramm"}).parent
            price_text = price_div.text
            price_students, price_emp, price_others = self._parse_prices(price_text)

            meals.append(
                Meal(
                    name=meal_name,
                    category=meal_category,
                    allergy_ids=allergy_ids,
                    type=meal_type,
                    types=meal_types,
                    price_students=price_students,
                    price_employees=price_emp,
                    price_others=price_others,
                )
            )

        return meals

    def _parse_prices(self, price: str) -> Tuple[str, str, str]:
        cleaned: str = price.replace("\xa0", " ").strip(" €&nbsp")
        split = list(map(lambda price: price.strip() + " €", cleaned.split("|")))
        return split[0], split[1], split[2]
