from datetime import datetime, date, timedelta
import aiohttp
from typing import List


def get_monday(week_offset=0):
    now = datetime.now() + timedelta(weeks=week_offset)
    monday = now - timedelta(days=now.weekday())
    return monday


def date_format_iso(d: date):
    return d.strftime("%Y-%m-%d")


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as resp:
        return await resp.text()


def normalize_str(s: str) -> str:
    return s.replace("&nbsp;", " ").replace("\xa0", " ").strip()


def get_weekdates_from_weekday(weekday: datetime) -> List[datetime]:
    start_of_current_week = weekday - timedelta(days=weekday.weekday())
    current_weekdates = [start_of_current_week + timedelta(days=i) for i in range(5)]
    return current_weekdates


def get_weekdates_this_and_next_week(weekday: datetime) -> List[datetime]:
    next_week = weekday + timedelta(weeks=1)
    return get_weekdates_from_weekday(weekday) + get_weekdates_from_weekday(next_week)
