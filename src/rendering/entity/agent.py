"""Agent entity rendering."""

from typing import Any

import pygame

from ..engine.camera import Camera
from ..engine.config import RenderingConfig
from .common import entity_center


def draw_agent(
    screen: pygame.Surface,
    agent: Any,
    camera: Camera,
    config: RenderingConfig,
) -> None:
    center = entity_center(agent.position, camera, config)
    radius = max(4, round(9 * camera.zoom))
    pygame.draw.ellipse(
        screen,
        (31, 66, 47),
        (center[0] - radius, center[1] + radius // 2, radius * 2, radius),
    )
    pygame.draw.circle(screen, (240, 210, 88), center, radius)
    delta = agent.orientation.delta
    end = (
        center[0] + round(delta[1] * radius * 1.5),
        center[1] + round(delta[0] * radius * 1.5),
    )
    pygame.draw.line(
        screen,
        (255, 250, 220),
        center,
        end,
        max(2, round(3 * camera.zoom)),
    )
