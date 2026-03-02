from __future__ import annotations

from core.domain import AddObstacle, Position
from core.experiments import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
    required_scenarios,
    run_scenario,
)


def _scenario_by_name(name: str):
    scenarios = {scenario.name: scenario for scenario in required_scenarios()}
    return scenarios[name]


def test_required_scenarios_define_policy_name() -> None:
    scenarios = required_scenarios()

    assert scenarios
    assert all(scenario.policy_name for scenario in scenarios)


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


def test_temporary_slow_zone_expires() -> None:
    scenario = _scenario_by_name("temporary_slow_zone_expires")

    result = run_scenario(scenario)

    assert result.reason == "goal_reached"
    assert result.replans >= 1


def test_policy_name_static_once_vs_event_based() -> None:
    base_kwargs = dict(
        world_config=WorldConfig(width=5, height=3),
        start=Position(0, 0),
        goal=Position(4, 0),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=20,
        scheduled_events={1: (AddObstacle(position=Position(0, 2)),)},
        expectation=ScenarioExpectation(allowed_reasons=("goal_reached", "stalled")),
    )
    dynamic_scenario = ScenarioDefinition(
        name="pair_event_based",
        policy_name="event_based",
        **base_kwargs,
    )
    static_scenario = ScenarioDefinition(
        name="pair_static_once",
        policy_name="static_once",
        **base_kwargs,
    )

    dynamic_result = run_scenario(dynamic_scenario)
    static_result = run_scenario(static_scenario)

    assert dynamic_result.replans != static_result.replans

    dynamic_result_repeat = run_scenario(dynamic_scenario)
    static_result_repeat = run_scenario(static_scenario)

    assert dynamic_result == dynamic_result_repeat
    assert static_result == static_result_repeat


def test_replan_mode_deprecated_mapping_and_policy_name_precedence() -> None:
    mapped = ScenarioDefinition(
        name="mapped_from_replan_mode",
        policy_name="",
        replan_mode="static_once",
        world_config=WorldConfig(width=3, height=3),
        start=Position(0, 0),
        goal=Position(2, 2),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=5,
        scheduled_events={},
        expectation=ScenarioExpectation(allowed_reasons=("goal_reached", "stalled", "max_ticks")),
    )
    assert mapped.policy_name == "static_once"

    precedence = ScenarioDefinition(
        name="policy_name_wins",
        policy_name="event_based",
        replan_mode="static_once",
        world_config=WorldConfig(width=3, height=3),
        start=Position(0, 0),
        goal=Position(2, 2),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=5,
        scheduled_events={},
        expectation=ScenarioExpectation(allowed_reasons=("goal_reached", "stalled", "max_ticks")),
    )
    assert precedence.policy_name == "event_based"
