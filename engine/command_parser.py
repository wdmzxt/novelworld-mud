from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    args: list[str]


class CommandParser:
    """Parse raw command text into a simple command object."""

    def parse(self, raw_command: str) -> Command:
        if not raw_command:
            return Command(name="look", args=[])

        parts = raw_command.strip().split()
        name = parts[0].lower()
        args = [" ".join(parts[1:])] if len(parts) > 1 else []
        return Command(name=name, args=args)
