"""Particle effects and celebratory backgrounds."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Tuple

import pygame

from .config import HEIGHT, PLAYER_COLOR, WIDTH


class Particle(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: Tuple[float, float],
        velocity: pygame.Vector2,
        color: Tuple[int, int, int],
        lifetime: float,
        size: int,
    ) -> None:
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.size = size
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size, size), size)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt: float) -> None:
        self.age += dt
        if self.age >= self.lifetime:
            self.kill()
            return

        self.pos += self.velocity * dt
        fade = max(0, 1 - self.age / self.lifetime)
        radius = max(1, int(self.size * fade))
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        rgba = (*self.color[:3], int(255 * fade))
        pygame.draw.circle(self.image, rgba, (radius, radius), radius)
        self.rect = self.image.get_rect(center=self.pos)


class ParticleSystem:
    """Manage particle sprites for simple burst and trail effects."""

    def __init__(self, group: pygame.sprite.Group) -> None:
        self.group = group

    def burst(
        self,
        pos: Tuple[float, float],
        base_color: Tuple[int, int, int],
        amount: int,
        speed: Tuple[float, float],
        lifetime: Tuple[float, float],
        size: Tuple[int, int],
    ) -> None:
        for _ in range(amount):
            angle = random.uniform(0, math.tau)
            magnitude = random.uniform(*speed)
            vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * magnitude
            color_variation = tuple(
                min(255, max(0, c + random.randint(-40, 40))) for c in base_color
            )
            particle = Particle(
                pos,
                vel,
                color_variation,
                lifetime=random.uniform(*lifetime),
                size=random.randint(*size),
            )
            self.group.add(particle)

    def trail(self, pos: Tuple[float, float], color: Tuple[int, int, int]) -> None:
        self.burst(pos, color, amount=4, speed=(20, 60), lifetime=(0.2, 0.45), size=(1, 2))


def emit_burst(
    system: ParticleSystem,
    pos: Tuple[float, float] | pygame.Vector2,
    base_color: Tuple[int, int, int],
    *,
    amount: int,
    speed: Tuple[float, float],
    lifetime: Tuple[float, float],
    size: Tuple[int, int],
) -> None:
    """Emit a configurable burst using the shared particle system."""
    pos_tuple = (float(pos[0]), float(pos[1]))
    system.burst(pos_tuple, base_color, amount=amount, speed=speed, lifetime=lifetime, size=size)


def emit_trail(
    system: ParticleSystem, pos: Tuple[float, float] | pygame.Vector2, color: Tuple[int, int, int]
) -> None:
    """Emit a short trail effect at the given position."""

    pos_tuple = (float(pos[0]), float(pos[1]))
    system.trail(pos_tuple, color)


@dataclass
class CelebrationParticle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    color: Tuple[int, int, int]
    size: int
    life: float
    max_life: float


class CelebrationBackground:
    """Background animation used on the high score screen."""

    def __init__(self, count: int = 220) -> None:
        self.particles: list[CelebrationParticle] = [self._create_particle() for _ in range(count)]

    def _create_particle(self) -> CelebrationParticle:
        position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        angle = random.uniform(0, math.tau)
        speed = random.uniform(60, 180)
        velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        color = (
            random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255),
        )
        size = random.randint(2, 5)
        life = random.uniform(1.8, 3.8)
        return CelebrationParticle(position, velocity, color, size, life, life)

    def _reset_particle(self, particle: CelebrationParticle) -> None:
        particle.position.update(
            WIDTH / 2 + random.uniform(-WIDTH / 3, WIDTH / 3),
            HEIGHT / 2 + random.uniform(-HEIGHT / 3, HEIGHT / 3),
        )
        angle = random.uniform(0, math.tau)
        speed = random.uniform(90, 220)
        particle.velocity.update(math.cos(angle) * speed, math.sin(angle) * speed)
        particle.color = (
            random.randint(120, 255),
            random.randint(120, 255),
            random.randint(120, 255),
        )
        particle.size = random.randint(2, 5)
        particle.max_life = random.uniform(1.6, 3.6)
        particle.life = particle.max_life

    def update(self, dt: float) -> None:
        for particle in self.particles:
            particle.life -= dt
            if particle.life <= 0:
                self._reset_particle(particle)
                continue
            particle.position += particle.velocity * dt
            particle.velocity.rotate_ip(random.uniform(-90, 90) * dt)
            if not (-120 <= particle.position.x <= WIDTH + 120) or not (
                -120 <= particle.position.y <= HEIGHT + 120
            ):
                self._reset_particle(particle)

    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            brightness = max(0.0, particle.life / particle.max_life)
            alpha = int(255 * brightness ** 2)
            radius = max(1, int(particle.size * (0.5 + brightness * 0.8)))
            color = (*particle.color, alpha)
            pygame.draw.circle(surface, color, particle.position, radius)


def player_trail(system: ParticleSystem, pos: Tuple[float, float]) -> None:
    emit_trail(system, pos, PLAYER_COLOR)


__all__ = [
    "Particle",
    "ParticleSystem",
    "emit_burst",
    "emit_trail",
    "player_trail",
    "CelebrationParticle",
    "CelebrationBackground",
]
