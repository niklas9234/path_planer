from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean

from core.domain.events import (
    AddObstacle,
    AddZone,
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
    zone_expirations: int = 0


@dataclass(slots=True)
class MetricsRecorder:
    ticks: list[TickMetrics] = field(default_factory=list)
    replan_count_total: int = 0
    no_path_events_total: int = 0
    obstacle_changes_total: int = 0
    zone_expirations_total: int = 0
    steps_taken_total: int = 0
    travel_cost_total: float = 0.0
    last_replan_trigger_reason: str | None = None

    def _current_tick(self, tick: int) -> TickMetrics:
        if not self.ticks or self.ticks[-1].tick != tick:
            self.ticks.append(TickMetrics(tick=tick))
        return self.ticks[-1]

    def _remaining_path(self, robot: RobotState) -> list:
        return robot.path[robot.path_index :]

    def _path_cost(self, world: World, robot: RobotState) -> float:
        cost = 0.0
        for pos in self._remaining_path(robot):
            try:
                cost += world.get_cell_cost(pos)
            except ValueError:
                continue
        return cost

    def _update_path_metrics(
        self, tick: TickMetrics, world: World, robot: RobotState
    ) -> None:
        remaining = self._remaining_path(robot)
        tick.path_length_current = len(remaining)
        tick.path_cost_current = self._path_cost(world, robot)

    def on_tick_start(
        self,
        *,
        tick: int,
        world: World,
        robot: RobotState,
        zone_expired_obstacle_cells: int = 0,
        zone_expired_cost_cells: int = 0,
    ) -> None:
        current = self._current_tick(tick)
        if zone_expired_obstacle_cells or zone_expired_cost_cells:
            self.zone_expirations_total += 1
            current.zone_expirations = self.zone_expirations_total
        self._update_path_metrics(current, world, robot)

    def on_event_applied(self, *, tick: int, event: DomainEvent) -> None:
        current = self._current_tick(tick)

        if isinstance(event, SetGoal):
            self.last_replan_trigger_reason = "event"
            current.replan_trigger_reason = self.last_replan_trigger_reason
        elif isinstance(event, SetRobotPosition):
            self.last_replan_trigger_reason = "event"
            current.replan_trigger_reason = self.last_replan_trigger_reason
        elif isinstance(event, (AddObstacle, RemoveObstacle)):
            self.obstacle_changes_total += 1
            current.obstacle_changes = self.obstacle_changes_total
            self.last_replan_trigger_reason = "event"
            current.replan_trigger_reason = self.last_replan_trigger_reason
        elif isinstance(event, AddZone):
            self.last_replan_trigger_reason = "event"
            current.replan_trigger_reason = self.last_replan_trigger_reason
        elif isinstance(event, (SetExtraCost, ClearExtraCost)):
            self.last_replan_trigger_reason = "event"
            current.replan_trigger_reason = self.last_replan_trigger_reason

    def on_replan(
        self,
        *,
        tick: int,
        replanned: bool,
        found_path: bool,
        world: World,
        robot: RobotState,
        reason: str | None,
    ) -> None:
        current = self._current_tick(tick)
        if replanned:
            self.replan_count_total += 1
            current.replan_count = 1
            self.last_replan_trigger_reason = reason
            current.replan_trigger_reason = reason
            if not found_path:
                self.no_path_events_total += 1
                current.no_path_events = self.no_path_events_total
        else:
            current.replan_count = 0
        self._update_path_metrics(current, world, robot)

    def on_step_executed(
        self,
        *,
        tick: int,
        moved: bool,
        world: World,
        robot: RobotState,
        step_cost: float = 0.0,
    ) -> None:
        current = self._current_tick(tick)
        if moved:
            self.steps_taken_total += 1
            self.travel_cost_total += step_cost
        current.steps_taken = self.steps_taken_total
        current.goal_reached = robot.at_goal()
        if current.goal_reached and current.ticks_to_goal is None:
            current.ticks_to_goal = tick
        self._update_path_metrics(current, world, robot)

    def on_done(
        self,
        *,
        tick: int,
        world: World,
        robot: RobotState,
        reason: str,
    ) -> None:
        del reason
        current = self._current_tick(tick)
        current.goal_reached = robot.at_goal()
        if current.goal_reached and current.ticks_to_goal is None:
            current.ticks_to_goal = tick
        self._update_path_metrics(current, world, robot)

    def record_apply_event(self, *, tick: int, event: DomainEvent) -> None:
        self.on_event_applied(tick=tick, event=event)

    def record_replan_result(
        self,
        *,
        tick: int,
        replanned: bool,
        found_path: bool,
        world: World,
        robot: RobotState,
        reason: str | None,
    ) -> None:
        self.on_replan(
            tick=tick,
            replanned=replanned,
            found_path=found_path,
            world=world,
            robot=robot,
            reason=reason,
        )

    def record_step(
        self,
        *,
        tick: int,
        moved: bool,
        world: World,
        robot: RobotState,
        step_cost: float = 0.0,
    ) -> None:
        self.on_step_executed(
            tick=tick,
            moved=moved,
            world=world,
            robot=robot,
            step_cost=step_cost,
        )

    def record_zone_added(
        self, *, tick: int, zone_type: object, cells: int, duration_ticks: int | None
    ) -> None:
        del zone_type, cells, duration_ticks
        self._current_tick(tick)

    def record_zone_expiration(
        self, *, tick: int, obstacle_cells: int, cost_cells: int
    ) -> None:
        current = self._current_tick(tick)
        if obstacle_cells or cost_cells:
            self.zone_expirations_total += 1
            current.zone_expirations = self.zone_expirations_total

    def finalize_run_metrics(self) -> dict[str, int | float | bool | str | None]:
        goal_tick = next(
            (item.ticks_to_goal for item in self.ticks if item.goal_reached), None
        )
        final_path_len = self.ticks[-1].path_length_current if self.ticks else 0
        final_path_cost = self.ticks[-1].path_cost_current if self.ticks else 0.0

        total_ticks = self.ticks[-1].tick if self.ticks else 0
        total_moves = self.steps_taken_total
        total_travel_cost = self.travel_cost_total

        return {
            "ticks_recorded": len(self.ticks),
            "total_ticks": total_ticks,
            "ticks_executed": total_ticks,
            "replan_count": self.replan_count_total,
            "replan_trigger_reason": self.last_replan_trigger_reason,
            "path_length_current": final_path_len,
            "path_cost_current": final_path_cost,
            "steps_taken": self.steps_taken_total,
            "total_moves": total_moves,
            "total_travel_cost": total_travel_cost,
            "mean_step_cost": (total_travel_cost / total_moves) if total_moves else 0.0,
            "goal_reached": any(item.goal_reached for item in self.ticks),
            "ticks_to_goal": goal_tick,
            "no_path_events": self.no_path_events_total,
            "obstacle_changes": self.obstacle_changes_total,
            "zone_expirations": self.zone_expirations_total,
            "mean_path_length_current": (
                mean([item.path_length_current for item in self.ticks])
                if self.ticks
                else 0.0
            ),
        }
