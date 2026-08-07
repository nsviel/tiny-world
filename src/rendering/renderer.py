"""Pygame renderer; importing the headless engine never imports this module."""

from dataclasses import dataclass
import math
import random
from typing import Any

import pygame

from src.app.state import RenderState

from .world import WorldRenderer

from .engine.assets import AssetStore
from .engine.camera import Camera
from .engine.config import RenderingConfig
from .panel import Panel


@dataclass(slots=True)
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float


class Renderer:
    """Draw an environment state without owning simulation logic."""

    def __init__(self, title: str = "TinyWorld AI", config: RenderingConfig | None = None) -> None:
        self.config = config or RenderingConfig()
        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(self.config.window_size, pygame.RESIZABLE)
        self.assets = AssetStore(self.config.assets_root)
        self.font = pygame.font.SysFont(self.config.font_name, self.config.font_size)
        self.small = pygame.font.SysFont(
            self.config.font_name,
            self.config.small_font_size,
        )
        self.large = pygame.font.SysFont(
            self.config.font_name,
            self.config.title_font_size,
            bold=True,
        )
        self.panel = Panel(self.screen, self.config, self.font, self.small)
        self.camera = Camera(
            zoom=self.config.zoom_default,
            min_zoom=self.config.zoom_min,
            max_zoom=self.config.zoom_max,
        )
        self.world_renderer = WorldRenderer(
            self.screen,
            self.camera,
            self.config,
            self.assets,
        )
        self.particles: list[Particle] = []
        self._last_food = 0
        self._rng = random.Random(7)

    @property
    def viewport(self) -> tuple[int, int]:
        width, height = self.screen.get_size()
        return max(self.config.viewport_min_width, width - self.config.panel_width), height

    def center_on_agent(self, env: Any) -> None:
        position = env.agent.position
        cell = self.config.cell_size
        self.camera.center_on((position.col + .5) * cell, (position.row + .5) * cell, self.viewport)

    def zoom(self, amount: int, anchor: tuple[int, int]) -> None:
        self.camera.set_zoom(self.camera.zoom * (self.config.zoom_step ** amount), anchor)

    def reset_effects(self) -> None:
        """Clear transient visual state for a new episode."""
        self.particles.clear()
        self._last_food = 0

    def add_food_particles(self, env: Any) -> None:
        if env.agent.food_eaten <= self._last_food:
            return
        p = env.agent.position
        for _ in range(14):
            angle = self._rng.random() * math.tau
            speed = self._rng.uniform(20, 70)
            self.particles.append(Particle((p.col + .5) * self.config.cell_size,
                                           (p.row + .5) * self.config.cell_size,
                                           math.cos(angle) * speed, math.sin(angle) * speed, .7))
        self._last_food = env.agent.food_eaten

    def draw(self, env: Any, state: RenderState) -> None:
        if state.auto_loop_timer > 0.0:
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            return

        self.add_food_particles(env)
        self._update_particles(state.frame_dt)
        self.screen.fill((17, 28, 29))
        self.world_renderer.draw(env, self.viewport)
        self._draw_particles()
        if state.show_observation and state.observation is not None:
            self.world_renderer.draw_observation(env, state.observation)
        self.panel.draw(env, state)
        if state.paused or state.game_over:
            self._draw_overlay("ÉPISODE TERMINÉ" if state.game_over else "PAUSE",
                               "R : recommencer" if state.game_over else "Espace : reprendre")
        pygame.display.flip()

    def _draw_particles(self) -> None:
        for particle in self.particles:
            center = self.camera.world_to_screen(particle.x, particle.y)
            pygame.draw.circle(self.screen, (236, 93, 106), center, max(1, round(3*self.camera.zoom*particle.life)))

    def _update_particles(self, dt: float) -> None:
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life > 0:
                p.x += p.vx*dt; p.y += p.vy*dt
                p.vy += 90*dt
                alive.append(p)
        self.particles = alive

    def _draw_overlay(self, title: str, subtitle: str) -> None:
        vw, vh = self.viewport
        veil = pygame.Surface((vw, vh), pygame.SRCALPHA); veil.fill((7, 13, 14, 165)); self.screen.blit(veil, (0,0))
        image = self.large.render(title, True, (250, 235, 179)); sub = self.font.render(subtitle, True, (210, 220, 207))
        self.screen.blit(image, image.get_rect(center=(vw//2, vh//2-18)))
        self.screen.blit(sub, sub.get_rect(center=(vw//2, vh//2+30)))

    def close(self) -> None:
        pygame.quit()
