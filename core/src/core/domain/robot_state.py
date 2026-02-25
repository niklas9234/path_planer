from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from core.domain.position import Position


@dataclass(slots=True)
class RobotState:
    position: Position
    goal: Position | None = None
    path: list[Position] | None = None
    path_index: int = 0
    speed_mps: float = 1.0

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = []
        if self.path_index < 0:
            raise ValueError("path_index must be >= 0.")
        if self.speed_mps <= 0:
            raise ValueError("speed_mps must be > 0.")

    def has_goal(self) -> bool:
        return self.goal is not None

    def clear_plan(self) -> None:
        self.path.clear()
        self.path_index = 0

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

    def next_waypoint(self) -> Position | None:
        if self.path_index >= len(self.path):
            return None
        return self.path[self.path_index]

    def advance_waypoint(self) -> None:
        if self.path_index < len(self.path):
            self.path_index += 1

    def at_goal(self) -> bool:
        return self.goal is not None and self.position == self.goal
