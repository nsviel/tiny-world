"""Water tile rendering."""

import pygame


def draw_water(screen: pygame.Surface, rect: pygame.Rect, shade: int) -> None:
    pygame.draw.rect(
        screen,
        (54, 132 + shade, 174 + shade),
        rect,
        border_radius=3,
    )
    pygame.draw.line(
        screen,
        (97, 175, 202),
        (rect.left + 4, rect.centery),
        (rect.right - 4, rect.centery),
        1,
    )
