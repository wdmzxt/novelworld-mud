# NovelWorld MUD Roadmap

## v0.1 Command-Line Skeleton

- Create project structure.
- Add a local command-line game loop.
- Define planned commands: `look`, `go <地点>`, `talk <人物>`, `take <物品>`, `bag`, `status`, `help`, `quit`.
- Add a JSON demo world for 青石村.
- Avoid AI, ChromaDB, and SQLite.

## v0.2 Basic Playable Demo

- Implement `look`, `go`, `talk`, `take`, `bag`, and `status`.
- Add simple location transitions.
- Add item pickup and inventory state.
- Add basic NPC dialogue lookup.

## v0.3 Save and Load

- Add local save files under `saves/`.
- Restore player location, inventory, and status.
- Keep save format human-readable.

## v0.4 Rule Engine

- Add action validation.
- Add simple conditions for locations, items, and NPC interactions.
- Separate command parsing from rule resolution.

## v0.5 Novel Import Prototype

- Define a novel-to-world data schema.
- Add tooling to manually convert chapters into locations, characters, items, and events.
- Keep generated world data editable.

## v0.6 AI Narrator Prototype

- Add an optional AI narration layer.
- Keep rules deterministic and let AI focus on prose generation.
- Record player history for contextual narration.

## v0.7 Memory Layer

- Introduce a structured memory store.
- Track player choices, discovered facts, NPC attitudes, and unresolved plot threads.
- Evaluate ChromaDB or another vector store only when needed.

## v0.8 Persistent World State

- Add durable world state storage.
- Evaluate SQLite for structured state.
- Support longer campaigns across multiple sessions.

## v0.9 Authoring Tools

- Add validation for world JSON files.
- Add helpers for creating locations, NPCs, items, exits, and quests.
- Improve documentation for world authors.

## v1.0 Playable AI-Powered Novel World

- Provide a complete playable loop with rules, memory, persistence, and AI narration.
- Support importing or authoring a small novel world.
- Ship a stable local single-player experience.
