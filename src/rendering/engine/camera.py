"""Camera transforms shared by the Pygame frontends."""

from dataclasses import dataclass


@dataclass(slots=True)
class Camera:
    """A zoomable camera whose coordinates are expressed in world pixels."""

    min_zoom: float
    max_zoom: float
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0

    def world_to_screen(self, x: float, y: float) -> tuple[int, int]:
        return round((x - self.x) * self.zoom), round((y - self.y) * self.zoom)

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        return x / self.zoom + self.x, y / self.zoom + self.y

    def pan(self, dx: float, dy: float) -> None:
        self.x += dx / self.zoom
        self.y += dy / self.zoom

    def set_zoom(self, value: float, anchor: tuple[int, int] | None = None) -> None:
        # Keep the anchored world point stationary.
        old_world = self.screen_to_world(*anchor) if anchor else None
        self.zoom = max(self.min_zoom, min(self.max_zoom, value))
        if anchor and old_world:
            new_world = self.screen_to_world(*anchor)
            self.x += old_world[0] - new_world[0]
            self.y += old_world[1] - new_world[1]

    def center_on(self, world_x: float, world_y: float, viewport: tuple[int, int]) -> None:
        self.x = world_x - viewport[0] / (2 * self.zoom)
        self.y = world_y - viewport[1] / (2 * self.zoom)
