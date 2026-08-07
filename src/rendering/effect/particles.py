"""Food collection particle effects."""

from dataclasses import dataclass
import math
import random
from typing import Any

import pygame

from ..engine.camera import Camera
from ..engine.config import RenderingConfig


@dataclass(slots=True)
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float


class ParticleSystem:
    """Create, update, and draw short-lived collection particles."""

    def __init__(
        self,
        screen: pygame.Surface,
        camera: Camera,
        config: RenderingConfig,
    ) -> None:
        self.screen = screen
        self.camera = camera
        self.config = config
        self.particles: list[Particle] = []
        self._last_food = 0
        self._rng = random.Random(7)

    def reset(self) -> None:
        self.particles.clear()
        self._last_food = 0

    def update(self, env: Any, dt: float) -> None:
        self._spawn_food_particles(env)
        alive: list[Particle] = []
        for particle in self.particles:
            particle.life -= dt
            if particle.life > 0:
                particle.x += particle.vx * dt
                particle.y += particle.vy * dt
                particle.vy += 90 * dt
                alive.append(particle)
        self.particles = alive

    def draw(self) -> None:
        for particle in self.particles:
            center = self.camera.world_to_screen(particle.x, particle.y)
            radius = max(1, round(3 * self.camera.zoom * particle.life))
            pygame.draw.circle(self.screen, (236, 93, 106), center, radius)

    def _spawn_food_particles(self, env: Any) -> None:
        if env.agent.food_eaten <= self._last_food:
            return
        position = env.agent.position
        cell = self.config.cell_size
        for _ in range(14):
            angle = self._rng.random() * math.tau
            speed = self._rng.uniform(20, 70)
            self.particles.append(
                Particle(
                    (position.col + 0.5) * cell,
                    (position.row + 0.5) * cell,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    0.7,
                )
            )
        self._last_food = env.agent.food_eaten
