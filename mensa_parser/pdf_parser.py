import re
from enum import Enum
import fitz
import requests
from datetime import timedelta, datetime
from dataclasses import dataclass

roles = ('student', 'employee', 'other')
weekdays = ('Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday')

legend = {
    'S': "Schwein",
    'R': "Rind",
    'G': "Geflügel",
    '1': "Farbstoff",
    '2': "Konservierungsstoff",
    '3': "Antioxidationsmittel",
    '4': "Geschmacksverstärker",
    '5': "geschwefelt",
    '6': "geschwärzt",
    '7': "gewachst",
    '8': "Phosphat",
    '9': "Süßungsmitteln",
    '10': "Phenylalani",
    '13': "Krebstieren",
    '14': "Ei",
    '22': "Erdnuss",
    '23': "Soja",
    '24': "Milch/Milchprodukte",
    '25': "Schalenfrucht (alle Nussarten)",
    '26': "Sellerie",
    '27': "Senf",
    '28': "Sesamsamen",
    '29': "Schwefeldioxid",
    '30': "Sulfit",
    '31': "Lupine",
    '32': "Weichtiere",
    '34': "Gluten",
    '35': "Fisch"
}


class Weekday(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5

    @staticmethod
    def name_from_value(val: int) -> str:
        w = None
        # sorry
        if val == 1:
            w = Weekday.MONDAY
        elif val == 2:
            w = Weekday.TUESDAY
        elif val == 3:
            w = Weekday.WEDNESDAY
        elif val == 4:
            w = Weekday.THURSDAY
        elif val == 5:
            w = Weekday.FRIDAY
        else:
            raise ValueError(f"{val} is not a valid Weekday")
        return w.name.lower()


class MealCategory(Enum):
    NONE = 0
    FLEISCH_UND_FISCH = 1
    PRIMA_KLIMA = 2
    SATTMACHER = 3
    TOPF_UND_PFANNE = 4
    EXTRA = 5

    @staticmethod
    def from_str(label: str):
        l = label.lower().strip().replace("_", " ")  # all smallercase and trim whitespace
        if "fleisch und fisch" in l:
            return MealCategory.FLEISCH_UND_FISCH
        elif "prima klima" in l:
            return MealCategory.PRIMA_KLIMA
        elif "sattmacher" in l:
            return MealCategory.SATTMACHER
        elif "topf und pfanne" in l:
            return MealCategory.TOPF_UND_PFANNE
        elif "extra" in l:
            return MealCategory.EXTRA
        else:
            raise ValueError(f"parse error with input {label}")

    @staticmethod
    def pretty_print(value: str):
        l = value.upper().strip()
        if "FLEISCH_UND_FISCH" in l:
            return "Fleisch und Fisch"
        elif "PRIMA_KLIMA" in l:
            return "Prima Klima"
        elif "SATTMACHER" in l:
            return "Sattmacher"
        elif "TOPF_UND_PFANNE" in l:
            return "Topf und Pfanne"
        elif "EXTRA" in l:
            return "Extra"
        else:
            return ""

    @staticmethod
    def is_meal_category(line: str) -> bool:
        try:
            MealCategory.from_str(line)
            return True
        except ValueError:
            return False


class Canteens(Enum):
    NONE = 0
    UL_UNI_Sued = 1
    UL_UNI_Nord = 2
    UL_UNI_Helmholtz = 3
    UL_UNI_West = 4

    def __str__(self):
        return ''

    @staticmethod
    def from_str(label: str):
        l = label.lower().strip()  # all smallercase and trim whitespace
        if "ul uni mensa süd" in l:
            return Canteens.UL_UNI_Sued
        elif "ul uni nord" in l:
            return Canteens.UL_UNI_Nord
        elif "ul uni helmholtz" in l:
            return Canteens.UL_UNI_Helmholtz
        elif "ul uni west" in l:
            return Canteens.UL_UNI_West
        else:
            raise NotImplementedError

    def to_fs_str(self):
        if self == self.UL_UNI_Sued:
            return "Mensa"
        elif self == self.UL_UNI_Nord:
            return "Bistro"
        elif self == self.UL_UNI_West:
            return "West"
        else:
            return ""


@dataclass
class Meal:
    name: str
    category: MealCategory
    date: str
    week_number: int
    price_students: str
    price_employees: str
    price_others: str
    canteen: Canteens


class MensaParser():

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

    def parse_plan_from_url(self, pdf_url: str):
        with requests.get(pdf_url) as data:
            document = fitz.open("pdf", data.content)
            text = document[0].get_text()
            self.init_mensa_opened(document[0])
            return self.parse_plan(text)

    def parse_plan_from_file(self, path: str):
        document = fitz.open(filename=path, filetype="pdf")
        text = document[0].get_text()
        self.init_mensa_opened(document[0])
        return self.parse_plan(text)

    def init_mensa_opened(self, page: fitz.Page):
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

    def parse_plan(self, plan_source: str):
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

        # parse weekdays
        for day in Weekday:
            self._parse_weekday(day)

        # convert meals to new format
        new_meals = []

        for d in self.plan["weekdays"]:
            day = self.plan["weekdays"][d]
            for meal_cat in day["meals"]:
                m = day["meals"][meal_cat]
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
                except:
                    pass

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
        dates = l.split(" ")  # not - because a weird form is used in the pdf
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
