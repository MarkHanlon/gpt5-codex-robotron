"""Simple star field background animation."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List

import pygame

from .config import HEIGHT, WIDTH


@dataclass
class Star:
    position: pygame.Vector2
    speed: float
    size: int

    def update(self, dt: float) -> None:
        self.position.y += self.speed * dt
        if self.position.y > HEIGHT:
            self.position.y = -10
            self.position.x = random.uniform(0, WIDTH)


class StarField:
    def __init__(self) -> None:
        self.stars: List[Star] = [
            Star(
                pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)),
                random.uniform(20, 80),
                random.randint(1, 3),
            )
            for _ in range(120)
        ]

    def update(self, dt: float) -> None:
        for star in self.stars:
            star.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        for star in self.stars:
            pygame.draw.circle(surface, (star.size * 40, star.size * 40, 255), star.position, star.size)


__all__ = ["Star", "StarField"]
