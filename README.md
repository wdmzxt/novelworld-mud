# NovelWorld MUD

NovelWorld MUD is a local-first bilingual MUD engine for turning novels into playable text adventure worlds.

Turn novels into playable bilingual text adventure worlds.

## 中文简介

NovelWorld MUD 是一个本地优先的双语文字冒险 MUD 引擎。它把小说中的地点、人物、物品、任务和事件组织成可交互的 `world.json` 世界，让玩家通过命令探索故事世界。

当前正式版本是 v0.8。该版本不使用 AI、不使用 SQLite、不使用 ChromaDB，也不需要 API Key；它专注于一个可运行、可保存、可验证、可双语展示的小型本地 MUD 原型。

## English Intro

NovelWorld MUD is a local-first bilingual text adventure engine. It represents a novel world as structured data, then lets players explore locations, talk to NPCs, collect items, trigger events, complete quests, and save progress.

The current official version is v0.8. It does not use AI, SQLite, ChromaDB, or any API keys. The focus is a small but playable local MUD prototype with data-driven world content and Chinese/English presentation.

## Current v0.8 Features

- Basic MUD prototype
- Command-line gameplay loop
- Chinese and English language selection
- Bilingual location, NPC, item, quest, and event text
- Save/load system using local JSON
- Quest system
- Event system
- Data-driven quests and events
- World schema validation
- Expanded demo world: Qingshi Village and the back mountain
- Local-first design with no network dependency

## Quick Start

```bash
python main.py
```

Then select a language:

```text
请选择语言 / Please select language:
1. 中文
2. English
```

## Commands

| English | 中文 | Description |
| --- | --- | --- |
| `look` | `查看` | Show current location, description, NPCs, items, and exits |
| `go <location>` | `去 <地点>` | Move to a connected location |
| `talk <npc>` | `对话 <人物>` | Talk to an NPC in the current location |
| `take <item>` | `拾取 <物品>` | Pick up an item in the current location |
| `bag` | `背包` | Show inventory |
| `status` | `状态` | Show player status |
| `quests` | `任务` | Show active and completed quests |
| `events` | `事件` | Show triggered events |
| `save` | `保存` | Save current game state |
| `load` | `读取` | Load saved game state |
| `help` | `帮助` | Show command help |
| `quit` | `退出` | Exit the game |

## Demo Transcript

```text
NovelWorld MUD v0.8
请选择语言 / Please select language:
1. 中文
2. English
> 2

Location
  Qingshi Village Gate
Description
  A weathered stone marker stands at the village gate...
People
  Village Child
Items
  None
Exits
  Village Road, Back Mountain Entrance

> talk village child
Village Child:
Yesterday I saw someone go into the back mountain, but they never came back.

> go village road
You arrive at: Village Road

> talk old village chief
Old Village Chief:
Traveler, the back mountain has not been peaceful lately...
Quest accepted: Investigate the Strange Sounds.

> go back mountain entrance
You find several fresh claw marks in the mud...
Quest completed: Investigate the Strange Sounds. You received: Village Chief's Token.

> save
Game saved.
```

See [examples/demo_transcript.md](examples/demo_transcript.md) for a longer bilingual walkthrough.

## Project Vision

NovelWorld MUD explores a simple idea: novels can become playable worlds.

The long-term goal is to build a pipeline where authors or readers can transform novel chapters into structured, interactive worlds. The engine should remain local-first, inspectable, and data-driven, with optional AI narration added only after deterministic rules, world schema, save/load, and authoring flows are stable.

Design principles:

- 小说是世界: the novel provides places, characters, conflicts, tone, and lore.
- 规则引擎是裁判: the rules engine resolves actions and state changes.
- 数据库是记忆: persistence stores player state, world state, history, and memory.
- AI 是叙事者: future AI should narrate and enrich prose, not replace game rules.

## Roadmap

Completed:

- v0.1 Basic playable MUD prototype
- v0.2 JSON save/load system
- v0.3 Basic quest system
- v0.4 Basic event system
- v0.5 Data-driven quests and events
- v0.6 World schema validation
- v0.7 Expanded demo world content
- v0.8 Bilingual language support

Planned:

- v0.9 Optional LLM narration
- v1.0 Novel import prototype
- v1.1 GUI prototype
- v1.2 Novel-to-world extraction

## Project Structure

```text
novelworld-mud/
├── main.py
├── engine/
│   ├── actions.py
│   ├── command_parser.py
│   ├── game.py
│   ├── i18n.py
│   ├── player.py
│   ├── save_manager.py
│   ├── world_loader.py
│   └── world_validator.py
├── data/
│   └── world_demo.json
├── saves/
├── docs/
│   ├── architecture.md
│   ├── design.md
│   ├── promotion.md
│   ├── roadmap.md
│   └── world_schema.md
└── examples/
    └── demo_transcript.md
```

## Security / Privacy

- Runs locally from the command line.
- Does not require API keys.
- Does not call external AI services in v0.8.
- Does not use SQLite, ChromaDB, or network storage in v0.8.
- Save files are local JSON files under `saves/`.
- Demo world data is local JSON under `data/`.

## License

License: TBD.

This repository currently uses a placeholder license notice. Add a formal open-source license before public distribution or reuse.
