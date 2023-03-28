from enum import Enum
from dataclasses import dataclass

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
