from __future__ import annotations

from typing import Any

from engine.command_parser import Command
from engine.player import Player


HELP_TEXT = """可用命令：
look：查看当前位置
go <地点>：移动到指定地点
talk <人物>：和人物对话
take <物品>：拾取物品
bag：查看背包
status：查看角色状态
help：显示帮助
quit：退出游戏"""


class ActionHandler:
    """Execute parsed commands against the loaded world and player state."""

    def __init__(self, world: dict[str, Any], player: Player) -> None:
        self.world = world
        self.player = player
        self.locations_by_name = {location["name"]: location for location in world.get("locations", [])}
        self.npcs_by_id = {npc["id"]: npc for npc in world.get("npcs", [])}
        self.npcs_by_name = {npc["name"]: npc for npc in world.get("npcs", [])}
        self.items_by_id = {item["id"]: item for item in world.get("items", [])}
        self.items_by_name = {item["name"]: item for item in world.get("items", [])}

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
        elif command.name == "help":
            print(HELP_TEXT)
        elif command.name == "quit":
            print("再会。")
            return False
        else:
            print(f"未知命令：{command.name}。输入 help 查看可用命令。")

        return True

    def look(self) -> None:
        location = self._current_location()
        print(f"\n{location['name']}")
        print(location.get("description", "这里没有特别的描述。"))

        npcs = [self._npc_name(npc_id) for npc_id in location.get("npcs", [])]
        items = [self._item_name(item_id) for item_id in location.get("items", [])]
        exits = list(location.get("exits", {}).keys())

        print(f"人物：{self._format_list(npcs)}")
        print(f"物品：{self._format_list(items)}")
        print(f"出口：{self._format_list(exits)}")

    def go(self, target_name: str | None) -> None:
        if not target_name:
            return

        location = self._current_location()
        exits = location.get("exits", {})
        target_id = exits.get(target_name)

        if not target_id:
            print(f"目标地点不存在或不在出口中：{target_name}")
            return

        target_location = self._location_by_id(target_id)
        if not target_location:
            print(f"世界数据错误：找不到地点 ID {target_id}")
            return

        self.player.location = target_location["name"]
        print(f"你来到：{self.player.location}")
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

    def _current_location(self) -> dict[str, Any]:
        location = self.locations_by_name.get(self.player.location)
        if not location:
            raise RuntimeError(f"玩家当前位置不存在：{self.player.location}")
        return location

    def _location_by_id(self, location_id: str) -> dict[str, Any] | None:
        for location in self.world.get("locations", []):
            if location.get("id") == location_id:
                return location
        return None

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
