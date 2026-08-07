"""Ground tile rendering."""

import pygame


def draw_ground(screen: pygame.Surface, rect: pygame.Rect, shade: int) -> None:
    pygame.draw.rect(screen, (74 + shade, 137 + shade, 78 + shade), rect)
