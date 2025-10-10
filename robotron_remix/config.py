"""Configuration constants for Robotron Remix."""
from __future__ import annotations

from pathlib import Path

import pygame

# Ensure audio mixer is configured before the rest of pygame initialises.
pygame.mixer.pre_init(44100, -16, 1, 512)

# Display configuration.
WIDTH, HEIGHT = 960, 720
FPS = 60

# Gameplay tuning.
ARENA_MARGIN = 32
PLAYER_SPEED = 320
BULLET_SPEED = 640
ENEMY_SPEED = 140
MAX_ENEMIES = 30
INVULNERABLE_TIME = 2.0
SHOOT_COOLDOWN = 0.16
BASE_SPAWN_INTERVAL = 1.2
MIN_SPAWN_INTERVAL = 0.45
BASE_ENEMIES_PER_WAVE = 12
ENEMIES_PER_WAVE_INCREASE = 6
SAMPLE_RATE = 44100

# Colours.
BACKGROUND_COLOR = (5, 5, 25)
ARENA_COLOR = (40, 40, 90)
PLAYER_COLOR = (60, 220, 255)
BULLET_COLOR = (255, 245, 180)
ENEMY_COLOR_SETS = [
    [(255, 70, 90), (255, 130, 70), (255, 200, 70)],
    [(120, 255, 190), (80, 240, 220), (160, 220, 255)],
    [(200, 140, 255), (255, 120, 210), (255, 180, 240)],
    [(255, 220, 120), (255, 185, 90), (255, 240, 170)],
]

# High score handling.
MAX_HIGH_SCORES = 5
HIGH_SCORE_PATH = Path(__file__).with_name("high_scores.json")

__all__ = [
    "WIDTH",
    "HEIGHT",
    "FPS",
    "ARENA_MARGIN",
    "PLAYER_SPEED",
    "BULLET_SPEED",
    "ENEMY_SPEED",
    "MAX_ENEMIES",
    "INVULNERABLE_TIME",
    "SHOOT_COOLDOWN",
    "BASE_SPAWN_INTERVAL",
    "MIN_SPAWN_INTERVAL",
    "BASE_ENEMIES_PER_WAVE",
    "ENEMIES_PER_WAVE_INCREASE",
    "SAMPLE_RATE",
    "BACKGROUND_COLOR",
    "ARENA_COLOR",
    "PLAYER_COLOR",
    "BULLET_COLOR",
    "ENEMY_COLOR_SETS",
    "MAX_HIGH_SCORES",
    "HIGH_SCORE_PATH",
]
