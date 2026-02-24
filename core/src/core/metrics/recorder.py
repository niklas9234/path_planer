from __future__ import annotations

from dataclasses import asdict, dataclass

from core.domain.position import Position
from core.domain.world import World


@dataclass(frozen=True, slots=True)
class TickMetric:
    tick: int
    position: tuple[int, int]
    moved: bool
    replanned: bool
    at_goal: bool
    reason: str
    cumulative_cost: float


class RunMetricsRecorder:
    def __init__(self) -> None:
        self._ticks: list[TickMetric] = []
        self._cumulative_cost = 0.0

    @staticmethod
    def _step_cost(world: World, start: Position, end: Position) -> float:
        for neighbor, cost in world.neighbors(start):
            if neighbor == end:
                return cost
        return 0.0

    def record_tick(
        self,
        *,
        tick: int,
        world: World,
        previous_position: Position,
        current_position: Position,
        moved: bool,
        replanned: bool,
        at_goal: bool,
        reason: str,
    ) -> None:
        if moved:
            self._cumulative_cost += self._step_cost(world, previous_position, current_position)

        self._ticks.append(
            TickMetric(
                tick=tick,
                position=(current_position.x, current_position.y),
                moved=moved,
                replanned=replanned,
                at_goal=at_goal,
                reason=reason,
                cumulative_cost=self._cumulative_cost,
            ),
        )

    @property
    def total_cost(self) -> float:
        return self._cumulative_cost

    def ticks_as_dict(self) -> list[dict[str, object]]:
        return [asdict(item) for item in self._ticks]
