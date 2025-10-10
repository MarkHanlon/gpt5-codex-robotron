"""Executable entry point for Robotron Remix."""
from __future__ import annotations

import pygame

from .game import Game


def main() -> None:
    game = Game()
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
