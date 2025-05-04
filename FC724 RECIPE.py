#Interactive Recipe Manager


# All necessary imports
import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from collections import defaultdict
from itertools import combinations


# 
class Ingredient:
    def __init__(self, name, quantity, unit, cost_per_unit=0.0):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.cost_per_unit=cost_per_unit

    def display(self):
        return f"{self.quantity} {self.unit} {self.name}"
    
    def total_cost(self):
        quantity = self.quantity if self.quantity is not None else 0
        cost = self.cost_per_unit if self.cost_per_unit is not None else 0
        return quantity * cost
    
    
# Recipe class
class Recipe:
    def __init__(self, title, description, servings, cuisine, category,
                 ingredients=None, steps=None, rating=None, notes=None, image_path=None, total_cost=0.0):
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
        self.total_recipe_cost = total_cost  

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
            return
        factor = new_servings / self.servings
        for ing in self.ingredients:
            ing.quantity *= factor
        self.servings = new_servings

    def cost_per_serving(self):
        return self.total_recipe_cost / self.servings if self.servings else 0

    @classmethod
    def from_dict(cls, data):
        ingredients = [
            Ingredient(i["name"], i["quantity"], i["unit"], i.get("cost_per_unit", 0.0))
            for i in data.get("ingredients", [])
        ]
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            servings=data.get("servings", 1),
            cuisine=data.get("cuisine", ""),
            category=data.get("category", ""),
            ingredients=ingredients,
            steps=data.get("steps", []),
            rating=data.get("rating"),
            notes=data.get("notes"),
            image_path=data.get("image_path"),
            total_cost=data.get("total_cost", 0.0)
        )




    
    
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

# 
class RecipeManager:
    def __init__(self):
        self.recipes = []
        self.load_from_file()
        
    def to_dict(self):
        recipe_dicts = []
        for r in self.recipes:
            recipe_data = {
                "title": r.title,
                "description": r.description,
                "servings": r.servings,
                "cuisine": r.cuisine,
                "category": r.category,
                "ingredients": [
                        {"name": i.name, "quantity": i.quantity, "unit": i.unit, "cost_per_unit": i.cost_per_unit} for i in r.ingredients
                    ],
                "steps": r.steps,
                "total_cost": r.total_recipe_cost

            }
            if r.rating is not None:
                recipe_data["rating"] = r.rating
            if r.notes:
                recipe_data["notes"] = r.notes
            if r.image_path:
                recipe_data["image_path"] = r.image_path
            recipe_dicts.append(recipe_data)
        return recipe_dicts


   
    def from_dict(self, data):
        self.recipes = [Recipe.from_dict(item) for item in data]     

    def save_to_file(self, filename="recipes.json"):
        try:
             with open(filename, "w") as f:
                 json.dump(self.to_dict(), f, indent=4) # Use indent for readability
        except IOError as e:
            print(f"Error saving to {filename}: {e}")

    def load_from_file(self, filename="recipes.json"):
        try:
            with open(filename, "r") as f:
                if os.path.getsize(filename) > 0:
                     data = json.load(f)
                     self.from_dict(data)
                else:
                     self.recipes = []
        except FileNotFoundError:
             self.recipes = []
        except json.JSONDecodeError:
             print(f"Error decoding JSON from {filename}. The file may be corrupted or empty.")
             self.recipes = []
        

    def add_recipe(self, recipe):
        if not any(isinstance(r, Recipe) and r.title and r.title.lower() == recipe.title.lower() for r in self.recipes):

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
    
    def get_all_ingredients_recursive(self, recipe_title, visited=None):
        if visited is None:
            visited = set()

        recipe = next((r for r in self.recipes if r.title == recipe_title), None)
        if not recipe or recipe.title in visited:
            return []

        visited.add(recipe.title)
        collected = []

        for ing in recipe.ingredients:
            
            sub_recipe = next((r for r in self.recipes if r.title == ing.name), None)
            if sub_recipe:
                collected += self.get_all_ingredients_recursive(sub_recipe.title, visited)
            else:
                collected.append(ing)

        return collected

    
    from itertools import combinations

    def select_cheapest_meals(self, target_servings):
        valid_combinations = []

        # try all combinations of 1 to len(recipes) recipes
        for r in range(1, len(self.recipes) + 1):
            for combo in combinations(self.recipes, r):
                total_servings = sum(recipe.servings for recipe in combo)
                if total_servings == target_servings:
                    total_cost = sum(recipe.total_recipe_cost for recipe in combo)
                    valid_combinations.append((combo, total_cost))

        # return the cheapest valid combo, if any
        if valid_combinations:
            best_combo = min(valid_combinations, key=lambda x: x[1])
            return best_combo[0]  # just return the recipes
        return []




    
    def display_all_recipes(self):
        if not self.recipes:
            print("No recipes found.")
        else:
            print("Recipes:")
            for i, recipe in enumerate(self.recipes, 1):
                print(f"{i}. {recipe.title}")
    
    



class MealPlanner:
    def __init__(self, recipe_manager):
        self.planned_meals = defaultdict(list)
        self.load_from_file(recipe_manager)
        self.load_from_file(recipe_manager)
        
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
        return {'planned_meals': {day: [recipe.id for recipe in recipes] for day, recipes in self.planned_meals.items()}}
 




    def from_dict(self, data,recipe_manager):
        self.planned_meals = defaultdict(list)
        for day, recipes in data.get('planned_meals', {}).items():
             self.planned_meals[day] = [recipe_manager.get_recipe_by_id(recipe_id) for recipe_id in recipes if recipe_manager.get_recipe_by_id(recipe_id)]
 

    def save_to_file(self, filename="mealplan.json"):
        try:
             with open(filename, "w") as f:
                 json.dump(self.to_dict(), f, indent=4)
        except IOError as e:
             print(f"Error saving to {filename}: {e}")

    def load_from_file(self, recipe_manager, filename="mealplan.json"):
         try:
             with open(filename, "r") as f:
                 if os.path.getsize(filename) > 0:
                     data = json.load(f)
                     self.from_dict(data, recipe_manager)
                 else:
                     self.planned_meals = defaultdict(list)
         except FileNotFoundError:
             self.planned_meals = defaultdict(list)
         except json.JSONDecodeError:
             print(f"Error decoding JSON from {filename}. The file may be corrupted or empty.")
             self.planned_meals = defaultdict(list)







from collections import defaultdict

#makes sure duplicate ingredients are added together and help to clearify what to buy
class ShoppingListGenerator:
    def __init__(self, recipe_manager):
        self.recipe_manager = recipe_manager
    
    def generate_list(self, recipes):
        from collections import defaultdict
        shopping_list = defaultdict(lambda: defaultdict(float))
        
        for recipe in recipes:
            for ing in recipe.ingredients:
                shopping_list[ing.name][ing.unit] += ing.quantity

        formatted_list = []
        for name, units in shopping_list.items():
            for unit, qty in units.items():
                formatted_list.append(f"{qty:.2f} {unit} {name}")
        return formatted_list



    def display_list(self, shopping_list):
        print("\n🛒 Shopping List:")
        for item in shopping_list:
            print(f" - {item}")

class ShoppingListManager:
    def __init__(self):
        self.list_by_date = {}
        self.load_from_file()

    def save_list(self, date, items):
        self.list_by_date[date] = items

    def get_list(self, date):
        return {'shopping_list': self.list_by_date}

    def to_dict(self):
        return self.list_by_date

    def from_dict(self, data):
        self.list_by_date = data.get('shopping_list', {})

    def save_to_file(self, filename="shoppinglist.json"):
        try:
             with open(filename, "w") as f:
                 json.dump(self.to_dict(), f, indent=4)
        except IOError as e:
             print(f"Error saving to {filename}: {e}")

    def load_from_file(self, filename="shoppinglist.json"):
         try:
             with open(filename, "r") as f:
                 if os.path.getsize(filename) > 0:
                     data = json.load(f)
                     self.from_dict(data)
                 else:
                     self.list_by_date = {}
         except FileNotFoundError:
             self.list_by_date = {}
         except json.JSONDecodeError:
             print(f"Error decoding JSON from {filename}. The file may be corrupted or empty.")
             self.list_by_date = {}



class RecipeApp:
    def __init__(self, master):
        self.root=master
        self.recipe_manager = RecipeManager()
        self.meal_planner = MealPlanner(self.recipe_manager)
        self.shopping_list_manager = ShoppingListManager()
        self.shopper = ShoppingListGenerator(self.recipe_manager)
        
        self.meal_planner.load_from_file(self.recipe_manager)
        
        self.setup_gui()
        self.refresh_recipe_list()
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)
        self.update_recipe_list()
        self.update_meal_plan_display()
        self.update_shopping_list_display()
        
    def load_data(self):
         self.recipe_manager.load_from_file()
         self.meal_planner.load_from_file(self.recipe_manager)
         self.shopping_list_manager.load_from_file()
         self.update_recipe_list()
         self.update_meal_plan_display()
         self.update_shopping_list_display()
 

    def save_data(self):
         self.recipe_manager.save_to_file()
         self.meal_planner.save_to_file()
         self.shopping_list_manager.save_to_file()
 

    def close_application(self):
         self.save_data() 
         self.root.destroy()
     

        

    def setup_gui(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack()

        self.recipe_listbox = tk.Listbox(self.main_frame, height=10)
        self.recipe_listbox.bind("<<ListboxSelect>>", self.display_recipe)
        self.recipe_listbox.grid(row=0, column=0, rowspan=8, padx=10)

        ttk.Button(self.main_frame, text="Add Recipe", command=self.add_recipe).grid(row=0, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Edit Recipe", command=self.edit_recipe).grid(row=1, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Plan Meal", command=self.plan_meal).grid(row=2, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="View Meal Plan", command=self.view_plan).grid(row=3, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Shopping List", command=self.generate_shopping_list).grid(row=4, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Show Full Ingredients", command=self.show_full_ingredients).grid(row=5, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Optimise Meals", command=self.optimise_meal_plan).grid(row=6, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Exit", command=self.on_close).grid(row=7, column=1, sticky="ew")

        self.recipe_text = tk.Text(self.main_frame, width=70, height=25)
        self.recipe_text.grid(row=8, column=0, columnspan=2, pady=(10, 0))

    def show_full_ingredients(self):
        if not self.recipe_manager.recipes:
            messagebox.showinfo("Info", "No recipes available.")
            return

    
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Recipe")

        label = ttk.Label(selection_window, text="Enter a recipe name:")
        label.pack(pady=5)

        recipe_combo = ttk.Combobox(selection_window, values=[r.title for r in self.recipe_manager.recipes], state="readonly")
        recipe_combo.pack(pady=5)

        def show_ingredients():
            title = recipe_combo.get()
            if not title:
                messagebox.showinfo("Selection", "Please select a recipe.")
                return
            ingredients = self.recipe_manager.get_all_ingredients_recursive(title)
            if not ingredients:
                messagebox.showinfo("Result", "No ingredients found.")
            else:
                message = "\n".join(ing.display() for ing in ingredients)
                messagebox.showinfo("Full Ingredients", message)
                selection_window.destroy()

        ttk.Button(selection_window, text="Show Ingredients", command=show_ingredients).pack(pady=5)


    def optimise_meal_plan(self):
        try:
            target = simpledialog.askstring("Target Servings", "Enter number of people to feed:")
            if not target:
                return
            target = int(target)
            recipes = self.recipe_manager.select_cheapest_meals(target)
            if not recipes:
                messagebox.showinfo("No Recipes", "No suitable recipes found.")
                return

            # count how many times each recipe was chosen
            from collections import Counter
            recipe_counts = Counter(r.title for r in recipes)

            # get unique recipes in order
            unique_recipes = []
            seen = set()
            for r in recipes:
                if r.title not in seen:
                    unique_recipes.append(r)
                    seen.add(r.title)

       
            message = f"Optimised Meal Suggestions for exactly {target} servings:\n\n"
            total_combined_cost = 0.0
            total_combined_servings = 0
            
            for r in unique_recipes:
                count = recipe_counts[r.title]
                total_servings = r.servings * count
                total_cost = r.total_recipe_cost * count
                cost_per_serving = r.cost_per_serving()

                total_combined_cost += total_cost
                total_combined_servings += total_servings

                message += (
                    f"{r.title} (x{count}) — Total Servings: {total_servings}\n"
                    f"  • Total Cost: £{total_cost:.2f}\n"
                    f"  • Cost per Serving: £{cost_per_serving:.2f}\n\n"
                )

            message += f"📊 Combined Cost: £{total_combined_cost:.2f} for {total_combined_servings} servings"
            messagebox.showinfo("Optimised Meals", message)

        except Exception as e:
            messagebox.showerror("Error", str(e))

  

    def refresh_recipe_list(self):
        self.recipe_listbox.delete(0, tk.END)
        seen=set()
        for r in self.recipe_manager.recipes:
            if r.title.lower() not in seen:
                self.recipe_listbox.insert(tk.END, r.title)
                seen.add(r.title.lower())
    def add_recipe(self):
        title = simpledialog.askstring("Title", "Recipe title:")
        if not title:
            return
        desc = simpledialog.askstring("Description", "Description:")
        servings = simpledialog.askinteger("Servings", "Servings:")
        cuisine = simpledialog.askstring("Cuisine", "Cuisine type:")
        category = simpledialog.askstring("Category", "Meal category:")

        recipe = Recipe(title, desc, servings, cuisine, category)

        while messagebox.askyesno("Ingredient", "Add ingredient?"):
            name = simpledialog.askstring("Ingredient", "Name:")
            qty_str = simpledialog.askstring("Ingredient", "Quantity:")
            qty = float(qty_str) if qty_str else 0.0
            unit = simpledialog.askstring("Ingredient", "Unit:")
            recipe.add_ingredient(Ingredient(name, qty, unit))

        while messagebox.askyesno("Step", "Add step?"):
            step = simpledialog.askstring("Step", "Description:")
            recipe.add_step(step)

        rating = simpledialog.askfloat("Rating", "Rating out of 10:")
        notes = simpledialog.askstring("Notes", "Any notes?")
        image_path = simpledialog.askstring("Image Path", "Path to image?")

        total_cost = simpledialog.askfloat("Total Cost", "Enter total cost of the recipe:", minvalue=0.0)

        recipe.rating = rating
        recipe.notes = notes
        recipe.image_path = image_path
        recipe.total_recipe_cost = total_cost if total_cost else 0.0

        self.recipe_manager.add_recipe(recipe)
        self.refresh_recipe_list()
        self.recipe_manager.save_to_file()


        
        
    def display_recipe(self, event):
        selected = self.recipe_listbox.curselection()
        if not selected:
            return
        index = selected[0]
        recipe = self.recipe_manager.recipes[index]
        self.recipe_text.delete(1.0, tk.END)
        self.recipe_text.insert(tk.END, f"🍽️ {recipe.title}\n")
        self.recipe_text.insert(tk.END, f"(👩🏻‍💻{recipe.description})\n\n")
        self.recipe_text.insert(tk.END, f"Servings: {recipe.servings} | Cuisine: {recipe.cuisine} | Category: {recipe.category}\n")
        self.recipe_text.insert(tk.END, f"💰 Total Cost: £{recipe.total_recipe_cost:.2f} | Cost per Serving: £{recipe.cost_per_serving():.2f}\n")

        if recipe.rating is not None:
            self.recipe_text.insert(tk.END, f"⭐ Rating: {recipe.rating}/10\n")

        self.recipe_text.insert(tk.END, "\n🧂 Ingredients:\n")
        for i in recipe.ingredients:
            self.recipe_text.insert(tk.END, f" - {i.display()}\n")
    
        self.recipe_text.insert(tk.END, "\n👩🏼‍🌾🍳 Steps:\n")
        for idx, s in enumerate(recipe.steps, 1):
            self.recipe_text.insert(tk.END, f"{idx}. {s}\n")

        if recipe.notes:
            self.recipe_text.insert(tk.END, f"\n📝 Notes: {recipe.notes}\n\n")
        if recipe.image_path:
            self.recipe_text.insert(tk.END, f"🖼 Image Path: {recipe.image_path}\n")


    def plan_meal(self):
        if not self.recipe_manager.recipes:
            messagebox.showinfo("Info", "No recipes to plan.")
            return

        plan_window = tk.Toplevel(self.root)
        plan_window.title("Plan Meal")

        ttk.Label(plan_window, text="Enter date (YYYY-MM-DD):").pack(pady=5)
        date_entry = ttk.Entry(plan_window)
        date_entry.pack(pady=5)

        ttk.Label(plan_window, text="Select a recipe:").pack(pady=5)
        recipe_combo = ttk.Combobox(plan_window, values=[r.title for r in self.recipe_manager.recipes], state="readonly")
        recipe_combo.pack(pady=5)

        def confirm_plan():
            date = date_entry.get()
            title = recipe_combo.get()
            if not date or not title:
                messagebox.showinfo("Missing Info", "Please enter a date and select a recipe.")
                return
            recipe = next((r for r in self.recipe_manager.recipes if r.title == title), None)
            if recipe:
                self.meal_planner.add_meal(date, recipe)
                messagebox.showinfo("Planned", f"Added {title} to {date}")
                plan_window.destroy()

        ttk.Button(plan_window, text="Plan", command=confirm_plan).pack(pady=10)


    def view_plan(self):
        date = simpledialog.askstring("View Meal Plan", "Enter date (YYYY-MM-DD):")
        meals = self.meal_planner.get_meals_for_date(date)
        if not meals:
            messagebox.showinfo("Meal Plan", "No meals planned.")
            return

        self.recipe_text.delete(1.0, tk.END)
        self.recipe_text.insert(tk.END, f"📅 {date} Meal Plan\n\n")

        for title in meals:
            recipe = next((r for r in self.recipe_manager.recipes if r.title == title), None)
            if not recipe:
                continue
            
            self.recipe_text.insert(tk.END, f"📋 {recipe.title}\n")
            self.recipe_text.insert(tk.END, f"{recipe.description}\n")
            self.recipe_text.insert(tk.END, f"Servings: {recipe.servings} | Cuisine: {recipe.cuisine} | Category: {recipe.category}\n")
            self.recipe_text.insert(tk.END, "\n🧂 Ingredients:\n")
            for ing in recipe.ingredients:
                self.recipe_text.insert(tk.END, f" - {ing.display()}\n")
            self.recipe_text.insert(tk.END, "\n👩🏼‍🌾🍳 Steps:\n")
            
            for idx, step in enumerate(recipe.steps, 1):
                self.recipe_text.insert(tk.END, f"{idx}. {step}\n")
            self.recipe_text.insert(tk.END, "\n" + ("=" * 40) + "\n\n")
            
            if recipe.notes:
                self.recipe_text.insert(tk.END, f"\n📝 Notes:\n{recipe.notes}\n")
            if recipe.image_path:
                self.recipe_text.insert(tk.END, f"\n🖼️ Image Path: {recipe.image_path}\n")

    def generate_shopping_list(self):
         date = simpledialog.askstring("Shopping List", "Enter date (YYYY-MM-DD):")
         meals = self.meal_planner.get_meals_for_date(date)
         if not meals:
             messagebox.showinfo("List", "No meals planned.")
             return
         items = self.shopper.generate_list(meals)
         self.shopping_list_manager.save_list(date, items)
 
         unique_items = list(dict.fromkeys(items))  
 
         self.recipe_text.delete(1.0, tk.END)
         self.recipe_text.insert(tk.END, f"🛒 Shopping List for {date}\n\n")
         for item in unique_items:
             self.recipe_text.insert(tk.END, f" - {item}\n")



    def edit_recipe(self):
        selected = self.recipe_listbox.curselection()
        if not selected:
            messagebox.showinfo("Edit", "Select a recipe to edit.")
            return

        index = selected[0]
        recipe = self.recipe_manager.recipes[index]

    
        title = simpledialog.askstring("Title", "Recipe title:", initialvalue=recipe.title)
        desc = simpledialog.askstring("Description", "Description:", initialvalue=recipe.description)
        servings = simpledialog.askinteger("Servings", "Servings:", initialvalue=recipe.servings)
        cuisine = simpledialog.askstring("Cuisine", "Cuisine type:", initialvalue=recipe.cuisine)
        category = simpledialog.askstring("Category", "Meal category:", initialvalue=recipe.category)
        rating = simpledialog.askfloat("Rating", "Rating (1-5):", initialvalue=recipe.rating)
        notes = simpledialog.askstring("Notes", "Any notes?", initialvalue=recipe.notes)
        image_path = simpledialog.askstring("Image Path", "Path to image?", initialvalue=recipe.image_path)

   
        if messagebox.askyesno("Ingredients", "Do you want to edit ingredients? This will reset them."):
            recipe.ingredients = []
            while messagebox.askyesno("Ingredient", "Add ingredient?"):
                name = simpledialog.askstring("Ingredient", "Name:")
                qty_str = simpledialog.askstring("Ingredient", "Quantity:")
                qty = float(qty_str) if qty_str else 0.0
                unit = simpledialog.askstring("Ingredient", "Unit:")
                recipe.add_ingredient(Ingredient(name, qty, unit)) 




   
        if messagebox.askyesno("Steps", "Do you want to edit steps? This will reset them."):
            recipe.steps = []
            while messagebox.askyesno("Step", "Add step?"):
                step = simpledialog.askstring("Step", "Description:")
                recipe.add_step(step)

    
        recipe.title = title
        recipe.description = desc
        recipe.servings = servings
        recipe.cuisine = cuisine
        recipe.category = category
        recipe.rating = rating
        recipe.notes = notes
        recipe.image_path = image_path
        cost = simpledialog.askfloat("Total Cost", "Enter total cost of the recipe:", initialvalue=recipe.total_recipe_cost)
        recipe.total_recipe_cost = cost if cost else 0.0

        # replace recipe in all planned meals with the updated one
        for date, recipes in self.meal_planner.planned_meals.items():
            for i, r in enumerate(recipes):
                if r.title.lower() == recipe.title.lower():
                    self.meal_planner.planned_meals[date][i] = recipe

        self.refresh_recipe_list()
        messagebox.showinfo("Updated", "Recipe updated successfully.")
        
        
    def on_close(self):
        print("Attempting to save and close...")
        try:
            self.recipe_manager.save_to_file()
            self.meal_planner.save_to_file()
            self.shopping_list_manager.save_to_file()
            print("Files saved successfully.")
        except Exception as e:
            print(f"Error saving data: {e}")
        finally:
            self.root.quit()
            self.root.after(100, self.root.destroy)
            
            
            
 
             
             


    
    
        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Recipe Manager")  
    app = RecipeApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


