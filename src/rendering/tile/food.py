"""Food tile rendering with an optional PNG asset."""

import pygame

from ..engine.assets import AssetStore


def draw_food(
    screen: pygame.Surface,
    rect: pygame.Rect,
    zoom: float,
    assets: AssetStore,
) -> None:
    image = assets.get("food", rect.size)
    if image is not None:
        screen.blit(image, rect)
        return

    pygame.draw.ellipse(
        screen,
        (35, 78, 40),
        rect.inflate(-rect.width // 3, -rect.height // 2).move(2, 3),
    )
    cx, cy = rect.center
    radius = max(2, round(3 * zoom))
    for dx, dy in ((-4, 1), (3, -2), (4, 4)):
        pygame.draw.circle(
            screen,
            (191, 45, 72),
            (cx + round(dx * zoom), cy + round(dy * zoom)),
            radius,
        )
