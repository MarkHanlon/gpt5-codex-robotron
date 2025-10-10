"""Audio subsystem for Robotron Remix."""
from __future__ import annotations

import math
from array import array
from typing import Iterable, Protocol

import pygame

from .config import SAMPLE_RATE


class HasPosition(Protocol):
    """Protocol describing objects that expose a pygame position vector."""

    pos: pygame.Vector2


class AudioManager:
    """Generate and play synthesised sound effects."""

    def __init__(self) -> None:
        self.available = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)
        except pygame.error:
            self.available = False
            return

        self.move_channel = pygame.mixer.Channel(1)
        self.proximity_channel = pygame.mixer.Channel(2)

        self.move_sound = self._create_engine_sound()
        self.shoot_sound = self._create_shot_sound()
        self.death_sound = self._create_death_sound()
        self.proximity_sound = self._create_proximity_loop()

    def _generate_wave(
        self,
        frequency: float,
        duration: float,
        volume: float,
        *,
        harmonics: list[tuple[float, float]] | None = None,
    ) -> bytes:
        sample_count = max(1, int(SAMPLE_RATE * duration))
        data = array("h")
        harmonics = harmonics or []
        attack = int(0.02 * SAMPLE_RATE)
        release = int(0.04 * SAMPLE_RATE)
        for index in range(sample_count):
            base_phase = (index / SAMPLE_RATE) * frequency * math.tau
            sample = math.sin(base_phase)
            for multiplier, weight in harmonics:
                sample += weight * math.sin(base_phase * multiplier)
            envelope = 1.0
            if attack:
                envelope *= min(1.0, index / max(1, attack))
            if release and index >= sample_count - release:
                envelope *= max(0.0, (sample_count - index) / max(1, release))
            data.append(int(sample * volume * 32767 * envelope))
        return data.tobytes()

    def _create_engine_sound(self) -> pygame.mixer.Sound:
        buffer = array("h")
        chunk = self._generate_wave(110, 0.18, 0.25, harmonics=[(2.0, 0.35), (3.0, 0.2)])
        buffer.frombytes(chunk)
        return pygame.mixer.Sound(buffer=buffer.tobytes())

    def _create_shot_sound(self) -> pygame.mixer.Sound:
        chunk = self._generate_wave(760, 0.12, 0.35, harmonics=[(1.5, 0.5), (2.0, 0.3)])
        return pygame.mixer.Sound(buffer=chunk)

    def _create_death_sound(self) -> pygame.mixer.Sound:
        duration = 0.6
        sample_count = max(1, int(SAMPLE_RATE * duration))
        data = array("h")
        for index in range(sample_count):
            t = index / SAMPLE_RATE
            freq = max(70.0, 320.0 * (1 - t))
            phase = freq * math.tau * t
            envelope = max(0.0, 1 - t / duration)
            sample = math.sin(phase) * envelope
            data.append(int(sample * 0.5 * 32767))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def _create_proximity_loop(self) -> pygame.mixer.Sound:
        duration = 0.5
        sample_count = max(1, int(SAMPLE_RATE * duration))
        data = array("h")
        pulse_width = int(0.08 * SAMPLE_RATE)
        for index in range(sample_count):
            cycle_position = index % int(0.25 * SAMPLE_RATE)
            envelope = 0.0
            if cycle_position < pulse_width:
                envelope = 1.0 - (cycle_position / max(1, pulse_width))
            noise = math.sin(index / SAMPLE_RATE * 220 * math.tau) * 0.6
            sample = (noise + math.sin(index / SAMPLE_RATE * 440 * math.tau) * 0.3) * envelope
            data.append(int(sample * 0.4 * 32767))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def update_player_movement(self, moving: bool) -> None:
        if not self.available:
            return
        if moving:
            if not self.move_channel.get_busy():
                self.move_channel.play(self.move_sound, loops=-1)
            self.move_channel.set_volume(0.3)
        else:
            if self.move_channel.get_busy():
                self.move_channel.fadeout(150)

    def play_shoot(self) -> None:
        if not self.available:
            return
        self.shoot_sound.play()

    def play_player_death(self) -> None:
        if not self.available:
            return
        self.death_sound.play()

    def update_enemy_proximity(
        self, player_pos: pygame.Vector2, enemies: Iterable[HasPosition]
    ) -> None:
        if not self.available:
            return
        enemy_positions = [enemy.pos for enemy in enemies]
        if not enemy_positions:
            if self.proximity_channel.get_busy():
                self.proximity_channel.fadeout(200)
            return
        min_distance = min(player_pos.distance_to(position) for position in enemy_positions)
        proximity = max(0.0, min(1.0, 1 - min_distance / 420))
        if proximity <= 0:
            if self.proximity_channel.get_busy():
                self.proximity_channel.fadeout(200)
            return
        if not self.proximity_channel.get_busy():
            self.proximity_channel.play(self.proximity_sound, loops=-1)
        self.proximity_channel.set_volume(0.1 + proximity * 0.5)

    def stop_all(self) -> None:
        if not self.available:
            return
        self.move_channel.stop()
        self.proximity_channel.stop()


__all__ = ["AudioManager", "HasPosition"]
