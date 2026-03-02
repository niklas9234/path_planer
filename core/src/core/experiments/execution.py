from __future__ import annotations

from typing import TYPE_CHECKING

from core.domain import AddObstacle, AddZone, SetGoal

if TYPE_CHECKING:
    from core.experiments.scenarios import ScenarioDefinition
from core.planning import Planner
from core.planning.astar import NoPath
from core.simulation import (
    PolicyContext,
    ReplanPolicy,
    SimulationEngine,
    SimulationState,
    make_policy,
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
    policy_name = scenario.replan_mode
    replan_policy: ReplanPolicy = make_policy(policy_name)

    return run_once(
        scenario,
        policy=replan_policy,
        planner=planner,
        max_ticks=max_ticks,
    )


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

    for _ in range(max_ticks):
        for event in scenario.scheduled_events.get(engine.state.tick, ()):
            engine.apply(event)

        obstacle_cells, cost_cells = engine.process_tick_updates()
        engine.state.metrics.on_tick_start(
            tick=engine.state.tick,
            world=engine.state.world,
            robot=engine.state.robot,
            zone_expired_obstacle_cells=obstacle_cells,
            zone_expired_cost_cells=cost_cells,
        )

        decision = policy.decide(PolicyContext.from_state(engine.state))
        if decision.replan:
            try:
                replanned = engine.replan(planner, reason=decision.reason)
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
                        policy_name=type(policy).__name__,
                        seed=None,
                        ticks_executed=engine.state.tick,
                        replans=replans + 1,
                        moves=moves,
                        done=True,
                        reason="stalled",
                        goal_reached=False,
                        stalled=True,
                    ),
                    engine,
                )
        else:
            replanned = False
            engine.state.metrics.on_replan(
                tick=engine.state.tick,
                replanned=False,
                found_path=bool(engine.state.robot.path),
                world=engine.state.world,
                robot=engine.state.robot,
                reason=None,
            )

        if replanned:
            replans += 1

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
                    policy_name=type(policy).__name__,
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
                    policy_name=type(policy).__name__,
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
