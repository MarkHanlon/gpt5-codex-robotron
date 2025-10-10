"""Projectile entities."""
from __future__ import annotations

import pygame

from ..config import BULLET_COLOR, BULLET_SPEED, HEIGHT, WIDTH
from ..particles import ParticleSystem, emit_trail


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, direction: pygame.Vector2, particles: ParticleSystem) -> None:
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.direction = pygame.Vector2(direction)
        self.particles = particles
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BULLET_COLOR, (5, 5), 5)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt: float) -> None:
        self.pos += self.direction * BULLET_SPEED * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        emit_trail(self.particles, self.pos, BULLET_COLOR)
        if not (-50 <= self.pos.x <= WIDTH + 50 and -50 <= self.pos.y <= HEIGHT + 50):
            self.kill()
