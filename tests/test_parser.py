from unittest import TestCase
from uniulm_mensaparser import api


class TestSpeiseplanWebsiteParser(TestCase):

    def test_parse_plan(self):
        test = api.get_plan()
        print(test)
