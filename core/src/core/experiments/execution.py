from __future__ import annotations

from typing import TYPE_CHECKING

from core.domain import AddObstacle, AddZone, SetGoal

if TYPE_CHECKING:
    from core.experiments.scenarios import ScenarioDefinition
from core.planning import Planner
from core.planning.astar import NoPath
from core.simulation import (
    EventBasedReplanPolicy,
    NoReplanPolicy,
    ReplanPolicy,
    SimulationEngine,
    SimulationState,
    run_tick,
)
from core.simulation.loop import RunResult


def build_engine_for_scenario(scenario: ScenarioDefinition) -> SimulationEngine:
    engine = SimulationEngine(
        SimulationState.create(
            width=scenario.world_config.width,
            height=scenario.world_config.height,
            robot_position=scenario.start,
            cell_size_m=scenario.world_config.cell_size_m,
            base_cost=scenario.world_config.base_cost,
        ),
    )
    engine.apply(SetGoal(goal=scenario.goal))
    for obstacle in scenario.initial_obstacles:
        engine.apply(AddObstacle(position=obstacle))
    for zone in scenario.initial_zones:
        engine.apply(
            AddZone(
                zone_type=zone.zone_type,
                cells=zone.cells,
                duration_ticks=zone.duration_ticks,
                extra_cost=zone.extra_cost,
            ),
        )
    return engine


def execute_scenario(
    scenario: ScenarioDefinition,
    planner: Planner,
    *,
    max_ticks: int,
) -> tuple[RunResult, SimulationEngine]:
    replan_policy = _policy_from_scenario(scenario)

    return run_once(
        scenario,
        policy=replan_policy,
        planner=planner,
        max_ticks=max_ticks,
    )




def _policy_from_scenario(scenario: ScenarioDefinition) -> ReplanPolicy:
    policy_name = scenario.policy_name
    if scenario.replan_mode is not None and not policy_name:
        policy_name = "static_once" if scenario.replan_mode == "static_once" else "event_based"

    if policy_name == "static_once":
        return NoReplanPolicy()
    if policy_name == "event_based":
        return EventBasedReplanPolicy()

    raise ValueError(f"Unsupported policy_name '{scenario.policy_name}' for scenario '{scenario.name}'.")

def run_once(
    scenario: ScenarioDefinition,
    policy: ReplanPolicy,
    planner: Planner,
    max_ticks: int,
) -> tuple[RunResult, SimulationEngine]:
    if max_ticks <= 0:
        raise ValueError(f"max_ticks must be > 0, got {max_ticks}.")

    engine = build_engine_for_scenario(scenario)
    replans = 0
    moves = 0

    if scenario.policy_name == "static_once":
        try:
            engine.replan(planner, reason="initial_static")
            replans += 1
        except NoPath:
            return (
                RunResult(
                    scenario_name=scenario.name,
                    policy_name=type(policy).__name__,
                    seed=None,
                    ticks_executed=engine.state.tick,
                    replans=1,
                    moves=0,
                    done=True,
                    reason="stalled",
                    goal_reached=False,
                    stalled=True,
                ),
                engine,
            )

    for _ in range(max_ticks):
        for event in scenario.scheduled_events.get(engine.state.tick, ()):
            engine.apply(event)

        tick = run_tick(engine, planner, replan_policy=policy)
        if tick.replanned:
            replans += 1
        if tick.moved:
            moves += 1

        if tick.done:
            return (
                RunResult(
                    scenario_name=scenario.name,
                    policy_name=type(policy).__name__,
                    seed=None,
                    ticks_executed=engine.state.tick,
                    replans=replans,
                    moves=moves,
                    done=True,
                    reason=tick.reason,
                    goal_reached=tick.reason == "goal_reached",
                    stalled=tick.reason == "stalled",
                ),
                engine,
            )

    return (
        RunResult(
            scenario_name=scenario.name,
            policy_name=type(policy).__name__,
            seed=None,
            ticks_executed=engine.state.tick,
            replans=replans,
            moves=moves,
            done=False,
            reason="max_ticks",
            goal_reached=False,
            stalled=False,
        ),
        engine,
    )
