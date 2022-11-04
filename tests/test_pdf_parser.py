from unittest import TestCase
from mensa_parser import pdf_parser

class TestPdfParser(TestCase):

    def test_parse_pdf_file(self):
        mp = pdf_parser.MensaParser()
        text = mp.parse_plan_from_file("resources/UL UNI Mensa Süd KW44 W3.pdf")

        mon = text["weekdays"]["monday"]
        self.assertEqual(mon["date"], '2022-10-31')
        self.assertEqual(mon["meals"]["fleisch_und_fisch"]["name"], 'Cevapcici mit Ajvar Djuvetschreis')
        self.assertEqual(mon["meals"]["fleisch_und_fisch"]["prices"], {'students': '4,30 €', 'employees': '6,20 €', 'others': '8,20 €'})
        self.assertEqual(mon["meals"]["prima_klima"]["name"], "Farfalle-Spinat-Pfanne, Kirschtomaten in Käsesahne")
