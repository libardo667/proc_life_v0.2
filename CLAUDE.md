# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Procedural text-based adventure game where an AI model generates the entire story (characters, locations, items, quests) as structured JSON, which is then processed into a playable game rendered via pygame in a retro terminal style. The game includes a text log view, an inventory panel, and a grid-based map view toggled with Tab.

## Running the Game

```bash
python main.py
```

Requires `pygame`, `openai`, `transformers`, `torch`, and `jsonschema`. No requirements.txt exists yet — dependencies must be installed manually.

The game needs either an OpenAI API key (env var `$OPENAI_API_KEY$`) or a HuggingFace token (env var `$OPENSOURCE_TOKEN$`) depending on which AI model class is used.

## Architecture

### Startup Flow

`main.py` → `GameEngine.__init__()` → `StoryGenerator.init_game_state()`:
1. AI generates a free-text story outline (up to 7 parts)
2. Outline is split on double newlines into parts
3. Each part is sent back to the AI to produce structured JSON matching `story_generation/schema.json`
4. JSON is validated with jsonschema, then parsed into `Entity` objects populating a `GameWorld`
5. A `GameState` is created with player reference, location tracking, and nearby entity resolution
6. `GameEngine.start()` enters the pygame event loop

### Key Modules

- **`game/game_engine.py`** — Pygame event loop, rendering (log view + grid map view), input processing, command dispatch. Contains command synonyms dict and color constants. Has a duplicate `assign_grid_positions` method (second overwrites first).
- **`story_generation/story_generator.py`** — Orchestrates AI-driven story generation: outline → parts → JSON → entities. Also handles runtime scene/entity/conversation description generation via AI prompts. Writes `story.json` and `game_state.json` to disk.
- **`story_generation/schema.json`** — JSON Schema (draft-07) defining the expected story structure: parts keyed as `part_1`, `part_2`, etc., each with characters, locations, items, and progression conditions.
- **`ai_model/ai_model.py`** — Two AI backend classes: `AIModel` (OpenAI gpt-4o) and `OpenSourceAIModel` (HuggingFace transformers, default model `allenai/MolmoE-1B-0924`). Both maintain conversation history in `self.messages` and expose `generate()`.
- **`entities/entity.py`** — Unified `Entity` class with factory classmethods (`main_character_entity`, `character_entity`, `location_entity`, `item_entity`). Tracks name, description, location, type, connections, inventory, visited/used flags, and grid position.
- **`entities/game_world.py`** — `GameWorld` holds a flat list of all entities with lookup methods by name, location, or type.
- **`game/game_state.py`** — `GameState` tracks the player entity, current location, nearby entities, and serializes to JSON for AI prompts.
- **`utils/log.py`** — Scrollable `Log` class for the pygame text display panels.
- **`utils/inventory.py`** — Simple list-based `Inventory` for player items.

### Player Commands

Processed in `GameEngine.process_player_input()`: `look`, `move to <location>`, `inspect <entity>`, `take <item>`, `talk to <character>`, `quit`/`exit`.

### Story JSON Structure

```
story.json: { "story": { "part_1": { description, relevant_characters[], relevant_locations[], relevant_items[], progression_condition }, ... } }
```

Each location has `connections` (list of location name strings). Characters and items have `location` (string name). The player character is identified by `is_player_character: true`.

## Current State / Known Issues

- `StoryGenerator` currently defaults to `OpenSourceAIModel` — swap to `AIModel` for OpenAI usage
- `describe_scene()` has an early return before the AI prompt code (returns raw JSON + connections instead of a narrated description)
- `assign_grid_positions` is defined twice in `GameEngine`; the second definition silently overwrites the first
- Progression conditions from `story.json` are parsed but not yet processed (`TODO` in `get_entities_from_story_json`)
- No `__init__.py` files exist in the packages — relies on implicit namespace packages
- No tests or linting configuration exists
- `game_state.json` and `story.json` are written to the repo root at runtime
