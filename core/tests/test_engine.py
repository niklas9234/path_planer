from __future__ import annotations

from core.domain.Position import Position
from core.domain.events import AddObstacle, ClearGoal, SetGoal, SetRobotPosition
from core.planning.astar import plan
from core.simulation.engine import SimulationEngine
from core.simulation.state import SimulationState


def _make_engine() -> SimulationEngine:
    state = SimulationState.create(width=5, height=5, robot_position=Position(0, 0))
    return SimulationEngine(state)


def test_set_goal_marks_state_dirty_for_replanning() -> None:
    engine = _make_engine()

    engine.apply(SetGoal(goal=Position(4, 4)))

    assert engine.state.robot.goal == Position(4, 4)
    assert engine.state.dirty_replan is True


def test_replan_and_step_moves_robot() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))

    replanned = engine.replan_if_needed(plan)
    moved = engine.step()

    assert replanned is True
    assert moved is True
    assert engine.state.robot.position == Position(1, 1)
    assert engine.state.tick == 1


def test_obstacle_event_triggers_replan_for_existing_goal() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))
    engine.replan_if_needed(plan)

    engine.apply(AddObstacle(position=Position(1, 1)))

    assert engine.state.dirty_replan is True

    engine.replan_if_needed(plan)

    assert Position(1, 1) not in engine.state.robot.path


def test_set_robot_position_clears_plan_and_requires_replan_when_goal_exists() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))
    engine.replan_if_needed(plan)

    engine.apply(SetRobotPosition(position=Position(0, 1)))

    assert engine.state.robot.position == Position(0, 1)
    assert engine.state.robot.path == []
    assert engine.state.dirty_replan is True


def test_clear_goal_resets_plan_and_dirty_flag() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))

    engine.apply(ClearGoal())

    assert engine.state.robot.goal is None
    assert engine.state.robot.path == []
    assert engine.state.dirty_replan is False
