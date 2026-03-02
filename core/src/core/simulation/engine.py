from __future__ import annotations

from collections.abc import Callable

from core.domain import (
    AddObstacle,
    AddZone,
    ClearExtraCost,
    ClearGoal,
    DomainEvent,
    InitWorld,
    Position,
    RemoveObstacle,
    ResetSimulation,
    RobotState,
    SetExtraCost,
    SetGoal,
    SetRobotPosition,
    World,
    ZoneType,
)
from core.metrics.recorder import MetricsRecorder
from core.planning.astar import NoPath, PlanResult
from core.simulation.state import SimulationState

PlannerFn = Callable[[World, Position, Position], PlanResult]


class SimulationEngine:
    def __init__(self, state: SimulationState) -> None:
        self.state = state
        if not hasattr(self.state, "metrics") or self.state.metrics is None:
            self.state.metrics = MetricsRecorder()

    def apply(self, event: DomainEvent) -> None:
        self.state.metrics.on_event_applied(tick=self.state.tick, event=event)
        if isinstance(event, InitWorld):
            self._apply_init_world(event)
            self.state.world_delta.world_reinitialized = True
            self.state.replan_events.add("world_reinitialized")
            return
        if isinstance(event, SetRobotPosition):
            self.state.world.assert_in_bounds(event.position.x, event.position.y)
            self.state.robot.set_position(event.position)
            self.state.dirty_replan = self.state.robot.goal is not None
            self.state.replan_events.add("robot_repositioned")
            return
        if isinstance(event, SetGoal):
            self.state.world.assert_in_bounds(event.goal.x, event.goal.y)
            if self.state.world.is_blocked(event.goal):
                raise ValueError(f"Goal position is blocked: {event.goal}")
            self.state.robot.set_goal(event.goal)
            self.state.dirty_replan = True
            self.state.replan_events.add("goal_changed")
            return
        if isinstance(event, ClearGoal):
            self.state.robot.clear_goal()
            self.state.dirty_replan = False
            self.state.replan_events.clear()
            return
        if isinstance(event, AddObstacle):
            self.state.world.add_obstacle(event.position)
            self.state.world_delta.obstacle_cells_changed.add(event.position)
            self.state.dirty_replan = self.state.robot.goal is not None
            self.state.replan_events.add("obstacle_changed")
            return
        if isinstance(event, RemoveObstacle):
            self.state.world.remove_obstacle(event.position)
            self.state.world_delta.obstacle_cells_changed.add(event.position)
            self.state.dirty_replan = self.state.robot.goal is not None
            self.state.replan_events.add("obstacle_changed")
            return
        if isinstance(event, SetExtraCost):
            self.state.world.set_extra_cost(event.position, event.value)
            self.state.world_delta.cost_cells_changed.add(event.position)
            self.state.dirty_replan = self.state.robot.goal is not None
            self.state.replan_events.add("cost_changed")
            return
        if isinstance(event, ClearExtraCost):
            self.state.world.clear_extra_cost(event.position)
            self.state.world_delta.cost_cells_changed.add(event.position)
            self.state.dirty_replan = self.state.robot.goal is not None
            self.state.replan_events.add("cost_changed")
            return
        if isinstance(event, AddZone):
            self.state.world.add_zone(
                zone_type=event.zone_type,
                cells=event.cells,
                current_tick=self.state.tick,
                duration_ticks=event.duration_ticks,
                extra_cost=event.extra_cost,
            )
            if event.zone_type is ZoneType.OBSTACLE:
                self.state.world_delta.obstacle_cells_changed.update(event.cells)
            else:
                self.state.world_delta.cost_cells_changed.update(event.cells)
            self.state.dirty_replan = self.state.robot.goal is not None
            self.state.replan_events.add("zone_changed")
            return
        if isinstance(event, ResetSimulation):
            del event.seed
            self.state.tick = 0
            self.state.robot.clear_plan()
            self.state.dirty_replan = self.state.robot.goal is not None
            self.state.replan_events = {"reset"} if self.state.robot.goal is not None else set()
            return
        raise TypeError(f"Unsupported event type: {type(event)!r}")

    def process_tick_updates(self) -> tuple[int, int]:
        changes = self.state.world.expire_zones(self.state.tick)
        if changes.obstacle_cells_changed:
            self.state.world_delta.obstacle_cells_changed.update(changes.obstacle_cells_changed)
        if changes.cost_cells_changed:
            self.state.world_delta.cost_cells_changed.update(changes.cost_cells_changed)

        obstacle_count = len(changes.obstacle_cells_changed)
        cost_count = len(changes.cost_cells_changed)
        if obstacle_count or cost_count:
            self.state.dirty_replan = self.state.robot.goal is not None
            self.state.replan_events.add("zone_expired")
        return obstacle_count, cost_count

    def replan(self, planner: PlannerFn, *, reason: str | None = None) -> bool:
        if not self.state.dirty_replan and reason != "periodic":
            self.state.metrics.on_replan(
                tick=self.state.tick,
                replanned=False,
                found_path=bool(self.state.robot.path),
                world=self.state.world,
                robot=self.state.robot,
                reason=reason,
            )
            return False

        goal = self.state.robot.goal
        if goal is None:
            self.state.robot.clear_plan()
            self.state.dirty_replan = False
            self._clear_world_delta()
            self.state.metrics.on_replan(
                tick=self.state.tick,
                replanned=False,
                found_path=False,
                world=self.state.world,
                robot=self.state.robot,
                reason=reason,
            )
            return False

        try:
            result = planner(self.state.world, self.state.robot.position, goal)
        except NoPath:
            self.state.metrics.on_replan(
                tick=self.state.tick,
                replanned=True,
                found_path=False,
                world=self.state.world,
                robot=self.state.robot,
                reason=reason,
            )
            raise

        if not result.path:
            self.state.metrics.on_replan(
                tick=self.state.tick,
                replanned=True,
                found_path=False,
                world=self.state.world,
                robot=self.state.robot,
                reason=reason,
            )
            raise NoPath(f"No path from {self.state.robot.position} to {goal}.")

        start_index = 1 if result.path[0] == self.state.robot.position else 0
        self.state.robot.set_path(result.path, start_index=start_index)
        self.state.dirty_replan = False
        self._clear_world_delta()
        self.state.replan_events.clear()
        self.state.metrics.on_replan(
            tick=self.state.tick,
            replanned=True,
            found_path=bool(result.path),
            world=self.state.world,
            robot=self.state.robot,
            reason=reason,
        )
        return True

    def replan_if_needed(self, planner: PlannerFn) -> bool:
        if not self.state.dirty_replan:
            self.state.metrics.on_replan(
                tick=self.state.tick,
                replanned=False,
                found_path=bool(self.state.robot.path),
                world=self.state.world,
                robot=self.state.robot,
                reason=None,
            )
            return False
        return self.replan(planner, reason="event")

    def step(self) -> bool:
        self.state.tick += 1

        waypoint = self.state.robot.next_waypoint()
        if waypoint is None:
            self.state.metrics.on_step_executed(
                tick=self.state.tick,
                moved=False,
                world=self.state.world,
                robot=self.state.robot,
            )
            return False

        if self.state.world.is_blocked(waypoint):
            self.state.metrics.on_step_executed(
                tick=self.state.tick,
                moved=False,
                world=self.state.world,
                robot=self.state.robot,
            )
            return False

        step_cost = self.state.world.get_cell_cost(waypoint)
        self.state.robot.set_position(waypoint, clear_plan=False)
        self.state.robot.advance_waypoint()
        self.state.metrics.on_step_executed(
            tick=self.state.tick,
            moved=True,
            world=self.state.world,
            robot=self.state.robot,
            step_cost=step_cost,
        )
        return True

    def _apply_init_world(self, event: InitWorld) -> None:
        self.state.world = World(
            width=event.width,
            height=event.height,
            cell_size_m=event.cell_size_m,
            base_cost=event.base_cost,
        )
        self.state.robot = RobotState(position=Position(0, 0))
        self.state.dirty_replan = False
        self.state.tick = 0
        self.state.replan_events.clear()
        self.state.metrics = MetricsRecorder()

    def _clear_world_delta(self) -> None:
        self.state.world_delta.obstacle_cells_changed.clear()
        self.state.world_delta.cost_cells_changed.clear()
        self.state.world_delta.world_reinitialized = False
