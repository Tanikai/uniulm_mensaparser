from datetime import datetime
from pathlib import Path
from unittest import TestCase

from uniulm_mensaparser.html_parser import HtmlMensaParser
from uniulm_mensaparser.models import Canteen, Meal, MealType


class TestHtmlParser(TestCase):
    def setUp(self):
        self.test_data_dir = Path(__file__).parent / "new-html"

    def test_wrapped_html_still_parses(self):
        with open(self.test_data_dir / "locid1.html") as f:
            parser = HtmlMensaParser()
            wrapped = f"<html><body><div id='wrapper'>{f.read()}</div></body></html>"
            plan = parser.parse_plan(
                wrapped, datetime(2023, 12, 19), Canteen.UL_UNI_Sued
            )
            self.assertGreater(len(plan), 0, "wrapped HTML should still produce meals")

    def test_multiple_types(self):
        with open(self.test_data_dir / "double.html") as f:
            parser = HtmlMensaParser()
            plan = parser.parse_plan(
                f.read(), datetime(2023, 12, 19), Canteen.UL_UNI_Sued
            )
            meal: Meal = next(filter(lambda p: p.category == "Fleisch und Fisch", plan))
            self.assertListEqual(
                meal.types,
                [MealType.FISH, MealType.POULTRY],
                "meal has to contain both categories",
            )

    def test_extra_category(self):
        with open(self.test_data_dir / "wiener.html") as f:
            parser = HtmlMensaParser()
            plan = parser.parse_plan(
                f.read(), datetime(2023, 12, 21), Canteen.UL_UNI_Sued
            )
            meal: Meal = next(filter(lambda p: p.category == "Extra", plan))
            self.assertEqual(meal.name, "1 Wienerle")
