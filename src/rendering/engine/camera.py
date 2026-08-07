"""Camera transforms shared by the Pygame frontends."""

from typing import Any

import pygame

from .config import RenderingConfig


class Camera:
    """Manage viewport, centering, panning, and zoom."""

    def __init__(self, screen: pygame.Surface, config: RenderingConfig) -> None:
        self.screen = screen
        self.config = config
        self.x = 0.0
        self.y = 0.0
        self.zoom = config.zoom_default

    @property
    def viewport(self) -> tuple[int, int]:
        width, height = self.screen.get_size()
        viewport_width = max(
            self.config.viewport_min_width,
            width - self.config.panel_width,
        )
        return viewport_width, height

    def world_to_screen(self, x: float, y: float) -> tuple[int, int]:
        return round((x - self.x) * self.zoom), round((y - self.y) * self.zoom)

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        return x / self.zoom + self.x, y / self.zoom + self.y

    def pan(self, dx: float, dy: float) -> None:
        self.x += dx / self.zoom
        self.y += dy / self.zoom

    def change_zoom(self, amount: int, anchor: tuple[int, int]) -> None:
        value = self.zoom * (self.config.zoom_step ** amount)
        self.set_zoom(value, anchor)

    def set_zoom(self, value: float, anchor: tuple[int, int] | None = None) -> None:
        # Keep the anchored world point stationary.
        old_world = self.screen_to_world(*anchor) if anchor else None
        self.zoom = max(self.config.zoom_min, min(self.config.zoom_max, value))
        if anchor and old_world:
            new_world = self.screen_to_world(*anchor)
            self.x += old_world[0] - new_world[0]
            self.y += old_world[1] - new_world[1]

    def center_on_agent(self, env: Any) -> None:
        position = env.agent.position
        cell = self.config.cell_size
        self.center_on(
            (position.col + 0.5) * cell,
            (position.row + 0.5) * cell,
        )

    def center_on(self, world_x: float, world_y: float) -> None:
        self.x = world_x - self.viewport[0] / (2 * self.zoom)
        self.y = world_y - self.viewport[1] / (2 * self.zoom)
