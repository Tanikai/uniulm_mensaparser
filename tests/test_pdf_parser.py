from unittest import TestCase
from uniulm_mensaparser.mensaparser import parse_plan_from_file
from uniulm_mensaparser.pdf_parser import DefaultMensaParser, MensaNordParser, parse_date_string, build_meal_name
from uniulm_mensaparser.models import Weekday, Canteen, BistroMealCategory


class TestPdfParser(TestCase):

    def test_parse_pdf_file(self):
        mp = DefaultMensaParser(Canteen.UL_UNI_Sued)
        meals = parse_plan_from_file("resources/UL UNI Mensa Süd KW44 W3.pdf", mp)

        mon_fuf = meals[0]
        self.assertEqual(mon_fuf.date, "2022-10-31")
        self.assertEqual(mon_fuf.name, 'Cevapcici mit Ajvar Djuvetschreis')
        self.assertEqual(mon_fuf.price_students, "4,30 €")
        self.assertEqual(mon_fuf.price_employees, "6,20 €")
        self.assertEqual(mon_fuf.price_others, "8,20 €")

    def test_mensa_nord(self):
        mp = MensaNordParser(Canteen.UL_UNI_Nord)
        parsed = parse_plan_from_file("resources/UL UNI Nord KW44 W2.pdf", mp)

        print(parsed)
        self.assertEqual(BistroMealCategory.PIZZA_I, parsed[0].category)
        self.assertEqual(BistroMealCategory.PIZZA_II, parsed[1].category)
        self.assertEqual(BistroMealCategory.PIZZA_III, parsed[2].category)
        self.assertEqual(BistroMealCategory.PASTA_I, parsed[3].category)
        self.assertEqual(BistroMealCategory.PASTA_II, parsed[4].category)

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

    def test_build_meal_name(self):
        meal_lines = ['Wiener Backhendl (14,', '34W)', 'Remouladensoße, (2, 9, 14, 24,', '27, 30, 35),',
                      'Kartoffel-Gurkensalat (27)']
        self.assertEqual('Wiener Backhendl Remouladensoße, Kartoffel-Gurkensalat', build_meal_name(meal_lines))
