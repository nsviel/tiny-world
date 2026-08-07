"""Predator entity rendering."""

from typing import Any

import pygame

from ..engine.camera import Camera
from ..engine.config import RenderingConfig
from .common import entity_center


def draw_predator(
    screen: pygame.Surface,
    predator: Any,
    camera: Camera,
    config: RenderingConfig,
) -> None:
    center = entity_center(predator.position, camera, config)
    radius = max(4, round(10 * camera.zoom))
    pygame.draw.ellipse(
        screen,
        (65, 38, 39),
        (center[0] - radius, center[1] + radius // 2, radius * 2, radius),
    )
    pygame.draw.circle(screen, (192, 57, 58), center, radius)
    eye_radius = max(1, radius // 5)
    for direction in (-1, 1):
        pygame.draw.circle(
            screen,
            (245, 210, 165),
            (center[0] + direction * radius // 3, center[1] - radius // 4),
            eye_radius,
        )
