from unittest import TestCase
from mensa_parser.parser import parse_from_url
from mensa_parser.pdf_parser import MensaParser
from mensa_parser.speiseplan_website_parser import get_speiseplan, Canteens

class TestPdfParser(TestCase):

    def test_parse_pdf_file(self):
        mp = MensaParser()
        text = mp.parse_plan_from_file("resources/UL UNI Mensa Süd KW44 W3.pdf")

        mon = text["weekdays"]["monday"]
        self.assertEqual(mon["date"], '2022-10-31')
        self.assertEqual(mon["meals"]["fleisch_und_fisch"]["name"], 'Cevapcici mit Ajvar Djuvetschreis')
        self.assertEqual(mon["meals"]["fleisch_und_fisch"]["prices"], {'students': '4,30 €', 'employees': '6,20 €', 'others': '8,20 €'})
        self.assertEqual(mon["meals"]["prima_klima"]["name"], "Farfalle-Spinat-Pfanne, Kirschtomaten in Käsesahne")

    def test_uni_west(self):
        plans = get_speiseplan({Canteens.UL_UNI_West})
        for p in plans:
            p["parsed"] = parse_from_url(p["url"])

        print(plans)
