"""Interactive TinyWorld frontend: ``python -m src.main``."""

import time

import pygame

from src.arguments import parse_arguments
from src.engine.control import Controls
from src.engine.renderer import Renderer
from src.engine.restart import restart_episode
from src.world.env import TinyWorldEnv


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)

    # Init
    env = TinyWorldEnv(seed=args.seed)
    renderer = Renderer()
    controls = Controls()
    state = restart_episode(env, renderer, args.agent, args.seed)
    clock = pygame.time.Clock()

    ## Loop
    while controls.running:
        dt = min(clock.tick(60) / 1000.0, .1)
        commands = controls.update(renderer, env, dt)
        if commands.selected_agent is not None:
            args.agent = commands.selected_agent
        if commands.selected_agent is not None or commands.restart:
            state = restart_episode(env, renderer, args.agent, args.seed)

        if not controls.paused and not state.game_over:
            state.accumulator += dt * controls.speed
            while state.accumulator >= 1.0 and not state.game_over:
                state.accumulator -= 1.0
                state.last_action = state.policy.act(state.observation)
                state.observation, reward, terminated, truncated, _ = env.step(
                    state.last_action
                )
                state.recorder.record(env, state.last_action, reward)
                state.total_reward += reward
                state.game_over = terminated or truncated
        renderer.draw(env, agent_name=args.agent, seed=args.seed,
                      total_reward=state.total_reward,
                      observation=state.observation if controls.show_observation else None,
                      paused=controls.paused, game_over=state.game_over,
                      last_action=state.last_action, dt=dt)

    # Replay
    if args.replay:
        state.recorder.metadata["saved_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        state.recorder.save(args.replay)
        print(f"Replay saved to: {args.replay}")

    # Exit
    renderer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
