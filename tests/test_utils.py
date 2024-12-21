from unittest import TestCase

from uniulm_mensaparser.utils import get_weekdates_this_and_next_week
from datetime import datetime

class TestUtils(TestCase):
    def test_generate_weekdays(self):
        test_time = datetime(year=2024, month=12, day=21)
        generated_dates = get_weekdates_this_and_next_week(test_time)

        self.assertListEqual(generated_dates, [
            datetime(year=2024, month=12, day=16),
            datetime(year=2024, month=12, day=17),
            datetime(year=2024, month=12, day=18),
            datetime(year=2024, month=12, day=19),
            datetime(year=2024, month=12, day=20),
            datetime(year=2024, month=12, day=23),
            datetime(year=2024, month=12, day=24),
            datetime(year=2024, month=12, day=25),
            datetime(year=2024, month=12, day=26),
            datetime(year=2024, month=12, day=27),
        ])
