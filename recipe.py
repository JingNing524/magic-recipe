
#Interactive Recipe Manager



import json   #for saving and loading data
import os   #for checking if files exist
import tkinter as tk   
from tkinter import simpledialog, messagebox, ttk
from collections import defaultdict   #dictionary that makes defult values
from itertools import combinations   # use for generating combinations of item



class Ingredient:
    def __init__(self, name, quantity, unit, cost_per_unit=0.0):
        self.name = name
        self.quantity = quantity   #amount use of ingridient
        self.unit = unit
        self.cost_per_unit=cost_per_unit

    def display(self):
        # returrn a string to show the ingredient
        return f"{self.quantity} {self.unit} {self.name}"
    
    def total_cost(self):
        #caculate total cost of the ingredient
        quantity = self.quantity if self.quantity is not None else 0
        cost = self.cost_per_unit if self.cost_per_unit is not None else 0
        return quantity * cost   #total=quantity*cost per unit
    
    

class Recipe:
    def __init__(self, title, description, servings, cuisine, category,
                 ingredients=None, steps=None, rating=None, notes=None, image_path=None, total_cost=0.0):
        self.title = title
        self.description = description
        self.servings = servings
        self.cuisine = cuisine
        self.category = category
        self.ingredients = ingredients if ingredients else []   #list of Ingredient objects
        self.steps = steps if steps else []   #list of steps to make recipe
        self.rating = rating   #this is optional for user rating
        self.notes = notes   #optional foe user's notes
        self.image_path = image_path   #optional 
        self.total_recipe_cost = total_cost  

    def add_ingredient(self, ingredient):
        #add an ingredient object to the list  of ingredients
        self.ingredients.append(ingredient)

    def remove_ingredient(self, ingredient_name):
        #remove an ingredient from the list by name(ignore if it is capital letetr or not)
        self.ingredients = [
            ing for ing in self.ingredients if ing.name.lower() != ingredient_name.lower()
        ]

    def add_step(self, step):
        #add cooking steps to the steps list
        self.steps.append(step)

    def remove_step(self, step_number):
        #removea step by its index in valid range
        if 0 <= step_number < len(self.steps):
            self.steps.pop(step_number)

    def update_servings(self, new_servings):
        #adjust ingredient quantities when the number of serving changes
        if new_servings <= 0:
            return   #do nothing if the new value is invalid
        factor = new_servings / self.servings
        for ing in self.ingredients:
            ing.quantity *= factor   #scale each ingredient's quantity
        self.servings = new_servings   #update the servings

    def cost_per_serving(self):
        #caculate cost per serving safely and avoid dividing by zero
        return self.total_recipe_cost / self.servings if self.servings else 0

    @classmethod
    def from_dict(cls, data):
    #when loading from file create a Recipe object from a dictionary
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
        #print the recipe details in a readable format
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