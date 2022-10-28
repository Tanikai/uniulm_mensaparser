from unittest import TestCase
import pdf_parser

class Test(TestCase):
    def test_parse_pdf(self):
        with open('../tests/resources/UL UNI Mensa Süd KW43 W2.pdf', "rb") as pdf:
            pdf_parser.parse_pdf_file(pdf)
        self.fail()
