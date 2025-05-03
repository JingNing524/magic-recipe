#Interactive Recipe Manager


import json
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from collections import defaultdict

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

    def update_servings(self, new_servings):
        if new_servings <= 0:
            print("New servings must be greater than 0.")
            return
        factor = new_servings / self.servings
        for ing in self.ingredients:
            ing.quantity *= factor
        self.servings = new_servings

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
                "image_path": r.image_path,
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

    def add_recipe(self, recipe):
        self.recipes.append(recipe)

    def remove_recipe(self, recipe_title):
        self.recipes = [r for r in self.recipes if r.title.lower() != recipe_title.lower()]

    def search_recipes(self, query):
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

class ShoppingListGenerator:
    def generate_list(self, recipes):
        shopping_list = defaultdict(lambda: defaultdict(float))
        for recipe in recipes:
            for ing in recipe.ingredients:
                shopping_list[ing.name][ing.unit] += ing.quantity
        formatted_list = []
        for name, units in shopping_list.items():
            for unit, qty in units.items():
                formatted_list.append(f"{qty:.2f} {unit} {name}")
        return formatted_list

class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Manager")
        self.manager = RecipeManager()
        self.planner = MealPlanner()
        self.shopper = ShoppingListGenerator()

        self.setup_gui()
        self.manager.load_from_file()
        self.refresh_recipe_list()

    def setup_gui(self):
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        self.recipe_listbox = tk.Listbox(self.main_frame, height=10)
        self.recipe_listbox.grid(row=0, column=0, rowspan=6, padx=10)
        self.recipe_listbox.bind('<<ListboxSelect>>', self.display_recipe)

        ttk.Button(self.main_frame, text="Add Recipe", command=self.add_recipe).grid(row=0, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Plan Meal", command=self.plan_meal).grid(row=1, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="View Meal Plan", command=self.view_plan).grid(row=2, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Shopping List", command=self.generate_shopping_list).grid(row=3, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Exit", command=self.root.quit).grid(row=4, column=1, sticky="ew")

        self.recipe_text = tk.Text(self.main_frame, width=70, height=25)
        self.recipe_text.grid(row=6, column=0, columnspan=2, pady=(10, 0))

    def refresh_recipe_list(self):
        self.recipe_listbox.delete(0, tk.END)
        for r in self.manager.recipes:
            self.recipe_listbox.insert(tk.END, r.title)

    def add_recipe(self):
        title = simpledialog.askstring("Title", "Recipe title:")
        if not title:
            return
        if any(r.title.lower() == title.lower() for r in self.manager.recipes):
            messagebox.showerror("Error", "Recipe title already exists.")
            return
        desc = simpledialog.askstring("Description", "Description:")
        servings = simpledialog.askinteger("Servings", "Servings:")
        cuisine = simpledialog.askstring("Cuisine", "Cuisine type:")
        category = simpledialog.askstring("Category", "Meal category:")

        if not all([desc, servings, cuisine, category]):
            messagebox.showerror("Error", "Missing required fields.")
            return

        recipe = Recipe(title, desc, servings, cuisine, category)

        while messagebox.askyesno("Ingredient", "Add ingredient?"):
            name = simpledialog.askstring("Ingredient", "Name:")
            qty = simpledialog.askfloat("Ingredient", "Quantity:")
            unit = simpledialog.askstring("Ingredient", "Unit:")
            if name and qty and unit:
                recipe.add_ingredient(Ingredient(name, qty, unit))

        while messagebox.askyesno("Step", "Add step?"):
            step = simpledialog.askstring("Step", "Description:")
            if step:
                recipe.add_step(step)

        self.manager.add_recipe(recipe)
        self.refresh_recipe_list()

    def display_recipe(self, event):
        selected = self.recipe_listbox.curselection()
        if not selected:
            return
        index = selected[0]
        recipe = self.manager.recipes[index]
        self.recipe_text.delete(1.0, tk.END)
        self.recipe_text.insert(tk.END, f"\U0001F4CB {recipe.title}\n")
        self.recipe_text.insert(tk.END, f"{recipe.description}\n\n")
        self.recipe_text.insert(tk.END, f"Servings: {recipe.servings} | Cuisine: {recipe.cuisine} | Category: {recipe.category}\n")
        self.recipe_text.insert(tk.END, "\n\U0001F9C2 Ingredients:\n")
        for i in recipe.ingredients:
            self.recipe_text.insert(tk.END, f" - {i.display()}\n")
        self.recipe_text.insert(tk.END, "\n\U0001F469\u200D\U0001F33E\U0001F373 Steps:\n")
        for idx, s in enumerate(recipe.steps, 1):
            self.recipe_text.insert(tk.END, f"{idx}. {s}\n")
        if recipe.rating is not None:
            self.recipe_text.insert(tk.END, f"\nRating: {recipe.rating}/5\n")
        if recipe.notes:
            self.recipe_text.insert(tk.END, f"Notes: {recipe.notes}\n")

    def plan_meal(self):
        if not self.manager.recipes:
            messagebox.showinfo("Info", "No recipes to plan.")
            return
        date = simpledialog.askstring("Plan Meal", "Enter date (YYYY-MM-DD):")
        title = simpledialog.askstring("Plan Meal", "Enter recipe title:")
        recipe = next((r for r in self.manager.recipes if r.title.lower() == title.lower()), None)
        if recipe:
            self.planner.add_meal(date, recipe)
            messagebox.showinfo("Planned", f"Added {title} to {date}")
        else:
            messagebox.showerror("Not found", "Recipe not found.")

    def view_plan(self):
        date = simpledialog.askstring("View Meal Plan", "Enter date (YYYY-MM-DD):")
        meals = self.planner.get_meals_for_date(date)
        if not meals:
            messagebox.showinfo("Meal Plan", "No meals planned.")
            return
        info = f"\U0001F4C5 {date}:\n" + "\n".join(f" - {r.title}" for r in meals)
        messagebox.showinfo("Meal Plan", info)

    def generate_shopping_list(self):
        date = simpledialog.askstring("Shopping List", "Enter date (YYYY-MM-DD):")
        meals = self.planner.get_meals_for_date(date)
        if not meals:
            messagebox.showinfo("List", "No meals planned.")
            return
        items = self.shopper.generate_list(meals)
        self.recipe_text.delete(1.0, tk.END)
        self.recipe_text.insert(tk.END, f"\U0001F6D2 Shopping List for {date}\n\n")
        for item in items:
            self.recipe_text.insert(tk.END, f" - {item}\n")

    def on_close(self):
        self.manager.save_to_file()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
















