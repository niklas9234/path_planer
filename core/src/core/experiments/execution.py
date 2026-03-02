from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

from core.domain import AddObstacle, AddZone, SetGoal

if TYPE_CHECKING:
    from core.experiments.scenarios import ScenarioDefinition
from core.planning import Planner
from core.planning.astar import NoPath
from core.simulation import ReplanPolicy, SimulationEngine, SimulationState
from core.simulation.replan_policy import make_policy
from core.simulation.loop import RunResult, run_until_done


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
    replan_policy = make_policy(effective_policy_name, dict(effective_policy_params))

    return run_once(
        scenario,
        policy=replan_policy,
        planner=planner,
        max_ticks=max_ticks,
        policy_name=effective_policy_name,
        policy_params=effective_policy_params,
    )

def run_once(
    scenario: ScenarioDefinition,
    policy: ReplanPolicy,
    planner: Planner,
    max_ticks: int,
    policy_name: str | None = None,
    policy_params: Mapping[str, object] | None = None,
) -> tuple[RunResult, SimulationEngine]:
    if max_ticks <= 0:
        raise ValueError(f"max_ticks must be > 0, got {max_ticks}.")

    engine = build_engine_for_scenario(scenario)
    replans = 0
    moves = 0

    resolved_policy_name = policy_name or scenario.policy_name
    resolved_policy_params = dict(policy_params or scenario.policy_params)

    if resolved_policy_name == "static_once":
        try:
            engine.replan(planner, reason="initial_static")
            replans += 1
        except NoPath:
            engine.state.metrics.on_done(
                tick=engine.state.tick,
                world=engine.state.world,
                robot=engine.state.robot,
                reason="stalled",
            )
            return (
                RunResult(
                    scenario_name=scenario.name,
                    policy_name=resolved_policy_name,
                    policy_params=resolved_policy_params,
                    seed=None,
                    ticks_executed=engine.state.tick,
                    replans=replans,
                    moves=moves,
                    done=True,
                    reason="stalled",
                    goal_reached=False,
                    stalled=True,
                ),
                engine,
            )

        moved = engine.step()
        if moved:
            moves += 1

        at_goal = engine.state.robot.at_goal()
        if at_goal:
            engine.state.metrics.on_done(
                tick=engine.state.tick,
                world=engine.state.world,
                robot=engine.state.robot,
                reason="goal_reached",
            )
            return (
                RunResult(
                    scenario_name=scenario.name,
                    policy_name=resolved_policy_name,
                    policy_params=resolved_policy_params,
                    seed=None,
                    ticks_executed=engine.state.tick,
                    replans=replans,
                    moves=moves,
                    done=True,
                    reason="goal_reached",
                    goal_reached=True,
                    stalled=False,
                ),
                engine,
            )

        if not moved:
            engine.state.metrics.on_done(
                tick=engine.state.tick,
                world=engine.state.world,
                robot=engine.state.robot,
                reason="stalled",
            )
            return (
                RunResult(
                    scenario_name=scenario.name,
                    policy_name=resolved_policy_name,
                    policy_params=resolved_policy_params,
                    seed=None,
                    ticks_executed=engine.state.tick,
                    replans=replans,
                    moves=moves,
                    done=True,
                    reason="stalled",
                    goal_reached=False,
                    stalled=True,
                ),
                engine,
            )

    return (
        run_until_done(
            engine,
            planner,
            max_ticks=max_ticks,
            replan_policy=policy,
            scenario_name=scenario.name,
            policy_name=resolved_policy_name,
            policy_params=resolved_policy_params,
            seed=None,
        ),
        engine,
    )
