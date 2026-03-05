from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from core.config.defaults import (
    CARDINAL_STEP_FACTOR,
    DEFAULT_BASE_COST,
    DEFAULT_CELL_SIZE_M,
    DEFAULT_CONNECTIVITY,
    DEFAULT_EXTRA_COST,
    DIAGONAL_STEP_FACTOR,
)
from core.domain.position import Position


class ZoneType(str, Enum):
    OBSTACLE = "obstacle"
    SLOW = "slow"


@dataclass(frozen=True, slots=True)
class ZoneChangeSet:
    obstacle_cells_changed: set[Position]
    cost_cells_changed: set[Position]


@dataclass(frozen=True, slots=True)
class ActiveZone:
    zone_id: int
    zone_type: ZoneType
    cells: tuple[Position, ...]
    extra_cost: float
    expires_at_tick: int | None


class World:
    def __init__(
        self,
        width: int,
        height: int,
        *,
        cell_size_m: float = DEFAULT_CELL_SIZE_M,
        base_cost: float = DEFAULT_BASE_COST,
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
        self.connectivity = DEFAULT_CONNECTIVITY
        self.base_cost = float(base_cost)

        self.blocked: list[list[bool]] = [
            [False for _ in range(self.width)] for _ in range(self.height)
        ]
        self._zone_blocked_refcount: list[list[int]] = [
            [0 for _ in range(self.width)] for _ in range(self.height)
        ]
        self.extra_cost: list[list[float]] = [
            [DEFAULT_EXTRA_COST for _ in range(self.width)] for _ in range(self.height)
        ]
        self._zone_extra_cost: list[list[float]] = [
            [DEFAULT_EXTRA_COST for _ in range(self.width)] for _ in range(self.height)
        ]
        self._zones: dict[int, ActiveZone] = {}
        self._next_zone_id = 1

        self._diag_factor = DIAGONAL_STEP_FACTOR

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
        return (
            self.blocked[pos.y][pos.x] or self._zone_blocked_refcount[pos.y][pos.x] > 0
        )

    def get_extra_cost(self, pos: Position) -> float:
        self.assert_in_bounds(pos.x, pos.y)
        return self.extra_cost[pos.y][pos.x] + self._zone_extra_cost[pos.y][pos.x]

    def get_cell_cost(self, pos: Position) -> float:
        self.assert_in_bounds(pos.x, pos.y)
        if self.blocked[pos.y][pos.x]:
            raise ValueError(f"Cell ({pos.x}, {pos.y}) is blocked.")
        return self.base_cost + self.get_extra_cost(pos)

    def neighbors(self, pos: Position) -> list[tuple[Position, float]]:
        self.assert_in_bounds(pos.x, pos.y)

        deltas: list[tuple[int, int, float]] = [
            (1, 0, CARDINAL_STEP_FACTOR),
            (-1, 0, CARDINAL_STEP_FACTOR),
            (0, 1, CARDINAL_STEP_FACTOR),
            (0, -1, CARDINAL_STEP_FACTOR),
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
            if self.blocked[ny][nx] or self._zone_blocked_refcount[ny][nx] > 0:
                continue

            step_cost = factor * (
                self.base_cost + self.extra_cost[ny][nx] + self._zone_extra_cost[ny][nx]
            )
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
        self.set_extra_cost(pos, DEFAULT_EXTRA_COST)

    def apply_cost_zone(self, cells: Iterable[Position], delta: float) -> None:
        self._assert_nonnegative(delta, "delta")
        for pos in cells:
            self.add_cost(pos, delta)

    def clear_cost_zone(self, cells: Iterable[Position]) -> None:
        for pos in cells:
            self.clear_extra_cost(pos)

    def add_zone(
        self,
        *,
        zone_type: ZoneType,
        cells: Iterable[Position],
        current_tick: int,
        duration_ticks: int | None = None,
        extra_cost: float = DEFAULT_EXTRA_COST,
    ) -> int:
        if duration_ticks is not None and duration_ticks <= 0:
            raise ValueError(f"duration_ticks must be > 0, got {duration_ticks}.")
        if current_tick < 0:
            raise ValueError(f"current_tick must be >= 0, got {current_tick}.")

        cells_tuple = tuple(cells)
        for pos in cells_tuple:
            self.assert_in_bounds(pos.x, pos.y)

        if zone_type is ZoneType.SLOW:
            self._assert_nonnegative(extra_cost, "extra_cost")
        elif extra_cost != DEFAULT_EXTRA_COST:
            raise ValueError("extra_cost can only be used for slow zones.")

        expires_at_tick = (
            None if duration_ticks is None else current_tick + duration_ticks
        )
        zone_id = self._next_zone_id
        self._next_zone_id += 1

        zone = ActiveZone(
            zone_id=zone_id,
            zone_type=zone_type,
            cells=cells_tuple,
            extra_cost=float(extra_cost),
            expires_at_tick=expires_at_tick,
        )
        self._zones[zone_id] = zone
        self._apply_zone(zone, sign=1)
        return zone_id

    def expire_zones(self, current_tick: int) -> ZoneChangeSet:
        if current_tick < 0:
            raise ValueError(f"current_tick must be >= 0, got {current_tick}.")

        obstacle_cells_changed: set[Position] = set()
        cost_cells_changed: set[Position] = set()
        expired_zone_ids = [
            zone_id
            for zone_id, zone in self._zones.items()
            if zone.expires_at_tick is not None and zone.expires_at_tick <= current_tick
        ]

        for zone_id in expired_zone_ids:
            zone = self._zones.pop(zone_id)
            self._apply_zone(zone, sign=-1)
            if zone.zone_type is ZoneType.OBSTACLE:
                obstacle_cells_changed.update(zone.cells)
            else:
                cost_cells_changed.update(zone.cells)

        return ZoneChangeSet(
            obstacle_cells_changed=obstacle_cells_changed,
            cost_cells_changed=cost_cells_changed,
        )

    def _apply_zone(self, zone: ActiveZone, *, sign: int) -> None:
        for pos in zone.cells:
            if zone.zone_type is ZoneType.OBSTACLE:
                self._zone_blocked_refcount[pos.y][pos.x] += sign
                if self._zone_blocked_refcount[pos.y][pos.x] < 0:
                    raise RuntimeError("Zone blocked reference count underflow.")
            elif zone.zone_type is ZoneType.SLOW:
                self._zone_extra_cost[pos.y][pos.x] += sign * zone.extra_cost
                if self._zone_extra_cost[pos.y][pos.x] < 0:
                    raise RuntimeError("Zone extra cost underflow.")
