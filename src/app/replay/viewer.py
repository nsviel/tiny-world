"""Pygame replay viewer and command-line interface."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import time

from src.simulation.config import SimulationConfig
from src.world.environment.config import WorldConfig

from .recorder import ReplayRecorder


def main(argv: list[str] | None = None) -> int:
    """Play a recorded trajectory with the standard Pygame renderer."""
    import argparse

    parser = argparse.ArgumentParser(description="View a TinyWorld AI replay")
    parser.add_argument("path", type=Path)
    parser.add_argument("--fps", type=float, default=8.0)
    args = parser.parse_args(argv)
    if args.fps <= 0:
        parser.error("--fps must be positive")

    replay = ReplayRecorder.load(args.path)
    if not replay.steps:
        parser.error("the replay contains no steps")

    # Keep headless replay recording free of rendering imports.
    from src.rendering.engine.control import ReplayControls
    from src.rendering.renderer import Renderer
    from src.world.environment.env import TinyWorldEnv

    from ..state import RenderState

    world_fields = WorldConfig.__dataclass_fields__
    simulation_fields = SimulationConfig.__dataclass_fields__
    world_values = replay.config.get("world", replay.config)
    simulation_values = replay.config.get("simulation", replay.config)
    if not isinstance(world_values, Mapping) or not isinstance(simulation_values, Mapping):
        raise ValueError("replay config must contain configuration objects")
    world_config = WorldConfig(
        **{key: value for key, value in world_values.items() if key in world_fields}
    )
    simulation_config = SimulationConfig(
        **{key: value for key, value in simulation_values.items() if key in simulation_fields}
    )
    env = TinyWorldEnv(world_config, simulation_config, replay.seed)
    renderer = Renderer(f"TinyWorld Replay — {args.path.name}")
    renderer.camera.center_on_agent(env)
    index = 0
    controls = ReplayControls()
    render_state = RenderState(
        agent_name=str(replay.metadata.get("agent", "replay")),
        seed=replay.seed,
    )
    accumulator = 0.0
    total_reward = 0.0
    while controls.running:
        dt = renderer.display.tick()
        commands = controls.update(renderer, env, dt)
        if commands.restart:
            index = 0
            total_reward = 0.0
        if not controls.paused:
            # Decouple replay cadence from render frames.
            accumulator += dt * args.fps
            if accumulator >= 1.0:
                accumulator -= 1.0
                step = replay.steps[index]
                env.elapsed_steps = step.time
                env.agent.position = step.agent_position
                env.agent.orientation = step.orientation
                env.agent.energy = step.energy
                env.agent.food_eaten = step.food_collected
                env.world.predator.position = step.predator_position
                total_reward += step.reward
                index = (index + 1) % len(replay.steps)
                if index == 0:
                    time.sleep(.25)
                    total_reward = 0.0
        current = replay.steps[index - 1]
        render_state.total_reward = total_reward
        render_state.last_action = current.action
        render_state.paused = controls.paused
        render_state.frame_dt = dt
        renderer.draw(env, render_state)
    renderer.close()
    return 0
