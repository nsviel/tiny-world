"""Pygame drawing for world terrain and entities."""

import math
from typing import TYPE_CHECKING, Any

import pygame

from src.simulation.observations import Observation

from src.world.entities import Tile

if TYPE_CHECKING:
    from .assets import AssetStore
    from .camera import Camera
    from .config import RenderingConfig


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
        for row in range(env.config.height):
            for col in range(env.config.width):
                rect = self._tile_rect(row, col)
                if not rect.colliderect((0, 0, viewport_width, viewport_height)):
                    continue
                self._draw_tile(env, row, col, rect)
        self._draw_agent(env)
        self._draw_predator(env)
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
        pygame.draw.rect(self.screen, (74 + shade, 137 + shade, 78 + shade), rect)
        if tile == Tile.WATER:
            self._draw_water(rect, shade)
        elif tile == Tile.TREE:
            self._draw_tree(rect)
        elif tile == Tile.FOOD:
            self._draw_food(rect)

    def _draw_water(self, rect: pygame.Rect, shade: int) -> None:
        pygame.draw.rect(
            self.screen,
            (54, 132 + shade, 174 + shade),
            rect,
            border_radius=3,
        )
        pygame.draw.line(
            self.screen,
            (97, 175, 202),
            (rect.left + 4, rect.centery),
            (rect.right - 4, rect.centery),
            1,
        )

    def _draw_tree(self, rect: pygame.Rect) -> None:
        image = self.assets.get("tree", rect.size)
        if image is not None:
            self.screen.blit(image, rect)
            return
        cx, cy = rect.center
        scale = self.camera.zoom
        pygame.draw.ellipse(self.screen, (30, 70, 42), rect.move(round(3 * scale), round(4 * scale)))
        pygame.draw.rect(
            self.screen,
            (105, 72, 42),
            (cx - round(3 * scale), cy, max(2, round(6 * scale)), max(3, round(10 * scale))),
        )
        pygame.draw.circle(self.screen, (30, 92, 48), (cx, cy - round(3 * scale)), max(3, round(10 * scale)))
        pygame.draw.circle(
            self.screen,
            (46, 116, 58),
            (cx - round(4 * scale), cy - round(6 * scale)),
            max(2, round(7 * scale)),
        )

    def _draw_food(self, rect: pygame.Rect) -> None:
        image = self.assets.get("food", rect.size)
        if image is not None:
            self.screen.blit(image, rect)
            return
        pygame.draw.ellipse(
            self.screen,
            (35, 78, 40),
            rect.inflate(-rect.width // 3, -rect.height // 2).move(2, 3),
        )
        cx, cy = rect.center
        radius = max(2, round(3 * self.camera.zoom))
        for dx, dy in ((-4, 1), (3, -2), (4, 4)):
            pygame.draw.circle(
                self.screen,
                (191, 45, 72),
                (cx + round(dx * self.camera.zoom), cy + round(dy * self.camera.zoom)),
                radius,
            )

    def _entity_center(self, position: Any) -> tuple[int, int]:
        cell = self.config.cell_size
        return self.camera.world_to_screen(
            (position.col + 0.5) * cell,
            (position.row + 0.5) * cell,
        )

    def _draw_agent(self, env: Any) -> None:
        center = self._entity_center(env.agent.position)
        radius = max(4, round(9 * self.camera.zoom))
        pygame.draw.ellipse(
            self.screen,
            (31, 66, 47),
            (center[0] - radius, center[1] + radius // 2, radius * 2, radius),
        )
        pygame.draw.circle(self.screen, (240, 210, 88), center, radius)
        delta = env.agent.orientation.delta
        end = (
            center[0] + round(delta[1] * radius * 1.5),
            center[1] + round(delta[0] * radius * 1.5),
        )
        pygame.draw.line(
            self.screen,
            (255, 250, 220),
            center,
            end,
            max(2, round(3 * self.camera.zoom)),
        )

    def _draw_predator(self, env: Any) -> None:
        center = self._entity_center(env.world.predator.position)
        radius = max(4, round(10 * self.camera.zoom))
        pygame.draw.ellipse(
            self.screen,
            (65, 38, 39),
            (center[0] - radius, center[1] + radius // 2, radius * 2, radius),
        )
        pygame.draw.circle(self.screen, (192, 57, 58), center, radius)
        eye_radius = max(1, radius // 5)
        pygame.draw.circle(
            self.screen,
            (245, 210, 165),
            (center[0] - radius // 3, center[1] - radius // 4),
            eye_radius,
        )
        pygame.draw.circle(
            self.screen,
            (245, 210, 165),
            (center[0] + radius // 3, center[1] - radius // 4),
            eye_radius,
        )
