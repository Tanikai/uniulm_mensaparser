import unittest
from unittest import TestCase

import aiohttp

from uniulm_mensaparser import api
from json import dumps

from uniulm_mensaparser.studierendenwerk_scraper import get_maxmanager_website
from datetime import date


class TestSpeiseplanWebsiteParser(TestCase):
    def test_parse_plan(self):
        test = api.get_plan()
        with open("parser_output.json", "w") as f:
            f.write(dumps(test, indent=2, ensure_ascii=False))


class TestAsyncPlanFetch(unittest.IsolatedAsyncioTestCase):
    async def test_maxmanager_api(self):
        async with aiohttp.ClientSession() as session:
            with open("new-html/output.txt", "w") as f:
                test = await get_maxmanager_website(session, loc_id=1, plan_date=date(2025, 1, 7))
                f.write(test)
