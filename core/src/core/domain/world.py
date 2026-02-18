"""Grid-based world model for path-planning simulation.

This module defines the core `World` domain object: a 2D grid with
hard obstacles (blocked cells) and optional additional traversal costs
(soft constraints / slow zones).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Literal, Optional


Connectivity = Literal[4, 8]


@dataclass(frozen=True, slots=True)
class Position:
    """Discrete grid position in (x, y) coordinates."""

    x: int
    y: int


@dataclass(frozen=True, slots=True)
class WorldSnapshot:
    """Serializable snapshot of the world state.

    Note: This snapshot is intentionally "sparse" for costs to keep payloads small.
    """

    width: int
    height: int
    cell_size_m: float
    blocked_cells: list[Position]
    extra_cost_cells: list[tuple[Position, float]]  # only where extra_cost > 0


class World:
    """Grid world with obstacles and additional traversal costs.

    The world is modeled as a height x width grid with:
    - `blocked[y][x]`: impassable cells
    - `extra_cost[y][x]`: additional cost added to `base_cost` (>= 0)

    Movement supports 4- or 8-connectivity. Diagonal steps are weighted by sqrt(2).
    """

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
        """Return True if (x, y) is within the grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def assert_in_bounds(self, x: int, y: int) -> None:
        """Raise ValueError if (x, y) is outside the grid bounds."""
        if not self.in_bounds(x, y):
            raise ValueError(f"Out of bounds position: ({x}, {y}).")

    def _assert_nonnegative(self, value: float, name: str) -> None:
        if value < 0:
            raise ValueError(f"{name} must be >= 0, got {value}.")

    # ----------------------------
    # Queries
    # ----------------------------

    def is_blocked(self, x: int, y: int) -> bool:
        """Return True if the cell is blocked (impassable)."""
        self.assert_in_bounds(x, y)
        return self.blocked[y][x]

    def get_extra_cost(self, x: int, y: int) -> float:
        """Return the additional traversal cost for this cell (>= 0)."""
        self.assert_in_bounds(x, y)
        return self.extra_cost[y][x]

    def get_cell_cost(self, x: int, y: int) -> float:
        """Return the base traversal cost of entering the cell (no diagonal factor)."""
        self.assert_in_bounds(x, y)
        if self.blocked[y][x]:
            raise ValueError(f"Cell ({x}, {y}) is blocked.")
        return self.base_cost + self.extra_cost[y][x]

    def neighbors(self, x: int, y: int) -> list[tuple[Position, float]]:
        """Return reachable neighbors and the step cost to enter each neighbor.

        The returned cost already includes the diagonal factor (sqrt(2)) when applicable.
        Blocked cells are not returned.
        """
        self.assert_in_bounds(x, y)

        deltas: list[tuple[int, int, float]]
        deltas = [
            (1, 0, 1.0),
            (-1, 0, 1.0),
            (0, 1, 1.0),
            (0, -1, 1.0),
        ]
        if self.connectivity == 8:
            deltas.extend(
                [
                    (1, 1, self._diag_factor),
                    (1, -1, self._diag_factor),
                    (-1, 1, self._diag_factor),
                    (-1, -1, self._diag_factor),
                ]
            )

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

    # ----------------------------
    # Mutations (events will call these)
    # ----------------------------

    def set_obstacle(self, x: int, y: int, blocked: bool) -> None:
        """Set or clear a hard obstacle at (x, y)."""
        self.assert_in_bounds(x, y)
        self.blocked[y][x] = bool(blocked)

    def add_obstacle(self, x: int, y: int) -> None:
        """Mark (x, y) as blocked."""
        self.set_obstacle(x, y, True)

    def remove_obstacle(self, x: int, y: int) -> None:
        """Mark (x, y) as free."""
        self.set_obstacle(x, y, False)

    def set_extra_cost(self, x: int, y: int, value: float) -> None:
        """Set the additional traversal cost at (x, y) to an absolute value (>= 0)."""
        self.assert_in_bounds(x, y)
        self._assert_nonnegative(value, "extra_cost")
        self.extra_cost[y][x] = float(value)

    def add_cost(self, x: int, y: int, delta: float) -> None:
        """Add a non-negative delta to the additional traversal cost."""
        self.assert_in_bounds(x, y)
        self._assert_nonnegative(delta, "delta")
        self.extra_cost[y][x] += float(delta)

    def clear_extra_cost(self, x: int, y: int) -> None:
        """Reset additional traversal cost at (x, y) to 0."""
        self.set_extra_cost(x, y, 0.0)

    def apply_cost_zone(self, cells: Iterable[Position], delta: float) -> None:
        """Apply a non-negative cost delta to multiple cells."""
        self._assert_nonnegative(delta, "delta")
        for pos in cells:
            self.add_cost(pos.x, pos.y, delta)

    def clear_cost_zone(self, cells: Iterable[Position]) -> None:
        """Clear extra cost for multiple cells."""
        for pos in cells:
            self.clear_extra_cost(pos.x, pos.y)

    # ----------------------------
    # Snapshot
    # ----------------------------

    def to_snapshot(self) -> WorldSnapshot:
        """Create a serializable snapshot of the world.

        - blocked_cells: list of all blocked positions
        - extra_cost_cells: list of (position, extra_cost) where extra_cost > 0
        """
        blocked_cells: list[Position] = []
        extra_cost_cells: list[tuple[Position, float]] = []

        for y in range(self.height):
            for x in range(self.width):
                if self.blocked[y][x]:
                    blocked_cells.append(Position(x, y))
                cost = self.extra_cost[y][x]
                if cost > 0:
                    extra_cost_cells.append((Position(x, y), cost))

        return WorldSnapshot(
            width=self.width,
            height=self.height,
            cell_size_m=self.cell_size_m,
            blocked_cells=blocked_cells,
            extra_cost_cells=extra_cost_cells,
        )

