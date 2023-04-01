from unittest import TestCase
from uniulm_mensaparser.mensaparser import parse_plan_from_file
from uniulm_mensaparser.pdf_parser import DefaultMensaParser, MensaNordParser, parse_date_string
from uniulm_mensaparser.models import Weekday, Canteen, Plan
from uniulm_mensaparser.adapter import SimpleAdapter2
import json
import io


class TestAdapter(TestCase):
    def test_new_and_legacy_simple_adapter(self):
        mp = DefaultMensaParser(Canteen.UL_UNI_Sued)
        meal = parse_plan_from_file("resources/UL UNI Mensa Süd KW13 W3.pdf", mp)
        plans = Plan(meals=meal)
        adapter = SimpleAdapter2()
        actual = json.dumps(adapter.convert_plans([plans]), indent=2)
        with io.open("resources/UL UNI Mensa Süd KW13 W3 expected.json", mode="r", encoding="utf-8") as f:
            expected = json.dumps(json.load(f), indent=2)
            actual_split = actual.split("\n")
            expected_split = expected.split("\n")
            self.assertListEqual(expected_split, actual_split)  # sorry
