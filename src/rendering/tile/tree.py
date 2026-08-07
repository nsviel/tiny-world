"""Tree tile rendering with an optional PNG asset."""

import pygame

from ..engine.assets import AssetStore


def draw_tree(
    screen: pygame.Surface,
    rect: pygame.Rect,
    zoom: float,
    assets: AssetStore,
) -> None:
    image = assets.get("tree", rect.size)
    if image is not None:
        screen.blit(image, rect)
        return

    cx, cy = rect.center
    pygame.draw.ellipse(screen, (30, 70, 42), rect.move(round(3 * zoom), round(4 * zoom)))
    pygame.draw.rect(
        screen,
        (105, 72, 42),
        (cx - round(3 * zoom), cy, max(2, round(6 * zoom)), max(3, round(10 * zoom))),
    )
    pygame.draw.circle(screen, (30, 92, 48), (cx, cy - round(3 * zoom)), max(3, round(10 * zoom)))
    pygame.draw.circle(
        screen,
        (46, 116, 58),
        (cx - round(4 * zoom), cy - round(6 * zoom)),
        max(2, round(7 * zoom)),
    )
