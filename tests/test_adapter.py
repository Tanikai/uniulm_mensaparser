from unittest import TestCase
from uniulm_mensaparser.mensaparser import parse_plan_from_file
from uniulm_mensaparser.pdf_parser import DefaultMensaParser, MensaNordParser, parse_date_string
from uniulm_mensaparser.models import Weekday, Canteen, Plan
from uniulm_mensaparser.adapter import SimpleAdapter2, FsEtAdapter
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

    def test_simple_adapter_empty_day(self):
        """
        Mensa closed on friday -> empty array
        :return:
        """
        mp = DefaultMensaParser(Canteen.UL_UNI_Sued)
        meal = parse_plan_from_file("resources/UL UNI Mensa Süd KW14 W4.pdf", mp)
        plan = Plan(meals=meal)
        plan.canteen = Canteen.UL_UNI_Sued
        plan.opened_days = mp.get_opened_days()
        adapter = SimpleAdapter2()
        actual = adapter.convert_plans([plan])
        self.assertEqual([], actual["ul_uni_sued"]["2023-04-07"])

    def test_fset_adapter_empty_day(self):
        mp = DefaultMensaParser(Canteen.UL_UNI_Sued)
        meal = parse_plan_from_file("resources/UL UNI Mensa Süd KW14 W4.pdf", mp)
        plan = Plan(meals=meal)
        plan.canteen = Canteen.UL_UNI_Sued
        plan.opened_days = mp.get_opened_days()
        plan.week = "KW14"
        adapter = FsEtAdapter()
        actual = adapter.convert_plans([plan])
        self.assertEqual(False, actual["weeks"][0]["days"][4]["Mensa"]["open"])
        self.assertEqual([], actual["weeks"][0]["days"][4]["Mensa"]["meals"])

    def test_fset_adapter(self):
        mp = MensaNordParser(Canteen.UL_UNI_West)
        meal = parse_plan_from_file("resources/UL UNI Nord KW44 W2.pdf", mp)
        plans = Plan(meals=meal)
        adapter = FsEtAdapter()
        actual = json.dumps(adapter.convert_plans([plans]), indent=2)
        print(actual)