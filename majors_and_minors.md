# Majors and Minors

Prioritized list of what to tackle next to turn this into a polished vertical slice.

---

## Major

### 1. Fix `describe_scene()` so the player sees narrated prose, not raw JSON

`story_generator.py:349` has an early `return` that bypasses the AI narration prompt already
written below it. The player currently sees a dump of the game state dict and a connections
list. Removing that early return and letting the prompt run is the single biggest thing
that makes this feel like a real game.

### 2. Implement story progression conditions

`story_generator.py:315` has a `TODO` — progression conditions exist in every part of
`story.json` but nothing checks them. The game is permanently stuck in Part 1's entity
set. Need a system that evaluates each part's `progression_condition` (e.g. "Alex picks
up the keycard") against player actions and unlocks the next part's characters, locations,
and items into the `GameWorld` when conditions are met.

### 3. Validate movement against connected locations

`game_engine.py:412-424` — `move_player_to()` checks that the destination exists and is
a location, but never checks whether it's actually reachable from the player's current
location. The player can teleport anywhere. Should verify
`destination.name in current_location.connected_locations` and show the list of valid
exits on failure.

### 4. Wire up the SYNONYMS dict for natural language input

`game_engine.py:14-19` defines synonyms ("go", "walk", "run" → "move", etc.) but
`process_player_input()` only does exact prefix matching. "go to the lobby" or "grab the
letter" should work. Normalize the first word of input against the synonyms dict before
dispatching.

### 5. Fix `set_nearby_entities()` — it accumulates instead of resetting

`game_state.py:35-39` — each call appends to `self.nearby_entities` without clearing the
list first. Every time the player moves, old entities remain and the list grows forever.
Add `self.nearby_entities = []` (or equivalent clear) at the top of the method.

### 6. Show a loading screen during story generation

`GameEngine.__init__()` triggers multiple sequential AI calls (outline + up to 7 part
conversions) before the pygame window displays anything. The window is blank and
unresponsive for a long time. Render a loading screen with generation progress
("Generating Part 3 of 7...") so the user knows it's working.

### 7. Make the AI backend configurable

`story_generator.py:11` hardcodes `OpenSourceAIModel()`. Both the OpenAI and open-source
backends exist in `ai_model.py` but there's no way to switch between them. Add a config
mechanism (env var, CLI flag, or config file) so users can choose which backend to use
at startup.

### 8. Add a "help" command that lists available actions

There's no way for the player to discover what commands exist. `process_player_input()`
silently returns "Unknown command." with no guidance. A `help` command that prints the
available verbs (move to, inspect, take, talk to, look, quit) and their usage would make
the game playable without reading the source code.

### 9. Handle AI generation failures without crashing

`story_generator.py:218` calls `json.loads(part_json)` on raw AI output with no error
handling. If the AI returns malformed JSON (extra markdown fences, truncated output, etc.),
the game crashes during startup. Need retry logic, JSON repair attempts, or a graceful
fallback (e.g. re-prompt the AI asking it to fix the output).

### 10. Add save and load so a playthrough survives across sessions

`game_state.json` is written to disk every scene change but never read back. Implement a
`save` command that serializes the full game state (player location, inventory, visited
flags, current story part) and a way to `load` it at startup so the player doesn't lose a
long AI-generated story when they close the game.

---

## Minor

### 1. Remove the duplicate `assign_grid_positions` method

`game_engine.py:178-220` and `game_engine.py:222-267` are two definitions of the same
method. The second silently overwrites the first. Delete the first one (the second adds
`grid_size` scaling to the direction offsets, which is the correct version).

### 2. Add a `requirements.txt`

Dependencies (pygame, openai, transformers, torch, jsonschema) are undocumented. A
`requirements.txt` lets anyone set up the project with `pip install -r requirements.txt`.

### 3. Fix the mutable default argument in `Entity.__init__`

`entity.py:4` — `connected_location_names=[]` is a shared mutable default. All entities
created without explicit connections silently share the same list object. Change to
`connected_location_names=None` and default to `[]` inside the body.

### 4. Remove `print(os.environ)` from `AIModel.__init__`

`ai_model.py:61` dumps the entire environment (potentially including secrets/tokens) to
stdout every time the OpenAI backend is initialized. Delete it.

### 5. Fix the `look` command to display in the game window

`game_engine.py:388` — `look` calls `print()` to the terminal instead of rendering to the
description log. Should call `self.describe_current_scene()` or at minimum display the
nearby entities and connected locations in the description log.

### 6. Highlight the player's current location on the map

`render_grid_map()` draws all visited locations as identical green squares. The player's
current position should be visually distinct (different color, pulsing, or larger) so the
map is actually useful for orientation.

### 7. Add `__init__.py` files to all packages

`game/`, `entities/`, `ai_model/`, `story_generation/`, and `utils/` all lack them.
While implicit namespace packages work, explicit `__init__.py` files prevent subtle import
issues and make the package structure clear.

### 8. Gitignore the runtime-generated files

`story.json` and `game_state.json` are generated fresh on every run but are currently
tracked by git. Add them to `.gitignore` so they don't create noise in diffs.

### 9. Fix input prompt x-position to be relative to the log area

`game_engine.py:331` renders the `> ` input prompt at hardcoded `x=10` instead of using
`log.log_area.x + 10`. When the window is resized, the prompt can misalign from the
description log it belongs to.

### 10. Add a blinking cursor to the text input line

The input prompt (`> `) has no visible cursor, so it's not obvious the game is waiting for
typed input. A simple blinking `_` or `|` appended to `self.input_text` on a timer would
make the UI feel responsive.
