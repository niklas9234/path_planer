from __future__ import annotations

import pytest

from core.domain import (
    AddObstacle,
    AddZone,
    ClearExtraCost,
    ClearGoal,
    Position,
    SetExtraCost,
    SetGoal,
    SetRobotPosition,
    ZoneType,
)
from core.planning import plan
from core.planning.astar import NoPath
from core.simulation import SimulationEngine, SimulationState


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

    replanned = engine.replan(plan)
    moved = engine.step()

    assert replanned is True
    assert moved is True
    assert engine.state.robot.position == Position(1, 1)
    assert engine.state.tick == 1


def test_obstacle_event_triggers_replan_for_existing_goal() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))
    engine.replan(plan)

    engine.apply(AddObstacle(position=Position(1, 1)))

    assert engine.state.dirty_replan is True

    engine.replan(plan)

    assert Position(1, 1) not in engine.state.robot.path
    assert engine.state.world_delta.obstacle_cells_changed == set()


def test_world_delta_tracks_and_clears_cost_changes_after_replan() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))
    engine.apply(SetExtraCost(position=Position(1, 0), value=2.0))
    engine.apply(ClearExtraCost(position=Position(1, 0)))

    assert engine.state.world_delta.cost_cells_changed == {Position(1, 0)}

    engine.replan(plan)

    assert engine.state.world_delta.cost_cells_changed == set()
    assert engine.state.world_delta.world_reinitialized is False


def test_set_robot_position_clears_plan_and_requires_replan_when_goal_exists() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))
    engine.replan(plan)

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


def test_step_without_valid_plan_order_returns_stalled() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))

    moved = engine.step()

    assert moved is False


def test_replan_without_new_event_is_noop() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))

    assert engine.replan(plan) is True
    old_path = list(engine.state.robot.path)

    assert engine.replan(plan) is False
    assert engine.state.robot.path == old_path


def test_event_during_running_path_can_continue_until_replan() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))
    engine.replan(plan)

    assert engine.step() is True

    engine.apply(AddObstacle(position=Position(3, 2)))

    assert engine.step() is True
    assert engine.replan(plan) is True


def test_replan_propagates_nopath_and_keeps_dirty_flag() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))
    engine.apply(AddObstacle(position=Position(1, 1)))
    engine.apply(AddObstacle(position=Position(1, 0)))
    engine.apply(AddObstacle(position=Position(0, 1)))

    with pytest.raises(NoPath):
        engine.replan(plan)

    assert engine.state.dirty_replan is True


def test_add_slow_zone_triggers_replan_and_changes_cell_cost() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))

    engine.apply(
        AddZone(
            zone_type=ZoneType.SLOW,
            cells=(Position(1, 1),),
            duration_ticks=3,
            extra_cost=5.0,
        ),
    )

    assert engine.state.dirty_replan is True
    assert engine.state.world.get_extra_cost(Position(1, 1)) == 5.0


def test_expired_zone_marks_world_delta_and_requires_replan() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))
    engine.apply(
        AddZone(
            zone_type=ZoneType.OBSTACLE,
            cells=(Position(1, 0),),
            duration_ticks=1,
        ),
    )

    assert engine.state.world.is_blocked(Position(1, 0)) is True

    engine.process_tick_updates()
    assert engine.state.world.is_blocked(Position(1, 0)) is True

    engine.state.tick = 1
    engine.process_tick_updates()

    assert engine.state.world.is_blocked(Position(1, 0)) is False
    assert Position(1, 0) in engine.state.world_delta.obstacle_cells_changed
    assert engine.state.dirty_replan is True
