import re

from bs4 import BeautifulSoup, Tag, NavigableString
from uniulm_mensaparser.models import Meal, MealCategory, Canteen, MealNutrition
from typing import List, Tuple
from dataclasses import dataclass

from datetime import datetime

from uniulm_mensaparser.pdf_parser import build_meal_name
from uniulm_mensaparser.utils import date_format_iso, normalize_str


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
            meal_type_icons = mealDiv.findAll(
                "img", {"class": "icon", "title": re.compile("^(?:(?!BIO).)*$")}
            )  # not bio
            if meal_type_icons is not None and not len(meal_type_icons) == 0:
                meal_type = meal_type_icons[0].attrs["title"]
                meal_types = list(
                    map(lambda icon: icon.attrs["title"], meal_type_icons)
                )

            price_div = meal_block.find("span", {"class": "preisgramm"}).parent
            price_text = price_div.text
            price_students, price_emp, price_others = self._parse_prices(price_text)

            # Get co2 and nutrition information
            nutri_div = mealDiv.find("div", {"class": "azn"})

            co2_list = list(filter(lambda elem: isinstance(elem, NavigableString), nutri_div.contents))
            co2_str = " ".join(co2_list).strip()
            co2_str = re.sub(r"^.*Portion ", "", co2_str)

            nutri_rows = nutri_div.findAll("tr")
            nutri_rows = nutri_rows[1:] # remove header row
            nutrition = self._parse_meal_nutrition(nutri_rows)

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
                    co2=co2_str,
                    nutrition=nutrition,
                )
            )

        return meals

    def _parse_prices(self, price: str) -> Tuple[str, str, str]:
        cleaned: str = price.replace("\xa0", " ").strip(" €&nbsp")
        split = list(map(lambda price: price.strip() + " €", cleaned.split("|")))
        if len(split) != 3:
            return "n/a", "n/a", "n/a"
        return split[0], split[1], split[2]

    def _parse_meal_nutrition(self, divs) -> MealNutrition:
        try:
            # energy
            energy_cells = divs[0].findAll("td")
            energy_value = energy_cells[1].decode_contents().strip()

            # protein
            protein_cells = divs[1].findAll("td")
            protein_value = protein_cells[1].decode_contents().strip()

            # fat & saturated fat
            fat_cells = divs[2].findAll("td")
            fat_value = fat_cells[1].decode_contents().strip()
            saturated_fat_value = normalize_str(fat_cells[2].decode_contents()).strip(" ()") # uses non-default parentheses

            # carbohydrates & sugar
            carb_cells = divs[3].findAll("td")
            carb_value = carb_cells[1].decode_contents().strip()
            sugar_value = normalize_str(carb_cells[2].decode_contents()).strip(" ()")

            # salt
            salt_cells = divs[4].findAll("td")
            salt_value = salt_cells[1].decode_contents().strip()

            return MealNutrition(
                calories=energy_value,
                protein=protein_value,
                fat=fat_value,
                saturated_fat=saturated_fat_value,
                carbohydrates=carb_value,
                sugar=sugar_value,
                salt=salt_value,
            )

        except Exception as e:
            # old html format does not have nutrition list
            return MealNutrition()
