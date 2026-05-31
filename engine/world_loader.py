import json
from pathlib import Path
from typing import Any


WORLD_DEMO_PATH = Path(__file__).resolve().parent.parent / "data" / "world_demo.json"


def load_demo_world() -> dict[str, Any]:
    try:
        with WORLD_DEMO_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise RuntimeError(f"世界文件不存在：{WORLD_DEMO_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"世界文件 JSON 格式错误：第 {exc.lineno} 行，第 {exc.colno} 列") from exc
