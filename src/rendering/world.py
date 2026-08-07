"""Pygame drawing for world terrain and entities."""

import math
from typing import TYPE_CHECKING, Any

import pygame

from src.simulation.observations import Observation

from src.world.environment.tile import Tile

from .entity import draw_agent, draw_predator
from .tile import draw_food, draw_ground, draw_tree, draw_water

if TYPE_CHECKING:
    from .engine.assets import AssetStore
    from .engine.camera import Camera
    from .engine.config import RenderingConfig


class WorldRenderer:
    """Draw the world viewport without drawing application UI."""

    def __init__(
        self,
        screen: pygame.Surface,
        camera: "Camera",
        config: "RenderingConfig",
        assets: "AssetStore",
    ) -> None:
        self.screen = screen
        self.camera = camera
        self.config = config
        self.assets = assets

    def draw(self, env: Any, viewport: tuple[int, int]) -> None:
        viewport_width, viewport_height = viewport
        clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(0, 0, viewport_width, viewport_height))
        for row in range(env.world_config.height):
            for col in range(env.world_config.width):
                rect = self._tile_rect(row, col)
                if not rect.colliderect((0, 0, viewport_width, viewport_height)):
                    continue
                self._draw_tile(env, row, col, rect)
        draw_agent(self.screen, env.agent, self.camera, self.config)
        draw_predator(self.screen, env.world.predator, self.camera, self.config)
        self.screen.set_clip(clip)

    def draw_observation(self, env: Any, observation: Observation) -> None:
        radius = observation.local_grid.shape[1] // 2
        position = env.agent.position
        cell = self.config.cell_size
        x, y = self.camera.world_to_screen(
            (position.col - radius) * cell,
            (position.row - radius) * cell,
        )
        size = round(observation.local_grid.shape[1] * cell * self.camera.zoom)
        pygame.draw.rect(
            self.screen,
            (255, 231, 125),
            (x, y, size, size),
            max(1, round(2 * self.camera.zoom)),
        )

    def _tile_rect(self, row: int, col: int) -> pygame.Rect:
        x, y = self.camera.world_to_screen(
            col * self.config.cell_size,
            row * self.config.cell_size,
        )
        size = math.ceil(self.config.cell_size * self.camera.zoom) + 1
        return pygame.Rect(x, y, size, size)

    def _draw_tile(self, env: Any, row: int, col: int, rect: pygame.Rect) -> None:
        shade = ((row * 17 + col * 31) % 3) * 4
        tile = Tile(int(env.world.tiles[row, col]))
        draw_ground(self.screen, rect, shade)
        if tile == Tile.WATER:
            draw_water(self.screen, rect, shade)
        elif tile == Tile.TREE:
            draw_tree(self.screen, rect, self.camera.zoom, self.assets)
        elif tile == Tile.FOOD:
            draw_food(self.screen, rect, self.camera.zoom, self.assets)

