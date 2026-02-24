from __future__ import annotations

from typing import Protocol

from core.domain import Position, World
from core.planning.astar import PlanResult


class Planner(Protocol):
    def __call__(self, world: World, start: Position, goal: Position) -> PlanResult: ...
