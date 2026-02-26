from __future__ import annotations

from core.experiments.runner import run_experiment
from core.experiments.scenarios import required_scenarios


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
