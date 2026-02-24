from __future__ import annotations

from collections.abc import Callable

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
from core.domain.position import Position
from core.domain.robot_state import RobotState
from core.domain.world import World
from core.planning.astar import PlanResult
from core.planning.interface import NoPath
from core.simulation.state import SimulationState

PlannerFn = Callable[[World, Position, Position], PlanResult]


class SimulationEngine:
    """Simulation coordinator with strict tick contract.

    Tick order is fixed and must be respected by callers:
      1) ``apply(event)`` mutates domain state and only sets ``dirty_replan``.
      2) ``replan(planner)`` is the only method that invokes planning and only
         when ``dirty_replan`` is ``True``.
      3) ``step()`` advances exactly one waypoint along ``robot.path``.

    Error behaviour:
    - Calling ``step()`` while ``dirty_replan`` is ``True`` raises
      ``RuntimeError`` because event changes must be replanned first.
    - ``replan()`` propagates ``NoPath`` from the planner and keeps
      ``dirty_replan`` set to ``True`` so callers cannot step accidentally.
    """

    def __init__(self, state: SimulationState) -> None:
        self.state = state

    def apply(self, event: DomainEvent) -> None:
        """Apply one domain event; never plan or move within this method."""
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

    def replan(self, planner: PlannerFn) -> bool:
        """Recompute ``robot.path`` exactly once when ``dirty_replan`` is set."""
        if not self.state.dirty_replan:
            return False

        goal = self.state.robot.goal
        if goal is None:
            self.state.robot.clear_plan()
            self.state.dirty_replan = False
            return False

        result = planner(self.state.world, self.state.robot.position, goal)
        if not result.path:
            raise NoPath(f"No path from {self.state.robot.position} to {goal}.")

        start_index = 1 if result.path[0] == self.state.robot.position else 0
        self.state.robot.set_path(result.path, start_index=start_index)
        self.state.dirty_replan = False
        return True

    def replan_if_needed(self, planner: PlannerFn) -> bool:
        """Backward-compatible alias for ``replan``."""
        return self.replan(planner)

    def step(self) -> bool:
        """Advance exactly one waypoint along the current path.

        Returns ``False`` when no waypoint remains. Raises ``RuntimeError`` when
        called before pending replanning is resolved.
        """
        if self.state.dirty_replan:
            raise RuntimeError("step() requires a clean plan; call replan() after apply().")

        self.state.tick += 1

        waypoint = self.state.robot.next_waypoint()
        if waypoint is None:
            return False

        self.state.robot.position = waypoint
        self.state.robot.advance_waypoint()
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
