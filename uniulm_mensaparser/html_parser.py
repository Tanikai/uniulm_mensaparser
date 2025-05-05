import re

from bs4 import BeautifulSoup, Tag, NavigableString
from uniulm_mensaparser.models import Meal, Canteen, MealNutrition, MealType
from typing import List, Tuple
from dataclasses import dataclass

from datetime import date

from uniulm_mensaparser.utils import date_format_iso


@dataclass
class SoupMealCategory:
    headerDiv: Tag
    mealDivs: List[Tag]


def remove_allergens(line: str) -> str:
    parentheses_re = r"\(.*?\)"  # ? == greedy match
    return re.sub(parentheses_re, "", line)


def build_meal_name(meal_lines: [str]) -> str:
    meal_name = " ".join(meal_lines)

    meal_name = remove_allergens(meal_name)
    # remove duplicate whitespaces
    meal_name = re.sub(r"\s+", r" ", meal_name)
    # if the next word begins with an uppercase letter, the - is part of
    # the word and should be kept
    meal_name = re.sub(r"- ([A-Z])", r"-\g<1>", meal_name)
    # if the next word begins with a lowercase letter, the - is used for
    # hyphenation and thus should be removed
    meal_name = re.sub(r"- ([a-z])", r"\g<1>", meal_name)
    meal_name = re.sub(r" ,", r",", meal_name)  # remove space before comma
    meal_name = re.sub(r"(?<=,)(?=\S)", " ", meal_name)  # add space after comma
    meal_name = re.sub(
        r" , ", r" ", meal_name
    )  # remove commas without content before or after
    meal_name = meal_name.strip()  # strip remaining whitespace before and after string
    return meal_name


def _pretty_print_meal(meal_category: str) -> str:
    words = meal_category.strip().split()
    formatted = []
    for word in words:
        if word == "+":
            formatted.append("und")
            continue

        if all(letter.lower() == 'i' for letter in word):
            formatted.append(word.upper())
            continue

        formatted.append(word.capitalize())

    return " ".join(formatted)


class HtmlMensaParser:
    def __init__(self):
        pass

    # Gets the source of a day and parses it into meals.
    def parse_plan(self, source: str, plan_date: date, canteen: Canteen) -> List[Meal]:
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

        year, week_number, _ = plan_date.isocalendar()
        for m in meals:
            # name and
            # category is already set
            m.date = date_format_iso(plan_date)
            m.week_number = week_number
            # prices for students, employees, others is already set
            m.canteen = canteen
            # allergy and type is already set

        return meals

    @staticmethod
    def _split_categories(meal_categories: List[Tag]) -> List[SoupMealCategory]:
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
        meal_category = str(category.headerDiv.find("div", {"class": "gruppenname"}).contents[0])
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
            meal_types = []
            meal_type_icons = mealDiv.findAll(
                "img", {"class": "icon"}
            )  # not bio
            if meal_type_icons is not None and not len(meal_type_icons) == 0:
                meal_types = list(
                    map(lambda icon: MealType.from_filename_str(icon.attrs["src"].removeprefix("assets/icons/").removesuffix(".png")),
                        meal_type_icons)
                )

            price_div = meal_block.find("span", {"class": "preisgramm"}).parent
            price_text = price_div.text
            price_students, price_emp, price_others, price_note = self._parse_prices(price_text)

            # Get co2 and nutrition information
            nutri_div = mealDiv.find("div", {"class": "azn"})

            co2_str = ""
            nutrition = MealNutrition()
            if nutri_div:
                co2_list = list(filter(lambda elem: isinstance(elem, NavigableString), nutri_div.contents))
                co2_full_str = " ".join(co2_list).strip()
                matches = re.findall(r"[\d\.\,]*\sg", co2_full_str)
                if len(matches) == 1:
                    co2_str = matches[0]
                elif len(matches) > 1:
                    co2_str = matches[-1]

                nutri_rows = nutri_div.findAll("tr")
                nutri_rows = nutri_rows[1:]  # remove header row
                nutrition = self._parse_meal_nutrition(nutri_rows)

            meals.append(
                Meal(
                    name=meal_name,
                    category=_pretty_print_meal(meal_category),
                    allergy_ids=allergy_ids,
                    types=meal_types,
                    price_note=price_note,
                    price_students=price_students,
                    price_employees=price_emp,
                    price_others=price_others,
                    co2=co2_str,
                    nutrition=nutrition,
                )
            )

        return meals

    @staticmethod
    def _parse_prices(price: str) -> Tuple[str, str, str, str]:
        """
        price_note is an additional information regarding the price, e.g. "pro 100g"

        Args:
            price:

        Returns: [price_students, price_employees, price_others, price_note]

        """
        price_note = ""
        if "(" in price:
            left_parentheses_index = price.find("(")
            right_parentheses_index = price.find(")")
            price_note = price[left_parentheses_index + 1:right_parentheses_index]
            price = price[right_parentheses_index + 1:]

        cleaned: str = price.replace("\xa0", " ").strip(" €&nbsp")

        split = list(map(lambda p: p.strip() + " €", cleaned.split("|")))
        if len(split) != 3:
            return "n/a", "n/a", "n/a", price_note
        return split[0], split[1], split[2], price_note

    @staticmethod
    def _parse_meal_nutrition(divs) -> MealNutrition:

        def _parse_nutrition_with_parentheses(div_text: str) -> Tuple[str, str]:
            gram_index = div_text.find("g")
            first_value = div_text[:gram_index + 1]
            left_parentheses_index = div_text.find("(")
            right_parentheses_index = div_text.find(")")
            parentheses_value = div_text[left_parentheses_index + 1:right_parentheses_index]

            return first_value, parentheses_value

        try:
            # energy
            energy_cells = divs[0].findAll("td")
            energy_value = energy_cells[1].decode_contents().strip()

            # protein
            protein_cells = divs[1].findAll("td")
            protein_value = protein_cells[1].decode_contents().strip()

            # fat & saturated fat
            fat_cells = divs[2].findAll("td")
            fat_value, saturated_fat_value = _parse_nutrition_with_parentheses(fat_cells[1].decode_contents().strip())

            # carbohydrates & sugar
            carb_cells = divs[3].findAll("td")
            carb_value, sugar_value = _parse_nutrition_with_parentheses(carb_cells[1].decode_contents().strip())

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
