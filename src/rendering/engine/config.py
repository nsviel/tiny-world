"""Configuration for the Pygame engine and camera."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RenderingConfig:
    assets_root: Path | None = None
    window_size: tuple[int, int] = (1500, 1000)
    panel_width: int = 400
    panel_value_offset: int = 200  # Label-to-value spacing
    viewport_min_width: int = 300
    cell_size: int = 28

    font_name: str = "dejavusans"
    font_size: int = 20
    small_font_size: int = 20
    title_font_size: int = 40

    zoom_default: float = 1.0
    zoom_min: float = 0.45
    zoom_max: float = 2.5
    zoom_step: float = 1.12
    camera_pan_speed: float = 380.0
