"""Game orchestration for Robotron Remix."""
from __future__ import annotations

import random

import pygame

from .audio import AudioManager
from .background import StarField
from .config import (
    ARENA_COLOR,
    ARENA_MARGIN,
    BACKGROUND_COLOR,
    BASE_ENEMIES_PER_WAVE,
    BASE_SPAWN_INTERVAL,
    ENEMIES_PER_WAVE_INCREASE,
    ENEMY_COLOR_SETS,
    FPS,
    HEIGHT,
    INVULNERABLE_TIME,
    MAX_ENEMIES,
    MIN_SPAWN_INTERVAL,
    PLAYER_COLOR,
    WIDTH,
)
from .entities import Bullet, Enemy, EnemyAppearance, Player
from .high_scores import HighScoreManager
from .particles import ParticleSystem, emit_burst
from .ui.high_score_screen import HighScoreOutcome, HighScoreScreen


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Robotron Remix")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = False
        self.exiting = False

        self.all_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.particle_sprites = pygame.sprite.Group()

        self.particles = ParticleSystem(self.particle_sprites)
        self.audio = AudioManager()
        self.player = Player(self.particles, audio=self.audio)
        self.all_sprites.add(self.player)

        self.star_field = StarField()
        self.high_scores = HighScoreManager()
        self.high_score_screen = HighScoreScreen(self.screen, self.clock, self.high_scores)

        self.time_since_spawn = 0.0
        self.wave = 1
        self.score = 0
        self.spawned_this_wave = 0
        self.current_wave_enemy_limit = 0
        self.spawn_interval = 0.0
        self.current_enemy_appearance = self.get_wave_appearance(self.wave)
        self.prepare_wave()

    def enemies_for_wave(self, wave: int) -> int:
        return BASE_ENEMIES_PER_WAVE + (wave - 1) * ENEMIES_PER_WAVE_INCREASE

    def spawn_interval_for_wave(self, wave: int) -> float:
        return max(MIN_SPAWN_INTERVAL, BASE_SPAWN_INTERVAL * (0.88 ** (wave - 1)))

    def get_wave_appearance(self, wave: int) -> EnemyAppearance:
        palette = ENEMY_COLOR_SETS[(wave - 1) % len(ENEMY_COLOR_SETS)]
        shapes = ["square", "triangle", "circle"]
        shape = shapes[(wave - 1) % len(shapes)]
        accent = (255, 255, 255) if shape != "circle" else (20, 20, 20)
        return EnemyAppearance(palette, shape, accent)

    def prepare_wave(self) -> None:
        self.spawned_this_wave = 0
        self.current_wave_enemy_limit = self.enemies_for_wave(self.wave)
        self.spawn_interval = self.spawn_interval_for_wave(self.wave)
        self.current_enemy_appearance = self.get_wave_appearance(self.wave)
        self.time_since_spawn = 0.0

    def spawn_enemy(self) -> None:
        if len(self.enemy_sprites) >= MAX_ENEMIES:
            return
        if self.spawned_this_wave >= self.current_wave_enemy_limit:
            return
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            pos = (random.uniform(ARENA_MARGIN, WIDTH - ARENA_MARGIN), -20)
        elif side == "bottom":
            pos = (random.uniform(ARENA_MARGIN, WIDTH - ARENA_MARGIN), HEIGHT + 20)
        elif side == "left":
            pos = (-20, random.uniform(ARENA_MARGIN, HEIGHT - ARENA_MARGIN))
        else:
            pos = (WIDTH + 20, random.uniform(ARENA_MARGIN, HEIGHT - ARENA_MARGIN))
        enemy = Enemy(pos, self.current_enemy_appearance)
        self.enemy_sprites.add(enemy)
        self.all_sprites.add(enemy)
        wave_color = random.choice(self.current_enemy_appearance.colors)
        emit_burst(self.particles, pos, wave_color, amount=25, speed=(40, 150), lifetime=(0.4, 0.8), size=(2, 4))
        self.spawned_this_wave += 1

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        shots = self.player.update(dt, keys)
        for pos, direction in shots:
            bullet = Bullet(pos, direction, self.particles)
            self.bullet_sprites.add(bullet)
            self.all_sprites.add(bullet)

        for enemy in list(self.enemy_sprites):
            enemy.update(dt, self.player.pos)

        for bullet in list(self.bullet_sprites):
            bullet.update(dt)

        for particle in list(self.particle_sprites):
            particle.update(dt)

        self.handle_collisions()
        self.star_field.update(dt)
        self.audio.update_enemy_proximity(self.player.pos, self.enemy_sprites)

        self.time_since_spawn += dt
        if (
            self.spawned_this_wave < self.current_wave_enemy_limit
            and self.time_since_spawn >= self.spawn_interval
        ):
            self.time_since_spawn = 0.0
            self.spawn_enemy()

        if (
            self.spawned_this_wave >= self.current_wave_enemy_limit
            and not self.enemy_sprites
            and self.spawned_this_wave > 0
        ):
            self.wave += 1
            self.prepare_wave()

    def handle_collisions(self) -> None:
        for bullet in pygame.sprite.groupcollide(self.bullet_sprites, self.enemy_sprites, True, True):
            self.score += 15
            emit_burst(self.particles, bullet.pos, (255, 180, 80), amount=40, speed=(100, 260), lifetime=(0.3, 0.7), size=(2, 4))
            emit_burst(self.particles, bullet.pos, (255, 255, 255), amount=12, speed=(200, 360), lifetime=(0.2, 0.4), size=(1, 2))

        if self.player.invulnerable:
            return

        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, dokill=True):
            self.player.lives -= 1
            self.player.invulnerable_timer = INVULNERABLE_TIME
            emit_burst(self.particles, self.player.pos, PLAYER_COLOR, amount=60, speed=(120, 260), lifetime=(0.4, 0.8), size=(2, 4))
            self.audio.play_player_death()
            if self.player.lives <= 0:
                self.running = False
            else:
                self.player.reset()

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.star_field.draw(self.screen)

        arena_rect = pygame.Rect(ARENA_MARGIN, ARENA_MARGIN, WIDTH - 2 * ARENA_MARGIN, HEIGHT - 2 * ARENA_MARGIN)
        pygame.draw.rect(self.screen, ARENA_COLOR, arena_rect, 4)
        glow_rect = arena_rect.inflate(12, 12)
        pygame.draw.rect(self.screen, (80, 80, 160), glow_rect, 2)

        for sprite in self.enemy_sprites:
            self.screen.blit(sprite.image, sprite.rect)
        for sprite in self.bullet_sprites:
            self.screen.blit(sprite.image, sprite.rect)
        for sprite in self.particle_sprites:
            self.screen.blit(sprite.image, sprite.rect)
        self.screen.blit(self.player.image, self.player.rect)

        self.draw_hud()
        pygame.display.flip()

    def draw_hud(self) -> None:
        font = pygame.font.SysFont("Consolas", 28)
        score_surface = font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_surface = font.render(f"Lives: {self.player.lives}", True, (255, 140, 180))
        wave_surface = font.render(f"Wave: {self.wave}", True, (200, 220, 255))
        self.screen.blit(score_surface, (ARENA_MARGIN, 8))
        self.screen.blit(wave_surface, (WIDTH / 2 - wave_surface.get_width() / 2, 8))
        self.screen.blit(lives_surface, (WIDTH - ARENA_MARGIN - lives_surface.get_width(), 8))
        if self.player.invulnerable:
            warning = font.render("Re-initializing!", True, (255, 240, 120))
            self.screen.blit(warning, (WIDTH / 2 - warning.get_width() / 2, HEIGHT - 40))

    def start_new_game(self) -> None:
        self.score = 0
        self.player.lives = 3
        self.player.reset()
        self.enemy_sprites.empty()
        self.bullet_sprites.empty()
        self.particle_sprites.empty()
        self.time_since_spawn = 0.0
        self.wave = 1
        self.prepare_wave()
        self.running = True
        self.exiting = False
        self.audio.stop_all()

    def run(self) -> None:
        show_intro = True
        continue_playing = True
        while continue_playing:
            if show_intro:
                outcome = self.high_score_screen.show(start=True)
                self.exiting = outcome.exit_requested
                if outcome.exit_requested:
                    break
                if not outcome.continue_playing:
                    break
                show_intro = False
            self.start_new_game()
            self.game_loop()
            if self.exiting:
                break
            outcome = self.game_over()
            self.exiting = outcome.exit_requested
            continue_playing = outcome.continue_playing and not outcome.exit_requested

    def game_loop(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.exiting = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            if not self.running:
                break

            self.update(dt)
            self.draw()

        self.audio.stop_all()

    def game_over(self) -> HighScoreOutcome:
        return self.high_score_screen.show(start=False, new_score=self.score)
