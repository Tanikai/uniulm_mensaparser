from enum import Enum
from dataclasses import dataclass, field
from .utils import date_format_iso, get_monday
from datetime import datetime

legend = {
    "S": "Schwein",
    "R": "Rind",
    "G": "Geflügel",
    "1": "Farbstoff",
    "2": "Konservierungsstoff",
    "3": "Antioxidationsmittel",
    "4": "Geschmacksverstärker",
    "5": "geschwefelt",
    "6": "geschwärzt",
    "7": "gewachst",
    "8": "Phosphat",
    "9": "Süßungsmitteln",
    "10": "Phenylalani",
    "13": "Krebstieren",
    "14": "Ei",
    "22": "Erdnuss",
    "23": "Soja",
    "24": "Milch/Milchprodukte",
    "25": "Schalenfrucht (alle Nussarten)",
    "26": "Sellerie",
    "27": "Senf",
    "28": "Sesamsamen",
    "29": "Schwefeldioxid",
    "30": "Sulfit",
    "31": "Lupine",
    "32": "Weichtiere",
    "34": "Gluten",
    "35": "Fisch",
}


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

    def to_fs_str(self):
        if self == self.UL_UNI_Sued:
            return "Mensa"
        elif self == self.UL_UNI_West:
            return "West"
        else:
            return ""


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
    week_number: int = -1  # can be derived from the date but included for easier use of data
    price_students: str = ""
    price_employees: str = ""
    price_others: str = ""
    price_note: str = ""
    canteen: Canteen = Canteen.NONE
    allergy_ids: set = field(default_factory=set)  # e.g. 26, 34W, 27
    types: list[str] = field(default_factory=list) # vegetarian / vegan / etc. -> parsed from used icon
    co2: str = ""
    nutrition: MealNutrition = field(default_factory=MealNutrition)


@dataclass
class Plan:
    canteen: Canteen = Canteen.NONE
    url: str = ""
    week: str = ""
    opened_days: dict[str, bool] = field(default_factory=dict)
    meals: list[Meal] = field(default_factory=list)
    first_date: datetime = 0


@dataclass
class MaxmanagerRequest:
    func: str = "make_spl"
    locId: int = 1  # 1 is Mensa Süd
    date: datetime = datetime.now()
    lang: str = "de"
    startThisWeek: datetime = get_monday()
    startNextWeek: datetime = get_monday(1)

    def generate_request_dictionary(self):
        return {
            "func": self.func,
            "locId": str(self.locId),
            "date": date_format_iso(self.date),
            "lang": self.lang,
            "startThisWeek": date_format_iso(self.startThisWeek),
            "startNextWeek": date_format_iso(self.startNextWeek),
        }
