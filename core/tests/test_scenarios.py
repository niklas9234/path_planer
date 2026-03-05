from __future__ import annotations

from core.domain import AddObstacle, Position
from core.experiments import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
    required_scenarios,
    run_scenario,
)

EXPECTED_SCENARIOS = {
    "s01_corridor_baseline",
    "s02_corridor_static",
    "s03_long_slow_zone_corridor",
    "s04_short_slow_zone_corridor",
    "s05_dynamic_obstacle_corridor",
    "s06_dynamic_zone_then_block",
}


def _scenario_by_name(name: str):
    scenarios = {scenario.name: scenario for scenario in required_scenarios()}
    return scenarios[name]


def test_required_scenarios_define_policy_name() -> None:
    scenarios = required_scenarios()

    assert scenarios
    assert all(scenario.policy_name for scenario in scenarios)


def test_required_scenarios_match_bachelor_scenario_set() -> None:
    names = {scenario.name for scenario in required_scenarios()}

    assert names == EXPECTED_SCENARIOS


def test_s01_corridor_baseline_reaches_goal() -> None:
    scenario = _scenario_by_name("s01_corridor_baseline")

    result = run_scenario(scenario)

    assert result.reason == "goal_reached"
    assert result.moves > 0


def test_s05_dynamic_obstacle_triggers_replans() -> None:
    scenario = _scenario_by_name("s05_dynamic_obstacle_corridor")

    result = run_scenario(scenario)

    assert result.replans >= 1
    assert result.reason in {"goal_reached", "stalled", "max_ticks"}


def test_s06_dynamic_zone_then_block_runs_to_terminal_reason() -> None:
    scenario = _scenario_by_name("s06_dynamic_zone_then_block")

    result = run_scenario(scenario)

    assert result.reason in {"goal_reached", "stalled", "max_ticks"}


def test_static_once_includes_initial_replan() -> None:
    scenario = ScenarioDefinition(
        name="static_once_initial_replan",
        world_config=WorldConfig(width=5, height=3),
        start=Position(0, 0),
        goal=Position(4, 0),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=20,
        scheduled_events={},
        expectation=ScenarioExpectation(allowed_reasons=("goal_reached", "stalled")),
        replan_mode="static_once",
    )

    result = run_scenario(scenario)

    assert result.replans == 1


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
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks")
        ),
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
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks")
        ),
    )
    assert precedence.policy_name == "event_based"
