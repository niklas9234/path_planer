from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from core.domain import Position, World


@dataclass(frozen=True, slots=True)
class ReplanDecision:
    replan: bool
    reason: str


@dataclass(frozen=True, slots=True)
class PolicyContext:
    tick: int
    has_goal: bool
    dirty_replan: bool
    robot_position: Position
    goal_position: Position | None
    path: tuple[Position, ...] = field(default_factory=tuple)
    path_index: int = 0
    world: World | None = None
    replan_events: frozenset[str] = field(default_factory=frozenset)
    obstacle_cells_changed: frozenset[Position] = field(default_factory=frozenset)
    cost_cells_changed: frozenset[Position] = field(default_factory=frozenset)
    world_reinitialized: bool = False

    def remaining_path(self) -> tuple[Position, ...]:
        if self.path_index >= len(self.path):
            return ()
        return self.path[self.path_index :]

    def remaining_path_cells(self) -> frozenset[Position]:
        return frozenset(self.remaining_path())

    def is_blocked(self, position: Position) -> bool:
        if self.world is None:
            raise ValueError("PolicyContext.world is required for is_blocked checks.")
        return self.world.is_blocked(position)

    def get_extra_cost(self, position: Position) -> float:
        if self.world is None:
            raise ValueError("PolicyContext.world is required for cost checks.")
        return self.world.get_extra_cost(position)


class ReplanPolicy(Protocol):
    def decide(self, context: PolicyContext) -> ReplanDecision: ...


@dataclass(frozen=True, slots=True)
class EventBasedReplanPolicy:
    def decide(self, context: PolicyContext) -> ReplanDecision:
        if context.has_goal and context.dirty_replan:
            return ReplanDecision(replan=True, reason="event")
        return ReplanDecision(replan=False, reason="")


@dataclass(slots=True)
class StaticOnceReplanPolicy:
    _did_initial_replan: bool = False

    def decide(self, context: PolicyContext) -> ReplanDecision:
        if not context.has_goal or self._did_initial_replan:
            return ReplanDecision(replan=False, reason="")

        self._did_initial_replan = True
        return ReplanDecision(replan=True, reason="initial_static")


@dataclass(frozen=True, slots=True)
class PeriodicReplanPolicy:
    interval_ticks: int = 1

    def __post_init__(self) -> None:
        if self.interval_ticks <= 0:
            raise ValueError("interval_ticks must be > 0.")

    def decide(self, context: PolicyContext) -> ReplanDecision:
        if context.has_goal and context.tick % self.interval_ticks == 0:
            return ReplanDecision(replan=True, reason="periodic")
        return ReplanDecision(replan=False, reason="")


@dataclass(frozen=True, slots=True)
class PathAffectedReplanPolicy:
    cost_delta_threshold: float = 0.0

    def decide(self, context: PolicyContext) -> ReplanDecision:
        if not context.has_goal:
            return ReplanDecision(replan=False, reason="")

        if "goal_changed" in context.replan_events or "robot_repositioned" in context.replan_events:
            return ReplanDecision(replan=True, reason="event")

        if context.world_reinitialized:
            return ReplanDecision(replan=True, reason="path_affected")

        changed_cells = set(context.obstacle_cells_changed)
        changed_cells.update(context.cost_cells_changed)
        remaining_cells = context.remaining_path_cells()

        if changed_cells and remaining_cells.intersection(changed_cells):
            return ReplanDecision(replan=True, reason="path_affected")

        if self.cost_delta_threshold > 0 and context.world is not None:
            affected_cost = 0.0
            for position in context.cost_cells_changed:
                if position in remaining_cells:
                    affected_cost += context.get_extra_cost(position)
            if affected_cost >= self.cost_delta_threshold:
                return ReplanDecision(replan=True, reason="path_affected")

        return ReplanDecision(replan=False, reason="")
