from .models import Meal, MultiCanteenPlan
from abc import abstractmethod
from .utils import date_format_iso


# Strategy Pattern
class PlanAdapter:
    """
    Interface for Mensa Plan adapter.
    """

    @abstractmethod
    def convert_plans(self, plan: MultiCanteenPlan) -> dict:
        pass


class SimpleAdapter2(PlanAdapter):
    def convert_plans(self, plan: MultiCanteenPlan) -> dict:
        result = {}

        for canteen, daily_meal_dict in plan.items():
            canteen_name = canteen.name.lower()
            result[canteen_name] = {}

            for meals_date, meals in daily_meal_dict.items():
                date_formatted = date_format_iso(meals_date)
                result[canteen_name][date_formatted] = []

                for m in meals:
                    self._add_meal(result, canteen_name, date_formatted, m)

        return result

    @staticmethod
    def _add_meal(result: dict, canteen_name: str, date: str, meal: Meal):
        result[canteen_name][date].append(
            {
                "name": meal.name,
                "category": meal.category,
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
