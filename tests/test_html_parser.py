from unittest import TestCase
from uniulm_mensaparser.models import MealCategory, BistroMealCategory

from unittest import TestCase
from uniulm_mensaparser.html_parser import HtmlMensaParser
from uniulm_mensaparser.models import Canteen, DefaultMealCategory, Meal
from datetime import datetime


class TestHtmlParser(TestCase):

    def test_multiple_types(self):
        with open("new-html/double.html") as f:
            parser = HtmlMensaParser()
            plan = parser.parse_plan(f.read(), datetime(2023, 12, 19), Canteen.UL_UNI_Sued)
            meal: Meal = next(filter(lambda p: p.category == DefaultMealCategory.FLEISCH_UND_FISCH, plan))
            self.assertListEqual(meal.types, ["Fisch", "GeflÃ¼gel"], "meal has to contain both categories")

    def test_extra_category(self):
        with open("new-html/wiener.html") as f:
            parser = HtmlMensaParser()
            plan = parser.parse_plan(f.read(), datetime(2023, 12, 21), Canteen.UL_UNI_Sued)
            meal: Meal = next(filter(lambda p: p.category == DefaultMealCategory.EXTRA, plan))
            self.assertEqual(meal.name, "1 Wienerle")
