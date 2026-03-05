from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from core.domain import AddObstacle, AddZone, SetGoal

if TYPE_CHECKING:
    from core.experiments.scenarios import ScenarioDefinition
from core.planning import Planner
from core.planning.astar import NoPath
from core.simulation import ReplanPolicy, SimulationEngine, SimulationState, make_policy
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
    resolved_policy_name = policy_name or scenario.policy_name
    resolved_policy_params = dict(policy_params or scenario.policy_params)
    policy_impl_module = type(policy).__module__

    replans = 0
    moves = 0

    for _ in range(max_ticks):
        for event in scenario.scheduled_events.get(
            engine.state.tick, ()
        ):  # apply at current tick
            engine.apply(event)

        engine.process_tick_updates()
        should_replan, replan_reason = policy.should_replan(engine.state)

        if should_replan:
            try:
                replanned = engine.replan(planner, reason=replan_reason)
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
                        policy_impl_module=policy_impl_module,
                        seed=None,
                        ticks_executed=engine.state.tick,
                        replans=replans + 1,
                        moves=moves,
                        done=True,
                        reason="stalled",
                        goal_reached=False,
                        stalled=True,
                        run_metrics=engine.state.metrics.finalize_run_metrics(),
                    ),
                    engine,
                )
            if replanned:
                replans += 1

        moved = engine.step()
        if moved:
            moves += 1

        if engine.state.robot.at_goal():
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
                    policy_impl_module=policy_impl_module,
                    seed=None,
                    ticks_executed=engine.state.tick,
                    replans=replans,
                    moves=moves,
                    done=True,
                    reason="goal_reached",
                    goal_reached=True,
                    stalled=False,
                    run_metrics=engine.state.metrics.finalize_run_metrics(),
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
                    policy_impl_module=policy_impl_module,
                    seed=None,
                    ticks_executed=engine.state.tick,
                    replans=replans,
                    moves=moves,
                    done=True,
                    reason="stalled",
                    goal_reached=False,
                    stalled=True,
                    run_metrics=engine.state.metrics.finalize_run_metrics(),
                ),
                engine,
            )

    engine.state.metrics.on_done(
        tick=engine.state.tick,
        world=engine.state.world,
        robot=engine.state.robot,
        reason="max_ticks",
    )
    return (
        RunResult(
            scenario_name=scenario.name,
            policy_name=resolved_policy_name,
            policy_params=resolved_policy_params,
            policy_impl_module=policy_impl_module,
            seed=None,
            ticks_executed=engine.state.tick,
            replans=replans,
            moves=moves,
            done=False,
            reason="max_ticks",
            goal_reached=False,
            stalled=False,
            run_metrics=engine.state.metrics.finalize_run_metrics(),
        ),
        engine,
    )
