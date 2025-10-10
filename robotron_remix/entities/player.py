"""Player entity and control logic."""
from __future__ import annotations

from typing import List, Tuple

import pygame

from ..audio import AudioManager
from ..config import (
    ARENA_MARGIN,
    BULLET_COLOR,
    HEIGHT,
    INVULNERABLE_TIME,
    PLAYER_COLOR,
    PLAYER_SPEED,
    SHOOT_COOLDOWN,
    WIDTH,
)
from ..particles import ParticleSystem, emit_burst, player_trail


class Player(pygame.sprite.Sprite):
    def __init__(self, particles: ParticleSystem, audio: AudioManager | None = None) -> None:
        super().__init__()
        self.pos = pygame.Vector2()
        self.velocity = pygame.Vector2()
        self.particles = particles
        self.audio = audio
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, PLAYER_COLOR, [(15, 0), (30, 25), (15, 30), (0, 25)])
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.cooldown = 0.0
        self.invulnerable_timer = 0.0
        self.lives = 3
        self.reset()

    def reset(self) -> None:
        self.pos.update(WIDTH / 2, HEIGHT / 2)
        self.velocity.update()
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.invulnerable_timer = INVULNERABLE_TIME
        self.cooldown = 0.0

    def update(
        self, dt: float, keys: pygame.key.ScancodeWrapper
    ) -> List[Tuple[pygame.Vector2, pygame.Vector2]]:
        move = pygame.Vector2(
            int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
            int(keys[pygame.K_s]) - int(keys[pygame.K_w]),
        )
        if move.length_squared() > 0:
            move = move.normalize()
        self.velocity = move * PLAYER_SPEED
        self.pos += self.velocity * dt
        self.pos.x = max(ARENA_MARGIN, min(WIDTH - ARENA_MARGIN, self.pos.x))
        self.pos.y = max(ARENA_MARGIN, min(HEIGHT - ARENA_MARGIN, self.pos.y))
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        moving = self.velocity.length_squared() > 0
        if moving:
            player_trail(self.particles, self.pos)
        if self.audio:
            self.audio.update_player_movement(moving)

        self.cooldown = max(0.0, self.cooldown - dt)
        self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        shots: List[Tuple[pygame.Vector2, pygame.Vector2]] = []
        shoot_dir = pygame.Vector2(
            int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]),
            int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]),
        )
        if shoot_dir.length_squared() > 0:
            shoot_dir = shoot_dir.normalize()
            if self.cooldown <= 0:
                shots.append((self.pos.copy(), shoot_dir))
                self.cooldown = SHOOT_COOLDOWN
                emit_burst(
                    self.particles,
                    self.pos,
                    BULLET_COLOR,
                    amount=12,
                    speed=(240, 380),
                    lifetime=(0.15, 0.4),
                    size=(2, 3),
                )
                if self.audio:
                    self.audio.play_shoot()
        return shots

    @property
    def invulnerable(self) -> bool:
        return self.invulnerable_timer > 0
