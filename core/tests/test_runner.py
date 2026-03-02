from __future__ import annotations

from core.domain import AddObstacle, Position
from core.experiments.runner import run_experiment
from core.experiments.scenarios import ScenarioDefinition, ScenarioExpectation, WorldConfig, required_scenarios


def _scenario_by_name(name: str):
    scenarios = {scenario.name: scenario for scenario in required_scenarios()}
    return scenarios[name]


def test_run_experiment_is_reproducible_for_fixed_inputs() -> None:
    scenario = _scenario_by_name("replan_after_obstacle")

    first = run_experiment(scenario)
    second = run_experiment(scenario)

    assert first.run_context.run_id == second.run_context.run_id
    assert first.run_result == second.run_result
    assert first.metrics.ticks_executed == second.metrics.ticks_executed
    assert first.metrics.replans == second.metrics.replans
    assert first.metrics.moves == second.metrics.moves
    assert first.metrics.reason == second.metrics.reason


def test_run_context_available_in_metrics_and_exports() -> None:
    scenario = _scenario_by_name("empty_world_reaches_goal")

    result = run_experiment(scenario)
    payload = result.to_export_dict()

    assert result.metrics.run_context is result.run_context
    assert payload["run_context"]["run_id"] == result.run_context.run_id
    assert payload["metrics"]["run_id"] == result.run_context.run_id
    assert payload["snapshots"][0]["meta"]["run_id"] == result.run_context.run_id
    assert payload["snapshots"][0]["meta"]["tick"] == result.run_result.ticks_executed


def test_periodic_runner_replans_minimally_without_changes_and_by_next_interval_with_change() -> None:
    base_kwargs = dict(
        world_config=WorldConfig(width=6, height=3),
        start=Position(0, 0),
        goal=Position(5, 0),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=8,
        policy_name="periodic",
        policy_params={"interval": 3},
        expectation=ScenarioExpectation(allowed_reasons=("goal_reached", "stalled", "max_ticks")),
    )

    no_change = ScenarioDefinition(
        name="periodic_no_change",
        scheduled_events={},
        **base_kwargs,
    )
    with_change = ScenarioDefinition(
        name="periodic_with_change",
        scheduled_events={1: (AddObstacle(position=Position(0, 2)),)},
        **base_kwargs,
    )

    no_change_result = run_experiment(no_change).run_result
    with_change_result = run_experiment(with_change).run_result

    assert no_change_result.replans == 1
    assert with_change_result.replans >= 2
