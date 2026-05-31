from engine.actions import ActionHandler
from engine.command_parser import CommandParser
from engine.player import Player
from engine.world_loader import load_demo_world


class Game:
    """Minimal command-line game loop for the v0.1 skeleton."""

    def __init__(self) -> None:
        self.world = load_demo_world()
        self.player = Player(name="旅人", location=self.world["start_location"])
        self.parser = CommandParser()
        self.actions = ActionHandler(self.world, self.player)
        self.running = True

    def run(self) -> None:
        print("NovelWorld MUD v0.1")
        print("输入 help 查看命令。")
        self.actions.look()

        while self.running:
            try:
                raw_command = input("\n> ")
                command = self.parser.parse(raw_command)
                self.running = self.actions.execute(command)
            except RuntimeError as exc:
                print(f"错误：{exc}")
                self.running = False
