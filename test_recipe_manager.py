import unittest
from recipe import Recipe, Ingredient
from manager import RecipeManager, MealPlanner, ShoppingListGenerator

class TestRecipeManager(unittest.TestCase):

    def setUp(self):
        self.manager = RecipeManager()
        self.recipe = Recipe(
            title="Test Recipe",
            description="A test recipe",
            servings=2,
            cuisine="Test Cuisine",
            category="Test",
            ingredients=[
                Ingredient(name="Flour", quantity=1, unit="kg", cost_per_unit=2.0),
                Ingredient(name="Sugar", quantity=0.5, unit="kg", cost_per_unit=1.5)
            ],
            steps=["Mix ingredients", "Bake for 20 minutes"],
            total_cost=5.0
        )
        self.manager.add_recipe(self.recipe)

    def test_add_recipe(self):
        self.assertIn(self.recipe, self.manager.recipes)

    def test_get_recipe_by_title(self):
        found = self.manager.get_recipe_by_title("Test Recipe")
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Test Recipe")

class TestMealPlanner(unittest.TestCase):

    def setUp(self):
        self.recipe = Recipe(
            title="Planned Recipe",
            description="For planning",
            servings=1,
            cuisine="Test",
            category="Meal",
            ingredients=[],
            steps=[],
            total_cost=0
        )
        self.manager = RecipeManager()
        self.manager.add_recipe(self.recipe)
        self.planner = MealPlanner(recipe_manager=self.manager)
        self.planner.add_meal("2025-05-10", self.recipe)

    def test_meal_plan_storage(self):
        meals = self.planner.get_meals_for_date("2025-05-10")
        self.assertIn(self.recipe, meals)


class TestShoppingListGenerator(unittest.TestCase):

    def test_generate_list_output(self):
        recipe = Recipe(
            title="Shopping Test",
            description="",
            servings=1,
            cuisine="",
            category="",
            ingredients=[Ingredient(name="Rice", quantity=1, unit="kg", cost_per_unit=2)],
            steps=[],
            total_cost=2.0
        )
        generator = ShoppingListGenerator(recipe_manager=None)
        result = generator.generate_list([recipe])
        self.assertIn("1.00 kg Rice", result)

if __name__ == "__main__":
    unittest.main()

