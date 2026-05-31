import json
from pathlib import Path
from typing import Any

from engine.player import Player


SAVE_PATH = Path(__file__).resolve().parent.parent / "saves" / "save_demo.json"


def save_exists() -> bool:
    return SAVE_PATH.exists()


def save_game(player: Player, world: dict[str, Any]) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_data = {
        "player": {
            "name": player.name,
            "hp": player.hp,
            "location": player.location,
            "bag": player.bag,
            "quests": player.quests,
            "events": player.events,
        },
        "world": world,
    }

    with SAVE_PATH.open("w", encoding="utf-8") as file:
        json.dump(save_data, file, ensure_ascii=False, indent=2)


def load_game() -> tuple[Player, dict[str, Any]]:
    try:
        with SAVE_PATH.open("r", encoding="utf-8") as file:
            save_data = json.load(file)
    except FileNotFoundError as exc:
        raise RuntimeError("存档文件不存在。") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"存档文件 JSON 格式错误：第 {exc.lineno} 行，第 {exc.colno} 列") from exc

    try:
        player_data = save_data["player"]
        world = save_data["world"]
        player = Player(
            name=player_data["name"],
            location=player_data["location"],
            hp=player_data["hp"],
            bag=list(player_data.get("bag", [])),
            quests=list(player_data.get("quests", [])),
            events=list(player_data.get("events", [])),
        )
    except (KeyError, TypeError) as exc:
        raise RuntimeError("存档文件内容不完整或已损坏。") from exc

    return player, world
