from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean

from core.domain.events import (
    AddObstacle,
    ClearExtraCost,
    DomainEvent,
    RemoveObstacle,
    SetExtraCost,
    SetGoal,
    SetRobotPosition,
)
from core.domain.robot_state import RobotState
from core.domain.world import World


@dataclass(slots=True)
class TickMetrics:
    tick: int
    replan_count: int = 0
    replan_trigger_reason: str | None = None
    path_length_current: int = 0
    path_cost_current: float = 0.0
    steps_taken: int = 0
    goal_reached: bool = False
    ticks_to_goal: int | None = None
    no_path_events: int = 0
    obstacle_changes: int = 0


@dataclass(slots=True)
class MetricsRecorder:
    """Collects standardized per-tick and run-level metrics.

    Write responsibilities:
    - Engine.apply(event): trigger metrics (`replan_trigger_reason`, `obstacle_changes`).
    - Engine.replan_if_needed(...): planning outcome metrics (`replan_count`, `no_path_events`, path metrics).
    - Engine.step(): progress metrics (`steps_taken`, `goal_reached`, `ticks_to_goal`, path metrics).
    """

    ticks: list[TickMetrics] = field(default_factory=list)
    replan_count_total: int = 0
    no_path_events_total: int = 0
    obstacle_changes_total: int = 0
    steps_taken_total: int = 0
    last_replan_trigger_reason: str | None = None

    def _current_tick(self, tick: int) -> TickMetrics:
        if not self.ticks or self.ticks[-1].tick != tick:
            self.ticks.append(TickMetrics(tick=tick))
        return self.ticks[-1]

    def _remaining_path(self, robot: RobotState) -> list:
        return robot.path[robot.path_index :]

    def _path_cost(self, world: World, robot: RobotState) -> float:
        return sum(world.get_cell_cost(pos) for pos in self._remaining_path(robot))

    def _update_path_metrics(self, tick: TickMetrics, world: World, robot: RobotState) -> None:
        remaining = self._remaining_path(robot)
        tick.path_length_current = len(remaining)
        tick.path_cost_current = self._path_cost(world, robot)

    def record_apply_event(self, *, tick: int, event: DomainEvent) -> None:
        current = self._current_tick(tick)

        if isinstance(event, SetGoal):
            self.last_replan_trigger_reason = "set_goal"
            current.replan_trigger_reason = self.last_replan_trigger_reason
        elif isinstance(event, SetRobotPosition):
            self.last_replan_trigger_reason = "set_robot_position"
            current.replan_trigger_reason = self.last_replan_trigger_reason
        elif isinstance(event, (AddObstacle, RemoveObstacle)):
            self.obstacle_changes_total += 1
            current.obstacle_changes = self.obstacle_changes_total
            self.last_replan_trigger_reason = "obstacle_changed"
            current.replan_trigger_reason = self.last_replan_trigger_reason
        elif isinstance(event, (SetExtraCost, ClearExtraCost)):
            self.last_replan_trigger_reason = "cost_changed"
            current.replan_trigger_reason = self.last_replan_trigger_reason

    def record_replan_result(self, *, tick: int, replanned: bool, found_path: bool, world: World, robot: RobotState) -> None:
        current = self._current_tick(tick)
        if replanned:
            self.replan_count_total += 1
            current.replan_count = 1
            current.replan_trigger_reason = self.last_replan_trigger_reason
            if not found_path:
                self.no_path_events_total += 1
                current.no_path_events = self.no_path_events_total
        else:
            current.replan_count = 0
        self._update_path_metrics(current, world, robot)

    def record_step(self, *, tick: int, moved: bool, world: World, robot: RobotState) -> None:
        current = self._current_tick(tick)
        if moved:
            self.steps_taken_total += 1
        current.steps_taken = self.steps_taken_total
        current.goal_reached = robot.at_goal()
        if current.goal_reached and current.ticks_to_goal is None:
            current.ticks_to_goal = tick
        self._update_path_metrics(current, world, robot)

    def finalize_run_metrics(self) -> dict[str, int | float | bool | str | None]:
        goal_tick = next((item.ticks_to_goal for item in self.ticks if item.goal_reached), None)
        final_path_len = self.ticks[-1].path_length_current if self.ticks else 0
        final_path_cost = self.ticks[-1].path_cost_current if self.ticks else 0.0

        return {
            "ticks_recorded": len(self.ticks),
            "replan_count": self.replan_count_total,
            "replan_trigger_reason": self.last_replan_trigger_reason,
            "path_length_current": final_path_len,
            "path_cost_current": final_path_cost,
            "steps_taken": self.steps_taken_total,
            "goal_reached": any(item.goal_reached for item in self.ticks),
            "ticks_to_goal": goal_tick,
            "no_path_events": self.no_path_events_total,
            "obstacle_changes": self.obstacle_changes_total,
            "mean_path_length_current": mean([item.path_length_current for item in self.ticks]) if self.ticks else 0.0,
        }
