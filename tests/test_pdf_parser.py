from unittest import TestCase
from uniulm_mensaparser.mensaparser import parse_plan_from_file
from uniulm_mensaparser.pdf_parser import DefaultMensaParser, MensaNordParser, parse_date_string
from uniulm_mensaparser.models import Weekday


class TestPdfParser(TestCase):

    def test_parse_pdf_file(self):
        mp = DefaultMensaParser()
        parsed = parse_plan_from_file("resources/UL UNI Mensa Süd KW44 W3.pdf", mp)

        mon = parsed["weekdays"]["monday"]
        self.assertEqual(mon["date"], '2022-10-31')
        self.assertEqual(mon["meals"]["fleisch_und_fisch"]["name"], 'Cevapcici mit Ajvar Djuvetschreis')
        self.assertEqual(mon["meals"]["fleisch_und_fisch"]["prices"], {'students': '4,30 €', 'employees': '6,20 €', 'others': '8,20 €'})
        self.assertEqual(mon["meals"]["prima_klima"]["name"], "Farfalle-Spinat-Pfanne, Kirschtomaten in Käsesahne")

    def test_mensa_nord(self):
        mp = MensaNordParser()
        parsed = parse_plan_from_file("resources/UL UNI Nord KW44 W2.pdf", mp)
        print("result", parsed)

    def test_parse_date_string(self):
        wd = parse_date_string("27.03. - 31.03.2023")
        self.assertEqual("2023-03-27", wd[Weekday.MONDAY])
        self.assertEqual("2023-03-28", wd[Weekday.TUESDAY])
        self.assertEqual("2023-03-29", wd[Weekday.WEDNESDAY])
        self.assertEqual("2023-03-30", wd[Weekday.THURSDAY])
        self.assertEqual("2023-03-31", wd[Weekday.FRIDAY])

        wd = parse_date_string("27.02. - 03.03.2023")
        self.assertEqual("2023-02-27", wd[Weekday.MONDAY])
        self.assertEqual("2023-02-28", wd[Weekday.TUESDAY])
        self.assertEqual("2023-03-01", wd[Weekday.WEDNESDAY])
        self.assertEqual("2023-03-02", wd[Weekday.THURSDAY])
        self.assertEqual("2023-03-03", wd[Weekday.FRIDAY])

        wd = parse_date_string("30.12. - 03.01.2023")
        self.assertEqual("2022-12-30", wd[Weekday.MONDAY])
        self.assertEqual("2022-12-31", wd[Weekday.TUESDAY])
        self.assertEqual("2023-01-01", wd[Weekday.WEDNESDAY])
        self.assertEqual("2023-01-02", wd[Weekday.THURSDAY])
        self.assertEqual("2023-01-03", wd[Weekday.FRIDAY])
