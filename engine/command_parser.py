from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    args: list[str]


class CommandParser:
    """Parse raw command text into a simple command object."""

    COMMAND_ALIASES = {
        "查看": "look",
        "去": "go",
        "对话": "talk",
        "拾取": "take",
        "背包": "bag",
        "状态": "status",
        "帮助": "help",
        "退出": "quit",
        "保存": "save",
        "读取": "load",
        "任务": "quests",
    }

    def parse(self, raw_command: str) -> Command:
        if not raw_command:
            return Command(name="look", args=[])

        parts = raw_command.strip().split()
        name = self.COMMAND_ALIASES.get(parts[0], parts[0].lower())
        args = [" ".join(parts[1:])] if len(parts) > 1 else []
        return Command(name=name, args=args)
