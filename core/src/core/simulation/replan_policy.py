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
    remaining_path_cells: frozenset[Position]
    obstacle_cells_changed: frozenset[Position]
    cost_cells_changed: frozenset[Position]
    world_reinitialized: bool

    @classmethod
    def from_state(cls, state: SimulationState) -> PolicyContext:
        remaining_cells = state.robot.remaining_path_cells()
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
            remaining_path_cells=frozenset(remaining_cells),
            obstacle_cells_changed=frozenset(state.world_delta.obstacle_cells_changed),
            cost_cells_changed=frozenset(state.world_delta.cost_cells_changed),
            world_reinitialized=state.world_delta.world_reinitialized,
        )


class ReplanPolicy(Protocol):
    def decide(self, ctx: PolicyContext) -> PolicyDecision: ...

    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]: ...


@dataclass(frozen=True, slots=True)
class PeriodicReplanPolicy:
    interval_ticks: int = 1

    def __post_init__(self) -> None:
        if self.interval_ticks <= 0:
            raise ValueError("interval_ticks must be > 0.")

    def decide(self, ctx: PolicyContext) -> PolicyDecision:
        if not ctx.has_goal:
            return PolicyDecision(replan=False)
        if ctx.tick % self.interval_ticks == 0:
            return PolicyDecision(replan=True, reason="periodic")
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
        if not ctx.has_goal:
            return PolicyDecision(replan=False)

        if "goal_changed" in ctx.replan_events or "robot_repositioned" in ctx.replan_events:
            return PolicyDecision(replan=True, reason="event")

        changed_cells = set(ctx.obstacle_cells_changed)
        changed_cells.update(ctx.cost_cells_changed)

        if ctx.world_reinitialized:
            return PolicyDecision(replan=True, reason="path_affected")

        if changed_cells and bool(ctx.remaining_path_cells.intersection(changed_cells)):
            return PolicyDecision(replan=True, reason="path_affected")

        if self.cost_delta_threshold > 0:
            affected_cost = 0.0
            for pos in ctx.cost_cells_changed:
                if pos in ctx.remaining_path_cells:
                    affected_cost += ctx.world.get_extra_cost(pos)
            if affected_cost >= self.cost_delta_threshold:
                return PolicyDecision(replan=True, reason="path_affected")

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
        interval_ticks = int(params.get("interval_ticks", 1))
        return PeriodicReplanPolicy(interval_ticks=interval_ticks)
    if normalized in {"path_affected", "pathaffected"}:
        threshold = float(params.get("cost_delta_threshold", 0.0))
        return PathAffectedReplanPolicy(cost_delta_threshold=threshold)

    raise ValueError(f"Unknown policy_name: {policy_name}")
