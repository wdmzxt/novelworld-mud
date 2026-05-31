from dataclasses import dataclass, field


@dataclass
class Player:
    name: str
    location: str
    hp: int = 100
    bag: list[str] = field(default_factory=list)
    quests: list[dict[str, str]] = field(default_factory=list)
    events: list[dict[str, str]] = field(default_factory=list)
