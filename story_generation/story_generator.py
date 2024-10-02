import json
import os
from entities.game_world import GameWorld
from entities.entity import Entity
from game.game_state import GameState
from ai_model.ai_model import OpenSourceAIModel
from story_generation.validate_story import validate_json

class StoryGenerator:
    def __init__(self):
        self.ai_model = OpenSourceAIModel()
        self.entities = []
        self.outline = ""
        self.outline_parts = []
        self.story = ""
        
    def init_game_state(self):
        self.generate_story_outline()
        self.parse_outline_into_parts()
        self.generate_story_json_from_outline_parts()
        game_world, player, is_valid, error = self.get_entities_from_story_json()
    
        if is_valid: print("GameWorld is in a valid JSON format!")
        else: print("game_world is not valid: \n" + error.message)
        
        game_state = GameState(player, game_world)
        game_state.set_nearby_entities()
        return game_state

    def generate_story_outline(self):
        system_prompt = {
            "role": "system", 
            "content": """
You are a the creative director of an indie game company who specializes in creating rich, 
diverse worlds in text only formats. While your stories can touch on themes
and ideas presented in popular media, you should strive to create unique
stories that provide the user with a sense of wonder at how a story like
*this* was made just for them. You should not stick to one particular genre but
should instead draw from a diverse set of genres and time periods for your creations. 
Particularly, be sure not to lean too heavily on fantasy stories and characters, as you have
received negative reviews for this recently. """
        }
        
        story_outline_prompt = {
            "role": "user",
            "content": """
Create an outline for an original story that would make a great text-based adventure game. Avoid always creating fantasy stories; strive to craft unique narratives that will surprise the user with creativity. The story can be set in any time period or setting, real or fictional.

### Guidelines

- The outline should have **up to 7 major plot points**.
- Each plot point should be clearly numbered as follows: "1.", "2.", etc.
- There should be no space between each part's heading and its description.
- Each plot point should include:
- A brief description of events.
- Relevant characters, locations, and items.
- Use clear headings and consistent formatting.
- This output will be directly parsed by code, so consistent formatting is crucial! 
- Please separate each part with two new lines to allow the code to easily split the outline into parts at the new line characters.
- Write in the third-person narrative style.
- Do not include any other text aside from the outline.

### Desired format (please follow exactly)

\"\"\"
Part 1:
Description: [insert description here, describing key characters, locations, and items and their roles in this part]
Characters: [insert comma-separated list of characters (main and side, named and unnamed) who are relevant this part of the story]
Locations: [insert comma-separated list of locations relevant to this part of the story (no overarching locations like the name of a country or a whole city, these should be granular, allowing for exploration)]
Items: [insert comma-separated list of items relevant to this part of the story (there should be key items, but also miscellaneous stuff.)]

Part 2:
Description: [insert description here, describing key characters, locations, and items and their roles in this part]
Characters: [insert comma-separated list of characters (main and side, named and unnamed) who are relevant this part of the story]
Locations: [insert comma-separated list of locations relevant to this part of the story (no overarching locations like the name of a country or a whole city, these should be granular, allowing for exploration)]
Items: [insert comma-separated list of items relevant to this part of the story (there should be key items, but also miscellaneous stuff.)]

<<repeat for all parts>>
\"\"\"

Provide the full outline below:
    """
        }

        self.ai_model.messages.append(system_prompt)
        self.ai_model.messages.append(story_outline_prompt)

        print("Generating outline...")
        self.outline, finish_reason = self.ai_model.generate()
        print(f"Finished generating outline. Finish reason: {finish_reason}")
        
        self.ai_model.messages.append({
            "role":"assistant",
            "content":self.outline
        })
        print(self.outline)
    
    def parse_outline_into_parts(self):
        self.outline_parts = self.outline.strip().split('\n\n')
        self.outline_parts = [part.strip() for part in self.outline_parts if part.strip()]
    
    def generate_story_part_json(self, outline_part, part_number):
        print(f"Generating story json for part {part_number}...")
        first_time_content = f"""
Instructions:

Please convert the following story outline part into a structured JSON format as specified below based on the outline you generated before. Each part of the story should include:

- Description: A detailed narrative of the events in this part.
- Relevant Characters: A list of characters involved in this part, each with:
    - name: The character's name.
    - description: A brief description of the character.
    - location: The location where the character is present during this part.
    - is_player_character: A boolean (True or False) indicating whether this character is the player character.
- Relevant Locations: A list of locations introduced or visited in this part, each with:
    - name: The name of the location.
    - description: A vivid description of the location.
    - connections: A list of names of other locations connected to this one.
        * NOTE: for a given part, if there are no obvious connections listed in the outline for 
        a given location, make up sublocations that connect the relevant 
        locations in the given part and include them in the relevant locations for that part.
- Relevant Items: A list of items that appear in this part, each with:
    - name: The name of the item.
    - description: A description of the item.
    - location: The location where the item is found.
- Progression Condition: An object specifying:
    - name: A unique identifier for the progression condition.
    - condition: A condition expression that must be met for the story to progress.
    - action: An action expression that occurs when the condition is met.

Please adhere strictly to the following JSON format, ensuring all data is properly nested and formatted and
that each object is fully defined with no empty strings or lists (including connections):

    {{
        "description": "Description of Part 1",
        "relevant_characters": [
        {{
            "name": "Character Name",
            "description": "Character Description",
            "location": "Location Name",
            "is_player_character": True
        }}
        // Additional characters...
        ],
        "relevant_locations": [
        {{
            "name": "Location Name",
            "description": "Location Description",
            "connections": ["Connected Location 1", "Connected Location 2"]
        }}
        // Additional locations...
        ],
        "relevant_items": [
        {{
            "name": "Item Name",
            "description": "Item Description",
            "location": "Location Name"
        }}
        // Additional items...
        ],
        "progression_condition": {{
        "name": "Condition Name",
        "condition": "Condition Expression",
        "action": "Action Expression"
        }}
    }}

Guidelines:

- DO NOT type the "```json" ... "```" at the beginning and end of the JSON output. This JSON will be directly used in code as a string.
- Replace placeholders with actual content from your story outline.
- Ensure that all JSON syntax is correct, with proper use of braces {{}}, brackets [], colons :, and commas ,.
- Enclose all string values in double quotes " (e.g., "name": "Elena").
- Use true or false (without quotes) for boolean values.
- For this part, include only the characters, locations, and items relevant to that part.
- The progression_condition should reflect any conditions that must be met to progress from the current part to the next. If there is no progression condition, you may set "progression_condition": null.

Here is the story outline part {part_number} to convert:

{outline_part}
"""
        further_content = f"""
Great, thank you! Please continue to adhere to the guidelines and instructions mentioned previously. 

Here is the story outline part {part_number} to convert:

{outline_part}
"""
        if part_number == "part_1":
            self.ai_model.messages.append(
                {
                    "role": "user",
                    "content": first_time_content

                }
            )
        else:
            self.ai_model.messages.append(
                {
                    "role": "user",
                    "content": further_content
                }
            )
        story_part_json, finish_reason = self.ai_model.generate()
        print(f"Finished generating {part_number}. Finish reason: {finish_reason}")
        return story_part_json

    def generate_story_json_from_outline_parts(self):
        story_json  = {"story": {}}
        for i, outline_part in enumerate(self.outline_parts):
            part_number = f"part_{i+1}"
            part_json = self.generate_story_part_json(outline_part, part_number)
            self.ai_model.messages.append({
                "role": "assistant",
                "content": part_json
            })
            if part_json:
                story_json['story'][part_number] = json.loads(part_json)
            else:
                print(f"Failed to generate JSON for {part_number}")
                break
        with open('story.json', 'w') as file:
            json.dump(story_json, file, sort_keys=True, indent=4)
        self.story = story_json
        
    def get_entities_from_story_json(self):
        game_world = GameWorld()
        all_entities = {
            'characters': {},
            'locations': {},
            'items': {}
        }
        player = None

        for part_name, part_data in self.story['story'].items():
            for loc_data in part_data.get('relevant_locations', []):
                loc_name = loc_data.get('name', '')
                if loc_name not in all_entities['locations']:
                    entity = Entity.location_entity(
                        name = loc_name,
                        description = loc_data.get('description', ''),
                        connected_location_names=loc_data.get('connections', [])
                    )
                    all_entities['locations'][loc_name] = entity
                    game_world.entities.append(entity)
                else:
                    existing_entity = all_entities['locations'][loc_name]
                    existing_connections = set(existing_entity.connected_locations)
                    new_connections = set(loc_data.get('connections', []))
                    existing_entity.connected_locations = list(existing_connections.union(new_connections))
                       
            for char_data in part_data.get("relevant_characters", []):
                char_name = char_data.get('name', '')
                if char_name not in all_entities['characters']:
                    char_location = all_entities['locations'].get(char_data.get('location'))
                    if char_location:
                        char_location_name = char_location.name
                        entity = Entity.character_entity(
                            name=char_name,
                            description=char_data.get('description', ''),
                            location_name=char_location_name
                        )
                        all_entities['characters'][char_name] = entity
                        game_world.entities.append(entity)
                    else:
                        char_location_name = char_data.get('location', '')
                        char_location_entity = Entity.location_entity(
                            name = char_location_name,
                            description = "This is a generic description of this location. Fill in a description based on the surrounding context.",
                            connected_location_names = []
                        )
                        all_entities['locations'][char_location_name] = char_location_entity
                        game_world.entities.append(char_location_entity)
                        entity = Entity.character_entity(
                            name=char_name,
                            description=char_data.get('description', ''),
                            location_name=char_data.get('location', '')
                        )
                        all_entities['characters'][char_name] = entity
                        game_world.entities.append(entity)
                        
                    if char_data.get('is_player_character', False) and player is None:
                            player = entity
                            player.__setattr__("entity_type", "main character")

            for item_data in part_data.get('relevant_items', []):
                item_name = item_data.get('name', '')
                if item_name not in all_entities['items']:
                    item_location = all_entities["locations"].get(item_data.get('location', ''))
                    if item_location:
                        item_location_name = item_location.name
                        entity = Entity.item_entity(
                            name=item_name, 
                            description=item_data.get('description', ''),
                            location_name=item_location_name
                        )
                        all_entities['items'][item_name] = entity
                        game_world.entities.append(entity)
                    else:
                        item_location_entity = Entity.location_entity(
                            name = item_data.get('location', ''),
                            description = "This is a generic description of this location. Fill in a description based on the surrounding context.",
                            connected_location_names = []
                        )
                        all_entities['locations'][item_data.get('location')] = item_location_entity
                        game_world.entities.append(item_location_entity)
                        entity = Entity.character_entity(
                            name=item_name,
                            description=item_data.get('description', ''),
                            location_name=item_data.get('location', '')
                        )
                        all_entities['items'][item_name] = entity
                        game_world.entities.append(entity)

            ### TODO process progression conditions if needed
            
        for location_entity in all_entities['locations'].values():
            for connected_location_name in location_entity.connected_locations:
                connected_location_entity = all_entities['locations'].get(connected_location_name, None)
                if (connected_location_entity) and (location_entity.name not in connected_location_entity.connected_locations):
                    connected_location_entity.connected_locations.append(location_entity.name)
                elif not connected_location_entity:
                    connected_location_entity = Entity.location_entity(
                        name = connected_location_name,
                        description = "This is a generic description. Use the context to fill in this scene description.",
                        connected_location_names=[location_entity.name]
                    )

        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(script_dir, 'schema.json')
        with open(schema_path, "r") as json_schema:
            schema = json.load(json_schema)

            is_valid, err = validate_json(self.story, schema)

        return game_world, player, is_valid, err
    
    def describe_scene(self, game_state):
        game_state_json = game_state.to_json()
        with open("game_state.json", "w") as f:
            json.dump(game_state_json, f, sort_keys=True, indent=4)
            
        current_location_name = game_state.player.location
        current_location = game_state.game_world.get_entity_by_name(current_location_name)
        
        connected_locations = current_location.connected_locations
        print(game_state_json)
        print("\n\n" + str(connected_locations))
        return str(game_state_json) + f"\n\nconnected_locations: {connected_locations}"
        scene_description_prompt= f"""
## Instructions:
Now pretend that you are a narrator in a text-based adventure game, trying to paint rich word pictures for the
user based on the following JSON definition of the current game state. 

### Guidelines:
- DO NOT include any spoilers in the dialogue that will reveal what will happen later in the story.
- Foreshadowing is okay, sure, but don't explicitly describe upcoming plot points in detail.
- Your response should be in plain text with no formatting at all (aside from formatting necessary for sensible dialogue.). 
- Your response should be at most 2 paragraphs long 
- Your description must touch on all aspects of the game state. 
- When formulating the description, ask yourself these questions based on the JSON output that you previously generated for this part of the game:
    - What characters and items are in this location?
        - Describe these entities in your description.
    - What locations are connected to the player's current location?
        - Describe these locations in your description.
    - What part of the game is the player in?
        - Make your description appropriate to the part we are on.

### Game State:
        
{game_state_json}

Provide a vivid and immersive description of the scene from the player's perspective while 
not making it longer than 3 paragraphs.
"""
        print("Generating scene description...")
        self.ai_model.messages.append({"role": "user", "content":scene_description_prompt})
        scene_description, finish_reason = self.ai_model.generate()
        print(f"Finished generating scene description. Finish reason: {finish_reason}")
        self.ai_model.messages.append({"role": "assistant", "content":scene_description})
        return scene_description
    
    def describe_entity(self, entity, game_state):
        entity_json = entity.to_json()
        game_state_json = game_state.to_json()
        entity_description_prompt = f"""
Continue to follow the guidelines from before regarding your position as narrator.

Write at most one paragraph describing the following entity and all it's attributes that have values.

## Entity
{entity_json}

## GameState
{game_state_json}
        """
        self.ai_model.messages.append({"role":"user", "content": entity_description_prompt})
        entity_description, finish_reason = self.ai_model.generate()
        print(f"Finished generating entity description. Finish reason: {finish_reason}")
        self.ai_model.messages.append({"role":"assistant", "content":entity_description})
        return entity_description
    
    def describe_conversation(self, character, game_state):
        character_json = character.to_json()
        game_state_json = game_state.to_json()
        conversation_description_prompt = f"""
Continuing to follow the guidelines from before regarding your position as narrator. 

Write the dialogue between the following character and the player character using the
context provided in the game_state context and the previous context of this conversation.

## Character
{character_json}

## game_state
{game_state_json}
        """
        self.ai_model.messages.append({"role":"user", "content": conversation_description_prompt})
        conversation_description, finish_reason = self.ai_model.generate()
        print(f"Finished generating conversation dialogue. Finish reason: {finish_reason}")
        self.ai_model.messages.append({"role":"assistant", "content":conversation_description})
        return conversation_description