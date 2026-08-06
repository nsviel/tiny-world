"""Gym-like, dependency-free TinyWorld environment."""

from typing import Any

import numpy as np

from src.config import WorldConfig
from src.game.actions import Action
from src.game.observations import Observation, make_observation
from src.game.rewards import StepEvents, calculate_reward

from .entities import Agent, Orientation, Tile
from .validation import validate_world_config
from .world import World


class TinyWorldEnv:
    """Headless TinyWorld simulation.

    The API follows modern Gym conventions without importing Gym: ``reset``
    returns ``(observation, info)`` and ``step`` returns ``(observation, reward,
    terminated, truncated, info)``. Calling ``step`` after an episode ends is an
    error. Public attributes ``world``, ``agent``, ``elapsed_steps``,
    ``discovered`` and ``last_events`` support renderers, replay and tests.
    """

    action_count = len(Action)

    def __init__(self, config: WorldConfig | None = None, seed: int | None = None) -> None:
        self.config = config or WorldConfig()
        validate_world_config(self.config)
        self._seed = seed
        self.world: World
        self.agent: Agent
        self.elapsed_steps = 0
        self.discovered = np.zeros((self.config.height, self.config.width), dtype=np.bool_)
        self.last_events = StepEvents()
        self.terminated = False
        self.truncated = False
        self._renderer: Any | None = None
        self.reset(seed=seed)

    def reset(self, seed: int | None = None) -> tuple[Observation, dict[str, Any]]:
        if seed is not None:
            self._seed = seed
        self.world = World(self.config, self._seed)
        self.agent = Agent(
            position=self.world.spawn_position,
            orientation=Orientation.NORTH,
            energy=self.config.initial_energy,
        )
        self.elapsed_steps = 0
        self.discovered = np.zeros(self.world.shape, dtype=np.bool_)
        self.terminated = False
        self.truncated = False
        discovered = self._update_discovery()
        self.last_events = StepEvents(discovered_cells=discovered)
        return self._observation(), self._info()

    def step(self, action: Action | int) -> tuple[Observation, float, bool, bool, dict[str, Any]]:
        if self.terminated or self.truncated:
            raise RuntimeError("step() called after episode end; call reset()")
        try:
            selected = Action(action)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"unknown action {action!r}") from exc

        invalid = False
        ate_food = False
        if selected == Action.IDLE:
            cost = self.config.idle_cost
        elif selected == Action.MOVE_FORWARD:
            cost = self.config.move_cost
            destination = self.agent.position.moved(self.agent.orientation.delta)
            if self.world.is_walkable(destination) and destination != self.world.predator.position:
                self.agent.position = destination
            else:
                invalid = True
        elif selected == Action.TURN_LEFT:
            cost = self.config.turn_cost
            self.agent.orientation = self.agent.orientation.left()
        elif selected == Action.TURN_RIGHT:
            cost = self.config.turn_cost
            self.agent.orientation = self.agent.orientation.right()
        else:
            cost = self.config.eat_cost
            row, col = self.agent.position.row, self.agent.position.col
            if Tile(int(self.world.tiles[row, col])) == Tile.FOOD:
                self.world.tiles[row, col] = Tile.GROUND
                self.agent.food_eaten += 1
                self.agent.energy = min(self.config.max_energy, self.agent.energy + self.config.food_energy)
                ate_food = True
            else:
                invalid = True

        self.agent.energy -= cost
        predator_hit = False
        if self.agent.energy > 0:
            self.world.move_predator(self.agent.position)
            if self.world.predator.position == self.agent.position:
                predator_hit = True
                self.agent.energy -= self.config.predator_damage

        self.elapsed_steps += 1
        died = self.agent.energy <= 0
        if died:
            self.agent.energy = 0.0
            self.agent.alive = False
            self.terminated = True
        self.truncated = bool(
            not self.terminated
            and self.config.max_steps is not None
            and self.elapsed_steps >= self.config.max_steps
        )
        discovered = self._update_discovery()
        self.last_events = StepEvents(invalid, ate_food, predator_hit, died, discovered)
        reward = calculate_reward(self.last_events, self.config)
        return self._observation(), reward, self.terminated, self.truncated, self._info()

    def render(self) -> None:
        """Render the current state, lazily importing the optional Pygame frontend."""
        if self._renderer is None:
            from src.engine.renderer import Renderer

            self._renderer = Renderer()
            self._renderer.center_on_agent(self)
        self._renderer.draw(
            self,
            agent_name="external",
            seed=self._seed,
            total_reward=0.0,
        )

    def close(self) -> None:
        """Release renderer resources when rendering was requested."""
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None

    def _observation(self) -> Observation:
        return make_observation(
            self.world.tiles,
            self.agent,
            self.world.predator,
            self.elapsed_steps,
            self.config.view_size,
            self.config.max_energy,
            self.config.max_steps,
        )

    def _update_discovery(self) -> int:
        radius = self.config.view_size // 2
        row, col = self.agent.position.row, self.agent.position.col
        r0, r1 = max(0, row - radius), min(self.config.height, row + radius + 1)
        c0, c1 = max(0, col - radius), min(self.config.width, col + radius + 1)
        before = int(self.discovered[r0:r1, c0:c1].sum())
        self.discovered[r0:r1, c0:c1] = True
        return int(self.discovered[r0:r1, c0:c1].sum()) - before

    def _info(self) -> dict[str, Any]:
        delta_row = self.agent.position.row - self.world.predator.position.row
        delta_col = self.agent.position.col - self.world.predator.position.col
        return {
            "energy": float(self.agent.energy),
            "food_collected": int(self.agent.food_eaten),
            "survival_time": int(self.elapsed_steps),
            "distance_to_predator": float(np.hypot(delta_row, delta_col)),
            "seed": self._seed,
            "position": self.agent.position,
            "predator_position": self.world.predator.position,
            "events": self.last_events,
            "remaining_food": int(np.count_nonzero(self.world.tiles == Tile.FOOD)),
            "discovered_cells": int(self.discovered.sum()),
        }
