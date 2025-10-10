"""High score persistence and formatting utilities."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .config import HIGH_SCORE_PATH, MAX_HIGH_SCORES


@dataclass
class HighScoreEntry:
    initials: str
    score: int


class HighScoreManager:
    def __init__(self, path: Path = HIGH_SCORE_PATH) -> None:
        self.path = path
        self.scores: list[HighScoreEntry] = []
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
            valid_scores: list[HighScoreEntry] = []
            for item in data:
                if (
                    isinstance(item, dict)
                    and isinstance(item.get("initials"), str)
                    and isinstance(item.get("score"), int)
                ):
                    initials = item["initials"][:3].upper()
                    score = item["score"]
                    valid_scores.append(HighScoreEntry(initials, score))
            self.scores = sorted(valid_scores, key=lambda entry: entry.score, reverse=True)[
                :MAX_HIGH_SCORES
            ]
        else:
            self.scores = []

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", encoding="utf-8") as fh:
                json.dump(
                    [
                        {"initials": entry.initials, "score": entry.score}
                        for entry in self.scores
                    ],
                    fh,
                    indent=2,
                )
        except OSError:
            pass

    def qualifies(self, score: int) -> bool:
        if score <= 0:
            return False
        if len(self.scores) < MAX_HIGH_SCORES:
            return True
        return score > self.scores[-1].score

    def add_score(self, initials: str, score: int) -> HighScoreEntry:
        initials = initials[:3].upper()
        entry = HighScoreEntry(initials, score)
        self.scores.append(entry)
        self.scores.sort(key=lambda item: item.score, reverse=True)
        del self.scores[MAX_HIGH_SCORES:]
        self.save()
        return entry


def format_entries(entries: Sequence[HighScoreEntry], limit: int = MAX_HIGH_SCORES) -> list[tuple[str, int | None]]:
    """Return a list of `(initials, score_value)` pairs padded to `limit`."""

    formatted: list[tuple[str, int | None]] = []
    for entry in entries[:limit]:
        formatted.append((entry.initials, entry.score))
    while len(formatted) < limit:
        formatted.append(("---", None))
    return formatted


def iter_scores(manager: HighScoreManager) -> Iterable[HighScoreEntry]:
    """Convenience wrapper for iterating over the stored high scores."""

    return iter(manager.scores)


__all__ = [
    "HighScoreEntry",
    "HighScoreManager",
    "format_entries",
    "iter_scores",
]
