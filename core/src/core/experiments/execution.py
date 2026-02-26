from __future__ import annotations

from typing import TYPE_CHECKING

from core.domain import AddObstacle, SetGoal

if TYPE_CHECKING:
    from core.experiments.scenarios import ScenarioDefinition
from core.planning import Planner
from core.simulation import SimulationEngine, SimulationState, run_tick
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

    for _ in range(max_ticks):
        for obstacle in scenario.dynamic_obstacles_by_tick.get(engine.state.tick, ()):
            engine.apply(AddObstacle(position=obstacle))

        tick = run_tick(engine, planner)
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
