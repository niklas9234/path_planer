from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import sqrt
from typing import Literal

Connectivity = Literal[8]


@dataclass(frozen=True, slots=True)
class Position:
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class WorldSnapshot:

    width: int
    height: int
    cell_size_m: float
    blocked_cells: list[Position]
    extra_cost_cells: list[tuple[Position, float]]  # only where extra_cost > 0

    def __init__(
        self,
        width: int,
        height: int,
        *,
        cell_size_m: float = 1.0,
        connectivity: Connectivity = 8,
        base_cost: float = 1.0,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError(f"World dimensions must be > 0, got {width=} {height=}.")
        if cell_size_m <= 0:
            raise ValueError(f"cell_size_m must be > 0, got {cell_size_m}.")
        if base_cost <= 0:
            raise ValueError(f"base_cost must be > 0, got {base_cost}.")
        if connectivity not in (4, 8):
            raise ValueError(f"connectivity must be 4 or 8, got {connectivity}.")

        self.width = width
        self.height = height
        self.cell_size_m = float(cell_size_m)
        self.connectivity: Connectivity = connectivity
        self.base_cost = float(base_cost)

        # Layers
        self.blocked: list[list[bool]] = [
            [False for _ in range(self.width)] for _ in range(self.height)
        ]
        self.extra_cost: list[list[float]] = [
            [0.0 for _ in range(self.width)] for _ in range(self.height)
        ]

        self._diag_factor = sqrt(2.0)

    # ----------------------------
    # Bounds / validation
    # ----------------------------

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def assert_in_bounds(self, x: int, y: int) -> None:
        if not self.in_bounds(x, y):
            raise ValueError(f"Out of bounds position: ({x}, {y}).")

    def _assert_nonnegative(self, value: float, name: str) -> None:
        if value < 0:
            raise ValueError(f"{name} must be >= 0, got {value}.")

    # ----------------------------
    # Queries
    # ----------------------------

    def is_blocked(self, x: int, y: int) -> bool:
        self.assert_in_bounds(x, y)
        return self.blocked[y][x]

    def get_extra_cost(self, x: int, y: int) -> float:
        self.assert_in_bounds(x, y)
        return self.extra_cost[y][x]

    def get_cell_cost(self, x: int, y: int) -> float:
        self.assert_in_bounds(x, y)
        if self.blocked[y][x]:
            raise ValueError(f"Cell ({x}, {y}) is blocked.")
        return self.base_cost + self.extra_cost[y][x]

    def neighbors(self, x: int, y: int) -> list[tuple[Position, float]]:
        self.assert_in_bounds(x, y)

        deltas: list[tuple[int, int, float]]
        deltas = [
            ( 1, 0, 1.0),
            (-1, 0, 1.0),
            ( 0, 1, 1.0),
            ( 0,-1, 1.0),

            ( 1, 1, self._diag_factor),
            ( 1,-1, self._diag_factor),
            (-1, 1, self._diag_factor),
            (-1,-1, self._diag_factor),
        ]

        result: list[tuple[Position, float]] = []
        for dx, dy, factor in deltas:
            nx, ny = x + dx, y + dy
            if not self.in_bounds(nx, ny):
                continue
            if self.blocked[ny][nx]:
                continue

            # Cost is to ENTER the neighbor cell
            step_cost = factor * (self.base_cost + self.extra_cost[ny][nx])
            result.append((Position(nx, ny), step_cost))

        return result

    # -----------
    # Mutations
    # -----------

    def set_obstacle(self, x: int, y: int, blocked: bool) -> None:
        self.assert_in_bounds(x, y)
        self.blocked[y][x] = bool(blocked)

    def add_obstacle(self, x: int, y: int) -> None:
        self.set_obstacle(x, y, True)

    def remove_obstacle(self, x: int, y: int) -> None:
        self.set_obstacle(x, y, False)

    def set_extra_cost(self, x: int, y: int, value: float) -> None:
        self.assert_in_bounds(x, y)
        self._assert_nonnegative(value, "extra_cost")
        self.extra_cost[y][x] = float(value)

    def add_cost(self, x: int, y: int, delta: float) -> None:
        self.assert_in_bounds(x, y)
        self._assert_nonnegative(delta, "delta")
        self.extra_cost[y][x] += float(delta)

    def clear_extra_cost(self, x: int, y: int) -> None:
        self.set_extra_cost(x, y, 0.0)

    def apply_cost_zone(self, cells: Iterable[Position], delta: float) -> None:
        self._assert_nonnegative(delta, "delta")
        for pos in cells:
            self.add_cost(pos.x, pos.y, delta)

    def clear_cost_zone(self, cells: Iterable[Position]) -> None:
        for pos in cells:
            self.clear_extra_cost(pos.x, pos.y)
