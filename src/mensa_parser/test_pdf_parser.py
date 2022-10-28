from unittest import TestCase
import pdf_parser

class Test(TestCase):
    def test_parse_pdf(self):
        pdf_parser.parse_pdf('../../tests/resources/UL UNI Mensa Süd KW43 W2.pdf')
        #with open(, "rb") as pdf:
        #    pdf_parser.parse_pdf_file(pdf)
        self.fail()
