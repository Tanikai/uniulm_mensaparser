from bs4 import BeautifulSoup, Tag
from uniulm_mensaparser.models import Meal, MealCategory, Canteen
from typing import List, Tuple
from dataclasses import dataclass

from datetime import datetime

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

        categories: List[SoupMealCategory] = self._split_categories(meal_container.contents)
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

    def _split_categories(self, mealCategories: List[Tag]) -> List[SoupMealCategory]:
        result: List[SoupMealCategory] = []

        while len(mealCategories) > 0:
            categoryDiv = mealCategories.pop(0)
            if "gruppenkopf" not in categoryDiv.attrs["class"]:
                raise Exception("invalid input")
            mealDivs = []

            while len(mealCategories) > 0 and not "gruppenkopf" in mealCategories[0].attrs["class"]:
                mealDivs.append(mealCategories.pop(0))

            result.append(
                SoupMealCategory(
                    headerDiv=categoryDiv,
                    mealDivs=mealDivs,
                )
            )

        return result

    def _parse_category(self, category: SoupMealCategory) -> List[Meal]:
        meal_category = MealCategory.from_str(category.headerDiv.find("div", {"class": "gruppenname"}).contents[0])

        meals = []

        for mealDiv in category.mealDivs:
            allergy = mealDiv.attrs["lang"]
            mealBlock = mealDiv.find("div", {"class": "visible-xs-block"})  # first block due to
            fltlDivs = mealBlock.findAll("div", {"class": "fltl"})

            mealInfo = fltlDivs[1]
            mealName = mealInfo.contents[0].strip()

            if len(fltlDivs[3].contents) > 0:
                mealTypeImg = fltlDivs[3].contents[0]
                mealType = mealTypeImg.attrs["title"]

            priceDiv = mealBlock.find("span", {"class": "preisgramm"}).parent
            priceText = priceDiv.text
            price_students, price_emp, price_others = self._parse_prices(priceText)

            meals.append(Meal(
                name=mealName,
                category=meal_category,
                allergy=allergy,
                type=mealType,
                price_students=price_students,
                price_employees=price_emp,
                price_others=price_others
            ))

        return meals


    def _parse_prices(self, price: str) -> Tuple[str, str, str]:
        cleaned: str = price.replace(u'\xa0', ' ').strip(" €")
        split = list(map(lambda price: price.strip() + " €", cleaned.split("|")))
        return split[0], split[1], split[2]
