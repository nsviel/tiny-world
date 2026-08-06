"""Interactive TinyWorld frontend: ``python -m src.main``."""

import pygame

from src.app.application import App
from src.app.arguments import parse_arguments


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    app = App(agent_name=args.agent, seed=args.seed)
    clock = pygame.time.Clock()

    while app.running:
        # Cap stalls before updating the accumulator.
        dt = min(clock.tick(60) / 1000.0, 0.1)
        app.update(dt)

    if args.replay:
        app.replay(args.replay)

    app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
