from unittest import TestCase
from mensa_parser import parser, adapter

class TestSpeiseplanWebsiteParser(TestCase):

    def test_parse_plan(self):
        test = parser.get_current_plans(adapter.SimpleAdapter)
        pass
