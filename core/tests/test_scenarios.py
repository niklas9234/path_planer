from __future__ import annotations

from core.experiments.scenarios import required_scenarios, run_scenario


def _scenario_by_name(name: str):
    scenarios = {scenario.name: scenario for scenario in required_scenarios()}
    return scenarios[name]


def test_empty_world_reaches_goal() -> None:
    scenario = _scenario_by_name("empty_world_reaches_goal")

    result = run_scenario(scenario)

    assert result.reason == "goal_reached"
    assert result.moves > 0


def test_blocked_goal_stalls() -> None:
    scenario = _scenario_by_name("blocked_goal_stalls")

    result = run_scenario(scenario)

    assert result.reason == "stalled"
    assert result.moves == 0


def test_replan_after_obstacle() -> None:
    scenario = _scenario_by_name("replan_after_obstacle")

    result = run_scenario(scenario)

    assert result.replans >= 1
    assert result.reason in {"goal_reached", "stalled"}


def test_max_ticks_guard() -> None:
    scenario = _scenario_by_name("max_ticks_guard")

    result = run_scenario(scenario)

    assert result.reason == "max_ticks"
