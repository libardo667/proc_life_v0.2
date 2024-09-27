from utils.inventory import Inventory

class Entity:
    def __init__(self, name, description, location_name, entity_type, connected_location_names = []):
        self.name = name
        self.description = description
        self.location = location_name
        self.entity_type = entity_type
        self.relationships = {}
        self.connected_locations = connected_location_names
        self.inventory = Inventory()
        self.visited_by_player = False
        self.used_by_player = False
        self.grid_position = None
            
    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "entity_type": self.entity_type,
            "connected_locations": self.connected_locations,
            "inventory": self.inventory.items,
            "visited_by_player": self.visited_by_player,
            "used_by_player": self.used_by_player
        }

    @classmethod
    def main_character_entity(cls, name, description, location_name, ):
        return cls(name, description, location_name, 'main character')
    
    @classmethod
    def character_entity(cls, name, description, location_name):
        return cls(name, description, location_name, 'character')

    @classmethod
    def location_entity(cls, name, description, connected_location_names):
        return cls(name, description, None, 'location', connected_location_names)

    @classmethod
    def item_entity(cls, name, description, location_name):
        return cls(name, description, location_name, 'item', [])

    def set_relationship(self, other_entity, relationship):
        self.relationships[other_entity] = relationship