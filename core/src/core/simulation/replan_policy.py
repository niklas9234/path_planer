from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.simulation.state import SimulationState


class ReplanPolicy(Protocol):
    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]: ...


@dataclass(frozen=True, slots=True)
class PeriodicReplanPolicy:
    interval_ticks: int = 1

    def __post_init__(self) -> None:
        if self.interval_ticks <= 0:
            raise ValueError("interval_ticks must be > 0.")

    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]:
        if not state.robot.has_goal():
            return False, None
        if state.tick % self.interval_ticks == 0:
            return True, "periodic"
        return False, None


@dataclass(frozen=True, slots=True)
class EventBasedReplanPolicy:
    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]:
        if not state.robot.has_goal():
            return False, None
        if state.dirty_replan:
            return True, "event"
        return False, None


@dataclass(frozen=True, slots=True)
class NoReplanPolicy:
    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]:
        if state.dirty_replan:
            state.robot.clear_plan()
            state.dirty_replan = False
            state.replan_events.clear()
        return False, None


@dataclass(frozen=True, slots=True)
class PathAffectedReplanPolicy:
    cost_delta_threshold: float = 0.0

    def should_replan(self, state: SimulationState) -> tuple[bool, str | None]:
        if not state.robot.has_goal():
            return False, None

        if "goal_changed" in state.replan_events or "robot_repositioned" in state.replan_events:
            return True, "event"

        changed_cells = set(state.world_delta.obstacle_cells_changed)
        changed_cells.update(state.world_delta.cost_cells_changed)

        if state.world_delta.world_reinitialized:
            return True, "path_affected"

        if changed_cells and state.robot.remaining_path_intersects(changed_cells):
            return True, "path_affected"

        if self.cost_delta_threshold > 0:
            affected_cost = 0.0
            for pos in state.world_delta.cost_cells_changed:
                if pos in state.robot.remaining_path_cells():
                    affected_cost += state.world.get_extra_cost(pos)
            if affected_cost >= self.cost_delta_threshold:
                return True, "path_affected"

        return False, None
