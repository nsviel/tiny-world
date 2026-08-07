"""Interactive TinyWorld frontend: ``python -m src.main``."""

from src.app.application import App
from src.app.arguments import parse_arguments


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    app = App(agent_name=args.agent, seed=args.seed)

    while app.running:
        app.update(app.tick())

    if args.replay:
        app.replay(args.replay)

    app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
