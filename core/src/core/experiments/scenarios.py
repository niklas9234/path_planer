from __future__ import annotations

from dataclasses import dataclass

from core.domain import AddObstacle, Position, SetGoal
from core.planning import Planner, plan
from core.simulation import (
    RunReason,
    RunResult,
    SimulationEngine,
    SimulationState,
    run_tick,
)


@dataclass(frozen=True, slots=True)
class ScenarioExpectation:
    allowed_reasons: tuple[RunReason, ...]
    min_moves: int = 0
    max_moves: int | None = None
    min_replans: int = 0


@dataclass(frozen=True, slots=True)
class ScenarioDefinition:
    name: str
    width: int
    height: int
    start: Position
    goal: Position
    initial_obstacles: tuple[Position, ...]
    max_ticks: int
    dynamic_obstacles_by_tick: dict[int, tuple[Position, ...]]
    expectation: ScenarioExpectation


def _make_engine(scenario: ScenarioDefinition) -> SimulationEngine:
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


def run_scenario(scenario: ScenarioDefinition, planner: Planner = plan) -> RunResult:
    if scenario.max_ticks <= 0:
        raise ValueError(f"max_ticks must be > 0, got {scenario.max_ticks}.")

    engine = _make_engine(scenario)

    replans = 0
    moves = 0

    for _ in range(scenario.max_ticks):
        for obstacle in scenario.dynamic_obstacles_by_tick.get(engine.state.tick, ()):
            engine.apply(AddObstacle(position=obstacle))

        tick = run_tick(engine, planner)
        if tick.replanned:
            replans += 1
        if tick.moved:
            moves += 1

        if tick.done:
            return RunResult(
                ticks_executed=engine.state.tick,
                replans=replans,
                moves=moves,
                done=True,
                reason=tick.reason,
            )

    return RunResult(
        ticks_executed=engine.state.tick,
        replans=replans,
        moves=moves,
        done=False,
        reason="max_ticks",
    )


def required_scenarios() -> tuple[ScenarioDefinition, ...]:
    return (
        ScenarioDefinition(
            name="empty_world_reaches_goal",
            width=5,
            height=5,
            start=Position(0, 0),
            goal=Position(4, 4),
            initial_obstacles=(),
            max_ticks=20,
            dynamic_obstacles_by_tick={},
            expectation=ScenarioExpectation(
                allowed_reasons=("goal_reached",),
                min_moves=1,
            ),
        ),
        ScenarioDefinition(
            name="blocked_goal_stalls",
            width=3,
            height=3,
            start=Position(0, 0),
            goal=Position(2, 2),
            initial_obstacles=(
                Position(1, 1),
                Position(1, 0),
                Position(0, 1),
            ),
            max_ticks=10,
            dynamic_obstacles_by_tick={},
            expectation=ScenarioExpectation(
                allowed_reasons=("stalled",),
                min_moves=0,
                max_moves=0,
            ),
        ),
        ScenarioDefinition(
            name="replan_after_obstacle",
            width=5,
            height=3,
            start=Position(0, 0),
            goal=Position(4, 0),
            initial_obstacles=(),
            max_ticks=20,
            dynamic_obstacles_by_tick={
                1: (Position(2, 0),),
            },
            expectation=ScenarioExpectation(
                allowed_reasons=("goal_reached", "stalled"),
                min_replans=1,
            ),
        ),
        ScenarioDefinition(
            name="max_ticks_guard",
            width=5,
            height=5,
            start=Position(0, 0),
            goal=Position(4, 4),
            initial_obstacles=(),
            max_ticks=1,
            dynamic_obstacles_by_tick={},
            expectation=ScenarioExpectation(
                allowed_reasons=("max_ticks",),
            ),
        ),
    )


__all__ = [
    "ScenarioDefinition",
    "ScenarioExpectation",
    "required_scenarios",
    "run_scenario",
]
