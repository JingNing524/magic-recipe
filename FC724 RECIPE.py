#Interactive Recipe Manager


class Ingredient:
    def __init__(self, name, quantity, unit):
        self.name = name
        self.quantity = quantity
        self.unit = unit

    def display(self):
        return f"{self.quantity} {self.unit} {self.name}"

class Recipe:
    def __init__(self, title, description, servings, cuisine, category,
                 ingredients=None, steps=None, rating=None, notes=None, image_path=None):
        self.title = title
        self.description = description
        self.servings = servings
        self.cuisine = cuisine
        self.category = category
        self.ingredients = ingredients if ingredients else []
        self.steps = steps if steps else []
        self.rating = rating
        self.notes = notes
        self.image_path = image_path

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient)

    def remove_ingredient(self, ingredient_name):
        self.ingredients = [
            ing for ing in self.ingredients if ing.name.lower() != ingredient_name.lower()
        ]

    def add_step(self, step):
        self.steps.append(step)

    def remove_step(self, step_number):
        if 0 <= step_number < len(self.steps):
            self.steps.pop(step_number)
        else:
            print("Invalid step number.")

    def update_servings(self, new_servings):
        if new_servings <= 0:
            print("New servings must be greater than 0.")
            return
        factor = new_servings / self.servings
        for ing in self.ingredients:
            ing.quantity *= factor
        self.servings = new_servings

    def display(self):
        print(f"\n--- {self.title} ---")
        print(f"Description: {self.description}")
        print(f"Servings: {self.servings}")
        print(f"Cuisine: {self.cuisine}")
        print(f"Category: {self.category}")
        print("\nIngredients:")
        for ing in self.ingredients:
            print(f" - {ing.display()}")
        print("\nSteps:")
        for idx, step in enumerate(self.steps, 1):
            print(f"{idx}. {step}")
        if self.rating is not None:
            print(f"\nRating: {self.rating}/5")
        if self.notes:
            print(f"Notes: {self.notes}")
        if self.image_path:
            print(f"Image Path: {self.image_path}")


class RecipeManager:
    def __init__(self):
        self.recipes = []

    def add_recipe(self, recipe):
        self.recipes.append(recipe)

    def remove_recipe(self, recipe_title):
        self.recipes = [r for r in self.recipes if r.title.lower() != recipe_title.lower()]

    def search_recipes(self, query):
        """Search by title or ingredient name"""
        query = query.lower()
        results = []
        for recipe in self.recipes:
            if query in recipe.title.lower():
                results.append(recipe)
            elif any(query in ing.name.lower() for ing in recipe.ingredients):
                results.append(recipe)
        return results

    def filter_recipes(self, cuisine=None, category=None, rating=None):
        results = self.recipes
        if cuisine:
            results = [r for r in results if r.cuisine.lower() == cuisine.lower()]
        if category:
            results = [r for r in results if r.category.lower() == category.lower()]
        if rating:
            results = [r for r in results if r.rating and r.rating >= rating]
        return results

    def display_all_recipes(self):
        if not self.recipes:
            print("No recipes found.")
        else:
            print("Recipes:")
            for i, recipe in enumerate(self.recipes, 1):
                print(f"{i}. {recipe.title}")


from collections import defaultdict



class MealPlanner:
    def __init__(self):
        self.planned_meals = defaultdict(list)  # date: [Recipe, Recipe...]

    def add_meal(self, date, recipe):
        """Adds a recipe to a specific date (date should be a string or datetime object)."""
        self.planned_meals[date].append(recipe)

    def remove_meal(self, date, recipe_title):
        """Removes a recipe by title from the date's meal list."""
        self.planned_meals[date] = [
            r for r in self.planned_meals[date] if r.title.lower() != recipe_title.lower()
        ]
        if not self.planned_meals[date]:  # clean up if empty
            del self.planned_meals[date]

    def get_meals_for_date(self, date):
        return self.planned_meals.get(date, [])

    def display_schedule(self):
        for date, recipes in sorted(self.planned_meals.items()):
            print(f"\n📅 {date}:")
            for recipe in recipes:
                print(f" - {recipe.title}")
                




flour = Ingredient("flour", 2, "cups")
sugar = Ingredient("sugar", 1, "cup")

cake = Recipe(
    title="Simple Cake",
    description="A quick and easy cake recipe.",
    servings=4,
    cuisine="American",
    category="Dessert"
)


cake.add_ingredient(flour)
cake.add_ingredient(sugar)
cake.add_step("Preheat the oven to 350°F (175°C).")
cake.add_step("Mix all ingredients together.")
cake.add_step("Pour into a pan and bake for 30 minutes.")

cake.display()




manager = RecipeManager()


manager.add_recipe(cake)  


manager.display_all_recipes()


results = manager.search_recipes("cake")
for r in results:
    r.display()


filtered = manager.filter_recipes(cuisine="American")
for r in filtered:
    r.display()


planner = MealPlanner()
planner.add_meal("2025-05-01", cake)
planner.display_schedule()


















