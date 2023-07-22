import urllib.request
from datetime import datetime, timedelta


def get_monday(week_offset=0):
    now = datetime.now() + timedelta(weeks=week_offset)
    monday = now - timedelta(days=now.weekday())
    return monday


def date_format_iso(date: datetime):
    return date.strftime("%Y-%m-%d")


def get_website(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        source = response.read().decode("utf-8")
        return source
