from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class Position:
    x: int
    y: int

    def __post_init__(self) -> None:
        if not isinstance(self.x, int) or not isinstance(self.y, int):
            raise TypeError("Position coordinates must be integers.")

    def as_tuple(self) -> tuple[int, int]:
        return self.x, self.y
