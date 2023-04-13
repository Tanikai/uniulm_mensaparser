from datetime import datetime, timedelta


def get_monday(week_offset = 0):
    now = datetime.now() + timedelta(weeks=week_offset)
    monday = now - timedelta(days = now.weekday())
    return monday


def date_format_iso(date: datetime):
    return date.strftime("%Y-%m-%d")
