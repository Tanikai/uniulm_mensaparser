from .pdf_parser import MealCategory

# Strategy Pattern


class PlanAdapter:
    """
    Abstract class for Mensa Plan adapter.
    """
    def convert_plans(self, plans: []) -> dict:
        pass


class FsEtAdapter(PlanAdapter):

    """
    Plan adapter for Fachschaft Elektrotechnik.
    See https://mensaplan.fs-et.de/data/mensaplan.json for JSON layout.
    """
    def convert_plans(self, plans: []) -> dict:
        result = {"weeks": []}

        for p in plans:
            pass

        return result


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
