from unittest import TestCase
from uniulm_mensaparser.models import MealCategory, BistroMealCategory


class TestModel(TestCase):

    def test_meal_category_enum(self):
        self.assertEqual(BistroMealCategory.PIZZA_II, MealCategory.from_str("pizza ii"))
        self.assertEqual(MealCategory.pretty_print(BistroMealCategory.PIZZA_II.name), "Pizza II")
