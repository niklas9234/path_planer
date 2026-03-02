from __future__ import annotations

from typing import TYPE_CHECKING

from core.domain import AddObstacle, AddZone, SetGoal

if TYPE_CHECKING:
    from core.experiments.scenarios import ScenarioDefinition
from core.planning import Planner
from core.planning.astar import NoPath
from core.simulation import EventBasedReplanPolicy, NoReplanPolicy, SimulationEngine, SimulationState, run_tick
from core.simulation.loop import RunResult


def build_engine_for_scenario(scenario: ScenarioDefinition) -> SimulationEngine:
    engine = SimulationEngine(
        SimulationState.create(
            width=scenario.width,
            height=scenario.height,
            robot_position=scenario.start,
        ),
    )
    engine.apply(SetGoal(goal=scenario.goal))
    for obstacle in scenario.initial_obstacles:
        engine.apply(AddObstacle(position=obstacle))
    return engine


def execute_scenario(
    scenario: ScenarioDefinition,
    planner: Planner,
    *,
    max_ticks: int,
) -> tuple[RunResult, SimulationEngine]:
    if max_ticks <= 0:
        raise ValueError(f"max_ticks must be > 0, got {max_ticks}.")

    engine = build_engine_for_scenario(scenario)
    replans = 0
    moves = 0

    replan_policy = EventBasedReplanPolicy()
    if scenario.replan_mode == "static_once":
        try:
            engine.replan(planner, reason="initial_static")
            replans += 1
        except NoPath:
            return (
                RunResult(
                    ticks_executed=engine.state.tick,
                    replans=1,
                    moves=0,
                    done=True,
                    reason="stalled",
                ),
                engine,
            )
        replan_policy = NoReplanPolicy()

    for _ in range(max_ticks):
        for obstacle in scenario.dynamic_obstacles_by_tick.get(engine.state.tick, ()):
            engine.apply(AddObstacle(position=obstacle))
        for zone_type, cells, duration_ticks, extra_cost in scenario.dynamic_zones_by_tick.get(engine.state.tick, ()):
            engine.apply(
                AddZone(
                    zone_type=zone_type,
                    cells=cells,
                    duration_ticks=duration_ticks,
                    extra_cost=extra_cost,
                ),
            )

        tick = run_tick(engine, planner, replan_policy=replan_policy)
        if tick.replanned:
            replans += 1
        if tick.moved:
            moves += 1

        if tick.done:
            return (
                RunResult(
                    ticks_executed=engine.state.tick,
                    replans=replans,
                    moves=moves,
                    done=True,
                    reason=tick.reason,
                ),
                engine,
            )

    return (
        RunResult(
            ticks_executed=engine.state.tick,
            replans=replans,
            moves=moves,
            done=False,
            reason="max_ticks",
        ),
        engine,
    )
