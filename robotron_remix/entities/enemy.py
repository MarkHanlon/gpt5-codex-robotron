"""Enemy entity definitions."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple

import pygame

from ..config import ENEMY_SPEED


@dataclass
class EnemyAppearance:
    colors: List[Tuple[int, int, int]]
    shape: str
    accent: Tuple[int, int, int]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[float, float], appearance: EnemyAppearance) -> None:
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2()
        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)
        color = random.choice(appearance.colors)
        shape = appearance.shape
        if shape == "triangle":
            pygame.draw.polygon(self.image, color, [(18, 4), (32, 30), (4, 30)])
        elif shape == "circle":
            pygame.draw.circle(self.image, color, (18, 18), 16)
        else:
            pygame.draw.rect(self.image, color, (4, 4, 28, 28), border_radius=6)
        accent_color = appearance.accent
        pygame.draw.circle(self.image, accent_color, (18, 14), 6)
        pygame.draw.circle(self.image, (0, 0, 0), (18, 14), 3)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, target: pygame.Vector2) -> None:
        direction = target - self.pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.velocity = direction * ENEMY_SPEED
        self.pos += self.velocity * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
