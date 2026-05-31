# Architecture

NovelWorld MUD v0.8 is a local command-line MUD engine built around structured world data.

```text
data/world_demo.json
        |
        v
engine/world_loader.py
        |
        v
engine/world_validator.py
        |
        v
MUD Engine
        |
        v
Player commands
        |
        v
Locations / NPCs / Items / Quests / Events
        |
        v
Save / Load
```

## Data Flow

`world_demo.json` defines the playable world: locations, NPCs, items, quests, events, and bilingual display text.

`world_loader` reads the JSON file from disk.

`world_validator` checks the world schema before the game starts. If required fields or references are invalid, the game exits with a clear validation error.

The MUD engine runs the command loop, parses player input, resolves actions, updates player/world state, and prints localized output.

Save/load stores player state and current world state in local JSON.

## Core Runtime Concepts

- Locations define movement and available NPCs/items.
- NPCs provide dialogue and can trigger quests.
- Items can be picked up and stored in the player bag.
- Quests are data-driven and progress through configured triggers.
- Events are data-driven and trigger once when conditions are met.
- Bilingual text is resolved at display time through the selected language.

## Future Route

- Optional LLM narration: add AI-generated prose as an optional narration layer while keeping rules deterministic.
- Novel-to-world generation: convert novel chapters into structured world JSON.
- Local vector memory: experiment with local memory for lore, history, and contextual recall.
- GUI prototype: build a visual interface for playing and authoring worlds.
