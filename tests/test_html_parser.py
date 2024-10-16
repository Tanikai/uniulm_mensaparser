from unittest import TestCase
from uniulm_mensaparser.html_parser import HtmlMensaParser
from uniulm_mensaparser.models import Canteen, Meal, MealNutrition
from datetime import datetime
from dataclasses import asdict


class TestHtmlParser(TestCase):

    def test_multiple_types(self):
        with open("new-html/double.html") as f:
            parser = HtmlMensaParser()
            plan = parser.parse_plan(f.read(), datetime(2023, 12, 19), Canteen.UL_UNI_Sued)
            meal: Meal = next(filter(lambda p: p.category == "Fleisch und Fisch", plan))
            self.assertListEqual(meal.types, ["Fisch", "Geflügel"], "meal has to contain both categories")

    def test_extra_category(self):
        with open("new-html/wiener.html") as f:
            parser = HtmlMensaParser()
            plan = parser.parse_plan(f.read(), datetime(2023, 12, 21), Canteen.UL_UNI_Sued)
            meal: Meal = next(filter(lambda p: p.category == "Extra", plan))
            self.assertEqual(meal.name, "1 Wienerle")

    def test_nutrition(self):
        with open("new-html/nutrition.html", encoding="utf-8") as f:
            parser = HtmlMensaParser()
            plan = parser.parse_plan(f.read(), datetime(2024, 5, 21), Canteen.UL_UNI_Sued)

            tup: Meal = next(filter(lambda p: p.category == "Topf und Pfanne", plan))
            self.assertEqual(tup.co2, "744 g")
            self.assertDictEqual(asdict(tup.nutrition), asdict(MealNutrition(
                calories="565,0 kcal",
                protein="25,0 g",
                fat="18,6 g",
                saturated_fat='davon gesättigt 8,5 g',
                carbohydrates="76,1 g",
                sugar="davon Zucker 12,0 g",
                salt="2,5 g"
            )))
