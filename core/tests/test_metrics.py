from __future__ import annotations

from core.domain.events import AddObstacle, AddZone, ClearExtraCost, SetExtraCost, SetGoal
from core.domain.position import Position
from core.domain.world import ZoneType
from core.planning.astar import plan
from core.simulation.engine import SimulationEngine
from core.simulation.loop import run_tick, run_until_done
from core.simulation.state import SimulationState


def _make_engine() -> SimulationEngine:
    state = SimulationState.create(width=4, height=3, robot_position=Position(0, 1))
    return SimulationEngine(state)


def _make_linear_engine() -> SimulationEngine:
    state = SimulationState.create(width=4, height=1, robot_position=Position(0, 0))
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
    assert metrics["replan_trigger_reason"] == "event"
    assert metrics["path_length_current"] == 0
    assert metrics["path_cost_current"] == 0.0
    assert metrics["steps_taken"] == 3
    assert metrics["total_moves"] == 3
    assert metrics["total_ticks"] == 3
    assert metrics["ticks_executed"] == 3
    assert metrics["total_travel_cost"] == 3.0
    assert metrics["mean_step_cost"] == 1.0
    assert metrics["goal_reached"] is True
    assert metrics["ticks_to_goal"] == 3
    assert metrics["no_path_events"] == 0
    assert metrics["obstacle_changes"] == 1
    assert metrics["zone_expirations"] == 0


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


def test_metrics_counts_zone_expiration() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(3, 1)))
    engine.apply(
        AddZone(
            zone_type=ZoneType.SLOW,
            cells=(Position(1, 1),),
            duration_ticks=1,
            extra_cost=2.0,
        ),
    )

    run_until_done(engine, plan)

    assert engine.state.metrics.zone_expirations_total >= 1


def test_metrics_travel_cost_reflects_slowzone_with_equal_step_count() -> None:
    baseline = _make_linear_engine()
    baseline.apply(SetGoal(goal=Position(3, 0)))
    baseline_result = run_until_done(baseline, plan)

    assert baseline_result.reason == "goal_reached"
    assert baseline_result.run_metrics is not None

    slowzone = _make_linear_engine()
    slowzone.apply(SetGoal(goal=Position(3, 0)))
    slowzone.apply(SetExtraCost(position=Position(1, 0), value=4.0))
    slowzone_result = run_until_done(slowzone, plan)

    assert slowzone_result.reason == "goal_reached"
    assert slowzone_result.run_metrics is not None

    baseline_metrics = baseline_result.run_metrics
    slowzone_metrics = slowzone_result.run_metrics

    assert baseline_metrics["steps_taken"] == slowzone_metrics["steps_taken"] == 3
    assert slowzone_metrics["total_travel_cost"] > baseline_metrics["total_travel_cost"]


def test_metrics_travel_cost_without_slowzone_remains_base_cost() -> None:
    engine = _make_engine()
    engine.apply(SetGoal(goal=Position(3, 1)))

    run_result = run_until_done(engine, plan)

    assert run_result.reason == "goal_reached"
    assert run_result.run_metrics is not None
    assert run_result.run_metrics["steps_taken"] == 3
    assert run_result.run_metrics["total_travel_cost"] == 3.0


def test_metrics_travel_cost_handles_slowzone_clear() -> None:
    engine = _make_linear_engine()
    engine.apply(SetGoal(goal=Position(3, 0)))
    engine.apply(SetExtraCost(position=Position(1, 0), value=5.0))
    engine.apply(ClearExtraCost(position=Position(1, 0)))

    run_result = run_until_done(engine, plan)

    assert run_result.reason == "goal_reached"
    assert run_result.run_metrics is not None
    assert run_result.run_metrics["steps_taken"] == 3
    assert run_result.run_metrics["total_travel_cost"] == 3.0
