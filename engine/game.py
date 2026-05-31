from engine.actions import ActionHandler
from engine.command_parser import CommandParser
from engine.player import Player
from engine.save_manager import load_game, save_exists, save_game
from engine.world_loader import load_demo_world


class Game:
    """Minimal command-line game loop for the v0.1 skeleton."""

    def __init__(self) -> None:
        self.world = load_demo_world()
        self.player = Player(name="旅人", location=self.world["start_location"])
        self.parser = CommandParser()
        self.actions = self._create_action_handler()
        self.running = True

    def run(self) -> None:
        print("NovelWorld MUD v0.4")
        print("将小说变成可游玩的本地文字冒险世界。")
        print("输入 help 或 帮助 查看命令。")

        loaded_on_startup = self._offer_load_on_startup()
        if not loaded_on_startup:
            self.actions.look()

        while self.running:
            try:
                raw_command = input("\n> ")
                command = self.parser.parse(raw_command)
                self.running = self.actions.execute(command)
            except RuntimeError as exc:
                print(f"错误：{exc}")
                self.running = False

    def save_current_game(self) -> None:
        save_game(self.player, self.world)
        print("游戏已保存。")

    def load_saved_game(self) -> None:
        self.player, self.world = load_game()
        self.actions = self._create_action_handler()
        print("存档已读取。")
        self.actions.look()

    def _offer_load_on_startup(self) -> bool:
        if not save_exists():
            return False

        choice = input("检测到存档，是否读取？(y/是/n/否) ").strip().lower()
        if choice in {"y", "是"}:
            try:
                self.load_saved_game()
                return True
            except RuntimeError as exc:
                print(f"存档读取失败：{exc}")
                print("将开始新游戏。")
                return False
        elif choice in {"n", "否"}:
            print("开始新游戏。")
            return False
        else:
            print("输入无法识别，开始新游戏。")
            return False

    def _create_action_handler(self) -> ActionHandler:
        return ActionHandler(
            self.world,
            self.player,
            save_callback=self.save_current_game,
            load_callback=self.load_saved_game,
        )
