from __future__ import annotations

import pytest
from core.domain.events import AddObstacle, SetGoal
from core.domain.position import Position
from core.planning.astar import plan
from core.simulation.engine import SimulationEngine
from core.simulation.loop import run_tick, run_until_done
from core.simulation.state import SimulationState


def _make_engine(width: int = 5, height: int = 5, start: Position = Position(0, 0)) -> SimulationEngine:
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
