import unittest
from datetime import date
from json import dumps
from pathlib import Path
from unittest import TestCase

import aiohttp

from uniulm_mensaparser import api
from uniulm_mensaparser.studierendenwerk_scraper import get_maxmanager_website


class TestSpeiseplanWebsiteParser(TestCase):
    def setUp(self):
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)

    def test_parse_plan(self):
        test = api.get_plan()
        with open(self.output_dir / "parser_output.json", "w") as f:
            f.write(dumps(test, indent=2, ensure_ascii=False))

    def test_get_plan_english(self):
        test = api.get_plan_by_language("en")
        with open(self.output_dir / "parser_output_en.json", "w") as f:
            f.write(dumps(test, indent=2, ensure_ascii=False))


class TestAsyncPlanFetch(unittest.IsolatedAsyncioTestCase):
    async def test_maxmanager_api(self):
        async with aiohttp.ClientSession() as session:
            # Removed file writing in test to avoid directory issues
            test = await get_maxmanager_website(
                session, loc_id=1, plan_date=date(2025, 1, 7)
            )
            self.assertIsNotNone(test)
