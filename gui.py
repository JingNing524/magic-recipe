from manager import RecipeManager, MealPlanner, ShoppingListGenerator, ShoppingListManager
from recipe import Recipe, Ingredient

import json   #for saving and loading data
import os   #for checking if files exist
import tkinter as tk   
from tkinter import simpledialog, messagebox, ttk
from collections import defaultdict   #dictionary that makes defult values
from itertools import combinations   # use for generating combinations of item

class RecipeApp:
    def __init__(self, master):
        self.root=master   #main window
        self.recipe_manager = RecipeManager()   #handles recies
        self.meal_planner = MealPlanner(self.recipe_manager)   #planning
        self.shopping_list_manager = ShoppingListManager()   #save list
        self.shopper = ShoppingListGenerator(self.recipe_manager)   #generate new lists
        self.meal_planner.load_from_file(self.recipe_manager)   #load meal plan on start
        
        self.setup_gui()   #build GUI layout
        self.refresh_recipe_list()   #update the list shown on screen
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)   #window close
        self.refresh_recipe_list()   #update recipe list UI
        


    def load_data(self):
        #load all saved data from files
         self.recipe_manager.load_from_file()
         self.meal_planner.load_from_file(self.recipe_manager)
         self.shopping_list_manager.load_from_file()
         self.update_recipe_list()
         self.update_meal_plan_display()
         self.update_shopping_list_display()
 

    def save_data(self):
        #save all data to their files
         self.recipe_manager.save_to_file()
         self.meal_planner.save_to_file()
         self.shopping_list_manager.save_to_file()
 

    def close_application(self):
        #save everything before closing the window
         self.save_data() 
         self.root.destroy()
     

        

    def setup_gui(self):
        #create a main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack()

        #listbox for displaying recipe titles
        self.recipe_listbox = tk.Listbox(self.main_frame, height=10)
        self.recipe_listbox.bind("<<ListboxSelect>>", self.display_recipe)
        self.recipe_listbox.grid(row=0, column=0, rowspan=8, padx=10)

        
        #buttons for various actions
        ttk.Button(self.main_frame, text="Add Recipe", command=self.add_recipe).grid(row=0, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Edit Recipe", command=self.edit_recipe).grid(row=1, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Plan Meal", command=self.plan_meal).grid(row=2, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="View Meal Plan", command=self.view_plan).grid(row=3, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Shopping List", command=self.generate_shopping_list).grid(row=4, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Show Full Ingredients", command=self.show_full_ingredients).grid(row=5, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Optimise Meals", command=self.optimise_meal_plan).grid(row=6, column=1, sticky="ew")
        ttk.Button(self.main_frame, text="Exit", command=self.on_close).grid(row=7, column=1, sticky="ew")

        #text widget to show recipe details
        self.recipe_text = tk.Text(self.main_frame, width=70, height=25)
        self.recipe_text.grid(row=8, column=0, columnspan=2, pady=(10, 0))

    def show_full_ingredients(self):
        #make sure there are recipes
        if not self.recipe_manager.recipes:
            messagebox.showinfo("Info", "No recipes available.")
            return

        #popup window to select a recipe
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Recipe")

        label = ttk.Label(selection_window, text="Enter a recipe name:")
        label.pack(pady=5)

        #dropdown to choose a recipe
        recipe_combo = ttk.Combobox(selection_window, values=[r.title for r in self.recipe_manager.recipes], state="readonly")
        recipe_combo.pack(pady=5)

        def show_ingredients():
            #get selected recipe title
            title = recipe_combo.get()
            if not title:
                messagebox.showinfo("Selection", "Please select a recipe.")
                return
            #get all ingredients including from sub-recipes
            ingredients = self.recipe_manager.get_all_ingredients_recursive(title)
            if not ingredients:
                messagebox.showinfo("Result", "No ingredients found.")
            else:
                #show all ingredients in a message box
                message = "\n".join(ing.display() for ing in ingredients)
                messagebox.showinfo("Full Ingredients", message)
                selection_window.destroy()

        ttk.Button(selection_window, text="Show Ingredients", command=show_ingredients).pack(pady=5)


    def optimise_meal_plan(self):
        try:
            #ask how many people they want to feed
            target = simpledialog.askstring("Target Servings", "Enter number of people to feed:")
            if not target:
                return
            target = int(target)
            
            #use RecipeManager to select cheapest combination of meals
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

            #build the message to show the meal plan summary
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
            #if something goes wrong, show the error
            messagebox.showerror("Error", str(e))

  

    def refresh_recipe_list(self):
        #clear the listbox first
        self.recipe_listbox.delete(0, tk.END)
        seen=set()
        for r in self.recipe_manager.recipes:
            if r and r.title and r.title.lower() not in seen:
                self.recipe_listbox.insert(tk.END, r.title)
                seen.add(r.title.lower())
    def add_recipe(self):
        #ask user for basic recipe details
        title = simpledialog.askstring("Title", "Recipe title:")
        if not title:
            return
        desc = simpledialog.askstring("Description", "Description:")
        servings = simpledialog.askinteger("Servings", "Servings:")
        cuisine = simpledialog.askstring("Cuisine", "Cuisine type:")
        category = simpledialog.askstring("Category", "Meal category:")

        #create a new Recipe object with entered details
        recipe = Recipe(title, desc, servings, cuisine, category)

            
        #ask user to add ingredients in a loop
        while messagebox.askyesno("Ingredient", "Add ingredient?"):
            name = simpledialog.askstring("Ingredient", "Name:")
            qty_str = simpledialog.askstring("Ingredient", "Quantity:")
            qty = float(qty_str) if qty_str else 0.0
            unit = simpledialog.askstring("Ingredient", "Unit:")
            recipe.add_ingredient(Ingredient(name, qty, unit))

        #ask user to add preparation steps
        while messagebox.askyesno("Step", "Add step?"):
            step = simpledialog.askstring("Step", "Description:")
            recipe.add_step(step)

        #ask for optional fields
        rating = simpledialog.askfloat("Rating", "Rating out of 10:")
        notes = simpledialog.askstring("Notes", "Any notes?")
        image_path = simpledialog.askstring("Image Path", "Path to image?")
        total_cost = simpledialog.askfloat("Total Cost", "Enter total cost of the recipe:", minvalue=0.0)

        #set those values in the recipe
        recipe.rating = rating
        recipe.notes = notes
        recipe.image_path = image_path
        recipe.total_recipe_cost = total_cost if total_cost else 0.0

        #add recipe to manager and save
        self.recipe_manager.add_recipe(recipe)
        self.refresh_recipe_list()
        self.recipe_manager.save_to_file()


        
        
    def display_recipe(self, event):
        selected = self.recipe_listbox.curselection()
        if not selected:
            return
        index = selected[0]
        recipe = self.recipe_manager.recipes[index]
        
        self.recipe_text.delete(1.0, tk.END)   #clear old text
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

        #create a popup window to let user choose a date and recipe
        plan_window = tk.Toplevel(self.root)
        plan_window.title("Plan Meal")

        #date input
        ttk.Label(plan_window, text="Enter date (YYYY-MM-DD):").pack(pady=5)
        date_entry = ttk.Entry(plan_window)
        date_entry.pack(pady=5)

        #recipe dropdown
        ttk.Label(plan_window, text="Select a recipe:").pack(pady=5)
        recipe_combo = ttk.Combobox(plan_window, values=[r.title for r in self.recipe_manager.recipes], state="readonly")
        recipe_combo.pack(pady=5)

        #when user confirms, add meal to planner
        def confirm_plan():
            date = date_entry.get()
            title = recipe_combo.get()
            if not date or not title:
                messagebox.showinfo("Missing Info", "Please enter a date and select a recipe.")
                return
            recipe = next((r for r in self.recipe_manager.recipes if r.title == title), None)
            if recipe:
                self.meal_planner.add_meal(date, recipe)
                self.meal_planner.save_to_file()
                # Generate shopping list for this date using all planned meals
                meals = self.meal_planner.get_meals_for_date(date)
                items = self.shopper.generate_list(meals)
                self.shopping_list_manager.save_list(date, items)
                self.shopping_list_manager.save_to_file()
                
                messagebox.showinfo("Planned", f"Added {title} to {date}")
                plan_window.destroy()

        ttk.Button(plan_window, text="Plan", command=confirm_plan).pack(pady=10)


    def view_plan(self):
        #ask user to enter a date
        date = simpledialog.askstring("View Meal Plan", "Enter date (YYYY-MM-DD):")
        meals = self.meal_planner.get_meals_for_date(date)
        if not meals:
            messagebox.showinfo("Meal Plan", "No meals planned.")
            return
        
        #clear and update the recipe display area
        self.recipe_text.delete(1.0, tk.END)
        self.recipe_text.insert(tk.END, f"📅 {date} Meal Plan\n\n")

        for title in meals:
            recipe = next((r for r in self.recipe_manager.recipes if r.title and r.title.lower() == title.lower()), None)
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
        # ask user for the date
        date = simpledialog.askstring("Shopping List", "Enter date (YYYY-MM-DD):")
        titles = self.meal_planner.get_meals_for_date(date)
        meals = [self.recipe_manager.get_recipe_by_title(title) for title in titles if self.recipe_manager.get_recipe_by_title(title)]

        if not meals:
            messagebox.showinfo("List", "No meals planned.")
            return

        # generate list from planned meals
        items = self.shopper.generate_list(meals)
        
        # save list to manager
        self.shopping_list_manager.save_list(date, items)
        self.shopping_list_manager.save_to_file()

        # remove duplicates while keeping order
        unique_items = list(dict.fromkeys(items))  

        # show the list in the text area
        self.recipe_text.delete(1.0, tk.END)
        self.recipe_text.insert(tk.END, f"🛒 Shopping List for {date}\n\n")
        for item in unique_items:
            self.recipe_text.insert(tk.END, f" - {item}\n")

        # Show the generated shopping list in a popup
        if items:
            list_window = tk.Toplevel(self.root)
            list_window.title(f"Shopping List for {date}")
            text_widget = tk.Text(list_window, width=60, height=20)
            text_widget.pack(padx=10, pady=10)
            text_widget.insert("1.0", "\n".join(items))
        else:
            messagebox.showinfo("Info", "No items generated.")





    def edit_recipe(self):
        selected = self.recipe_listbox.curselection()
        if not selected:
            messagebox.showinfo("Edit", "Select a recipe to edit.")
            return

        index = selected[0]
        recipe = self.recipe_manager.recipes[index]

        #ask for updated values with current values as default
        title = simpledialog.askstring("Title", "Recipe title:", initialvalue=recipe.title)
        desc = simpledialog.askstring("Description", "Description:", initialvalue=recipe.description)
        servings = simpledialog.askinteger("Servings", "Servings:", initialvalue=recipe.servings)
        cuisine = simpledialog.askstring("Cuisine", "Cuisine type:", initialvalue=recipe.cuisine)
        category = simpledialog.askstring("Category", "Meal category:", initialvalue=recipe.category)
        rating = simpledialog.askfloat("Rating", "Rating (1-10):", initialvalue=recipe.rating)
        notes = simpledialog.askstring("Notes", "Any notes?", initialvalue=recipe.notes)
        image_path = simpledialog.askstring("Image Path", "Path to image?", initialvalue=recipe.image_path)

        
        #if editing ingredients, clear and re-enter
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

        #update the recipe attributes with new values
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
            #quit and destroy the Tkinter root window
            self.root.quit()
            self.root.after(100, self.root.destroy)


