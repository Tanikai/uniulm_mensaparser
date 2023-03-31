import re
import fitz
from datetime import timedelta, datetime
from .models import Weekday, MealCategory, Canteens, Meal
from abc import abstractmethod


class MensaParserIntf:
    @abstractmethod
    def parse_plan(self, page: fitz.Page):
        pass


def parse_date_string(line: str) -> dict[Weekday, str]:
    dates = line.split(" ")   # not '-' because a weird code point is used in the pdf
    from_date = datetime.strptime(dates[0], "%d.%m.")
    until_date = datetime.strptime(dates[2], "%d.%m.%Y")

    if until_date.month < from_date.month:
        from_date = from_date.replace(year=until_date.year - 1)  # new year
    else:
        from_date = from_date.replace(year=until_date.year)

    wd = {
        Weekday.MONDAY: "",
        Weekday.TUESDAY: "",
        Weekday.WEDNESDAY: "",
        Weekday.THURSDAY: "",
        Weekday.FRIDAY: "",
    }

    # set dates for
    for key in wd:
        wd[key] = from_date.strftime("%Y-%m-%d")
        from_date += timedelta(days=1)

    return wd


def get_weekday_dates(pdf_lines: [str]) -> dict[Weekday, str]:
    lines = re.split("\n+", pdf_lines)

    while len(lines) > 0:
        l = lines.pop(0).strip()  # clean whitespace
        if l == "":
            continue

        if "." in l:  # date found
            return parse_date_string(l)

class DefaultMensaParser(MensaParserIntf):

    def __init__(self):
        # @TODO SKIP EMPTY DAYS
        self.plan = {"weekdays": {}, "adapter_meals": []}
        for w in Weekday:
            weekdayname = w.name.lower()
            self.plan["weekdays"][weekdayname] = {"date": "",
                                                  "meals": {}}  # add weekdays to plan

            for cat in MealCategory:  # add meal categories to weekdays
                if cat is MealCategory.NONE:
                    continue
                categoryname = cat.name.lower()
                self.plan["weekdays"][weekdayname]["meals"][categoryname] = {}

        self.current_category = MealCategory.NONE  # MealCategory
        self.meal_weekday_counter = 1  # counts category of meal
        self.meal_category_counter = 1
        self.meal_lines = []

        # used to check whether mensa is open at a specific weekday
        self.is_open = {}
        for w in Weekday:
            self.is_open[w] = True

    def _init_mensa_opened(self, page: fitz.Page):
        col_h = 360
        col_w = 140
        col_top = 70
        col_bot = col_top + col_h

        rects = {
            Weekday.MONDAY: fitz.Rect(140, col_top, 140 + col_w, col_bot),
            Weekday.TUESDAY: fitz.Rect(280, col_top, 280 + col_w, col_bot),
            Weekday.WEDNESDAY: fitz.Rect(420, col_top, 420 + col_w, col_bot),
            Weekday.THURSDAY: fitz.Rect(560, col_top, 560 + col_w, col_bot),
            Weekday.FRIDAY: fitz.Rect(695, col_top, 695 + col_w, col_bot),
        }

        # if empty column is found, mensa is closed for that day
        for day in rects:
            found_text = page.get_text("text", clip=rects[day])
            # found_text = page.get_textbox(rects[day])
            if len(found_text) < 100:
                self.is_open[day] = False
            else:
                self.plan["weekdays"][day.name.lower()]["text"] = found_text

    def parse_plan(self, page: fitz.Page):
        self._init_mensa_opened(page)
        plan_source = page.get_text()

        lines = re.split("\n+", plan_source)

        # The plan begins with some date information / meals. We assume that we
        # have the date as it is contained in the pdf URL. This means that we
        # can skip until the "Fleisch und Fisch" category starts.
        meal_reached = False
        date_found = False
        while not meal_reached:
            l = self._clean_line(lines.pop(0))  # remove first item of list

            if not date_found and ("." in l):  # date found
                self._parse_week(l)
                date_found = True  # prevent multiple date parsing

            if MealCategory.is_meal_category(l):
                meal_reached = True
                self.current_category = MealCategory.from_str(l)

        # parse weekday columns
        for day in Weekday:
            self._parse_weekday(day)

        # convert meals to new format
        new_meals = []

        for d in self.plan["weekdays"]:
            day = self.plan["weekdays"][d]
            for meal_cat in day["meals"]:
                m = day["meals"][meal_cat]
                if m == {}:
                    continue
                try:
                    meal = Meal(
                        name=m["name"],
                        category=MealCategory.from_str(meal_cat),
                        date=day["date"],
                        week_number=-1,
                        price_students=m["prices"]["students"],
                        price_employees=m["prices"]["employees"],
                        price_others=m["prices"]["others"],
                        canteen=Canteens.NONE
                    )
                    new_meals.append(meal)
                except Exception as e:
                    print("An error occurred while converting", e)

        self.plan["adapter_meals"] = new_meals

        return self.plan

    def _parse_weekday(self, weekday: Weekday):
        if not self.is_open[weekday]:
            return
        col_text = self.plan["weekdays"][weekday.name.lower()]["text"]

        lines = re.split("\n+", col_text)
        for l in lines:
            self._parse_column_line(l, weekday)

        self.meal_lines = []  # clean up rest
        self.meal_category_counter = 1

    def _parse_column_line(self, line: str, weekday: Weekday):
        """
        Parses plan lines by column (i.e. by day)
        :param line:
        :return: Exit
        """
        l = self._clean_line(line)

        if len(l) == 0:
            return  # skip line if it i

        if self._is_co2(l):
            return

        if self._is_prices(l):
            category = MealCategory(self.meal_category_counter).name.lower()
            meal_dict = self.plan["weekdays"][weekday.name.lower()]["meals"][category]
            meal_dict["name"] = self._build_meal_name()
            self.meal_lines = []

            prices = self._parse_prices(l)
            meal_dict["prices"] = prices

            self.meal_category_counter += 1
            return

        self.meal_lines.append(l)

    def _parse_line(self, line: str):
        """
        Parses plan lines horizontally.
        :param line:
        :return:
        """
        l = self._clean_line(line)
        if len(l) == 0:
            return  # skip line if it i

        if MealCategory.is_meal_category(l):
            self.current_category = MealCategory.from_str(l)
            # if new weekday is found, go to monday again
            self._reset_weekday()
            return

        if self._is_co2(l):  # skip co2 lines for the time being
            return

        if self._is_prices(l):
            # price is last row of meal, so write all meal data to plan
            meal_dict = self._get_current_meal()
            meal_dict["name"] = self._build_meal_name()
            self.meal_lines = []

            prices = self._parse_prices(l)
            meal_dict["prices"] = prices
            return

        # else: it is part of the meal name =)
        self.meal_lines.append(l)

    def _next_weekday(self):
        # check whether mensa is opened on next day
        opened = False
        while not opened:
            self.meal_weekday_counter += 1

            if self.meal_weekday_counter > Weekday.FRIDAY.value:  # 6 or larger
                self.meal_weekday_counter = 1

            opened = self.is_open[Weekday(self.meal_weekday_counter)]

    def _reset_weekday(self):
        self.meal_weekday_counter = 1
        opened = self.is_open[Weekday(self.meal_weekday_counter)]
        if not opened:
            self._next_weekday()

    def _parse_week(self, line: str):
        l = line.strip()
        dates = l.split(" ")  # not - because a weird code point is used in the pdf
        from_date = datetime.strptime(dates[0], "%d.%m.")
        until_date = datetime.strptime(dates[2], "%d.%m.%Y")

        if until_date.month < from_date.month:
            from_date = from_date.replace(year=until_date.year - 1)  # new year
        else:
            from_date = from_date.replace(year=until_date.year)

        for i in range(5):
            self.plan["weekdays"][
                Weekday.name_from_value(self.meal_weekday_counter)][
                "date"] = from_date.strftime("%Y-%m-%d")
            self.meal_weekday_counter += 1
            from_date = from_date + timedelta(days=1)

        self.meal_weekday_counter = 1

    def _get_current_meal(self) -> dict:
        """
        Returns a reference to the current meal.
        :return:
        """
        weekday = Weekday.name_from_value(self.meal_weekday_counter)
        category = self.current_category.name.lower()
        return self.plan["weekdays"][weekday]["meals"][category]

    def _clean_line(self, line: str) -> str:
        l = line.strip()  # strip whitespace
        return l

    def _build_meal_name(self) -> str:
        meal_name = ""

        for i in range(len(self.meal_lines)):
            meal_name += self.meal_lines[i] + " "

        meal_name = self._remove_allergens(meal_name)
        # remove duplicate whitespaces
        meal_name = re.sub("\s+", " ", meal_name)
        # if the next word begins with an uppercase letter, the - is part of
        # the word and should be kept
        meal_name = re.sub("- ([A-Z])", "-\g<1>", meal_name)
        # if the next word begins with a lowercase letter, the - is used for
        # hyphenation and thus should be removed
        meal_name = re.sub("- ([a-z])", "\g<1>", meal_name)
        meal_name = re.sub(" ,", ",", meal_name)  # remove space before comma
        meal_name = re.sub(",[^ ]", ",", meal_name)  # add space after comma
        meal_name = meal_name.strip()  # strip remaining whitespace
        return meal_name

    def _remove_allergens(self, line: str) -> str:
        parentheses_re = "\(.*?\)"  # ? == greedy match
        return re.sub(parentheses_re, "", line)

    def _is_co2(self, line: str) -> bool:
        l = line.lower()
        return "co2 pro" in l

    def _is_prices(self, line: str) -> bool:
        """
        only price lines contain a pipe '|'
        :param line:
        :return:
        """
        return "|" in line  #

    def _parse_prices(self, line: str) -> dict:
        p = {}
        split = line.split(" | ")
        p["students"] = split[0]
        p["employees"] = split[1]
        p["others"] = split[2]
        return p


class MensaNordParser(MensaParserIntf):
    def __init__(self):
        # @TODO SKIP EMPTY DAYS
        self.plan = {"weekdays": {}, "adapter_meals": []}



        for w in Weekday:
            weekdayname = w.name.lower()
            self.plan["weekdays"][weekdayname] = {"date": "",
                                                  "meals": {}}  # add weekdays to plan

            for cat in MealCategory:  # add meal categories to weekdays
                if cat is MealCategory.NONE:
                    continue
                categoryname = cat.name.lower()
                self.plan["weekdays"][weekdayname]["meals"][categoryname] = {}

        self.current_category = MealCategory.NONE  # MealCategory
        self.meal_weekday_counter = 1  # counts category of meal
        self.meal_category_counter = 1
        self.meal_lines = []

        # used to check whether mensa is open at a specific weekday
        self.is_open = {}
        for w in Weekday:
            self.is_open[w] = True

    def _init_mensa_opened(self, page: fitz.Page):
        col_h = 380
        col_w = 125
        col_top = 85
        col_bot = col_top + col_h

        rects = {
            Weekday.MONDAY: fitz.Rect(185, col_top, 185 + col_w, col_bot),
            Weekday.TUESDAY: fitz.Rect(305, col_top, 305 + col_w, col_bot),
            Weekday.WEDNESDAY: fitz.Rect(430, col_top, 430 + col_w, col_bot),
            Weekday.THURSDAY: fitz.Rect(555, col_top, 555 + col_w, col_bot),
            Weekday.FRIDAY: fitz.Rect(675, col_top, 675 + col_w, col_bot),
        }

        # if empty column is found, mensa is closed for that day
        for day in rects:
            found_text = page.get_text("text", clip=rects[day])
            # found_text = page.get_textbox(rects[day])
            if len(found_text) < 100:
                self.is_open[day] = False
            else:
                self.plan["weekdays"][day.name.lower()]["text"] = found_text


    def _parse_weekday_date(self, line: str):
        l = line.strip()
        dates = l.split(" ")  # not - because a weird code point is used in the pdf
        from_date = datetime.strptime(dates[0], "%d.%m.")
        until_date = datetime.strptime(dates[2], "%d.%m.%Y")

        if until_date.month < from_date.month:
            from_date = from_date.replace(year=until_date.year - 1)  # new year
        else:
            from_date = from_date.replace(year=until_date.year)

        for i in range(5):
            self.plan["weekdays"][
                Weekday.name_from_value(self.meal_weekday_counter)][
                "date"] = from_date.strftime("%Y-%m-%d")
            self.meal_weekday_counter += 1
            from_date = from_date + timedelta(days=1)

        self.meal_weekday_counter = 1

    def parse_plan(self, page: fitz.Page):
        self._init_mensa_opened(page)
        plan_source = page.get_text()
        lines = plan_source.split("\n")
        self._parse_weekday_date(lines[0])


