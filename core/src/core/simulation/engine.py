from __future__ import annotations

from collections.abc import Callable

from core.domain.position import Position
from core.domain.robot_state import RobotState
from core.domain.events import (
    AddObstacle,
    ClearExtraCost,
    ClearGoal,
    DomainEvent,
    InitWorld,
    RemoveObstacle,
    ResetSimulation,
    SetExtraCost,
    SetGoal,
    SetRobotPosition,
)
from core.domain.world import World
from core.metrics.recorder import MetricsRecorder
from core.planning.astar import PlanResult
from core.simulation.state import SimulationState

PlannerFn = Callable[[World, Position, Position], PlanResult]


class SimulationEngine:
    def __init__(self, state: SimulationState) -> None:
        self.state = state
        if not hasattr(self.state, "metrics") or self.state.metrics is None:
            self.state.metrics = MetricsRecorder()

    def apply(self, event: DomainEvent) -> None:
        self.state.metrics.record_apply_event(tick=self.state.tick, event=event)
        if isinstance(event, InitWorld):
            self._apply_init_world(event)
            return
        if isinstance(event, SetRobotPosition):
            self.state.world.assert_in_bounds(event.position.x, event.position.y)
            self.state.robot.position = event.position
            self.state.robot.clear_plan()
            self.state.dirty_replan = self.state.robot.goal is not None
            return
        if isinstance(event, SetGoal):
            self.state.world.assert_in_bounds(event.goal.x, event.goal.y)
            if self.state.world.is_blocked(event.goal):
                raise ValueError(f"Goal position is blocked: {event.goal}")
            self.state.robot.set_goal(event.goal)
            self.state.dirty_replan = True
            return
        if isinstance(event, ClearGoal):
            self.state.robot.goal = None
            self.state.robot.clear_plan()
            self.state.dirty_replan = False
            return
        if isinstance(event, AddObstacle):
            self.state.world.add_obstacle(event.position)
            self.state.dirty_replan = self.state.robot.goal is not None
            return
        if isinstance(event, RemoveObstacle):
            self.state.world.remove_obstacle(event.position)
            self.state.dirty_replan = self.state.robot.goal is not None
            return
        if isinstance(event, SetExtraCost):
            self.state.world.set_extra_cost(event.position, event.value)
            self.state.dirty_replan = self.state.robot.goal is not None
            return
        if isinstance(event, ClearExtraCost):
            self.state.world.clear_extra_cost(event.position)
            self.state.dirty_replan = self.state.robot.goal is not None
            return
        if isinstance(event, ResetSimulation):
            del event.seed
            self.state.tick = 0
            self.state.robot.clear_plan()
            self.state.dirty_replan = self.state.robot.goal is not None
            return
        raise TypeError(f"Unsupported event type: {type(event)!r}")

    def replan_if_needed(self, planner: PlannerFn) -> bool:
        if not self.state.dirty_replan:
            self.state.metrics.record_replan_result(
                tick=self.state.tick,
                replanned=False,
                found_path=bool(self.state.robot.path),
                world=self.state.world,
                robot=self.state.robot,
            )
            return False

        goal = self.state.robot.goal
        if goal is None:
            self.state.robot.clear_plan()
            self.state.dirty_replan = False
            self.state.metrics.record_replan_result(
                tick=self.state.tick,
                replanned=False,
                found_path=False,
                world=self.state.world,
                robot=self.state.robot,
            )
            return False

        result = planner(self.state.world, self.state.robot.position, goal)

        if result.path:
            start_index = 1 if result.path[0] == self.state.robot.position else 0
            self.state.robot.set_path(result.path, start_index=start_index)
        else:
            self.state.robot.set_path([])

        self.state.dirty_replan = False
        self.state.metrics.record_replan_result(
            tick=self.state.tick,
            replanned=True,
            found_path=bool(result.path),
            world=self.state.world,
            robot=self.state.robot,
        )
        return True

    def step(self) -> bool:
        self.state.tick += 1

        waypoint = self.state.robot.next_waypoint()
        if waypoint is None:
            self.state.metrics.record_step(
                tick=self.state.tick,
                moved=False,
                world=self.state.world,
                robot=self.state.robot,
            )
            return False

        self.state.robot.position = waypoint
        self.state.robot.advance_waypoint()
        self.state.metrics.record_step(
            tick=self.state.tick,
            moved=True,
            world=self.state.world,
            robot=self.state.robot,
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
        self.state.metrics = MetricsRecorder()
