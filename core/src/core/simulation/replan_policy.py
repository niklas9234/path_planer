from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from core.domain import Position, RobotState, World
from core.simulation.state import SimulationState


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    replan: bool
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class PolicyContext:
    tick: int
    has_goal: bool
    goal: Position | None
    dirty_replan: bool
    replan_events: frozenset[str]
    world: World
    robot: RobotState
    path_length: int
    remaining_path_length: int
    remaining_path: tuple[Position, ...]
    remaining_path_cells: frozenset[Position]
    planned_cost_by_cell: dict[Position, float]
    obstacle_cells_changed: frozenset[Position]
    cost_cells_changed: frozenset[Position]
    world_reinitialized: bool

    @classmethod
    def from_state(cls, state: SimulationState) -> PolicyContext:
        remaining_path = tuple(state.robot.path[state.robot.path_index :])
        remaining_cells = set(remaining_path)
        return cls(
            tick=state.tick,
            has_goal=state.robot.has_goal(),
            goal=state.robot.goal,
            dirty_replan=state.dirty_replan,
            replan_events=frozenset(state.replan_events),
            world=state.world,
            robot=state.robot,
            path_length=len(state.robot.path),
            remaining_path_length=len(remaining_cells),
            remaining_path=remaining_path,
            remaining_path_cells=frozenset(remaining_cells),
            planned_cost_by_cell=dict(state.robot.planned_cost_by_cell),
            obstacle_cells_changed=frozenset(state.world_delta.obstacle_cells_changed),
            cost_cells_changed=frozenset(state.world_delta.cost_cells_changed),
            world_reinitialized=state.world_delta.world_reinitialized,
        )


class ReplanPolicy(Protocol):
    def decide(self, ctx: PolicyContext) -> PolicyDecision: ...

    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]: ...


@dataclass(frozen=True, slots=True)
class PeriodicReplanPolicy:
    interval: int = 1

    @property
    def interval_ticks(self) -> int:
        return self.interval

    def __post_init__(self) -> None:
        if self.interval <= 0:
            raise ValueError("interval must be > 0.")

    def decide(self, ctx: PolicyContext) -> PolicyDecision:
        if not ctx.has_goal:
            return PolicyDecision(replan=False)
        if not ctx.dirty_replan:
            return PolicyDecision(replan=False)
        if ctx.tick % self.interval == 0:
            return PolicyDecision(replan=True, reason="periodic_dirty")
        return PolicyDecision(replan=False)

    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]:
        decision = self.decide(PolicyContext.from_state(state))
        return decision.replan, decision.reason


@dataclass(frozen=True, slots=True)
class EventBasedReplanPolicy:
    def decide(self, ctx: PolicyContext) -> PolicyDecision:
        if not ctx.has_goal:
            return PolicyDecision(replan=False)
        if ctx.dirty_replan:
            return PolicyDecision(replan=True, reason="event")
        return PolicyDecision(replan=False)

    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]:
        decision = self.decide(PolicyContext.from_state(state))
        return decision.replan, decision.reason


@dataclass(frozen=True, slots=True)
class NoReplanPolicy:
    def decide(self, ctx: PolicyContext) -> PolicyDecision:
        del ctx
        return PolicyDecision(replan=False)

    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]:
        del state
        return False, None


@dataclass(slots=True)
class StaticOnceReplanPolicy:
    """Trigger exactly one event-driven replan per policy instance.

    Behavior on goal changes is intentionally *not* reset automatically: once the
    initial replan has happened, later `goal_changed` events do not trigger another
    static replan. To get one initial replan for a new run/goal lifecycle, create
    a new policy instance.
    """

    planned_once: bool = False

    def decide(self, ctx: PolicyContext) -> PolicyDecision:
        if not ctx.has_goal or not ctx.dirty_replan or self.planned_once:
            return PolicyDecision(replan=False)
        self.planned_once = True
        return PolicyDecision(replan=True, reason="initial")

    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]:
        decision = self.decide(PolicyContext.from_state(state))
        return decision.replan, decision.reason


@dataclass(frozen=True, slots=True)
class PathAffectedReplanPolicy:
    cost_delta_threshold: float = 0.0

    def decide(self, ctx: PolicyContext) -> PolicyDecision:
        if not ctx.has_goal or not ctx.dirty_replan:
            return PolicyDecision(replan=False)

        if not ctx.planned_cost_by_cell:
            return PolicyDecision(replan=True, reason="path_signature_missing")

        for pos in ctx.remaining_path:
            if ctx.world.is_blocked(pos):
                return PolicyDecision(replan=True, reason="path_blocked")
            planned_cost = ctx.planned_cost_by_cell.get(pos)
            if planned_cost is None:
                return PolicyDecision(replan=True, reason="path_signature_missing")
            if ctx.world.get_cell_cost(pos) != planned_cost:
                return PolicyDecision(replan=True, reason="path_cost_changed")

        return PolicyDecision(replan=False)

    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]:
        decision = self.decide(PolicyContext.from_state(state))
        return decision.replan, decision.reason


def make_policy(policy_name: str, policy_params: Mapping[str, Any] | None = None) -> ReplanPolicy:
    params = dict(policy_params or {})
    normalized = policy_name.strip().lower()

    if normalized in {"event_based", "dynamic_event"}:
        return EventBasedReplanPolicy()
    if normalized in {"none", "no_replan"}:
        return NoReplanPolicy()
    if normalized in {"static_once", "static"}:
        return StaticOnceReplanPolicy()
    if normalized in {"periodic", "periodic_replan"}:
        interval = int(params.get("interval", params.get("interval_ticks", 1)))
        return PeriodicReplanPolicy(interval=interval)
    if normalized in {"path_affected", "pathaffected"}:
        threshold = float(params.get("cost_delta_threshold", 0.0))
        return PathAffectedReplanPolicy(cost_delta_threshold=threshold)

    raise ValueError(f"Unknown policy_name: {policy_name}")
