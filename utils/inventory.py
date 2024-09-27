class Inventory():
    def __init__(self):
        self.items = []
        
    def add_item(self, item_name):
        self.items.append(item_name)
        
    def remove_item(self, item_name):
        self.items.remove(item_name)
        
    def display_items(self):
        display_list = ""
        for item in self.items:
            display_list += "- " + item + "\n\n"
        return display_list