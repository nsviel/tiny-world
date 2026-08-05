"""Pygame renderer; importing the headless engine never imports this module."""

from dataclasses import dataclass
import math
import random
from typing import Any

import pygame

from src.game.actions import Action
from src.game.observations import Observation
from src.world.entities import Tile

from .camera import Camera

WINDOW = (1180, 780)
PANEL_WIDTH = 300
VIEWPORT = (WINDOW[0] - PANEL_WIDTH, WINDOW[1])
CELL = 28


@dataclass(slots=True)
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float


class Renderer:
    """Draw an environment state without owning simulation logic."""

    def __init__(self, title: str = "TinyWorld AI") -> None:
        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(WINDOW, pygame.RESIZABLE)
        self.font = pygame.font.SysFont("dejavusans", 18)
        self.small = pygame.font.SysFont("dejavusans", 14)
        self.large = pygame.font.SysFont("dejavusans", 36, bold=True)
        self.camera = Camera()
        self.particles: list[Particle] = []
        self._last_food = 0
        self._rng = random.Random(7)

    @property
    def viewport(self) -> tuple[int, int]:
        width, height = self.screen.get_size()
        return max(300, width - PANEL_WIDTH), height

    def center_on_agent(self, env: Any) -> None:
        position = env.agent.position
        self.camera.center_on((position.col + .5) * CELL, (position.row + .5) * CELL, self.viewport)

    def zoom(self, amount: int, anchor: tuple[int, int]) -> None:
        self.camera.set_zoom(self.camera.zoom * (1.12 ** amount), anchor)

    def add_food_particles(self, env: Any) -> None:
        if env.agent.food_eaten <= self._last_food:
            return
        p = env.agent.position
        for _ in range(14):
            angle = self._rng.random() * math.tau
            speed = self._rng.uniform(20, 70)
            self.particles.append(Particle((p.col + .5) * CELL, (p.row + .5) * CELL,
                                           math.cos(angle) * speed, math.sin(angle) * speed, .7))
        self._last_food = env.agent.food_eaten

    def draw(self, env: Any, *, agent_name: str, seed: int | None, total_reward: float,
             observation: Observation | None = None, paused: bool = False,
             game_over: bool = False, last_action: Action | None = None,
             dt: float = 0.0) -> None:
        self.add_food_particles(env)
        self._update_particles(dt)
        self.screen.fill((17, 28, 29))
        self._draw_world(env)
        self._draw_particles()
        if observation is not None:
            self._draw_observation(env, observation)
        self._draw_panel(env, agent_name, seed, total_reward, last_action)
        if paused or game_over:
            self._draw_overlay("ÉPISODE TERMINÉ" if game_over else "PAUSE",
                               "R : recommencer" if game_over else "Espace : reprendre")
        pygame.display.flip()

    def _tile_rect(self, row: int, col: int) -> pygame.Rect:
        x, y = self.camera.world_to_screen(col * CELL, row * CELL)
        size = math.ceil(CELL * self.camera.zoom) + 1
        return pygame.Rect(x, y, size, size)

    def _draw_world(self, env: Any) -> None:
        viewport_w, viewport_h = self.viewport
        clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(0, 0, viewport_w, viewport_h))
        for row in range(env.config.height):
            for col in range(env.config.width):
                rect = self._tile_rect(row, col)
                if not rect.colliderect((0, 0, viewport_w, viewport_h)):
                    continue
                shade = ((row * 17 + col * 31) % 3) * 4
                tile = Tile(int(env.world.tiles[row, col]))
                pygame.draw.rect(self.screen, (74 + shade, 137 + shade, 78 + shade), rect)
                if tile == Tile.WATER:
                    pygame.draw.rect(self.screen, (54, 132 + shade, 174 + shade), rect, border_radius=3)
                    pygame.draw.line(self.screen, (97, 175, 202), (rect.left + 4, rect.centery), (rect.right - 4, rect.centery), 1)
                elif tile == Tile.TREE:
                    self._draw_tree(rect)
                elif tile == Tile.FOOD:
                    self._draw_food(rect)
        self._draw_agent(env)
        self._draw_predator(env)
        self.screen.set_clip(clip)

    def _draw_tree(self, rect: pygame.Rect) -> None:
        cx, cy = rect.center
        scale = self.camera.zoom
        pygame.draw.ellipse(self.screen, (30, 70, 42), rect.move(round(3*scale), round(4*scale)))
        pygame.draw.rect(self.screen, (105, 72, 42), (cx-round(3*scale), cy, max(2,round(6*scale)), max(3,round(10*scale))))
        pygame.draw.circle(self.screen, (30, 92, 48), (cx, cy-round(3*scale)), max(3,round(10*scale)))
        pygame.draw.circle(self.screen, (46, 116, 58), (cx-round(4*scale), cy-round(6*scale)), max(2,round(7*scale)))

    def _draw_food(self, rect: pygame.Rect) -> None:
        pygame.draw.ellipse(self.screen, (35, 78, 40), rect.inflate(-rect.width//3, -rect.height//2).move(2, 3))
        cx, cy = rect.center
        r = max(2, round(3*self.camera.zoom))
        for dx, dy in ((-4, 1), (3, -2), (4, 4)):
            pygame.draw.circle(self.screen, (191, 45, 72), (cx+round(dx*self.camera.zoom), cy+round(dy*self.camera.zoom)), r)

    def _entity_center(self, position: Any) -> tuple[int, int]:
        return self.camera.world_to_screen((position.col+.5)*CELL, (position.row+.5)*CELL)

    def _draw_agent(self, env: Any) -> None:
        center = self._entity_center(env.agent.position)
        radius = max(4, round(9*self.camera.zoom))
        pygame.draw.ellipse(self.screen, (31, 66, 47), (center[0]-radius, center[1]+radius//2, radius*2, radius))
        pygame.draw.circle(self.screen, (240, 210, 88), center, radius)
        delta = env.agent.orientation.delta
        end = (center[0]+round(delta[1]*radius*1.5), center[1]+round(delta[0]*radius*1.5))
        pygame.draw.line(self.screen, (255, 250, 220), center, end, max(2, round(3*self.camera.zoom)))

    def _draw_predator(self, env: Any) -> None:
        center = self._entity_center(env.world.predator.position)
        radius = max(4, round(10*self.camera.zoom))
        pygame.draw.ellipse(self.screen, (65, 38, 39), (center[0]-radius, center[1]+radius//2, radius*2, radius))
        pygame.draw.circle(self.screen, (192, 57, 58), center, radius)
        pygame.draw.circle(self.screen, (245, 210, 165), (center[0]-radius//3, center[1]-radius//4), max(1,radius//5))
        pygame.draw.circle(self.screen, (245, 210, 165), (center[0]+radius//3, center[1]-radius//4), max(1,radius//5))

    def _draw_observation(self, env: Any, observation: Observation) -> None:
        radius = observation.local_grid.shape[1] // 2
        p = env.agent.position
        x, y = self.camera.world_to_screen((p.col-radius)*CELL, (p.row-radius)*CELL)
        size = round(observation.local_grid.shape[1]*CELL*self.camera.zoom)
        pygame.draw.rect(self.screen, (255, 231, 125), (x, y, size, size), max(1, round(2*self.camera.zoom)))

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
        left = width - PANEL_WIDTH
        pygame.draw.rect(self.screen, (24, 37, 39), (left, 0, PANEL_WIDTH, height))
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
        bar = pygame.Rect(left+24, y+4, PANEL_WIDTH-48, 18)
        pygame.draw.rect(self.screen, (54, 65, 62), bar, border_radius=8)
        fill = bar.copy(); fill.width = round(bar.width * max(0, env.agent.energy/env.config.max_energy))
        pygame.draw.rect(self.screen, (72, 190, 112) if env.agent.energy > 30 else (218, 79, 67), fill, border_radius=8)
        self._draw_minimap(env, pygame.Rect(left+24, y+55, PANEL_WIDTH-48, PANEL_WIDTH-48))
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
