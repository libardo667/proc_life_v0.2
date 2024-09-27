class GameWorld:
    def __init__(self):
        self.entities = []

    def get_entity_description(self, entity_name):
        entity = self.get_entity_by_name(entity_name)
        if entity:
            return entity.description
        return None
    
    def get_entities_by_location(self, location_name):
        return [entity for entity in self.entities if entity.location == location_name]
    
    def get_entity_by_name(self, entity_name):
        for entity in self.entities:
            if entity.name.lower() == entity_name.lower():
                return entity
        return None
    
    def get_entities_by_type(self, entity_type):
        return [entity for entity in self.entities if entity.entity_type == entity_type]