from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from core.domain.position import Position


@dataclass(slots=True)
class RobotState:
    position: Position
    goal: Position | None = None
    path: list[Position] | None = None
    path_index: int = 0
    speed_mps: float = 1.0
    planned_cost_by_cell: dict[Position, float] = field(default_factory=dict)
    _remaining_path_set: set[Position] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = []
        if self.path_index < 0:
            raise ValueError("path_index must be >= 0.")
        if self.speed_mps <= 0:
            raise ValueError("speed_mps must be > 0.")
        self._rebuild_remaining_path_set()

    def has_goal(self) -> bool:
        return self.goal is not None

    def clear_plan(self) -> None:
        self.path.clear()
        self.path_index = 0
        self.planned_cost_by_cell.clear()
        self._remaining_path_set.clear()

    def set_goal(self, goal: Position) -> None:
        self.goal = goal
        self.clear_plan()

    def clear_goal(self) -> None:
        self.goal = None
        self.clear_plan()

    def set_position(self, position: Position, *, clear_plan: bool = True) -> None:
        self.position = position
        if clear_plan:
            self.clear_plan()

    def set_path(self, path: Iterable[Position], *, start_index: int = 0) -> None:
        self.path = list(path)
        if start_index < 0:
            raise ValueError("start_index must be >= 0.")
        self.path_index = start_index
        self.planned_cost_by_cell.clear()
        self._rebuild_remaining_path_set()

    def set_planned_cost_signature(self, planned_cost_by_cell: dict[Position, float]) -> None:
        self.planned_cost_by_cell = {
            pos: cost for pos, cost in planned_cost_by_cell.items() if pos in self._remaining_path_set
        }

    def next_waypoint(self) -> Position | None:
        if self.path_index >= len(self.path):
            return None
        return self.path[self.path_index]

    def advance_waypoint(self) -> None:
        if self.path_index < len(self.path):
            visited = self.path[self.path_index]
            self._remaining_path_set.discard(visited)
            self.planned_cost_by_cell.pop(visited, None)
            self.path_index += 1

    def remaining_path_cells(self) -> set[Position]:
        return set(self._remaining_path_set)

    def remaining_path_intersects(self, cells: set[Position]) -> bool:
        return bool(self._remaining_path_set.intersection(cells))

    def at_goal(self) -> bool:
        return self.goal is not None and self.position == self.goal

    def _rebuild_remaining_path_set(self) -> None:
        self._remaining_path_set = set(self.path[self.path_index :])
