from tkinter import Tk
from gui import RecipeApp
import json   #for saving and loading data
import os   #for checking if files exist
import tkinter as tk   
from tkinter import simpledialog, messagebox, ttk
from collections import defaultdict   #dictionary that makes defult values
from itertools import combinations   # use for generating combinations of item

root = Tk()    #create the main application window
root.title("Recipe Manager")   #set the window title
app = RecipeApp(root)  #create the app 
root.protocol("WM_DELETE_WINDOW", app.on_close)   #save before closing
root.mainloop()    #start the GUI loop

if __name__ == "__main__":
    root = tk.Tk()   #create the main application window
    root.title("Recipe Manager")   #set the window title
    app = RecipeApp(root)   #create the app
    root.protocol("WM_DELETE_WINDOW", app.on_close)   #save before closing
    root.mainloop()   #start the GUI loop
