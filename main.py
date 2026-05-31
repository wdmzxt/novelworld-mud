from engine.game import Game


def main() -> None:
    try:
        game = Game()
        game.run()
    except ValueError as exc:
        print(exc)
    except RuntimeError as exc:
        print(f"启动失败：{exc}")


if __name__ == "__main__":
    main()
