from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List

from .utils import date_format_iso, get_monday


class Weekday(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5

    @staticmethod
    def name_from_value(val: int) -> str:
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


class Canteen(Enum):
    NONE = 0
    UL_UNI_Sued = 1
    # UL_UNI_Nord = 2 # not a canteen anymore
    UL_UNI_Helmholtz = 16
    UL_UNI_West = 4

    def __str__(self):
        return ""

    def get_maxmanager_id(self) -> int:
        if self == self.UL_UNI_Sued:
            return 1
        if self == self.UL_UNI_West:
            return 2
        if self == self.UL_UNI_Helmholtz:
            return 3
        else:
            return -1

    @staticmethod
    def from_str(label: str):
        cleaned_label = label.lower().strip()  # all smallercase and trim whitespace
        if "ul uni mensa süd" in cleaned_label:
            return Canteen.UL_UNI_Sued
        elif "ul uni helmholtz" in cleaned_label:
            return Canteen.UL_UNI_Helmholtz
        elif "ul uni west" in cleaned_label:
            return Canteen.UL_UNI_West
        elif "ulm universitaet mensa uni sued" in cleaned_label:
            return Canteen.UL_UNI_Sued
        elif "ulm universitaet cafeteria uni west" in cleaned_label:
            return Canteen.UL_UNI_West
        else:
            raise NotImplementedError("Unknown Canteen:" + cleaned_label)


class MealType(str, Enum):
    NONE = "none"
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    PORK = "pork"
    BEEF = "beef"
    POULTRY = "poultry"
    FISH = "fish"
    LAMB = "lamb"
    GAME = "game"
    BIO = "bio"

    @staticmethod
    def from_filename_str(filename: str):
        cleaned = filename.lower().strip()
        mapping = {
            "van": MealType.VEGAN,
            "veg": MealType.VEGETARIAN,
            "s": MealType.PORK,
            "r": MealType.BEEF,
            "g": MealType.POULTRY,
            "f": MealType.FISH,
            "l": MealType.LAMB,
            "w": MealType.GAME,
            "bio": MealType.BIO,
        }
        return mapping.get(cleaned, MealType.NONE)


@dataclass
class MealNutrition:
    calories: str = ""
    protein: str = ""
    carbohydrates: str = ""
    sugar: str = ""
    fat: str = ""
    saturated_fat: str = ""
    salt: str = ""


@dataclass
class Meal:
    name: str = ""
    category: str = ""
    date: str = ""
    week_number: int = (
        -1
    )  # can be derived from the date but included for easier use of data
    price_students: str = ""
    price_employees: str = ""
    price_others: str = ""
    price_note: str = ""
    canteen: Canteen = Canteen.NONE
    allergy_ids: set = field(default_factory=set)  # e.g. 26, 34W, 27
    types: List[MealType] = field(
        default_factory=list
    )  # vegetarian / vegan / etc. -> parsed from used icon
    co2: str = ""
    nutrition: MealNutrition = field(default_factory=MealNutrition)


@dataclass
class MaxmanagerRequest:
    func: str = "make_spl"
    locId: int = 1  # 1 is Mensa Süd
    date: date = date.today()
    lang: str = "de"  # "de" | "en"
    startThisWeek: date = get_monday()
    startNextWeek: date = get_monday(1)

    def generate_request_dictionary(self):
        return {
            "func": self.func,
            "locId": str(self.locId),
            "date": date_format_iso(self.date),
            "lang": self.lang,
            "startThisWeek": date_format_iso(self.startThisWeek),
            "startNextWeek": date_format_iso(self.startNextWeek),
        }


DailyCanteenMeals = Dict[date, List[Meal]]

MultiCanteenPlan = Dict[Canteen, DailyCanteenMeals]
