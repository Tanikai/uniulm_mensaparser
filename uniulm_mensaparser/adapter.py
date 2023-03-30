from .models import MealCategory, Meal
from abc import abstractmethod

# Strategy Pattern


class PlanAdapter:
    """
    Abstract class for Mensa Plan adapter.
    """

    @abstractmethod
    def convert_plans(self, plans: []) -> dict:
        pass


class FsEtAdapter(PlanAdapter):
    """
    Plan adapter for Fachschaft Elektrotechnik.
    See https://mensaplan.fs-et.de/data/mensaplan.json for JSON layout.
    """

    def convert_plans(self, plans: []) -> dict:
        result = {"weeks": []}

        all_meals = []
        # iterate over every pdf file plan
        for p in plans:
            all_meals.extend(p["parsed"]["adapter_meals"])

        for m in all_meals:
            self._add_meal(result, m)

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

        meal_dict = {
            "category": MealCategory.pretty_print(str(meal.category)),
            "meal": meal.name,
            "price": f"{meal.price_students} | {meal.price_employees} | {meal.price_others}"
        }
        canteen = meal.canteen.to_fs_str()
        if canteen not in day:
            day[canteen] = {
                "meals": [],
                "open": True
            }

        day[canteen]["meals"].append(meal_dict)


class SimpleAdapter(PlanAdapter):

    def convert_plans(self, plans: []) -> dict:
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
                    if ("name" not in current_meal) or \
                            ("prices" not in current_meal):
                        continue
                    out = {
                        "name": current_meal["name"],
                        "category": MealCategory.pretty_print(
                            meal_category),
                        "prices": dict(current_meal["prices"]),
                    }
                    mensa_dict[date].append(out)

        return result
