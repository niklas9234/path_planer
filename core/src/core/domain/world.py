from __future__ import annotations

from collections.abc import Iterable
from math import sqrt

from core.domain.Position import Position


class World:
    def __init__(
        self,
        width: int,
        height: int,
        *,
        cell_size_m: float = 1.0,
        base_cost: float = 1.0,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError(f"World dimensions must be > 0, got {width=} {height=}.")
        if cell_size_m <= 0:
            raise ValueError(f"cell_size_m must be > 0, got {cell_size_m}.")
        if base_cost <= 0:
            raise ValueError(f"base_cost must be > 0, got {base_cost}.")

        self.width = width
        self.height = height
        self.cell_size_m = float(cell_size_m)
        self.connectivity = 8
        self.base_cost = float(base_cost)

        self.blocked: list[list[bool]] = [
            [False for _ in range(self.width)] for _ in range(self.height)
        ]
        self.extra_cost: list[list[float]] = [
            [0.0 for _ in range(self.width)] for _ in range(self.height)
        ]

        self._diag_factor = sqrt(2.0)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def assert_in_bounds(self, x: int, y: int) -> None:
        if not self.in_bounds(x, y):
            raise ValueError(f"Out of bounds position: ({x}, {y}).")

    def _assert_nonnegative(self, value: float, name: str) -> None:
        if value < 0:
            raise ValueError(f"{name} must be >= 0, got {value}.")

    def is_blocked(self, pos: Position) -> bool:
        self.assert_in_bounds(pos.x, pos.y)
        return self.blocked[pos.y][pos.x]

    def get_extra_cost(self, pos: Position) -> float:
        self.assert_in_bounds(pos.x, pos.y)
        return self.extra_cost[pos.y][pos.x]

    def get_cell_cost(self, pos: Position) -> float:
        self.assert_in_bounds(pos.x, pos.y)
        if self.blocked[pos.y][pos.x]:
            raise ValueError(f"Cell ({pos.x}, {pos.y}) is blocked.")
        return self.base_cost + self.extra_cost[pos.y][pos.x]

    def neighbors(self, pos: Position) -> list[tuple[Position, float]]:
        self.assert_in_bounds(pos.x, pos.y)

        deltas: list[tuple[int, int, float]] = [
            (1, 0, 1.0),
            (-1, 0, 1.0),
            (0, 1, 1.0),
            (0, -1, 1.0),
            (1, 1, self._diag_factor),
            (1, -1, self._diag_factor),
            (-1, 1, self._diag_factor),
            (-1, -1, self._diag_factor),
        ]

        result: list[tuple[Position, float]] = []
        for dx, dy, factor in deltas:
            nx, ny = pos.x + dx, pos.y + dy
            if not self.in_bounds(nx, ny):
                continue
            if self.blocked[ny][nx]:
                continue

            step_cost = factor * (self.base_cost + self.extra_cost[ny][nx])
            result.append((Position(nx, ny), step_cost))

        return result

    def set_obstacle(self, pos: Position, blocked: bool) -> None:
        self.assert_in_bounds(pos.x, pos.y)
        self.blocked[pos.y][pos.x] = bool(blocked)

    def add_obstacle(self, pos: Position) -> None:
        self.set_obstacle(pos, True)

    def remove_obstacle(self, pos: Position) -> None:
        self.set_obstacle(pos, False)

    def set_extra_cost(self, pos: Position, value: float) -> None:
        self.assert_in_bounds(pos.x, pos.y)
        self._assert_nonnegative(value, "extra_cost")
        self.extra_cost[pos.y][pos.x] = float(value)

    def add_cost(self, pos: Position, delta: float) -> None:
        self.assert_in_bounds(pos.x, pos.y)
        self._assert_nonnegative(delta, "delta")
        self.extra_cost[pos.y][pos.x] += float(delta)

    def clear_extra_cost(self, pos: Position) -> None:
        self.set_extra_cost(pos, 0.0)

    def apply_cost_zone(self, cells: Iterable[Position], delta: float) -> None:
        self._assert_nonnegative(delta, "delta")
        for pos in cells:
            self.add_cost(pos, delta)

    def clear_cost_zone(self, cells: Iterable[Position]) -> None:
        for pos in cells:
            self.clear_extra_cost(pos)
