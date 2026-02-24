from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from core.domain import Position, World
from core.planning.astar import PlanResult


class Planner(Protocol):
    """Pure planner interface.

    Implementations must be stateless from the caller perspective: they may only
    use ``world``, ``start`` and ``goal`` as inputs and return a ``PlanResult`` or
    raise ``NoPath``. They must not mutate engine/domain state as a side effect.
    """

    def __call__(self, world: World, start: Position, goal: Position) -> PlanResult: ...
