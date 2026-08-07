"""Shared entity rendering helpers."""

from typing import Any

from ..engine.camera import Camera
from ..engine.config import RenderingConfig


def entity_center(
    position: Any,
    camera: Camera,
    config: RenderingConfig,
) -> tuple[int, int]:
    cell = config.cell_size
    return camera.world_to_screen(
        (position.col + 0.5) * cell,
        (position.row + 0.5) * cell,
    )
