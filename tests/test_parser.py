from unittest import TestCase
from uniulm_mensaparser import api
from json import dumps


class TestSpeiseplanWebsiteParser(TestCase):

    def test_parse_plan(self):
        test = api.get_plan()
        with open("parser_output.json", "w") as f:
            f.write(dumps(test, indent=2, ensure_ascii=False))
