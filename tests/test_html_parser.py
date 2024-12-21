from unittest import TestCase
from uniulm_mensaparser.html_parser import HtmlMensaParser
from uniulm_mensaparser.models import Canteen, Meal
from datetime import datetime


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
