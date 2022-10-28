import re
import urllib.request
from enum import Enum
import fitz
import requests
from datetime import timedelta, datetime

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
    MONDAY = 1,
    TUESDAY = 2,
    WEDNESDAY = 3,
    THURSDAY = 4,
    FRIDAY = 5,

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
    NONE = 0,
    FLEISCH_UND_FISCH = 1,
    PRIMA_KLIMA = 2,
    SATTMACHER = 3,
    TOPF_UND_PFANNE = 4

    @staticmethod
    def from_str(label: str):
        l = label.lower().strip()  # all smallercase and trim whitespace
        if "fleisch und fisch" in l:
            return MealCategory.FLEISCH_UND_FISCH
        elif "prima klima" in l:
            return MealCategory.PRIMA_KLIMA
        elif "sattmacher" in l:
            return MealCategory.SATTMACHER
        elif "topf und pfanne" in l:
            return MealCategory.TOPF_UND_PFANNE
        else:
            raise ValueError(f"parse error with input {label}")

    @staticmethod
    def is_meal_category(line: str) -> bool:
        try:
            MealCategory.from_str(line)
            return True
        except ValueError:
            return False


class MensaParser():

    def __init__(self):
        self.plan = {"weekdays": {}}
        for w in Weekday:
            weekdayname = w.name.lower()
            self.plan["weekdays"][weekdayname] = {}  # add weekdays to plan

            for cat in MealCategory:  # add meal categories to weekdays
                if cat is MealCategory.NONE:
                    continue
                categoryname = cat.name.lower()
                self.plan["weekdays"][weekdayname][categoryname] = {}

        self.current_category = MealCategory.NONE  # MealCategory
        self.meal_weekday_counter = 1  # counts category of meal
        self.meal_lines = []
        pass

    def parse_plan_from_url(self, pdf_url: str):
        with requests.get(pdf_url) as data:
            document = fitz.open("pdf", data.content)
            text = document[0].get_text()
            return self.parse_plan(text)

    def parse_plan(self, plan_source: str):
        lines = re.split("\n+", plan_source)

        # The plan begins with some date information / meals. We assume that we
        # have the date as it is contained in the pdf URL. This means that we
        # can skip until the "Fleisch und Fisch" category starts.
        meal_reached = False
        date_found = False
        while not meal_reached:
            l = self._clean_line(lines.pop(0))  # remove first item of list

            if not date_found and ("." in l): # date found
                self._parse_week(l)
                date_found = True  # prevent multiple date parsing

            if MealCategory.is_meal_category(l):
                meal_reached = True
                self.current_category = MealCategory.from_str(l)

        # here, we begin with the first meal
        for l in lines:
            self._parse_line(l)

        return self.plan

    def _parse_line(self, line: str):
        l = self._clean_line(line)
        if len(l) == 0:
            return  # skip line if it i

        if MealCategory.is_meal_category(l):
            self.current_category = MealCategory.from_str(l)
            # if new weekday is found, go to monday again
            self.meal_weekday_counter = 1
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

            self.meal_weekday_counter += 1
            return

        # else: it is part of the meal name =)
        self.meal_lines.append(line)

    def _parse_week(self, line: str):
        l = line.strip()
        dates = l.split(" ") # not - because a weird form is used in the pdf
        from_date = datetime.strptime(dates[0], "%d.%m.")
        until_date = datetime.strptime(dates[2], "%d.%m.%Y")

        if until_date.month < from_date.month:
            from_date = from_date.replace(year=until_date.year-1) # new year
        else:
            from_date = from_date.replace(year=until_date.year)

        for i in range(5):
            self.plan["weekdays"][Weekday.name_from_value(self.meal_weekday_counter)]["date"] = from_date.strftime("%Y-%m-%d")
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
        return self.plan["weekdays"][weekday][category]

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
        meal_name = re.sub(" ,", ",", meal_name) # remove space before comma
        meal_name = re.sub(",[^ ]", ",", meal_name) # add space after comma
        meal_name = meal_name.strip() # strip remaining whitespace
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
