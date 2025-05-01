#Interactive Recipe Manager


class Ingredient:
    def __init__(self, name, quantity, unit):
        self.name = name
        self.quantity = quantity
        self.unit = unit

    def display(self):
        return f"{self.quantity} {self.unit} {self.name}"
