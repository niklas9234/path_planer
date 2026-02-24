from __future__ import annotations

from core.domain.events import AddObstacle, SetGoal
from core.domain.position import Position
from core.planning.astar import plan
from core.simulation.engine import SimulationEngine
from core.simulation.loop import run_tick, run_until_done
from core.simulation.state import SimulationState


def _make_engine() -> SimulationEngine:
    state = SimulationState.create(width=4, height=3, robot_position=Position(0, 1))
    return SimulationEngine(state)


def test_metrics_start_goal_obstacle_replanning_finalize() -> None:
    engine = _make_engine()

    engine.apply(SetGoal(goal=Position(3, 1)))
    first_tick = run_tick(engine, plan)
    assert first_tick.replanned is True
    assert engine.state.robot.position == Position(1, 1)

    engine.apply(AddObstacle(position=Position(2, 1)))

    run_result = run_until_done(engine, plan)

    assert run_result.reason == "goal_reached"
    assert run_result.run_metrics is not None

    metrics = run_result.run_metrics
    assert metrics["replan_count"] == 2
    assert metrics["replan_trigger_reason"] == "obstacle_changed"
    assert metrics["path_length_current"] == 0
    assert metrics["path_cost_current"] == 0.0
    assert metrics["steps_taken"] == 3
    assert metrics["goal_reached"] is True
    assert metrics["ticks_to_goal"] == 3
    assert metrics["no_path_events"] == 0
    assert metrics["obstacle_changes"] == 1


def test_metrics_no_path_event_is_counted() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(3, 1)))
    engine.apply(AddObstacle(position=Position(1, 0)))
    engine.apply(AddObstacle(position=Position(1, 1)))
    engine.apply(AddObstacle(position=Position(1, 2)))

    result = run_until_done(engine, plan)

    assert result.reason == "stalled"
    assert result.run_metrics is not None
    assert result.run_metrics["replan_count"] == 1
    assert result.run_metrics["no_path_events"] == 1
