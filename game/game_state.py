from entities.game_world import GameWorld
import json

class GameState:
    def __init__(self, player, game_world):
        self.player = player
        self.game_world = game_world
        self.log = []
        self.current_location = self.player.location
        self.nearby_entities = []
        self.locations = [e for e in self.game_world.entities if e.entity_type == "location"]
        self.characters = [e for e in self.game_world.entities if "character" in e.entity_type]
        self.items = [e for e in self.game_world.entities if e.entity_type == "item"]

    def to_json(self):
        return json.dumps({
            "player": self.player.to_json(),
            "current_location": self.current_location,
            "nearby_entities": [
                e.to_json() for e in self.nearby_entities
            ]
        })
    
    def update_current_location(self, location_name):
        self.player.location = location_name
        self.current_location = location_name
        self.set_nearby_entities()
        
    def update(self, action, result):
        self.log.append({'action': action, 'result': result})

    def get_last_log_entry(self):
        return self.log[-1] if self.log else None
    
    def set_nearby_entities(self):
        for e in self.game_world.entities:
            if e.location == self.player.location or e.name == self.player.location:
                if e != self.player:
                    self.nearby_entities.append(e)
                    
    def get_nearby_entities(self):
        return self.nearby_entities
    
    def get_all_characters(self):
        return self.characters
    
    def get_all_locations(self):
        return self.locations
    
    def get_all_items(self):
        return self.items
    
    def get_nearby_entities_as_string_list(self):
        return "\n".join([f"{e.entity_type.capitalize()}: {e.name} - {e.description}" for e in self.game_world.entities if e.location == self.player.location])