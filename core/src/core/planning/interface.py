from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from core.domain.position import Position
from core.domain.world import World

if TYPE_CHECKING:
    from core.planning.astar import PlanResult


class NoPath(RuntimeError):
    """Raised when a planner cannot produce any path from start to goal."""


class Planner(Protocol):
    """Pure planner interface.

    Implementations must be stateless from the caller perspective: they may only
    use ``world``, ``start`` and ``goal`` as inputs and return a ``PlanResult`` or
    raise ``NoPath``. They must not mutate engine/domain state as a side effect.
    """

    def __call__(self, world: World, start: Position, goal: Position) -> PlanResult: ...
