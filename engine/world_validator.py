from typing import Any


REQUIRED_TOP_LEVEL_FIELDS = ["start_location", "locations", "npcs", "items", "quests", "events"]
REQUIRED_LOCATION_FIELDS = ["name", "description", "exits", "npcs", "items"]
REQUIRED_NPC_FIELDS = ["name", "description", "dialogue"]
REQUIRED_ITEM_FIELDS = ["name", "description"]
REQUIRED_QUEST_FIELDS = [
    "id",
    "name",
    "giver_npc",
    "trigger_type",
    "trigger_target",
    "objective",
    "complete_type",
    "complete_target",
    "reward_item",
    "reward_text",
]
REQUIRED_EVENT_FIELDS = ["id", "name", "trigger_type", "trigger_target", "location", "description"]


def validate_world(world: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(world, dict):
        return ["world 必须是 dict"]

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in world:
            errors.append(f"缺少 {field}")

    locations = world.get("locations")
    npcs = world.get("npcs")
    items = world.get("items")
    quests = world.get("quests")
    events = world.get("events")

    if "locations" in world and not isinstance(locations, dict):
        errors.append("locations 必须是 dict")
    if "npcs" in world and not isinstance(npcs, dict):
        errors.append("npcs 必须是 dict")
    if "items" in world and not isinstance(items, dict):
        errors.append("items 必须是 dict")
    if "quests" in world and not isinstance(quests, list):
        errors.append("quests 必须是 list")
    if "events" in world and not isinstance(events, list):
        errors.append("events 必须是 list")

    if errors:
        return errors

    assert isinstance(locations, dict)
    assert isinstance(npcs, dict)
    assert isinstance(items, dict)
    assert isinstance(quests, list)
    assert isinstance(events, list)

    start_location = world.get("start_location")
    if start_location not in locations:
        errors.append(f"start_location 不存在于 locations 中：{start_location}")

    _validate_locations(locations, npcs, items, errors)
    _validate_npcs(npcs, errors)
    _validate_items(items, errors)
    _validate_quests(quests, locations, npcs, items, errors)
    _validate_events(events, locations, errors)

    return errors


def _validate_locations(
    locations: dict[str, Any],
    npcs: dict[str, Any],
    items: dict[str, Any],
    errors: list[str],
) -> None:
    for location_id, location in locations.items():
        if not isinstance(location, dict):
            errors.append(f"location {location_id} 必须是 dict")
            continue

        for field in REQUIRED_LOCATION_FIELDS:
            if field not in location:
                errors.append(f"location {location_id} 缺少 {field}")

        _validate_text_field(location, "name", f"location {location_id}", errors)
        _validate_text_field(location, "description", f"location {location_id}", errors)

        exits = location.get("exits")
        location_npcs = location.get("npcs")
        location_items = location.get("items")

        if "exits" in location and not isinstance(exits, dict):
            errors.append(f"location {location_id} 的 exits 必须是 dict")
        if "npcs" in location and not isinstance(location_npcs, list):
            errors.append(f"location {location_id} 的 npcs 必须是 list")
        if "items" in location and not isinstance(location_items, list):
            errors.append(f"location {location_id} 的 items 必须是 list")

        if isinstance(exits, dict):
            for exit_name, target_location_id in exits.items():
                if target_location_id not in locations:
                    errors.append(f"location {location_id} 的出口 {exit_name} 指向不存在的 location：{target_location_id}")

        if isinstance(location_npcs, list):
            for npc_id in location_npcs:
                if npc_id not in npcs:
                    errors.append(f"location {location_id} 引用了不存在的 npc：{npc_id}")

        if isinstance(location_items, list):
            for item_id in location_items:
                if item_id not in items:
                    errors.append(f"location {location_id} 引用了不存在的 item：{item_id}")


def _validate_npcs(npcs: dict[str, Any], errors: list[str]) -> None:
    for npc_id, npc in npcs.items():
        if not isinstance(npc, dict):
            errors.append(f"npc {npc_id} 必须是 dict")
            continue

        for field in REQUIRED_NPC_FIELDS:
            if field not in npc:
                errors.append(f"npc {npc_id} 缺少 {field}")

        _validate_text_field(npc, "name", f"npc {npc_id}", errors)
        _validate_text_field(npc, "description", f"npc {npc_id}", errors)
        dialogue = npc.get("dialogue")
        if "dialogue" in npc and not isinstance(dialogue, list):
            errors.append(f"npc {npc_id} 的 dialogue 必须是 list")
        elif isinstance(dialogue, list):
            for line_index, line in enumerate(dialogue):
                _validate_text_value(line, f"npc {npc_id} dialogue #{line_index}", errors)


def _validate_items(items: dict[str, Any], errors: list[str]) -> None:
    for item_id, item in items.items():
        if not isinstance(item, dict):
            errors.append(f"item {item_id} 必须是 dict")
            continue

        for field in REQUIRED_ITEM_FIELDS:
            if field not in item:
                errors.append(f"item {item_id} 缺少 {field}")

        _validate_text_field(item, "name", f"item {item_id}", errors)
        _validate_text_field(item, "description", f"item {item_id}", errors)


def _validate_quests(
    quests: list[Any],
    locations: dict[str, Any],
    npcs: dict[str, Any],
    items: dict[str, Any],
    errors: list[str],
) -> None:
    for index, quest in enumerate(quests):
        quest_label = _entry_label("quest", index, quest)
        if not isinstance(quest, dict):
            errors.append(f"{quest_label} 必须是 dict")
            continue

        for field in REQUIRED_QUEST_FIELDS:
            if field not in quest:
                errors.append(f"{quest_label} 缺少 {field}")

        for field in ["name", "objective", "reward_text"]:
            _validate_text_field(quest, field, quest_label, errors)

        quest_id = quest.get("id")
        if not quest_id:
            errors.append(f"{quest_label} 的 id 不能为空")

        if quest.get("giver_npc") not in npcs:
            errors.append(f"{quest_label} 的 giver_npc 不存在：{quest.get('giver_npc')}")
        if quest.get("trigger_type") != "talk":
            errors.append(f"{quest_label} 的 trigger_type 暂时只允许 talk")
        if quest.get("trigger_target") not in npcs:
            errors.append(f"{quest_label} 的 trigger_target 不存在：{quest.get('trigger_target')}")
        if quest.get("complete_type") != "enter_location":
            errors.append(f"{quest_label} 的 complete_type 暂时只允许 enter_location")
        if quest.get("complete_target") not in locations:
            errors.append(f"{quest_label} 的 complete_target 不存在：{quest.get('complete_target')}")
        if quest.get("reward_item") not in items:
            errors.append(f"{quest_label} 的 reward_item 不存在：{quest.get('reward_item')}")


def _validate_events(events: list[Any], locations: dict[str, Any], errors: list[str]) -> None:
    for index, event in enumerate(events):
        event_label = _entry_label("event", index, event)
        if not isinstance(event, dict):
            errors.append(f"{event_label} 必须是 dict")
            continue

        for field in REQUIRED_EVENT_FIELDS:
            if field not in event:
                errors.append(f"{event_label} 缺少 {field}")

        for field in ["name", "location", "description"]:
            _validate_text_field(event, field, event_label, errors)

        event_id = event.get("id")
        if not event_id:
            errors.append(f"{event_label} 的 id 不能为空")

        if event.get("trigger_type") != "enter_location":
            errors.append(f"{event_label} 的 trigger_type 暂时只允许 enter_location")
        if event.get("trigger_target") not in locations:
            errors.append(f"{event_label} 的 trigger_target 不存在：{event.get('trigger_target')}")


def _entry_label(kind: str, index: int, entry: Any) -> str:
    if isinstance(entry, dict) and entry.get("id"):
        return f"{kind} {entry['id']}"
    return f"{kind} #{index}"


def _validate_text_field(entry: dict[str, Any], field: str, label: str, errors: list[str]) -> None:
    if field not in entry:
        return
    _validate_text_value(entry[field], f"{label} 的 {field}", errors)


def _validate_text_value(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, str):
        return
    if isinstance(value, dict):
        if "zh" not in value:
            errors.append(f"{label} 缺少 zh")
        if "en" not in value:
            errors.append(f"{label} 缺少 en")
        if "zh" in value and not isinstance(value["zh"], str):
            errors.append(f"{label}.zh 必须是字符串")
        if "en" in value and not isinstance(value["en"], str):
            errors.append(f"{label}.en 必须是字符串")
        return
    errors.append(f"{label} 必须是字符串或包含 zh/en 的 dict")
