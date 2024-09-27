import pygame
import math

import pygame.draw
from utils.log import Log
from story_generation.story_generator import StoryGenerator

MIN_WIDTH = 1000
MIN_HEIGHT = 800

MAP_COLOR = (0, 255, 0)

# Defining some synonyms for text processing purposes
SYNONYMS = {
    "move": ["go", "walk", "run", "travel"],
    "talk": ["speak", "chat", "converse"],
    "pickup": ["take", "grab", "pick up"],
    "look": ["inspect", "examine", "observe"]
}

# Defining some default colors used for showing different kinds of text.
BACKGROUND = (0, 0, 0)
PLAYER = (255, 255, 255)
DESCRIPTION = (0, 255, 0)
CHARACTER = (255, 255, 0)
ACTION = (0, 255, 255)
ERROR = (255, 0, 0)

class GameEngine:
    """
    The main class of this game, GameEngine, contains attributes and methods related to:
        - Generating the story and the game state from that
        - Initializing the pygame display
        - Updating the display during gameplay
        - Rendering text and map displays
    """
    def __init__(self):
        pygame.init()
        
        # Generating the game state from the story generator class
        self.story_generator = StoryGenerator()
        self.game_state = self.story_generator.init_game_state()

        # Setting up some pygame related stuff
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen.fill((100, 100, 100))
        self.font = pygame.font.SysFont("Courier", 15)
        pygame.display.set_caption("Procedural Adventure Log")
        
        # Setting up some variables related to gameplay (like the input text and the logs)
        self.input_text = ''
        self.description_log = Log()
        self.map_log = Log()
        self.inventory_log = Log()
        self.logs = [self.description_log, self.map_log, self.inventory_log]
        self.focus = self.description_log
        
        # Arranging the text display logs on the screen accordingly and setting the default view
        self.update_layout(self.screen.get_width(), self.screen.get_height())
        self.set_log_max_displays()
        self.current_view = "log_view"

    def set_log_max_displays(self):
        """Calculates the max number of lines allowed in the current height of the log area."""
        for log in self.logs:
            total_height = log.log_area.height
            input_area_height = self.font.get_linesize() * 2
            available_log_height = total_height + input_area_height - 75
            log.max_display = available_log_height
            
    def start(self):
        # Implement the main game loop here
        player_location = self.game_state.game_world.get_entity_by_name(self.game_state.player.location)
        player_location.visited_by_player = True
        print(f"Player location {player_location.name} marked as visited: {player_location.visited_by_player}")
        self.describe_current_scene()
        running = True
        is_fullscreen = False
        pygame.key.start_text_input()
        grid = self.assign_grid_positions()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.VIDEORESIZE and not is_fullscreen:
                    # Handle window resizing when not in fullscreen mode
                    new_width, new_height = event.w, event.h
                    if new_width < MIN_WIDTH:
                        new_width= MIN_WIDTH
                    if new_height < MIN_HEIGHT:
                        new_height = MIN_HEIGHT
                    self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                    self.update_layout(new_width, new_height)
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.description_log.log_area.collidepoint(mouse_pos):
                        self.focus = self.description_log
                    elif self.map_log.log_area.collidepoint(mouse_pos):
                        self.focus = self.map_log
                    elif self.inventory_log.log_area.collidepoint(mouse_pos):
                        self.focus = self.inventory_log

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Press 'ESC' to toggle fullscreen
                        is_fullscreen = not is_fullscreen
                        if is_fullscreen:
                            # Enter fullscreen mode
                            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            # Exit fullscreen mode (resizeable window)
                            self.screen = pygame.display.set_mode((MIN_WIDTH, MIN_HEIGHT), pygame.RESIZABLE)
                        self.update_layout(self.screen.get_width(), self.screen.get_height())
                        
                    elif event.key == pygame.K_TAB:
                        if self.current_view == "log_view":
                            self.current_view = "map_view"
                        else:
                            self.current_view = "log_view"
                            
                    elif event.key == pygame.K_UP:
                        self.focus.scroll_up()
                    elif event.key == pygame.K_DOWN:
                        self.focus.scroll_down()
                        
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                        
                    elif event.key == pygame.K_RETURN:
                        player_input = self.input_text.strip()
                        self.input_text = ''
                        if player_input.lower() in ['quit', 'exit']:
                            self.add_to_log(self.description_log, "Goodbye!", DESCRIPTION)
                            running = False
                        else:
                            self.add_to_log(self.description_log, player_input, PLAYER)
                            self.process_player_input(player_input)
                    else:
                        pass
                    
                elif event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.focus.scroll_up()
                    elif event.y < 0:
                        self.focus.scroll_down()

                elif event.type == pygame.TEXTINPUT:
                    self.input_text += event.text

            self.screen.fill((100,100,100))
            
            if self.current_view == "log_view":
                for log in self.logs:
                    self.render_log(log)
            elif self.current_view == "map_view":
                self.render_grid_map(grid)
                                
            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.key.stop_text_input()
    
    def add_to_log(self, log, message, color):
        try:
            max_width = log.log_area.width - 20
            message_lines = self.wrap_text(message, self.font, max_width)
            for line in message_lines:
                log.add_message(line, color)
        except Exception as e:
            import traceback
            traceback.print_exc()
            
    def assign_grid_positions(self):
        locations = self.get_all_locations()
        grid = {}

        # Calculate the center of the map_log area for starting the grid
        start_x = self.map_log.log_area.x + self.map_log.log_area.width // 2
        start_y = self.map_log.log_area.y + self.map_log.log_area.height // 2

        def place_location(location, x, y):
            if location.name in grid:
                return

            # Assign grid position and store it
            print(f"Assigning grid position for {location.name}: ({x}, {y})")
            location.grid_position = (x, y)
            grid[location.name] = (x, y)

            # Spread connected locations evenly in 4 cardinal directions
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

            for i, connected_loc_name in enumerate(location.connected_locations):
                try:
                    connected_location = next(l for l in locations if l.name == connected_loc_name)
                    dx, dy = directions[i % len(directions)]
                    place_location(connected_location, x + dx, y + dy)
                except StopIteration:
                    print(f"Warning: Connected location '{connected_loc_name}' not found for {location.name}.")
                    pass

        # Start with the player's current location
        starting_location = self.game_state.game_world.get_entity_by_name(self.game_state.player.location)
        place_location(starting_location, start_x, start_y)

        # Ensure all unplaced locations are positioned, even if disconnected
        unplaced_locations = [loc for loc in locations if loc.name not in grid]
        offset_x, offset_y = 2, 2
        for unplaced_location in unplaced_locations:
            # Place remaining locations slightly away from the center
            print(f"Placing unconnected location: {unplaced_location.name}")
            offset_x += 2
            place_location(unplaced_location, start_x + offset_x * 3, start_y + offset_y * 3)

        return grid
        
    def assign_grid_positions(self):
        locations = self.get_all_locations()
        grid = {}

        # Calculate the center of the map_log area for starting the grid
        start_x = self.map_log.log_area.x + self.map_log.log_area.width // 2
        start_y = self.map_log.log_area.y + self.map_log.log_area.height // 2

        def place_location(location, x, y):
            if location.name in grid:
                return

            # Assign grid position and store it
            print(f"Assigning grid position for {location.name}: ({x}, {y})")
            location.grid_position = (x, y)
            grid[location.name] = (x, y)

            # Spread connected locations evenly in 4 cardinal directions
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

            for i, connected_loc_name in enumerate(location.connected_locations):
                try:
                    connected_location = next(l for l in locations if l.name == connected_loc_name)
                    dx, dy = directions[i % len(directions)]
                    grid_size = 20
                    dx *= grid_size
                    dy *= grid_size
                    place_location(connected_location, x + dx, y + dy)
                except StopIteration:
                    print(f"Warning: Connected location '{connected_loc_name}' not found for {location.name}.")
                    pass

        # Start with the player's current location
        starting_location = self.game_state.game_world.get_entity_by_name(self.game_state.player.location)
        place_location(starting_location, start_x, start_y)

        # Ensure all unplaced locations are positioned, even if disconnected
        unplaced_locations = [loc for loc in locations if loc.name not in grid]
        offset_x, offset_y = 2, 2
        for unplaced_location in unplaced_locations:
            # Place remaining locations slightly away from the center
            print(f"Placing unconnected location: {unplaced_location.name}")
            offset_x += 2
            place_location(unplaced_location, start_x + offset_x * 3, start_y + offset_y * 3)

        return grid
    
    def render_grid_map(self, grid):
        pygame.draw.rect(self.screen, BACKGROUND, self.map_log.log_area)
        grid_size = 20
        
        for location in self.get_all_locations():
            if location.visited_by_player:
                x, y = location.grid_position
                
                screen_x = self.map_log.log_area.x + x
                screen_y = self.map_log.log_area.y + y
                
                # Ensure the positions fall within the map_log area
                if screen_x < self.map_log.log_area.x or screen_x > self.map_log.log_area.right:
                    continue
                if screen_y < self.map_log.log_area.y or screen_y > self.map_log.log_area.bottom:
                    continue
                
                pygame.draw.rect(self.screen, MAP_COLOR, (screen_x, screen_y, grid_size - 5, grid_size - 5))
    
                if self.is_mouse_hovering_over_node(screen_x, screen_y, grid_size):
                    name_text = self.font.render(location.name, True, (255, 255, 255))
                    self.screen.blit(name_text, (screen_x + grid_size +5, screen_y))
                    
                # Draw lines between connected locations
                for connected_loc_name in location.connected_locations:
                    try:
                        connected_location = next(l for l in self.get_all_locations() if l.name == connected_loc_name)
                    except StopIteration as e:
                        self.add_to_log(self.description_log, f"{connected_loc_name}: {e}", ERROR)
                    if connected_location.visited_by_player:
                        conn_x, conn_y = connected_location.grid_position
                        screen_conn_x = self.map_log.log_area.x + conn_x
                        screen_conn_y = self.map_log.log_area.y + conn_y
                        pygame.draw.line(self.screen, MAP_COLOR, 
                                         (int(screen_x + grid_size // 2 - 2.5), int(screen_y + grid_size // 2 - 2.5)), 
                                         (int(screen_conn_x + grid_size // 2 - 2.5), int(screen_conn_y + grid_size // 2 - 5)), 4)
                        
    def is_mouse_hovering_over_node(self, node_x, node_y, grid_size):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return node_x <= mouse_x <= node_x + grid_size and node_y <= mouse_y <= node_y + grid_size
    
    def render_log(self, log):
        try:
            if log != self.map_log:
                pygame.draw.rect(self.screen, (0, 0, 0), log.log_area)
                visible_log = log.get_visible_log()
                y_offset = log.log_area.y + 10
                max_width = log.log_area.width - 20
                total_height = log.log_area.height
                input_area_height = self.font.get_linesize() * 2
                available_log_height = total_height + input_area_height - 75
                log.max_display = (available_log_height // self.font.get_linesize())

                for log_message in visible_log:
                    rendered_text = self.font.render(log_message[0], True, log_message[1])
                    self.screen.blit(rendered_text, (log.log_area.x + 10, y_offset))
                    y_offset += self.font.get_linesize()

                if log == self.description_log:
                    input_lines = self.wrap_text(" > " + self.input_text, self.font, max_width)
                    for line in input_lines:
                        input_prompt = self.font.render(line, True, (255, 255, 255))
                        self.screen.blit(input_prompt, (10, y_offset))
                        y_offset += self.font.get_linesize()
                
        except Exception as e:
            print(f"Exception in render_log: {e}")
            import traceback
            traceback.print_exc()

    def wrap_text(self, text, font, max_width):
        try:
            words = text.split(' ')
            lines = []
            current_line = ''
            for word in words:
                word = word.strip()
                if "\n\n" in word:
                    line_split=word.split("\n\n")
                    test_line = current_line + (' ' if current_line else '') + line_split[0]
                    lines.append(test_line)
                    lines.append("")
                    current_line = line_split[1]
                else:
                    test_line = current_line + (' ' if current_line else '') + word
                    text_width, _ = font.size(test_line)
                    if text_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
            if current_line:
                lines.append(current_line)
            return lines
        except Exception as e:
            print(f"Exception in wrap_text: {e}")
            import traceback
            traceback.print_exc()
            return []
        
    def update_layout(self, new_width, new_height):
        self.description_log.log_area = pygame.Rect(
            10, 10, 
            int(new_width * 0.75) - 20, new_height - 20
        )
        self.map_log.log_area = pygame.Rect(
            10, 10,
            new_width - 20, new_height - 20
        )
        self.inventory_log.log_area = pygame.Rect(
            new_width - int(new_width * 0.25) + 10, 10,
            int(new_width * 0.25) - 20, new_height - 20
        )

    def process_player_input(self, player_input):
        command = player_input.strip()
        if command == "look":
            print(self.game_state.to_json())
        elif command.startswith("move to"):
            location_name = command[8:].strip()
            self.move_player_to(location_name)
        elif command.startswith("inspect"):
            entity_name = command[7:].strip()
            self.inspect_entity(entity_name)
        elif command.startswith("take"):
            entity_name = command[4:].strip()
            self.take_item(entity_name)
        elif command.startswith("talk to"):
            character_name = command[7:].strip()
            self.talk_to(character_name)
        else:
            self.add_to_log(self.description_log, "Unknown command.", ERROR)

    def describe_current_scene(self):
        try:
            description = self.story_generator.describe_scene(self.game_state)
            self.add_to_log(self.description_log, description, DESCRIPTION)
        except Exception as e:
            import traceback
            traceback.print_exc()

    def move_player_to(self, location_name):
        destination = self.game_state.game_world.get_entity_by_name(location_name)
        if destination and destination.entity_type == 'location':
            destination.visited_by_player = True
            
            if destination.grid_position is None:
                self.assign_grid_positions()
                
            self.game_state.update_current_location(location_name)
            self.add_to_log(self.description_log, f"\nYou move to {destination.name}.", PLAYER)
            self.add_to_log(self.description_log, self.describe_current_scene(), DESCRIPTION)
        else:
            self.add_to_log(self.description_log, "You can't go there from here.", ERROR)

    def inspect_entity(self, entity_name):
        entity = self.game_state.game_world.get_entity_by_name(entity_name)
        if entity and entity in self.get_nearby_entities():
            self.add_to_log(self.description_log, self.story_generator.describe_entity(entity, self.game_state), DESCRIPTION)
        else:
            self.add_to_log(self.description_log, "There's nothing like that here.", ERROR)
        
    def take_item(self, item_name):
        item = self.game_state.game_world.get_entity_by_name(item_name)
        if item and item in self.get_nearby_entities():
            self.add_to_log(self.description_log, f"\nYou take it.", PLAYER)
            self.game_state.player.inventory.add_item(item_name)
            self.inventory_log.clear()
            self.add_to_log(self.inventory_log, f"\n{item_name} was added to your inventory.", ACTION)
            items_for_log = self.game_state.player.inventory.display_items()
            self.add_to_log(self.inventory_log, items_for_log, ACTION)
        else:
            self.add_to_log(self.description_log, "You can't find that here.", ERROR)
            
    def talk_to(self, character_name):
        character = self.game_state.game_world.get_entity_by_name(character_name)
        if character and character in self.get_nearby_entities():
            self.add_to_log(self.description_log, self.story_generator.describe_conversation(character, self.game_state), CHARACTER)

    def get_nearby_entities(self):
        return self.game_state.get_nearby_entities()
    
    def get_all_characters(self):
        return self.game_state.get_all_characters()
    
    def get_all_locations(self):
        return self.game_state.get_all_locations()
    
    def get_all_items(self):
        return self.game_state.get_all_items()

    def update_game_state(self):
        # Update the game state based on player actions
        pass