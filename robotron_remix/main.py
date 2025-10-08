"""Robotron-inspired twin-stick shooter with particle effects."""
from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

import pygame

WIDTH, HEIGHT = 960, 720
FPS = 60

ARENA_MARGIN = 32
PLAYER_SPEED = 320
BULLET_SPEED = 640
ENEMY_SPEED = 140
SPAWN_INTERVAL = 1.2
MAX_ENEMIES = 30
INVULNERABLE_TIME = 2.0
SHOOT_COOLDOWN = 0.16

BACKGROUND_COLOR = (5, 5, 25)
ARENA_COLOR = (40, 40, 90)
PLAYER_COLOR = (60, 220, 255)
BULLET_COLOR = (255, 245, 180)
ENEMY_COLORS = [(255, 70, 90), (255, 130, 70), (255, 200, 70)]

MAX_HIGH_SCORES = 5
HIGH_SCORE_PATH = Path(__file__).with_name("high_scores.json")


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[float, float], velocity: pygame.Vector2, color: Tuple[int, int, int],
                 lifetime: float, size: int) -> None:
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
    def __init__(self, group: pygame.sprite.Group) -> None:
        self.group = group

    def burst(self, pos: Tuple[float, float], base_color: Tuple[int, int, int], amount: int,
              speed: Tuple[float, float], lifetime: Tuple[float, float], size: Tuple[int, int]) -> None:
        for _ in range(amount):
            angle = random.uniform(0, math.tau)
            magnitude = random.uniform(*speed)
            vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * magnitude
            color_variation = tuple(min(255, max(0, c + random.randint(-40, 40))) for c in base_color)
            particle = Particle(pos, vel, color_variation,
                                lifetime=random.uniform(*lifetime),
                                size=random.randint(*size))
            self.group.add(particle)

    def trail(self, pos: Tuple[float, float], color: Tuple[int, int, int]) -> None:
        self.burst(pos, color, amount=4, speed=(20, 60), lifetime=(0.2, 0.45), size=(1, 2))


class HighScoreManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.scores: List[dict[str, int | str]] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.scores = []
            return
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            self.scores = []
            return
        if isinstance(data, list):
            valid_scores = []
            for item in data:
                if (
                    isinstance(item, dict)
                    and isinstance(item.get("initials"), str)
                    and isinstance(item.get("score"), int)
                ):
                    valid_scores.append({
                        "initials": item["initials"][:3].upper(),
                        "score": item["score"],
                    })
            self.scores = sorted(valid_scores, key=lambda entry: entry["score"], reverse=True)[:MAX_HIGH_SCORES]
        else:
            self.scores = []

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", encoding="utf-8") as fh:
                json.dump(self.scores, fh, indent=2)
        except OSError:
            pass

    def qualifies(self, score: int) -> bool:
        if score <= 0:
            return False
        if len(self.scores) < MAX_HIGH_SCORES:
            return True
        return score > self.scores[-1]["score"]

    def add_score(self, initials: str, score: int) -> None:
        initials = initials[:3].upper()
        self.scores.append({"initials": initials, "score": score})
        self.scores.sort(key=lambda entry: entry["score"], reverse=True)
        del self.scores[MAX_HIGH_SCORES:]
        self.save()


@dataclass
class CelebrationParticle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    color: Tuple[int, int, int]
    size: int
    life: float
    max_life: float


class CelebrationBackground:
    def __init__(self, count: int = 220) -> None:
        self.particles: List[CelebrationParticle] = [self._create_particle() for _ in range(count)]

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
            if not (-120 <= particle.position.x <= WIDTH + 120) or not (-120 <= particle.position.y <= HEIGHT + 120):
                self._reset_particle(particle)

    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            brightness = max(0.0, particle.life / particle.max_life)
            alpha = int(255 * brightness ** 2)
            radius = max(1, int(particle.size * (0.5 + brightness * 0.8)))
            color = (*particle.color, alpha)
            pygame.draw.circle(surface, color, particle.position, radius)


class Player(pygame.sprite.Sprite):
    def __init__(self, particles: ParticleSystem) -> None:
        super().__init__()
        self.pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.velocity = pygame.Vector2()
        self.particles = particles
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, PLAYER_COLOR, [(15, 0), (30, 25), (15, 30), (0, 25)])
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.cooldown = 0.0
        self.invulnerable_timer = 0.0
        self.lives = 3

    def reset(self) -> None:
        self.pos.update(WIDTH / 2, HEIGHT / 2)
        self.velocity.update()
        self.invulnerable_timer = INVULNERABLE_TIME

    def update(self, dt: float, keys: Iterable[int]) -> List[Tuple[pygame.Vector2, pygame.Vector2]]:
        keys_pressed = pygame.key.get_pressed()
        move = pygame.Vector2(
            int(keys_pressed[pygame.K_d]) - int(keys_pressed[pygame.K_a]),
            int(keys_pressed[pygame.K_s]) - int(keys_pressed[pygame.K_w]),
        )
        if move.length_squared() > 0:
            move = move.normalize()
        self.velocity = move * PLAYER_SPEED
        self.pos += self.velocity * dt
        self.pos.x = max(ARENA_MARGIN, min(WIDTH - ARENA_MARGIN, self.pos.x))
        self.pos.y = max(ARENA_MARGIN, min(HEIGHT - ARENA_MARGIN, self.pos.y))
        self.rect.center = self.pos

        if self.velocity.length_squared() > 0:
            self.particles.trail(self.pos, PLAYER_COLOR)

        self.cooldown = max(0.0, self.cooldown - dt)
        self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        shots: List[Tuple[pygame.Vector2, pygame.Vector2]] = []
        shoot_dir = pygame.Vector2(
            int(keys_pressed[pygame.K_RIGHT]) - int(keys_pressed[pygame.K_LEFT]),
            int(keys_pressed[pygame.K_DOWN]) - int(keys_pressed[pygame.K_UP]),
        )
        if shoot_dir.length_squared() > 0:
            shoot_dir = shoot_dir.normalize()
            if self.cooldown <= 0:
                shots.append((self.pos.copy(), shoot_dir))
                self.cooldown = SHOOT_COOLDOWN
                self.particles.burst(self.pos, BULLET_COLOR, 12, (240, 380), (0.15, 0.4), (2, 3))
        return shots

    @property
    def invulnerable(self) -> bool:
        return self.invulnerable_timer > 0


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
        self.rect.center = self.pos
        self.particles.trail(self.pos, BULLET_COLOR)
        if not (-50 <= self.pos.x <= WIDTH + 50 and -50 <= self.pos.y <= HEIGHT + 50):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[float, float]) -> None:
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        color = random.choice(ENEMY_COLORS)
        pygame.draw.rect(self.image, color, (0, 0, 32, 32), border_radius=8)
        pygame.draw.circle(self.image, (255, 255, 255), (16, 12), 5)
        pygame.draw.circle(self.image, (0, 0, 0), (16, 12), 2)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt: float, target: pygame.Vector2) -> None:
        direction = target - self.pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.velocity = direction * ENEMY_SPEED
        self.pos += self.velocity * dt
        self.rect.center = self.pos


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


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Robotron Remix")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = False

        self.all_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.particle_sprites = pygame.sprite.Group()

        self.particles = ParticleSystem(self.particle_sprites)
        self.player = Player(self.particles)
        self.all_sprites.add(self.player)

        self.star_field = StarField()

        self.time_since_spawn = 0.0
        self.score = 0
        self.exiting = False
        self.high_scores = HighScoreManager(HIGH_SCORE_PATH)

    def spawn_enemy(self) -> None:
        if len(self.enemy_sprites) >= MAX_ENEMIES:
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
        enemy = Enemy(pos)
        self.enemy_sprites.add(enemy)
        self.all_sprites.add(enemy)
        self.particles.burst(pos, random.choice(ENEMY_COLORS), 25, (40, 150), (0.4, 0.8), (2, 4))

    def update(self, dt: float) -> None:
        shots = self.player.update(dt, pygame.key.get_pressed())
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

        self.time_since_spawn += dt
        if self.time_since_spawn >= SPAWN_INTERVAL:
            self.time_since_spawn = 0.0
            self.spawn_enemy()

    def handle_collisions(self) -> None:
        for bullet in pygame.sprite.groupcollide(self.bullet_sprites, self.enemy_sprites, True, True):
            self.score += 15
            self.particles.burst(bullet.pos, (255, 180, 80), 40, (100, 260), (0.3, 0.7), (2, 4))
            self.particles.burst(bullet.pos, (255, 255, 255), 12, (200, 360), (0.2, 0.4), (1, 2))

        if self.player.invulnerable:
            return

        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, dokill=True):
            self.player.lives -= 1
            self.player.invulnerable_timer = INVULNERABLE_TIME
            self.particles.burst(self.player.pos, PLAYER_COLOR, 60, (120, 260), (0.4, 0.8), (2, 4))
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
        self.screen.blit(score_surface, (ARENA_MARGIN, 8))
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
        self.running = True
        self.exiting = False

    def run(self) -> None:
        show_intro = True
        continue_playing = True
        while continue_playing:
            if show_intro:
                if not self.show_high_score_screen(start=True):
                    break
                show_intro = False
            self.start_new_game()
            self.game_loop()
            if self.exiting:
                break
            continue_playing = self.game_over()

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

    def game_over(self) -> bool:
        return self.show_high_score_screen(start=False, new_score=self.score)

    def show_high_score_screen(self, start: bool, new_score: int | None = None) -> bool:
        background = CelebrationBackground()
        title_font = pygame.font.SysFont("Consolas", 64)
        entry_font = pygame.font.SysFont("Consolas", 36)
        small_font = pygame.font.SysFont("Consolas", 24)

        entering_initials = new_score is not None and self.high_scores.qualifies(new_score)
        initials = ["A", "A", "A"]
        selected_index = 0
        highlight_pair: Tuple[str, int] | None = None

        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exiting = True
                    return False
                if event.type == pygame.KEYDOWN:
                    if entering_initials:
                        if event.key == pygame.K_RIGHT:
                            selected_index = (selected_index + 1) % len(initials)
                        elif event.key == pygame.K_LEFT:
                            selected_index = (selected_index - 1) % len(initials)
                        elif event.key == pygame.K_UP:
                            initials[selected_index] = chr(
                                (ord(initials[selected_index]) - ord("A") + 1) % 26 + ord("A")
                            )
                        elif event.key == pygame.K_DOWN:
                            initials[selected_index] = chr(
                                (ord(initials[selected_index]) - ord("A") - 1) % 26 + ord("A")
                            )
                        elif event.key == pygame.K_RETURN:
                            initials_str = "".join(initials)
                            self.high_scores.add_score(initials_str, int(new_score))
                            highlight_pair = (initials_str, int(new_score))
                            entering_initials = False
                        elif event.key == pygame.K_ESCAPE:
                            return False
                    else:
                        if event.key == pygame.K_RETURN:
                            return True
                        if event.key == pygame.K_ESCAPE:
                            return False

            background.update(dt)
            self.screen.fill((10, 8, 40))
            background.draw(self.screen)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 10, 30, 180))
            self.screen.blit(overlay, (0, 0))

            title_text = title_font.render("HIGH SCORES", True, (255, 255, 255))
            self.screen.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, 60))

            if new_score is not None:
                score_label = entry_font.render(f"Your Score: {new_score}", True, (255, 230, 130))
                self.screen.blit(score_label, (WIDTH / 2 - score_label.get_width() / 2, 140))

            prompt_text: str
            if entering_initials:
                prompt_text = "New high score! Use arrow keys to set your initials."
            elif start:
                prompt_text = "Press Enter to start or Esc to quit."
            else:
                prompt_text = "Press Enter to play again or Esc to quit."

            prompt_surface = small_font.render(prompt_text, True, (200, 220, 255))
            self.screen.blit(prompt_surface, (WIDTH / 2 - prompt_surface.get_width() / 2, HEIGHT - 80))

            top_offset = 220
            highlight_consumed = False
            for index in range(MAX_HIGH_SCORES):
                if index < len(self.high_scores.scores):
                    entry = self.high_scores.scores[index]
                    initials_text = entry["initials"]
                    score_value: int | None = entry["score"]
                    score_display = str(entry["score"])
                else:
                    initials_text = "---"
                    score_value = None
                    score_display = "---"

                line_y = top_offset + index * 50
                label_surface = entry_font.render(f"{index + 1}.", True, (180, 200, 255))
                self.screen.blit(label_surface, (WIDTH / 2 - 220, line_y))

                highlight = False
                if highlight_pair and not highlight_consumed and score_value is not None:
                    if initials_text == highlight_pair[0] and score_value == highlight_pair[1]:
                        highlight = True
                        highlight_consumed = True

                initials_color = (255, 255, 255) if not highlight else (255, 250, 180)
                score_color = (200, 220, 255) if not highlight else (255, 240, 200)
                initials_surface = entry_font.render(initials_text, True, initials_color)
                score_surface = entry_font.render(score_display, True, score_color)
                self.screen.blit(initials_surface, (WIDTH / 2 - initials_surface.get_width() / 2, line_y))
                self.screen.blit(score_surface, (WIDTH / 2 + 140 - score_surface.get_width(), line_y))

            if entering_initials and new_score is not None:
                initials_display_y = HEIGHT - 160
                initials_label = entry_font.render("Initials:", True, (255, 255, 255))
                self.screen.blit(initials_label, (WIDTH / 2 - 200, initials_display_y))
                for idx, letter in enumerate(initials):
                    letter_surface = entry_font.render(letter, True, (255, 255, 255))
                    letter_x = WIDTH / 2 - 60 + idx * 60
                    letter_rect = letter_surface.get_rect(center=(letter_x, initials_display_y + 10))
                    if idx == selected_index:
                        highlight_rect = pygame.Rect(0, 0, 50, 60)
                        highlight_rect.center = letter_rect.center
                        pygame.draw.rect(self.screen, (255, 240, 120), highlight_rect, 3, border_radius=10)
                    self.screen.blit(letter_surface, letter_rect.topleft)

            pygame.display.flip()


def main() -> None:
    game = Game()
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
