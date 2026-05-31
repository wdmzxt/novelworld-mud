from __future__ import annotations

from collections.abc import Callable
from typing import Any

from engine.command_parser import Command
from engine.i18n import get_text, match_entity_by_name
from engine.player import Player


HELP_TEXT = {
    "zh": """可用命令与示例：
look / 查看：查看当前位置
  示例：查看
go <地点> / 去 <地点>：移动到指定地点
  示例：去 后山入口
talk <人物> / 对话 <人物>：和人物对话
  示例：对话 老村长
take <物品> / 拾取 <物品>：拾取当前位置的物品
  示例：拾取 火把
bag / 背包：查看背包
  示例：背包
status / 状态：查看玩家状态
  示例：状态
quests / 任务：查看当前任务
  示例：任务
events / 事件：查看已触发事件
  示例：事件
save / 保存：保存当前游戏
  示例：保存
load / 读取：读取存档
  示例：读取
help / 帮助：显示帮助
  示例：帮助
quit / 退出：退出游戏
  示例：退出""",
    "en": """Commands and examples:
look: show the current location
  Example: look
go <location>: move to a location
  Example: go back mountain entrance
talk <npc>: talk to an NPC
  Example: talk old village chief
take <item>: pick up an item here
  Example: take torch
bag: show inventory
  Example: bag
status: show player status
  Example: status
quests: show quests
  Example: quests
events: show triggered events
  Example: events
save: save the game
  Example: save
load: load the save
  Example: load
help: show help
  Example: help
quit: quit the game
  Example: quit""",
}


LABELS = {
    "zh": {
        "missing_go": "你想去哪里？",
        "missing_talk": "你想和谁说话？",
        "missing_take": "你想拾取什么？",
        "unknown": "未知命令：{name}。输入 help 查看可用命令。",
        "bye": "再会。",
        "current_location": "当前位置",
        "description": "描述",
        "people": "人物",
        "items": "物品",
        "exits": "出口",
        "none": "无",
        "bad_go": "目标地点不存在或不在出口中：{target}",
        "bad_npc": "NPC 不在当前位置：{target}",
        "bad_item": "物品不在当前位置：{target}",
        "arrive": "你来到：{name}",
        "take": "你拾取了：{name}",
        "bag": "背包：{items}",
        "player": "玩家",
        "hp": "生命值",
        "location": "当前位置",
        "bag_count": "背包数量",
        "quest_count": "任务数量",
        "event_count": "事件数量",
        "no_quests": "当前没有任务。",
        "quests": "当前任务：",
        "giver": "发布者",
        "objective": "目标",
        "reward": "奖励",
        "no_events": "当前没有已触发事件。",
        "events": "已触发事件：",
        "accepted": "你接取了任务：{name}。",
        "completed": "你完成了任务：{name}。你获得了：{reward}。",
    },
    "en": {
        "missing_go": "Where do you want to go?",
        "missing_talk": "Who do you want to talk to?",
        "missing_take": "What do you want to take?",
        "unknown": "Unknown command: {name}. Type help to view commands.",
        "bye": "Goodbye.",
        "current_location": "Location",
        "description": "Description",
        "people": "People",
        "items": "Items",
        "exits": "Exits",
        "none": "None",
        "bad_go": "Target location does not exist or is not an exit: {target}",
        "bad_npc": "NPC is not here: {target}",
        "bad_item": "Item is not here: {target}",
        "arrive": "You arrive at: {name}",
        "take": "You picked up: {name}",
        "bag": "Bag: {items}",
        "player": "Player",
        "hp": "HP",
        "location": "Location",
        "bag_count": "Inventory Items",
        "quest_count": "Quests",
        "event_count": "Events",
        "no_quests": "You have no quests.",
        "quests": "Quests:",
        "giver": "Giver",
        "objective": "Objective",
        "reward": "Reward",
        "no_events": "No events have been triggered.",
        "events": "Triggered Events:",
        "accepted": "Quest accepted: {name}.",
        "completed": "Quest completed: {name}. You received: {reward}.",
    },
}

STATUS_TEXT = {
    "zh": {"active": "进行中", "completed": "已完成"},
    "en": {"active": "In Progress", "completed": "Completed"},
}


class ActionHandler:
    """Execute parsed commands against the loaded world and player state."""

    def __init__(
        self,
        world: dict[str, Any],
        player: Player,
        save_callback: Callable[[], None],
        load_callback: Callable[[], None],
    ) -> None:
        self.world = world
        self.player = player
        self.save_callback = save_callback
        self.load_callback = load_callback
        self.locations_by_id = world.get("locations", {})
        self.npcs_by_id = world.get("npcs", {})
        self.items_by_id = world.get("items", {})
        self.quests_by_id = {quest["id"]: quest for quest in world.get("quests", [])}
        self._normalize_player_state()

    def execute(self, command: Command) -> bool:
        if command.name == "look":
            self.look()
        elif command.name == "go":
            self.go(self._first_arg(command, self._label("missing_go")))
        elif command.name == "talk":
            self.talk(self._first_arg(command, self._label("missing_talk")))
        elif command.name == "take":
            self.take(self._first_arg(command, self._label("missing_take")))
        elif command.name == "bag":
            self.bag()
        elif command.name == "status":
            self.status()
        elif command.name == "quests":
            self.quests()
        elif command.name == "events":
            self.events()
        elif command.name == "help":
            print(HELP_TEXT[self.lang])
        elif command.name == "save":
            self.save_callback()
        elif command.name == "load":
            self.load_callback()
        elif command.name == "quit":
            print(self._label("bye"))
            return False
        else:
            print(self._label("unknown").format(name=command.name))

        return True

    @property
    def lang(self) -> str:
        return self.player.language

    def look(self) -> None:
        location = self._current_location()

        npcs = [self._npc_name(npc_id) for npc_id in location.get("npcs", [])]
        items = [self._item_name(item_id) for item_id in location.get("items", [])]
        exits = [self._location_name(location_id) for location_id in location.get("exits", {}).values()]

        print()
        print(self._label("current_location"))
        print(f"  {self._location_name(self.player.location)}")
        print(self._label("description"))
        print(f"  {get_text(location.get('description'), self.lang)}")
        print(self._label("people"))
        print(f"  {self._format_list(npcs)}")
        print(self._label("items"))
        print(f"  {self._format_list(items)}")
        print(self._label("exits"))
        print(f"  {self._format_list(exits)}")

    def go(self, target_name: str | None) -> None:
        if not target_name:
            return

        location = self._current_location()
        exit_location_ids = list(location.get("exits", {}).values())
        exit_locations = {
            location_id: self.locations_by_id[location_id]
            for location_id in exit_location_ids
            if location_id in self.locations_by_id
        }
        target_id = match_entity_by_name(target_name, exit_locations, self.lang)

        if not target_id:
            print(self._label("bad_go").format(target=target_name))
            return

        self.player.location = target_id
        print(self._label("arrive").format(name=self._location_name(target_id)))
        self._trigger_enter_location_events(target_id)
        self._complete_enter_location_quests(target_id)
        self.look()

    def talk(self, npc_name: str | None) -> None:
        if not npc_name:
            return

        location = self._current_location()
        local_npcs = {
            npc_id: self.npcs_by_id[npc_id]
            for npc_id in location.get("npcs", [])
            if npc_id in self.npcs_by_id
        }
        npc_id = match_entity_by_name(npc_name, local_npcs, self.lang)
        if not npc_id:
            print(self._label("bad_npc").format(target=npc_name))
            return

        npc = self.npcs_by_id[npc_id]
        print(f"{self._npc_name(npc_id)}:")
        for line in npc.get("dialogue", []):
            print(get_text(line, self.lang))

        self._accept_talk_quests(npc_id)

    def take(self, item_name: str | None) -> None:
        if not item_name:
            return

        location = self._current_location()
        local_items = {
            item_id: self.items_by_id[item_id]
            for item_id in location.get("items", [])
            if item_id in self.items_by_id
        }
        item_id = match_entity_by_name(item_name, local_items, self.lang)
        if not item_id:
            print(self._label("bad_item").format(target=item_name))
            return

        location["items"].remove(item_id)
        self.player.bag.append(item_id)
        print(self._label("take").format(name=self._item_name(item_id)))

    def bag(self) -> None:
        items = [self._item_name(item_id) for item_id in self.player.bag]
        print(self._label("bag").format(items=self._format_list(items)))

    def status(self) -> None:
        sep = self._separator()
        print(f"{self._label('player')}{sep}{self.player.name}")
        print(f"{self._label('hp')}{sep}{self.player.hp}")
        print(f"{self._label('location')}{sep}{self._location_name(self.player.location)}")
        print(f"{self._label('bag_count')}{sep}{len(self.player.bag)}")
        print(f"{self._label('quest_count')}{sep}{len(self.player.quests)}")
        print(f"{self._label('event_count')}{sep}{len(self.player.events)}")

    def quests(self) -> None:
        if not self.player.quests:
            print(self._label("no_quests"))
            return

        print(self._label("quests"))
        sep = self._separator()
        for quest in self.player.quests:
            quest_config = self.quests_by_id.get(quest.get("id"), {})
            status = self._quest_status_text(quest.get("status", "进行中"))
            print(f"- {get_text(quest_config.get('name', quest.get('name')), self.lang)} [{status}]")
            print(f"  {self._label('giver')}{sep}{self._npc_name(quest_config.get('giver_npc', ''))}")
            print(f"  {self._label('objective')}{sep}{get_text(quest_config.get('objective', quest.get('objective')), self.lang)}")
            print(f"  {self._label('reward')}{sep}{get_text(quest_config.get('reward_text', quest.get('reward')), self.lang)}")

    def events(self) -> None:
        if not self.player.events:
            print(self._label("no_events"))
            return

        print(self._label("events"))
        events_by_id = {event["id"]: event for event in self.world.get("events", [])}
        sep = self._separator()
        for event in self.player.events:
            event_config = events_by_id.get(event.get("id"), event)
            print(f"- {get_text(event_config.get('name'), self.lang)}")
            print(f"  {self._label('location')}{sep}{get_text(event_config.get('location'), self.lang)}")
            print(f"  {self._label('description')}{sep}{get_text(event_config.get('description'), self.lang)}")

    def _current_location(self) -> dict[str, Any]:
        location = self.locations_by_id.get(self.player.location)
        if not location:
            raise RuntimeError(f"玩家当前位置不存在：{self.player.location}")
        return location

    def _location_name(self, location_id: str) -> str:
        return get_text(self.locations_by_id.get(location_id, {}).get("name", location_id), self.lang)

    def _npc_name(self, npc_id: str) -> str:
        return get_text(self.npcs_by_id.get(npc_id, {}).get("name", npc_id), self.lang)

    def _item_name(self, item_id: str) -> str:
        return get_text(self.items_by_id.get(item_id, {}).get("name", item_id), self.lang)

    def _first_arg(self, command: Command, missing_message: str) -> str | None:
        if not command.args or not command.args[0]:
            print(missing_message)
            return None
        return command.args[0]

    def _format_list(self, values: list[str]) -> str:
        return ("、" if self.lang == "zh" else ", ").join(values) if values else self._label("none")

    def _accept_talk_quests(self, npc_id: str) -> None:
        for quest_config in self.world.get("quests", []):
            if quest_config.get("trigger_type") != "talk":
                continue
            if quest_config.get("trigger_target") != npc_id:
                continue
            if self._find_quest(quest_config["id"]):
                continue

            quest = {
                "id": quest_config["id"],
                "status": "进行中",
                "reward_item": quest_config.get("reward_item", ""),
            }
            self.player.quests.append(quest)
            print(self._label("accepted").format(name=get_text(quest_config["name"], self.lang)))

    def _complete_enter_location_quests(self, location_id: str) -> None:
        for quest in self.player.quests:
            if quest.get("status") != "进行中":
                continue

            quest_config = self.quests_by_id.get(quest["id"], {})
            if quest_config.get("complete_type") != "enter_location":
                continue
            if quest_config.get("complete_target") != location_id:
                continue

            quest["status"] = "已完成"
            reward_item_id = quest_config.get("reward_item", "")
            self.player.bag.append(reward_item_id)
            print(
                self._label("completed").format(
                    name=get_text(quest_config["name"], self.lang),
                    reward=self._item_name(reward_item_id),
                )
            )

    def _trigger_enter_location_events(self, location_id: str) -> None:
        for event_config in self.world.get("events", []):
            if event_config.get("trigger_type") != "enter_location":
                continue
            if event_config.get("trigger_target") != location_id:
                continue
            if self._find_event(event_config["id"]):
                continue

            self.player.events.append({"id": event_config["id"]})
            print(get_text(event_config.get("description"), self.lang))

    def _find_quest(self, quest_id: str) -> dict[str, str] | None:
        for quest in self.player.quests:
            if quest.get("id") == quest_id:
                return quest
        return None

    def _find_event(self, event_id: str) -> dict[str, str] | None:
        for event in self.player.events:
            if event.get("id") == event_id:
                return event
        return None

    def _label(self, key: str) -> str:
        return LABELS[self.lang][key]

    def _separator(self) -> str:
        return "：" if self.lang == "zh" else ": "

    def _quest_status_text(self, status: str) -> str:
        if status in {"已完成", "completed"}:
            return STATUS_TEXT[self.lang]["completed"]
        return STATUS_TEXT[self.lang]["active"]

    def _normalize_player_state(self) -> None:
        if self.player.location not in self.locations_by_id:
            matched_location = match_entity_by_name(self.player.location, self.locations_by_id, self.lang)
            if matched_location:
                self.player.location = matched_location

        self.player.bag = [self._normalize_item_id(item) for item in self.player.bag]

    def _normalize_item_id(self, item: str) -> str:
        if item in self.items_by_id:
            return item
        return match_entity_by_name(item, self.items_by_id, self.lang) or item
