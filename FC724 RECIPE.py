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
        self.ingredients = ingredients if ingredients else []   #If the user gives ingredients, use them. If not, use an empty list.
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

    #adjusts the ingredient quantities to match the new serving
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



import json

class RecipeManager:
    def __init__(self):
        self.recipes = []

    def to_dict(self):
        return [
            {
                "title": r.title,
                "description": r.description,
                "servings": r.servings,
                "cuisine": r.cuisine,
                "category": r.category,
                "ingredients": [
                    {"name": i.name, "quantity": i.quantity, "unit": i.unit}
                    for i in r.ingredients
                ],
                "steps": r.steps,
                "rating": r.rating,
                "notes": r.notes,
                "image_path": r.image_path
            }
            for r in self.recipes
        ]

    def from_dict(self, data):
        for r in data:
            recipe = Recipe(
                r["title"], r["description"], r["servings"],
                r["cuisine"], r["category"],
                rating=r.get("rating"),
                notes=r.get("notes"),
                image_path=r.get("image_path")
            )
            for ing in r["ingredients"]:
                recipe.add_ingredient(Ingredient(ing["name"], ing["quantity"], ing["unit"]))
            for step in r["steps"]:
                recipe.add_step(step)
            self.add_recipe(recipe)

    def save_to_file(self, filename="recipes.json"):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_file(self, filename="recipes.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.from_dict(data)
        except FileNotFoundError:
            pass

class MealPlanner:
    def __init__(self):
        self.planned_meals = defaultdict(list)

    def add_meal(self, date, recipe):
        self.planned_meals[date].append(recipe)

    def remove_meal(self, date, recipe_title):
        self.planned_meals[date] = [
            r for r in self.planned_meals[date] if r.title.lower() != recipe_title.lower()
        ]
        if not self.planned_meals[date]:
            del self.planned_meals[date]

    def get_meals_for_date(self, date):
        return self.planned_meals.get(date, [])

    def display_schedule(self):
        for date, recipes in sorted(self.planned_meals.items()):
            print(f"\n📅 {date}:")
            for recipe in recipes:
                print(f" - {recipe.title}")

    def to_dict(self):
        return {
            date: [
                {
                    "title": r.title,
                    "description": r.description,
                    "servings": r.servings,
                    "cuisine": r.cuisine,
                    "category": r.category,
                    "ingredients": [
                        {"name": i.name, "quantity": i.quantity, "unit": i.unit} for i in r.ingredients
                    ],
                    "steps": r.steps,
                    "rating": r.rating,
                    "notes": r.notes,
                    "image_path": r.image_path
                }
                for r in recipes
            ]
            for date, recipes in self.planned_meals.items()
        }

    def from_dict(self, data):
        for date, recipe_list in data.items():
            for r in recipe_list:
                recipe = Recipe(
                    r["title"], r["description"], r["servings"],
                    r["cuisine"], r["category"],
                    rating=r.get("rating"),
                    notes=r.get("notes"),
                    image_path=r.get("image_path")
                )
                for ing in r["ingredients"]:
                    recipe.add_ingredient(Ingredient(ing["name"], ing["quantity"], ing["unit"]))
                for step in r["steps"]:
                    recipe.add_step(step)
                self.add_meal(date, recipe)

    def save_to_file(self, filename="mealplan.json"):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_file(self, filename="mealplan.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.from_dict(data)
        except FileNotFoundError:
            pass



    def on_close(self):
        try:
            self.manager.save_to_file()
            self.planner.save_to_file()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
        finally:
            self.root.quit()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    app.planner.load_from_file()
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
