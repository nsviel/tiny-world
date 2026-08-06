"""Configuration for the Pygame engine and camera."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EngineConfig:
    window_size: tuple[int, int] = (1180, 780)
    panel_width: int = 300
    viewport_min_width: int = 300
    cell_size: int = 28

    zoom_default: float = 1.0
    zoom_min: float = 0.45
    zoom_max: float = 2.5
    zoom_step: float = 1.12
    camera_pan_speed: float = 380.0
