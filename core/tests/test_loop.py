from __future__ import annotations

import pytest
from core.domain import AddObstacle, Position, SetExtraCost, SetGoal
from core.planning import plan
from core.simulation import (
    NoReplanPolicy,
    PathAffectedReplanPolicy,
    PeriodicReplanPolicy,
    SimulationEngine,
    SimulationState,
    StaticOnceReplanPolicy,
    run_tick,
    run_until_done,
)


def _make_engine(
    width: int = 5,
    height: int = 5,
    start: Position | None = None,
) -> SimulationEngine:
    if start is None:
        start = Position(0, 0)
    return SimulationEngine(
        SimulationState.create(width=width, height=height, robot_position=start),
    )


def test_run_tick_replans_and_moves_towards_goal() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))

    result = run_tick(engine, plan)

    assert result.replanned is True
    assert result.moved is True
    assert result.done is False
    assert result.reason == "running"
    assert engine.state.robot.position == Position(1, 1)


def test_periodic_policy_replans_every_two_ticks() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))

    t1 = run_tick(engine, plan, replan_policy=PeriodicReplanPolicy(interval=2))
    t2 = run_tick(engine, plan, replan_policy=PeriodicReplanPolicy(interval=2))

    assert t1.replanned is True
    assert t2.replanned is False


def test_path_affected_policy_ignores_changes_outside_remaining_path() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))
    run_tick(engine, plan, replan_policy=PathAffectedReplanPolicy())

    engine.apply(AddObstacle(position=Position(4, 0)))
    unaffected = run_tick(engine, plan, replan_policy=PathAffectedReplanPolicy())

    assert unaffected.replanned is False


def test_path_affected_policy_replans_on_slow_zone_in_remaining_path() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))
    run_tick(engine, plan, replan_policy=PathAffectedReplanPolicy())

    waypoint = engine.state.robot.next_waypoint()
    assert waypoint is not None
    engine.apply(SetExtraCost(position=waypoint, value=5.0))

    affected = run_tick(engine, plan, replan_policy=PathAffectedReplanPolicy())

    assert affected.replanned is True


def test_path_affected_policy_ignores_slow_zone_outside_remaining_path() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))
    run_tick(engine, plan, replan_policy=PathAffectedReplanPolicy())

    engine.apply(SetExtraCost(position=Position(4, 0), value=5.0))
    unaffected = run_tick(engine, plan, replan_policy=PathAffectedReplanPolicy())

    assert unaffected.replanned is False


def test_path_affected_policy_replans_on_blocked_remaining_path_cell() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))
    run_tick(engine, plan, replan_policy=PathAffectedReplanPolicy())

    waypoint = engine.state.robot.next_waypoint()
    assert waypoint is not None
    engine.apply(AddObstacle(position=waypoint))

    affected = run_tick(engine, plan, replan_policy=PathAffectedReplanPolicy())

    assert affected.replanned is True


def test_static_once_policy_replans_initial_dirty_goal_only_once() -> None:
    engine = _make_engine()
    policy = StaticOnceReplanPolicy()

    engine.apply(SetGoal(goal=Position(4, 4)))
    first = run_tick(engine, plan, replan_policy=policy)

    engine.apply(AddObstacle(position=Position(2, 0)))
    second = run_tick(engine, plan, replan_policy=policy)

    assert first.replanned is True
    assert first.moved is True
    assert second.replanned is False


def test_static_once_policy_ignores_late_dirty_events_in_run_until_done() -> None:
    engine = _make_engine(width=6, height=3)
    policy = StaticOnceReplanPolicy()

    engine.apply(SetGoal(goal=Position(5, 0)))
    initial = run_tick(engine, plan, replan_policy=policy)
    engine.apply(AddObstacle(position=Position(0, 2)))

    result = run_until_done(engine, plan, replan_policy=policy, max_ticks=20)

    assert initial.replanned is True
    assert initial.moved is True
    assert result.done is True
    assert initial.replanned + result.replans == 1


def test_no_replan_policy_keeps_existing_path_when_event_marks_dirty() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))
    run_tick(engine, plan)

    planned_path = list(engine.state.robot.path)
    planned_index = engine.state.robot.path_index

    engine.apply(AddObstacle(position=Position(4, 0)))
    tick = run_tick(engine, plan, replan_policy=NoReplanPolicy())

    assert tick.replanned is False
    assert engine.state.dirty_replan is True
    assert "obstacle_changed" in engine.state.replan_events
    assert engine.state.robot.path == planned_path
    assert engine.state.robot.path_index == planned_index + 1


def test_run_until_done_reaches_goal() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(2, 2)))

    result = run_until_done(engine, plan)

    assert result.done is True
    assert result.reason == "goal_reached"
    assert result.replans >= 1
    assert result.moves >= 1
    assert engine.state.robot.position == Position(2, 2)


def test_run_until_done_stalls_when_no_path_exists() -> None:
    engine = _make_engine(width=3, height=3)
    engine.apply(SetGoal(goal=Position(2, 2)))
    engine.apply(AddObstacle(position=Position(1, 1)))
    engine.apply(AddObstacle(position=Position(1, 0)))
    engine.apply(AddObstacle(position=Position(0, 1)))

    result = run_until_done(engine, plan)

    assert result.done is True
    assert result.reason == "stalled"
    assert result.moves == 0


def test_run_until_done_with_max_ticks_guard() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(4, 4)))

    result = run_until_done(engine, plan, max_ticks=1)

    assert result.done is False
    assert result.reason == "max_ticks"


def test_run_until_done_validates_max_ticks() -> None:
    engine = _make_engine()

    with pytest.raises(ValueError):
        run_until_done(engine, plan, max_ticks=0)
