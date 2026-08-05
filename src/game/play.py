"""Interactive TinyWorld frontend: ``python -m src.game.play``."""

import argparse
from dataclasses import asdict
from pathlib import Path
import time

import pygame

from src.agents import BaseAgent, RandomAgent, RuleBasedAgent
from src.engine.renderer import Renderer
from src.engine.replay import ReplayRecorder
from src.world.env import TinyWorldEnv


def _agent(name: str, seed: int) -> BaseAgent:
    return RuleBasedAgent(seed) if name == "rule" else RandomAgent(seed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Jouer une simulation TinyWorld AI")
    parser.add_argument("--agent", choices=("rule", "random"), default="rule")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--replay", type=Path, help="fichier JSON à enregistrer")
    args = parser.parse_args(argv)

    env = TinyWorldEnv(seed=args.seed)
    policy = _agent(args.agent, args.seed)
    observation, _ = env.reset(args.seed)
    policy.reset(args.seed)
    renderer = Renderer()
    renderer.center_on_agent(env)
    recorder = ReplayRecorder(args.seed, asdict(env.config), {"agent": args.agent})
    clock = pygame.time.Clock()
    paused = False
    show_observation = False
    running = True
    game_over = False
    speed = 8.0
    accumulator = 0.0
    total_reward = 0.0
    last_action = None
    dragging = False

    def restart() -> None:
        nonlocal observation, policy, recorder, game_over, total_reward, last_action
        observation, _ = env.reset(args.seed)
        policy = _agent(args.agent, args.seed)
        policy.reset(args.seed)
        recorder = ReplayRecorder(args.seed, asdict(env.config), {"agent": args.agent})
        game_over = False; total_reward = 0.0; last_action = None
        renderer._last_food = 0
        renderer.center_on_agent(env)

    while running:
        dt = min(clock.tick(60) / 1000.0, .1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                renderer.zoom(event.y, pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                renderer.camera.pan(-event.rel[0], -event.rel[1])
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: paused = not paused
                elif event.key == pygame.K_r: restart()
                elif event.key == pygame.K_o: show_observation = not show_observation
                elif event.key == pygame.K_c: renderer.center_on_agent(env)
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS): speed = min(60.0, speed * 1.5)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS): speed = max(.5, speed / 1.5)
                elif event.key in (pygame.K_1, pygame.K_2):
                    args.agent = "random" if event.key == pygame.K_1 else "rule"; restart()
        keys = pygame.key.get_pressed()
        pan = 380 * dt
        if keys[pygame.K_LEFT]: renderer.camera.pan(-pan, 0)
        if keys[pygame.K_RIGHT]: renderer.camera.pan(pan, 0)
        if keys[pygame.K_UP]: renderer.camera.pan(0, -pan)
        if keys[pygame.K_DOWN]: renderer.camera.pan(0, pan)

        if not paused and not game_over:
            accumulator += dt * speed
            while accumulator >= 1.0 and not game_over:
                accumulator -= 1.0
                last_action = policy.act(observation)
                observation, reward, terminated, truncated, _ = env.step(last_action)
                recorder.record(env, last_action, reward)
                total_reward += reward
                game_over = terminated or truncated
        renderer.draw(env, agent_name=args.agent, seed=args.seed, total_reward=total_reward,
                      observation=observation if show_observation else None, paused=paused,
                      game_over=game_over, last_action=last_action, dt=dt)

    if args.replay:
        recorder.metadata["saved_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        recorder.save(args.replay)
        print(f"Replay sauvegardé : {args.replay}")
    renderer.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
