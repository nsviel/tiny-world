"""Pygame renderer; importing the headless engine never imports this module."""

from dataclasses import dataclass
import math
import random
from typing import Any

import pygame

from src.app.state import RenderState
from src.simulation.actions import Action
from src.world.entities import Tile
from .world import WorldRenderer

from .assets import AssetStore
from .camera import Camera
from .config import RenderingConfig


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
        self.font = pygame.font.SysFont("dejavusans", 18)
        self.small = pygame.font.SysFont("dejavusans", 14)
        self.large = pygame.font.SysFont("dejavusans", 36, bold=True)
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
        self.add_food_particles(env)
        self._update_particles(state.frame_dt)
        self.screen.fill((17, 28, 29))
        self.world_renderer.draw(env, self.viewport)
        self._draw_particles()
        if state.show_observation and state.observation is not None:
            self.world_renderer.draw_observation(env, state.observation)
        self._draw_panel(
            env,
            state.agent_name,
            state.seed,
            state.total_reward,
            state.last_action,
        )
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

    def _draw_panel(self, env: Any, name: str, seed: int | None, reward: float,
                    action: Action | None) -> None:
        width, height = self.screen.get_size()
        panel_width = self.config.panel_width
        left = width - panel_width
        pygame.draw.rect(self.screen, (24, 37, 39), (left, 0, panel_width, height))
        pygame.draw.line(self.screen, (56, 79, 76), (left, 0), (left, height), 2)
        self.screen.blit(self.font.render("TINY WORLD  AI", True, (237, 230, 196)), (left+24, 24))
        labels = [("Agent", name), ("Énergie", f"{env.agent.energy:.1f}"),
                  ("Nourriture", str(env.agent.food_eaten)), ("Survie", str(env.elapsed_steps)),
                  ("Récompense", f"{reward:.2f}"), ("Action", action.name if action else "—"),
                  ("Seed", str(seed))]
        y = 72
        for label, value in labels:
            self.screen.blit(self.small.render(label.upper(), True, (132, 157, 148)), (left+24, y))
            self.screen.blit(self.font.render(value, True, (235, 239, 218)), (left+140, y-3)); y += 34
        bar = pygame.Rect(left+24, y+4, panel_width-48, 18)
        pygame.draw.rect(self.screen, (54, 65, 62), bar, border_radius=8)
        fill = bar.copy(); fill.width = round(bar.width * max(0, env.agent.energy/env.config.max_energy))
        pygame.draw.rect(self.screen, (72, 190, 112) if env.agent.energy > 30 else (218, 79, 67), fill, border_radius=8)
        self._draw_minimap(env, pygame.Rect(left+24, y+55, panel_width-48, panel_width-48))
        hints = "Espace pause · R reset · O vision\nMolette zoom · clic droit/glisser\nFlèches caméra · C recentrer"
        for i, line in enumerate(hints.splitlines()):
            self.screen.blit(self.small.render(line, True, (143, 158, 151)), (left+24, height-78+i*20))

    def _draw_minimap(self, env: Any, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, (17, 28, 29), rect)
        sx, sy = rect.width/env.config.width, rect.height/env.config.height
        colors = {Tile.GROUND:(70,116,70), Tile.WATER:(48,112,148), Tile.TREE:(29,74,42), Tile.FOOD:(178,63,75)}
        for row in range(env.config.height):
            for col in range(env.config.width):
                tile = Tile(int(env.world.tiles[row,col]))
                pygame.draw.rect(self.screen, colors[tile], (rect.x+col*sx, rect.y+row*sy, max(1,sx+1), max(1,sy+1)))
        a = env.agent.position; p = env.world.predator.position
        pygame.draw.circle(self.screen, (255,231,104), (round(rect.x+(a.col+.5)*sx), round(rect.y+(a.row+.5)*sy)), 3)
        pygame.draw.circle(self.screen, (238,69,66), (round(rect.x+(p.col+.5)*sx), round(rect.y+(p.row+.5)*sy)), 3)

    def _draw_overlay(self, title: str, subtitle: str) -> None:
        vw, vh = self.viewport
        veil = pygame.Surface((vw, vh), pygame.SRCALPHA); veil.fill((7, 13, 14, 165)); self.screen.blit(veil, (0,0))
        image = self.large.render(title, True, (250, 235, 179)); sub = self.font.render(subtitle, True, (210, 220, 207))
        self.screen.blit(image, image.get_rect(center=(vw//2, vh//2-18)))
        self.screen.blit(sub, sub.get_rect(center=(vw//2, vh//2+30)))

    def close(self) -> None:
        pygame.quit()
