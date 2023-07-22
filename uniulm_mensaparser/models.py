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


class MealCategory(Enum):
    @staticmethod
    def from_str(label: str):
        cleaned_label = (
            label.lower().strip().replace("_", " ")
        )  # all smallercase and trim whitespace
        if "fleisch" in cleaned_label:
            return DefaultMealCategory.FLEISCH_UND_FISCH
        elif "prima klima" in cleaned_label:
            return DefaultMealCategory.PRIMA_KLIMA
        elif "sattmacher" in cleaned_label:
            return DefaultMealCategory.SATTMACHER
        elif "topf" in cleaned_label:
            return DefaultMealCategory.TOPF_UND_PFANNE
        elif "extra" in cleaned_label:
            return DefaultMealCategory.EXTRA
        elif "beilagen" in cleaned_label:
            return DefaultMealCategory.BEILAGEN
        elif "salat" in cleaned_label:
            return DefaultMealCategory.SALAT
        elif "desserts" in cleaned_label:
            return DefaultMealCategory.DESSERTS
        elif "pizza iii" in cleaned_label:
            return BistroMealCategory.PIZZA_III
        elif "pizza ii" in cleaned_label:
            return BistroMealCategory.PIZZA_II
        elif "pizza i" in cleaned_label:
            return BistroMealCategory.PIZZA_I
        elif "pasta ii" in cleaned_label:
            return BistroMealCategory.PASTA_II
        elif "pasta i" in cleaned_label:
            return BistroMealCategory.PASTA_I
        else:
            raise ValueError(f"parse error with input {label}")

    @staticmethod
    def pretty_print(value: str):
        cleaned_label = value.lower().strip().replace("_", " ")
        if "fleisch" in cleaned_label:
            return "Fleisch und Fisch"
        elif "prima klima" in cleaned_label:
            return "Prima Klima"
        elif "sattmacher" in cleaned_label:
            return "Sattmacher"
        elif "topf" in cleaned_label:
            return "Topf und Pfanne"
        elif "extra" in cleaned_label:
            return "Extra"
        elif "beilagen" in cleaned_label:
            return "Beilagen"
        elif "salat" in cleaned_label:
            return "Salat"
        elif "desserts" in cleaned_label:
            return "Desserts"
        elif "pizza iii" in cleaned_label:
            return "Pizza III"
        elif "pizza ii" in cleaned_label:
            return "Pizza II"
        elif "pizza i" in cleaned_label:
            return "Pizza I"
        elif "pasta ii" in cleaned_label:
            return "Pasta II"
        elif "pasta i" in cleaned_label:
            return "Pasta I"
        else:
            return ""

    @staticmethod
    def is_meal_category(line: str) -> bool:
        try:
            MealCategory.from_str(line)
            return True
        except ValueError:
            return False


class DefaultMealCategory(MealCategory):
    NONE = 0
    FLEISCH_UND_FISCH = 1
    PRIMA_KLIMA = 2
    SATTMACHER = 3
    TOPF_UND_PFANNE = 4
    EXTRA = 5
    BEILAGEN = 6
    SALAT = 7
    DESSERTS = 8


class BistroMealCategory(MealCategory):
    NONE = 0
    PIZZA_I = 1
    PIZZA_II = 2
    PIZZA_III = 3
    PASTA_I = 4
    PASTA_II = 5


class Canteen(Enum):
    NONE = 0
    UL_UNI_Sued = 1
    UL_UNI_Nord = 2
    UL_UNI_Helmholtz = 3
    UL_UNI_West = 4

    def __str__(self):
        return ""

    def meal_category_order(self):
        if self == self.UL_UNI_Sued:
            return [
                DefaultMealCategory.PRIMA_KLIMA,
                DefaultMealCategory.TOPF_UND_PFANNE,
                DefaultMealCategory.FLEISCH_UND_FISCH,
                DefaultMealCategory.SATTMACHER,
                DefaultMealCategory.EXTRA,
            ]
        elif self == self.UL_UNI_West:
            return [
                DefaultMealCategory.PRIMA_KLIMA,
                DefaultMealCategory.TOPF_UND_PFANNE,
                DefaultMealCategory.FLEISCH_UND_FISCH,
                DefaultMealCategory.SATTMACHER,
                DefaultMealCategory.EXTRA,
            ]
        elif self == self.UL_UNI_Nord:
            return [
                BistroMealCategory.PIZZA_I,
                BistroMealCategory.PIZZA_II,
                BistroMealCategory.PIZZA_III,
                BistroMealCategory.PASTA_I,
                BistroMealCategory.PASTA_II,
            ]
        else:
            return []

    def get_maxmanager_id(self) -> int:
        if self == self.UL_UNI_Sued:
            return 1
        if self == self.UL_UNI_West:
            return 2
        else:
            return -1

    @staticmethod
    def from_str(label: str):
        cleaned_label = label.lower().strip()  # all smallercase and trim whitespace
        if "ul uni mensa süd" in cleaned_label:
            return Canteen.UL_UNI_Sued
        elif "ul uni nord" in cleaned_label:
            return Canteen.UL_UNI_Nord
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
        elif self == self.UL_UNI_Nord:
            return "Bistro"
        elif self == self.UL_UNI_West:
            return "West"
        else:
            return ""


@dataclass
class Meal:
    name: str = ""
    category: MealCategory = DefaultMealCategory.NONE
    date: str = ""
    week_number: int = -1
    price_students: str = ""
    price_employees: str = ""
    price_others: str = ""
    canteen: Canteen = Canteen.NONE
    allergy: str = ""
    type: str = ""  # vegetarian / vegan / etc.


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
