from __future__ import annotations

from collections.abc import Callable
from typing import Any

from engine.command_parser import Command
from engine.player import Player


HELP_TEXT = """可用命令与示例：
look / 查看：查看当前位置
  示例：查看
go <地点> / 去 <地点>：移动到指定地点
  示例：去 后山入口
talk <人物> / 对话 <人物>：和人物对话
  示例：对话 老村长
take <物品> / 拾取 <物品>：拾取当前位置的物品
  示例：拾取 生锈短刀
bag / 背包：查看背包
  示例：背包
status / 状态：查看玩家状态
  示例：状态
help / 帮助：显示帮助
  示例：帮助
save / 保存：保存当前游戏
  示例：保存
load / 读取：读取存档
  示例：读取
quests / 任务：查看当前任务
  示例：任务
events / 事件：查看已触发事件
  示例：事件
quit / 退出：退出游戏
  示例：退出"""


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
        self.locations_by_name = {
            location["name"]: location for location in self.locations_by_id.values()
        }
        self.npcs_by_id = world.get("npcs", {})
        self.npcs_by_name = {npc["name"]: npc for npc in self.npcs_by_id.values()}
        self.items_by_id = world.get("items", {})
        self.items_by_name = {item["name"]: item for item in self.items_by_id.values()}
        self.quests_by_id = {quest["id"]: quest for quest in world.get("quests", [])}

    def execute(self, command: Command) -> bool:
        if command.name == "look":
            self.look()
        elif command.name == "go":
            self.go(self._first_arg(command, "你想去哪里？"))
        elif command.name == "talk":
            self.talk(self._first_arg(command, "你想和谁说话？"))
        elif command.name == "take":
            self.take(self._first_arg(command, "你想拾取什么？"))
        elif command.name == "bag":
            self.bag()
        elif command.name == "status":
            self.status()
        elif command.name == "quests":
            self.quests()
        elif command.name == "events":
            self.events()
        elif command.name == "help":
            print(HELP_TEXT)
        elif command.name == "save":
            self.save_callback()
        elif command.name == "load":
            self.load_callback()
        elif command.name == "quit":
            print("再会。")
            return False
        else:
            print(f"未知命令：{command.name}。输入 help 查看可用命令。")

        return True

    def look(self) -> None:
        location = self._current_location()

        npcs = [self._npc_name(npc_id) for npc_id in location.get("npcs", [])]
        items = [self._item_name(item_id) for item_id in location.get("items", [])]
        exits = list(location.get("exits", {}).keys())

        print()
        print("当前位置")
        print(f"  {location['name']}")
        print("描述")
        print(f"  {location.get('description', '这里没有特别的描述。')}")
        print("人物")
        print(f"  {self._format_list(npcs)}")
        print("物品")
        print(f"  {self._format_list(items)}")
        print("出口")
        print(f"  {self._format_list(exits)}")

    def go(self, target_name: str | None) -> None:
        if not target_name:
            return

        location = self._current_location()
        target_id = location.get("exits", {}).get(target_name)

        if not target_id:
            print(f"目标地点不存在或不在出口中：{target_name}")
            return

        target_location = self._location_by_id(target_id)
        if not target_location:
            print(f"世界数据错误：找不到地点 ID {target_id}")
            return

        self.player.location = target_location["name"]
        print(f"你来到：{self.player.location}")
        self._trigger_enter_location_events(target_id)
        self._complete_enter_location_quests(target_id)
        self.look()

    def talk(self, npc_name: str | None) -> None:
        if not npc_name:
            return

        location = self._current_location()
        npc = self.npcs_by_name.get(npc_name)
        if not npc or npc["id"] not in location.get("npcs", []):
            print(f"NPC 不在当前位置：{npc_name}")
            return

        print(f"{npc['name']}：")
        for line in npc.get("dialogue", ["他没有什么要说的。"]):
            print(line)

        self._accept_talk_quests(npc["id"])

    def take(self, item_name: str | None) -> None:
        if not item_name:
            return

        location = self._current_location()
        item = self.items_by_name.get(item_name)
        if not item or item["id"] not in location.get("items", []):
            print(f"物品不在当前位置：{item_name}")
            return

        location["items"].remove(item["id"])
        self.player.bag.append(item["name"])
        print(f"你拾取了：{item['name']}")

    def bag(self) -> None:
        print(f"背包：{self._format_list(self.player.bag)}")

    def status(self) -> None:
        print(f"姓名：{self.player.name}")
        print(f"生命值：{self.player.hp}")
        print(f"当前位置：{self.player.location}")
        print(f"背包数量：{len(self.player.bag)}")
        print(f"任务数量：{len(self.player.quests)}")
        print(f"已触发事件数量：{len(self.player.events)}")

    def quests(self) -> None:
        if not self.player.quests:
            print("当前没有任务。")
            return

        print("当前任务：")
        for quest in self.player.quests:
            print(f"- {quest['name']} [{quest['status']}]")
            print(f"  发布者：{quest['giver']}")
            print(f"  目标：{quest['objective']}")
            print(f"  奖励：{quest['reward']}")

    def events(self) -> None:
        if not self.player.events:
            print("当前没有已触发事件。")
            return

        print("已触发事件：")
        for event in self.player.events:
            print(f"- {event['name']}")
            print(f"  地点：{event['location']}")
            print(f"  描述：{event['description']}")

    def _current_location(self) -> dict[str, Any]:
        location = self.locations_by_name.get(self.player.location)
        if not location:
            raise RuntimeError(f"玩家当前位置不存在：{self.player.location}")
        return location

    def _location_by_id(self, location_id: str) -> dict[str, Any] | None:
        return self.locations_by_id.get(location_id)

    def _npc_name(self, npc_id: str) -> str:
        return self.npcs_by_id.get(npc_id, {}).get("name", npc_id)

    def _item_name(self, item_id: str) -> str:
        return self.items_by_id.get(item_id, {}).get("name", item_id)

    def _first_arg(self, command: Command, missing_message: str) -> str | None:
        if not command.args or not command.args[0]:
            print(missing_message)
            return None
        return command.args[0]

    def _format_list(self, values: list[str]) -> str:
        return "、".join(values) if values else "无"

    def _accept_talk_quests(self, npc_id: str) -> None:
        for quest_config in self.world.get("quests", []):
            if quest_config.get("trigger_type") != "talk":
                continue
            if quest_config.get("trigger_target") != npc_id:
                continue
            if self._find_quest(quest_config["id"]):
                continue

            quest = self._build_player_quest(quest_config)
            self.player.quests.append(quest)
            print(f"你接取了任务：{quest['name']}。")

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
            reward_name = self._item_name(reward_item_id)
            quest["reward"] = reward_name
            if reward_name and reward_name not in self.player.bag:
                self.player.bag.append(reward_name)
            print(f"你完成了任务：{quest['name']}。你获得了：{reward_name}。")

    def _trigger_enter_location_events(self, location_id: str) -> None:
        for event_config in self.world.get("events", []):
            if event_config.get("trigger_type") != "enter_location":
                continue
            if event_config.get("trigger_target") != location_id:
                continue
            if self._find_event(event_config["id"]):
                continue

            event = {
                "id": event_config["id"],
                "name": event_config["name"],
                "location": event_config.get("location", self.player.location),
                "description": event_config.get("description", ""),
            }
            self.player.events.append(event)
            print(event["description"])

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

    def _build_player_quest(self, quest_config: dict[str, Any]) -> dict[str, str]:
        return {
            "id": quest_config["id"],
            "name": quest_config["name"],
            "status": "进行中",
            "giver": self._npc_name(quest_config.get("giver_npc", "")),
            "objective": quest_config.get("objective", ""),
            "reward": self._item_name(quest_config.get("reward_item", "")),
            "reward_item": quest_config.get("reward_item", ""),
        }
