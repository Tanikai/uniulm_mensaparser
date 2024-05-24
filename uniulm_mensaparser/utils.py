from datetime import datetime, timedelta
import aiohttp
import unicodedata

def get_monday(week_offset=0):
    now = datetime.now() + timedelta(weeks=week_offset)
    monday = now - timedelta(days=now.weekday())
    return monday


def date_format_iso(date: datetime):
    return date.strftime("%Y-%m-%d")


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as resp:
        return await resp.text()

def normalize_str(s: str) -> str:
    return s.replace("&nbsp;", " ").replace("\xa0", " ").strip()
