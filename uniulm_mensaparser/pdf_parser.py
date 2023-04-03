import re
import fitz
from datetime import timedelta, datetime
from .models import Weekday, DefaultMealCategory, BistroMealCategory, Canteen, Meal
from abc import abstractmethod


class MensaParserIntf:
    @abstractmethod
    def __init__(self, canteen: Canteen):
        pass

    @abstractmethod
    def parse_plan(self, page: fitz.Page) -> [Meal]:
        pass

    @abstractmethod
    def get_opened_days(self) -> dict[str, bool]:
        pass


def parse_date_string(line: str) -> dict[Weekday, str]:
    dates = line.split(" ")  # not '-' because a weird code point is used in the pdf
    offset = 2
    if len(dates) == 1:
        dates = line.split("-")
        offset = 1
    from_date = datetime.strptime(dates[0], "%d.%m.")
    until_date = datetime.strptime(dates[offset], "%d.%m.%Y")

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

    # set dates for weekdays, starting with monday
    for key in wd:
        wd[key] = from_date.strftime("%Y-%m-%d")
        from_date += timedelta(days=1)

    return wd


def get_weekday_dates(pdf_lines: str) -> dict[Weekday, str]:
    lines = re.split("\n+", pdf_lines)

    while len(lines) > 0:
        l = lines.pop(0).strip()  # clean whitespace
        if l == "":
            continue

        if "." in l:  # date found
            return parse_date_string(l)


def clean_line(line: str) -> str:
    l = line.strip()
    return l


def remove_allergens(line: str) -> str:
    parentheses_re = r"\(.*?\)"  # ? == greedy match
    return re.sub(parentheses_re, "", line)


def build_meal_name(meal_lines: [str]) -> str:
    meal_name = " ".join(meal_lines)

    meal_name = remove_allergens(meal_name)
    # remove duplicate whitespaces
    meal_name = re.sub(r"\s+", r" ", meal_name)
    # if the next word begins with an uppercase letter, the - is part of
    # the word and should be kept
    meal_name = re.sub(r"- ([A-Z])", r"-\g<1>", meal_name)
    # if the next word begins with a lowercase letter, the - is used for
    # hyphenation and thus should be removed
    meal_name = re.sub(r"- ([a-z])", r"\g<1>", meal_name)
    meal_name = re.sub(r" ,", r",", meal_name)  # remove space before comma
    meal_name = re.sub(r"(?<=,)(?=\S)", " ", meal_name)  # add space after comma
    meal_name = re.sub(r" , ", r" ", meal_name)  # remove commas without content before or after
    meal_name = meal_name.strip()  # strip remaining whitespace before and after string
    return meal_name


class DefaultMensaParser(MensaParserIntf):

    def __init__(self, canteen: Canteen):
        # @TODO SKIP EMPTY DAYS
        self.plan = []
        self.canteen = canteen

        self.meal_category_counter = 1
        self.meal_lines = []
        self.price_lines = []

        # used to check whether mensa is open at a specific weekday
        self.is_open = {}
        for w in Weekday:
            self.is_open[w] = True

        self.wd = {}  # weekday to date dictionary
        self.weekday_text = {}

    def get_opened_days(self) -> dict[str, bool]:
        open_status = {}
        for weekday, opened in self.is_open.items():
            open_status[self.wd[weekday]] = opened
            
        return open_status

    def _scrape_weekday_column_text(self, page: fitz.Page):
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
                self.weekday_text[day] = found_text

    def parse_plan(self, page: fitz.Page) -> [Meal]:
        self._scrape_weekday_column_text(page)
        self.wd = get_weekday_dates(page.get_text())

        # parse weekday columns
        for day in Weekday:
            self._parse_weekday_column(day)

        return self.plan

    def _parse_weekday_column(self, weekday: Weekday):
        if not self.is_open[weekday]:
            return

        column_text = self.weekday_text[weekday]
        self.meal_lines = []
        self.meal_category_counter = 1

        lines = re.split("\n+", column_text)
        for l in lines:
            self._ingest_column_line(l, weekday)

    def _ingest_column_line(self, line: str, weekday: Weekday):
        """
        Parses plan lines by column (i.e. by day)
        :param line:
        :return: Exit
        """
        l = clean_line(line)

        if len(l) == 0:
            return  # skip line if it i

        if self._is_co2(l):
            return

        if self._is_prices(l):
            prices = self._parse_prices(l)
            self._add_meal(weekday, prices)
            return

        self.meal_lines.append(l)

    def _add_meal(self, weekday: Weekday, prices: dict[str, str]):
        self.plan.append(Meal(
            name=build_meal_name(self.meal_lines),
            category=DefaultMealCategory(self.meal_category_counter),
            date=self.wd[weekday],
            week_number=int(datetime.strptime(self.wd[weekday], "%Y-%m-%d").strftime("%V")),
            price_students=prices["students"],
            price_employees=prices["employees"],
            price_others=prices["others"],
            canteen=self.canteen
        ))
        self.meal_category_counter += 1
        self.meal_lines = []

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
    def __init__(self, canteen: Canteen):
        # @TODO SKIP EMPTY DAYS
        self.plan = []
        self.canteen = canteen

        self.meal_category_counter = 1
        self.meal_lines = []
        self.price_lines = []

        # used to check whether mensa is open at a specific weekday
        self.is_open = {}
        for w in Weekday:
            self.is_open[w] = True

        self.wd = {}  # weekday to date dictionary
        self.weekday_text = {}

        self.first_meal_prices = {}

    def get_opened_days(self) -> dict[str, bool]:
        open_status = {}
        for weekday, opened in self.is_open.items():
            open_status[self.wd[weekday]] = opened

        return open_status

    def _scrape_weekday_column_text(self, page: fitz.Page):
        col_h = 390
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
        for day, r in rects.items():
            found_text = page.get_text("text", clip=r)
            # found_text = page.get_textbox(rects[day])
            if len(found_text) < 100:
                self.is_open[day] = False
            else:
                self.weekday_text[day] = found_text

    def _scrape_first_meal_prices(self, lines: [str]) -> dict:
        cell_reached = False
        prices = ""
        for l in lines:
            if "Pizza I" in l:
                cell_reached = True
                continue
            if not cell_reached:
                continue

            if "€" in l:
                prices += l.strip()
                continue

            break
        return self._parse_prices(prices)

    def _parse_prices(self, prices: str) -> dict[str, str]:
        prices = re.sub(r"[^a-zA-Z0-9.,€ ]", "", prices)  # pdf contains weird codepoint so use allowlist for string
        prices = re.sub(r"\s+", " ", prices)  # remove duplicate whitespace

        split_prices = prices.split(" ")

        p = {
            "students": split_prices[2] + " €",
            "employees": split_prices[5] + " €",
            "others": split_prices[8] + " €",
        }

        return p

    def parse_plan(self, page: fitz.Page) -> [Meal]:
        self._scrape_weekday_column_text(page)
        self.wd = get_weekday_dates(page.get_text())
        lines = re.split("\n+", page.get_text())
        self.first_meal_prices = self._scrape_first_meal_prices(lines)

        for w in Weekday:
            self._parse_weekday_column(w)

        return self.plan

    def _parse_weekday_column(self, weekday: Weekday):
        if not self.is_open[weekday]:
            return

        # setup
        column_text = self.weekday_text[weekday]
        self.meal_lines = []
        self.meal_category_counter = 1
        self.price_found = False

        lines = re.split("\n+", column_text)
        while "Pizza" not in lines[0]:
            lines.pop(0)
        lines.append("placeholder")  # add line at end so that parser can finish last meal
        first_meal = True
        for l in lines:
            l = clean_line(l)
            if first_meal:
                first_meal = self._ingest_first_meal_line(l, weekday)
            else:
                self._ingest_column_line(l, weekday)

    def _ingest_first_meal_line(self, line: str, weekday: Weekday) -> bool:
        self.meal_lines.append(line)
        if "(" in line:  # assume that allergy information is last line
            self._add_meal(weekday, self.first_meal_prices)
            return False

        return True

    def _add_meal(self, weekday: Weekday, prices: dict[str, str]):
        self.plan.append(Meal(
            name=build_meal_name(self.meal_lines),
            category=BistroMealCategory(self.meal_category_counter),
            date=self.wd[weekday],
            week_number=int(datetime.strptime(self.wd[weekday], "%Y-%m-%d").strftime("%V")),
            price_students=prices["students"],
            price_employees=prices["employees"],
            price_others=prices["others"],
            canteen=self.canteen
        ))

        self.meal_category_counter += 1
        self.meal_lines = []
        self.price_lines = []

    def _ingest_column_line(self, line: str, weekday: Weekday):
        """
       Parses plan lines by column (i.e. by day)
       :param line:
       :return: Exit
       """
        l = line
        if l == "":
            return  # skip line if empty

        if self._is_prices(l):
            self.price_found = True
            self.price_lines.append(l)
            return

        if self.price_found:  # price was found, but current line is not a price anymore
            prices = self._parse_prices(" ".join(self.price_lines))
            self._add_meal(weekday, prices)
            self.price_found = False
            # do not return as current line hasn't been parsed

        self.meal_lines.append(l)

    def _is_prices(self, line: str) -> bool:
        return "€" in line
