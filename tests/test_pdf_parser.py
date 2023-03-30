from unittest import TestCase
from uniulm_mensaparser.mensaparser import parse_plan_from_file
from uniulm_mensaparser.pdf_parser import DefaultMensaParser


class TestPdfParser(TestCase):

    def test_parse_pdf_file(self):
        mp = DefaultMensaParser()
        parsed = parse_plan_from_file("resources/UL UNI Mensa Süd KW44 W3.pdf", mp)

        mon = parsed["weekdays"]["monday"]
        self.assertEqual(mon["date"], '2022-10-31')
        self.assertEqual(mon["meals"]["fleisch_und_fisch"]["name"], 'Cevapcici mit Ajvar Djuvetschreis')
        self.assertEqual(mon["meals"]["fleisch_und_fisch"]["prices"], {'students': '4,30 €', 'employees': '6,20 €', 'others': '8,20 €'})
        self.assertEqual(mon["meals"]["prima_klima"]["name"], "Farfalle-Spinat-Pfanne, Kirschtomaten in Käsesahne")
