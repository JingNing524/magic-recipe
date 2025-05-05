
import json   #for saving and loading data
import os   #for checking if files exist
import tkinter as tk   
from tkinter import simpledialog, messagebox, ttk
from collections import defaultdict   #dictionary that makes defult values
from itertools import combinations   # use for generating combinations of item
from recipe import Recipe, Ingredient


#class to manage all recipes
class RecipeManager:
    def __init__(self):
        self.recipes = []   #list to store all Recipe objects
        self.load_from_file()   #load recipes from file when startin
        
    def to_dict(self):
        #convert all recipes into a list of dictionaries for saving
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
        return recipe_dicts   #return list of recipe dictionaries


   
    def from_dict(self, data):
        #create recipe objects from loaded dictionary data
        self.recipes = [Recipe.from_dict(item) for item in data]     

    def save_to_file(self, filename="recipes.json"):
        # Time Complexity: O(n)
        # n = number of items saved/loaded

        # save all recipes to a JSON file
        try:
             with open(filename, "w") as f:
                 json.dump(self.to_dict(), f, indent=4) # Use indent for readability
        except IOError as e:
            print(f"Error saving to {filename}: {e}")

    def load_from_file(self, filename="recipes.json"):
        # Time Complexity: O(n)
        # n = number of items saved/loaded

        
        #load recipes from a JSON file if it exists and is not empty
        try:
            with open(filename, "r") as f:
                if os.path.getsize(filename) > 0:   #the files cannot be empty
                     data = json.load(f)
                     self.from_dict(data)
                else:
                     self.recipes = []   #empty files no recipes
        except FileNotFoundError:
             self.recipes = []   #ifnno file exist , start with empty list
        except json.JSONDecodeError:
             print(f"Error decoding JSON from {filename}. The file may be corrupted or empty.")
             self.recipes = []
        

    def add_recipe(self, recipe):
        #add new recipe by title only if it is not already exist in the list
        if not any(isinstance(r, Recipe) and r.title and r.title.lower() == recipe.title.lower() for r in self.recipes):
            self.recipes.append(recipe)

    def remove_recipe(self, recipe_title):
        #remove recipe by title (ignore capital letter or not)
        self.recipes = [r for r in self.recipes if r.title.lower() != recipe_title.lower()]

    def search_recipes(self, query):
        #search recipes by title or igredient name
        query = query.lower()
        results = []
        for recipe in self.recipes:
            if query in recipe.title.lower():
                results.append(recipe)
            elif any(query in ing.name.lower() for ing in recipe.ingredients):
                results.append(recipe)
        return results

    def filter_recipes(self, cuisine=None, category=None, rating=None):
        # Time Complexity: O(n)
        # n = number of recipes

        
        #filter recipes by cuisine, category, and/or rating
        results = self.recipes
        if cuisine:
            results = [r for r in results if r.cuisine.lower() == cuisine.lower()]
        if category:
            results = [r for r in results if r.category.lower() == category.lower()]
        if rating:
            results = [r for r in results if r.rating and r.rating >= rating]
        return results
    
    def get_all_ingredients_recursive(self, recipe_title, visited=None, cache=None):
        # Time Complexity: O(n + m)
        # n: number of recipes checked
        # m: total number of ingredients in those recipes
        
        #recursively get all ingredients, including sub-recipes
        if visited is None:
            visited = set()
        if cache is None:
            cache = {}

        if recipe_title in cache:
            return cache[recipe_title]
    
        recipe = next((r for r in self.recipes if r.title == recipe_title), None)
        if not recipe or recipe.title in visited:
            return []
        
        #go deeper if ingredient is another recipe
        visited.add(recipe.title)
        collected = []

        for ing in recipe.ingredients:
            if not ing or not ing.name:
                continue  # skip invalid ingredients
            sub_recipe = next((r for r in self.recipes if r.title and r.title.lower() == ing.name.lower()), None)

            if sub_recipe:
                collected += self.get_all_ingredients_recursive(sub_recipe.title, visited, cache)
            else:
                collected.append(ing)

        cache[recipe_title] = collected
        return collected

       
        recipe = next((r for r in self.recipes if r.title == recipe_title), None)
        if visited is None:
            visited = set()
            if not recipe or recipe.title in visited:
                return []
            
            #go deeper if ingredient is another recipe
            visited.add(recipe.title)
            collected = []
            for ing in recipe.ingredients:
                sub_recipe = next((r for r in self.recipes if r.title.lower() == ing.name.lower()), None)
                if sub_recipe:
                    collected += self.get_all_ingredients_recursive(sub_recipe.title, visited)
                else:
                    collected.append(ing)
            return collected
        
        
    #mealplanning cheastest combination    
    from itertools import combinations

    def select_cheapest_meals(self, target_servings):
        # Time Complexity: O(2^n)
        # Tries all combinations of recipes to meet serving target (exponential)

        # try all combinations of 1 to len(recipes) recipes
        valid_combinations = []

        for r in range(1, len(self.recipes) + 1):
            for combo in combinations(self.recipes, r):
                total_servings = sum(recipe.servings for recipe in combo)
                if total_servings == target_servings:
                    total_cost = sum(recipe.total_recipe_cost for recipe in combo)
                    valid_combinations.append((combo, total_cost))

        # return the cheapest valid combo, if any
        if valid_combinations:
            best_combo = min(valid_combinations, key=lambda x: x[1])
            return best_combo[0]  # just return the recipes no cost
        return []

    def get_recipe_by_title(self, title):
        for recipe in self.recipes:
            if recipe.title.lower() == title.lower():
                return recipe
        return None




    def display_all_recipes(self):
        # Time Complexity: O(n)
        # n = number of items printed

        #print the titles of all saved recipes
        if not self.recipes:
            print("No recipes found.")
        else:
            print("Recipes:")
            for i, recipe in enumerate(self.recipes, 1):
                print(f"{i}. {recipe.title}")
    
    



class MealPlanner:
    def __init__(self, recipe_manager):
        self.planned_meals = defaultdict(list)   #store recipes by date
        self.load_from_file(recipe_manager)   #load previous meal plan


        
    def add_meal(self, date, recipe):
        #add a recipe to a specific date
        self.planned_meals[date].append(recipe)

    def remove_meal(self, date, recipe_title):
        #remove a recipe from a date's plan by title
        self.planned_meals[date] = [
            r for r in self.planned_meals[date] if r.title.lower() != recipe_title.lower()
        ]
        if not self.planned_meals[date]:   #remove date entry if no meals left
            del self.planned_meals[date]

    def get_meals_for_date(self, date):
        #get a list of planned meals for a given date
        return self.planned_meals.get(date, [])

    def display_schedule(self):
        ## Time Complexity: O(n)
        # n = number of items printed

        
        #print all planned meals in date order
        for date, recipes in sorted(self.planned_meals.items()):
            print(f"\n📅 {date}:")
            for recipe in recipes:
                print(f" - {recipe.title}")

    def to_dict(self):
        #convert meal plan to dictionary format for saving
        return {
            'planned_meals': {
                day: [recipe.title for recipe in recipes if recipe and recipe.title]
                for day, recipes in self.planned_meals.items()
                }
            }
 
    def from_dict(self, data, recipe_manager):
        #load planned meals from a dictionary by using recipe IDs
        self.planned_meals = defaultdict(list)
        for day, recipe_titles in data.get('planned_meals', {}).items():
            self.planned_meals[day] = [
                title for title in recipe_titles if title
            ]


    def save_to_file(self, filename="mealplan.json"):
        # Time Complexity: O(n)
        # n = number of items saved/loaded

        #save meal plan data to a JSON file
        try:
             with open(filename, "w") as f:
                 json.dump(self.to_dict(), f, indent=4)
        except IOError as e:
             print(f"Error saving to {filename}: {e}")

    def load_from_file(self, recipe_manager, filename="mealplan.json"):
        # Time Complexity: O(n)
        # n = number of items saved/loaded

        # load meal plan data from file
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
        # Time Complexity: O(n * m)
        # n: number of recipes
        # m: average number of ingredients per recipe
        
        #creates a shopping list by combining all ingredients from selected recipes
        combined = {}
        for recipe in recipes:
            for ing in recipe.ingredients:
                if not ing or not ing.name or not ing.unit:
                    continue  # skip invalid ingredient
                key = (ing.name.lower(), ing.unit)

                if key in combined:
                    combined[key] += ing.quantity
                else:
                    combined[key] = ing.quantity
        return [f"{quantity:.2f} {unit} {name.title()}" for (name, unit), quantity in combined.items()]   #turn the nested dictionary into a readable list
        
    



    def display_list(self, shopping_list):
        #print the shopping list
        print("\n🛒 Shopping List:")
        for item in shopping_list:
            print(f" - {item}")

class ShoppingListManager:
    def __init__(self):
        self.list_by_date = {}   #dic to store shopping list per date
        self.load_from_file()

    def save_list(self, date, items):
        #save list for a specific date
        self.list_by_date[date] = items

    def get_list(self, date):
        #get saved shopping list for a date
        return {'shopping_list': self.list_by_date}

    def to_dict(self):
        #convert list-by-date dictionary to savable format
        return self.list_by_date

    def from_dict(self, data):
        #load shopping list data from dictionary
        self.list_by_date = data.get('shopping_list', {})

    def save_to_file(self, filename="shoppinglist.json"):
        # Time Complexity: O(n)
        # n = number of items saved/loaded

        #save shopping lists to file
        try:
             with open(filename, "w") as f:
                 json.dump(self.to_dict(), f, indent=4)
        except IOError as e:
             print(f"Error saving to {filename}: {e}")

    def load_from_file(self, filename="shoppinglist.json"):
       # Time Complexity: O(n)
       # n = number of items saved/loaded

        #load shopping lists from file
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

