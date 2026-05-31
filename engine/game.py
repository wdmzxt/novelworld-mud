from engine.actions import ActionHandler
from engine.command_parser import CommandParser
from engine.i18n import normalize_language
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
        print("NovelWorld MUD v0.8")
        language_choice = input("请选择语言 / Please select language:\n1. 中文\n2. English\n> ")
        self.player.language = normalize_language(language_choice)
        self._print_welcome()

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
        print("游戏已保存。" if self.player.language == "zh" else "Game saved.")

    def load_saved_game(self) -> None:
        self.player, self.world = load_game()
        self._normalize_loaded_player_state()
        self.actions = self._create_action_handler()
        print("存档已读取。" if self.player.language == "zh" else "Save loaded.")
        self.actions.look()

    def _offer_load_on_startup(self) -> bool:
        if not save_exists():
            return False

        prompt = "检测到存档，是否读取？(y/是/n/否) " if self.player.language == "zh" else "Save found. Load it? (y/yes/n/no) "
        choice = input(prompt).strip().lower()
        if choice in {"y", "yes", "是"}:
            try:
                self.load_saved_game()
                return True
            except RuntimeError as exc:
                print(f"存档读取失败：{exc}" if self.player.language == "zh" else f"Failed to load save: {exc}")
                print("将开始新游戏。" if self.player.language == "zh" else "Starting a new game.")
                return False
        elif choice in {"n", "否", "no"}:
            print("开始新游戏。" if self.player.language == "zh" else "Starting a new game.")
            return False
        else:
            print("输入无法识别，开始新游戏。" if self.player.language == "zh" else "Input not recognized. Starting a new game.")
            return False

    def _create_action_handler(self) -> ActionHandler:
        return ActionHandler(
            self.world,
            self.player,
            save_callback=self.save_current_game,
            load_callback=self.load_saved_game,
        )

    def _print_welcome(self) -> None:
        if self.player.language == "zh":
            print("将小说变成可游玩的本地文字冒险世界。")
            print("输入 help 或 帮助 查看命令。")
        else:
            print("Turn novels into playable local text adventure worlds.")
            print("Type help to view commands.")

    def _normalize_loaded_player_state(self) -> None:
        locations = self.world.get("locations", {})
        if self.player.location not in locations:
            for location_id, location in locations.items():
                name = location.get("name", "")
                if isinstance(name, dict):
                    names = {name.get("zh"), name.get("en")}
                else:
                    names = {name}
                if self.player.location in names:
                    self.player.location = location_id
                    break
