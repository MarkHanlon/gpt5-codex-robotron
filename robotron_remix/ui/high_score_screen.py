"""High score screen loop and rendering."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pygame

from ..config import FPS, HEIGHT, WIDTH
from ..high_scores import HighScoreEntry, HighScoreManager, format_entries
from ..particles import CelebrationBackground


@dataclass
class HighScoreOutcome:
    continue_playing: bool
    exit_requested: bool


class HighScoreScreen:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, manager: HighScoreManager) -> None:
        self.screen = screen
        self.clock = clock
        self.high_scores = manager
        self.title_font = pygame.font.SysFont("Consolas", 64)
        self.entry_font = pygame.font.SysFont("Consolas", 36)
        self.small_font = pygame.font.SysFont("Consolas", 24)

    def show(self, start: bool, new_score: int | None = None) -> HighScoreOutcome:
        background = CelebrationBackground()
        entering_initials = new_score is not None and self.high_scores.qualifies(new_score)
        initials: List[str] = ["A", "A", "A"]
        selected_index = 0
        highlight_entry: HighScoreEntry | None = None

        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return HighScoreOutcome(False, True)
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
                        elif event.key == pygame.K_RETURN and new_score is not None:
                            highlight_entry = self.high_scores.add_score("".join(initials), int(new_score))
                            entering_initials = False
                        elif event.key == pygame.K_ESCAPE:
                            return HighScoreOutcome(False, False)
                    else:
                        if event.key == pygame.K_RETURN:
                            return HighScoreOutcome(True, False)
                        if event.key == pygame.K_ESCAPE:
                            return HighScoreOutcome(False, False)

            background.update(dt)
            self._draw_screen(background, start, new_score, entering_initials, initials, selected_index, highlight_entry)
            pygame.display.flip()

    def _draw_screen(
        self,
        background: CelebrationBackground,
        start: bool,
        new_score: int | None,
        entering_initials: bool,
        initials: List[str],
        selected_index: int,
        highlight_entry: HighScoreEntry | None,
    ) -> None:
        self.screen.fill((10, 8, 40))
        background.draw(self.screen)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 30, 180))
        self.screen.blit(overlay, (0, 0))

        title_text = self.title_font.render("HIGH SCORES", True, (255, 255, 255))
        self.screen.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, 60))

        if new_score is not None:
            score_label = self.entry_font.render(f"Your Score: {new_score}", True, (255, 230, 130))
            self.screen.blit(score_label, (WIDTH / 2 - score_label.get_width() / 2, 140))

        if entering_initials:
            prompt_text = "New high score! Use arrow keys to set your initials."
        elif start:
            prompt_text = "Press Enter to start or Esc to quit."
        else:
            prompt_text = "Press Enter to play again or Esc to quit."

        prompt_surface = self.small_font.render(prompt_text, True, (200, 220, 255))
        self.screen.blit(prompt_surface, (WIDTH / 2 - prompt_surface.get_width() / 2, HEIGHT - 80))

        highlight_consumed = False
        top_offset = 220
        for index, (initials_text, score_value) in enumerate(format_entries(self.high_scores.scores)):
            line_y = top_offset + index * 50
            label_surface = self.entry_font.render(f"{index + 1}.", True, (180, 200, 255))
            self.screen.blit(label_surface, (WIDTH / 2 - 220, line_y))

            highlight = False
            if highlight_entry and not highlight_consumed and score_value is not None:
                if initials_text == highlight_entry.initials and score_value == highlight_entry.score:
                    highlight = True
                    highlight_consumed = True

            initials_color = (255, 255, 255) if not highlight else (255, 250, 180)
            score_color = (200, 220, 255) if not highlight else (255, 240, 200)
            initials_surface = self.entry_font.render(initials_text, True, initials_color)
            score_display = "---" if score_value is None else str(score_value)
            score_surface = self.entry_font.render(score_display, True, score_color)
            self.screen.blit(initials_surface, (WIDTH / 2 - initials_surface.get_width() / 2, line_y))
            self.screen.blit(score_surface, (WIDTH / 2 + 140 - score_surface.get_width(), line_y))

        if entering_initials and new_score is not None:
            initials_display_y = HEIGHT - 160
            initials_label = self.entry_font.render("Initials:", True, (255, 255, 255))
            label_rect = initials_label.get_rect()
            label_rect.midright = (WIDTH / 2 - 120, initials_display_y + 15)
            self.screen.blit(initials_label, label_rect.topleft)

            letter_spacing = 70
            first_letter_x = label_rect.right + 20
            for idx, letter in enumerate(initials):
                letter_surface = self.entry_font.render(letter, True, (255, 255, 255))
                letter_rect = letter_surface.get_rect()
                letter_rect.center = (
                    first_letter_x + idx * letter_spacing,
                    initials_display_y + 15,
                )
                if idx == selected_index:
                    highlight_rect = pygame.Rect(0, 0, 54, 66)
                    highlight_rect.center = letter_rect.center
                    pygame.draw.rect(
                        self.screen,
                        (255, 240, 120),
                        highlight_rect,
                        3,
                        border_radius=12,
                    )
                self.screen.blit(letter_surface, letter_rect)


__all__ = ["HighScoreOutcome", "HighScoreScreen"]
