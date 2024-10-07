from typing import List
from .models import MealCategory, Meal, Plan
from abc import abstractmethod
from collections import defaultdict


def recursively_default_dict():
    return defaultdict(recursively_default_dict)


# Strategy Pattern


class PlanAdapter:
    """
    Interface for Mensa Plan adapter.
    """

    @abstractmethod
    def convert_plans(self, plans: List[Plan]) -> dict:
        pass


class FsEtAdapter(PlanAdapter):
    """
    Plan adapter for Fachschaft Elektrotechnik.
    See https://mensaplan.fs-et.de/data/mensaplan.json for JSON layout.
    """

    def convert_plans(self, plans: List[Plan]) -> dict:
        result = {"weeks": []}

        for p in plans:
            for m in p.meals:
                self._add_meal(result, m)

            for weekday_str, opened in p.opened_days.items():
                if opened:
                    continue

                self._add_meal(
                    result,
                    Meal(
                        name="[closed]",
                        week_number=int(p.week[2:]),
                        date=weekday_str,
                        canteen=p.canteen,
                    ),
                )

        return result

    def _add_meal(self, fsplan: dict, meal: Meal):
        week = None  # reference
        week_list = fsplan["weeks"]
        for i in range(len(week_list)):  # check if week number already in result
            if week_list[i]["weekNumber"] == meal.week_number:
                week = week_list[i]

        # if not in week_list -> add new week
        if week is None:
            week = {
                "weekNumber": meal.week_number,
                "days": [],
            }
            week_list.append(week)

        day = None
        day_list = week["days"]
        for i in range(len(day_list)):
            if day_list[i]["date"] == meal.date:
                day = day_list[i]
        if day is None:
            day = {
                "date": meal.date,
            }
            day_list.append(day)

        canteen = meal.canteen.to_fs_str()

        # special case to add empty day to plan
        if meal.name == "[closed]":
            day[canteen] = {"meals": [], "open": False}
            return

        meal_dict = {
            "category": MealCategory.pretty_print(str(meal.category)),
            "meal": meal.name,
            "price": f"{meal.price_students} | {meal.price_employees} | {meal.price_others}",
            "price_note": meal.price_note,
            "types": meal.types,
            "allergy": list(meal.allergy_ids),
            "co2": meal.co2,
            "nutrition": {
                "calories": meal.nutrition.calories,
                "protein": meal.nutrition.protein,
                "carbohydrates": meal.nutrition.carbohydrates,
                "sugar": meal.nutrition.sugar,
                "fat": meal.nutrition.fat,
                "saturated_fat": meal.nutrition.saturated_fat,
                "salt": meal.nutrition.salt,
            },
        }
        if canteen not in day:
            day[canteen] = {"meals": [], "open": True}

        day[canteen]["meals"].append(meal_dict)


class SimpleAdapter2(PlanAdapter):
    def convert_plans(self, plans: List[Plan]) -> dict:
        result = recursively_default_dict()

        for p in plans:
            for meal in p.meals:
                self._add_meal(result, meal)

            # add empty days
            for weekday_str, opened in p.opened_days.items():
                if opened:
                    continue
                # if day is not opened: create
                result[p.canteen.name.lower()][weekday_str] = []

        for k, v in result.items():
            result[k] = dict(v)  # convert to normal dict

        return dict(result)

    def _add_meal(self, result: dict, meal: Meal):
        mensa_name = meal.canteen.name.lower()
        result[mensa_name].setdefault(meal.date, [])
        result[mensa_name][meal.date].append(
            {
                "name": meal.name,
                "category": MealCategory.pretty_print(meal.category.name),
                "prices": {
                    "students": meal.price_students,
                    "employees": meal.price_employees,
                    "others": meal.price_others,
                },
                "price_note": meal.price_note,
                "types": meal.types,
                "allergy": list(meal.allergy_ids),
                "co2": meal.co2,
                "nutrition": {
                    "calories": meal.nutrition.calories,
                    "protein": meal.nutrition.protein,
                    "carbohydrates": meal.nutrition.carbohydrates,
                    "sugar": meal.nutrition.sugar,
                    "fat": meal.nutrition.fat,
                    "saturated_fat": meal.nutrition.saturated_fat,
                    "salt": meal.nutrition.salt,
                },
            }
        )


class SimpleAdapter(PlanAdapter):
    def convert_plans(self, plans: [Plan]) -> dict:
        result = {}

        for p in plans:
            mensa_name = p["mensa"].name.lower()
            if mensa_name not in result:
                result[mensa_name] = {}
            mensa_dict = result[mensa_name]
            # TODO: check if parsed is empty or not
            for day in p["parsed"]["weekdays"]:
                day_dict = p["parsed"]["weekdays"][day]
                date = day_dict["date"]

                if date not in mensa_dict:
                    mensa_dict[date] = []

                meals = day_dict["meals"]
                for meal_category in day_dict["meals"]:
                    current_meal = meals[meal_category]
                    if ("name" not in current_meal) or ("prices" not in current_meal):
                        continue
                    out = {
                        "name": current_meal["name"],
                        "category": MealCategory.pretty_print(meal_category),
                        "prices": dict(current_meal["prices"]),
                    }
                    mensa_dict[date].append(out)

        return result
