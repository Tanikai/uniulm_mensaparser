from unittest import TestCase
from uniulm_mensaparser import api, FsEtAdapter
from json import dumps
import asyncio


class TestSpeiseplanWebsiteParser(TestCase):

    def test_parse_plan(self):
        test = api.get_plan()
        with open("parser_output.json", "w") as f:
            f.write(dumps(test, indent=2, ensure_ascii=False))

        test2 = api.get_plan(adapter_class=FsEtAdapter)
        with open("parser_output_fset.json", "w") as f:
            f.write(dumps(test2, indent=2, ensure_ascii=False))
