# World Schema

`data/world_demo.json` is the structured world definition used by NovelWorld MUD. The v0.6 schema makes world data stable enough for future tooling that turns novel text into a playable `world.json`.

## Top-Level Fields

- `start_location`: ID of the location where a new player starts. It must exist in `locations`.
- `locations`: Dictionary of location IDs to location objects.
- `npcs`: Dictionary of NPC IDs to NPC objects.
- `items`: Dictionary of item IDs to item objects.
- `quests`: List of quest configuration objects.
- `events`: List of event configuration objects.

## locations

Each entry in `locations` uses a location ID as its key. The value has:

- `id`: Unique location ID. It should match the dictionary key.
- `name`: Display name shown to the player.
- `description`: Text shown by `look` / `查看`.
- `exits`: Dictionary mapping player-facing exit names to target location IDs.
- `npcs`: List of NPC IDs currently present in this location.
- `items`: List of item IDs currently present in this location.

## npcs

Each entry in `npcs` uses an NPC ID as its key. The value has:

- `id`: Unique NPC ID. It should match the dictionary key.
- `name`: Display name used by commands such as `talk 老村长`.
- `description`: Short NPC description.
- `dialogue`: List of dialogue lines shown when the player talks to the NPC.

## items

Each entry in `items` uses an item ID as its key. The value has:

- `id`: Unique item ID. It should match the dictionary key.
- `name`: Display name used by inventory and pickup commands.
- `description`: Short item description.

## quests

Each quest object has:

- `id`: Unique quest ID.
- `name`: Display name.
- `giver_npc`: NPC ID that gives the quest.
- `trigger_type`: Quest trigger type. v0.6 supports `talk`.
- `trigger_target`: NPC ID that triggers the quest.
- `objective`: Text shown in the task list.
- `complete_type`: Completion trigger type. v0.6 supports `enter_location`.
- `complete_target`: Location ID that completes the quest.
- `reward_item`: Item ID awarded on completion.
- `reward_text`: Player-facing reward name.

## events

Each event object has:

- `id`: Unique event ID.
- `name`: Display name.
- `trigger_type`: Event trigger type. v0.6 supports `enter_location`.
- `trigger_target`: Location ID that triggers the event.
- `location`: Player-facing location name shown in the event log.
- `description`: Text printed when the event triggers.

## Example

```json
{
  "start_location": "village_path",
  "locations": {
    "village_path": {
      "id": "village_path",
      "name": "村中小路",
      "description": "泥土路穿过低矮的屋舍。",
      "exits": {
        "后山入口": "back_mountain"
      },
      "npcs": ["old_chief"],
      "items": ["rusty_short_sword"]
    }
  },
  "npcs": {
    "old_chief": {
      "id": "old_chief",
      "name": "老村长",
      "description": "须发皆白的老人。",
      "dialogue": ["后山近来不太平。"]
    }
  },
  "items": {
    "rusty_short_sword": {
      "id": "rusty_short_sword",
      "name": "生锈短刀",
      "description": "刀刃布满锈迹。"
    },
    "village_chief_token": {
      "id": "village_chief_token",
      "name": "村长的信物",
      "description": "刻着青石村纹样的木制信物。"
    }
  },
  "quests": [
    {
      "id": "investigate_mountain",
      "name": "调查后山异响",
      "giver_npc": "old_chief",
      "trigger_type": "talk",
      "trigger_target": "old_chief",
      "objective": "前往后山入口调查异响",
      "complete_type": "enter_location",
      "complete_target": "back_mountain",
      "reward_item": "village_chief_token",
      "reward_text": "村长的信物"
    }
  ],
  "events": [
    {
      "id": "find_claw_marks",
      "name": "发现兽爪痕迹",
      "trigger_type": "enter_location",
      "trigger_target": "back_mountain",
      "location": "后山入口",
      "description": "你在泥地里发现了几道新鲜的兽爪印。"
    }
  ]
}
```

This schema will be the target format for future novel-to-world generation. A generator can extract places, characters, items, quests, and events from a novel, then produce a validated `world.json` for the engine.
