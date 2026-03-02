from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

from core.domain import AddObstacle, AddZone, SetGoal

if TYPE_CHECKING:
    from core.experiments.scenarios import ScenarioDefinition
from core.planning import Planner
from core.planning.astar import NoPath
from core.simulation import (
    EventBasedReplanPolicy,
    NoReplanPolicy,
    PathAffectedReplanPolicy,
    PeriodicReplanPolicy,
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
    policy_name: str | None = None,
    policy_params: Mapping[str, object] | None = None,
) -> tuple[RunResult, SimulationEngine]:
    effective_policy_name = policy_name or scenario.policy_name
    effective_policy_params = {**scenario.policy_params, **(dict(policy_params or {}))}
    replan_policy = _policy_from_name(effective_policy_name, effective_policy_params)

    return run_once(
        scenario,
        policy=replan_policy,
        planner=planner,
        max_ticks=max_ticks,
        policy_name=effective_policy_name,
    )

def _policy_from_name(policy_name: str, policy_params: Mapping[str, object]) -> ReplanPolicy:
    if policy_name == "static_once":
        return NoReplanPolicy()
    if policy_name == "event_based":
        return EventBasedReplanPolicy()
    if policy_name == "periodic":
        interval = int(policy_params.get("interval", 1))
        return PeriodicReplanPolicy(interval_ticks=interval)
    if policy_name == "path_affected":
        threshold = float(policy_params.get("cost_delta_threshold", 0.0))
        return PathAffectedReplanPolicy(cost_delta_threshold=threshold)

    raise ValueError(f"Unsupported policy_name '{policy_name}'.")

def run_once(
    scenario: ScenarioDefinition,
    policy: ReplanPolicy,
    planner: Planner,
    max_ticks: int,
    policy_name: str | None = None,
) -> tuple[RunResult, SimulationEngine]:
    if max_ticks <= 0:
        raise ValueError(f"max_ticks must be > 0, got {max_ticks}.")

    engine = build_engine_for_scenario(scenario)
    replans = 0
    moves = 0

    resolved_policy_name = policy_name or scenario.policy_name

    if resolved_policy_name == "static_once":
        try:
            engine.replan(planner, reason="initial_static")
            replans += 1
        except NoPath:
            return (
                RunResult(
                    scenario_name=scenario.name,
                    policy_name=resolved_policy_name,
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
                    policy_name=resolved_policy_name,
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
            policy_name=resolved_policy_name,
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
