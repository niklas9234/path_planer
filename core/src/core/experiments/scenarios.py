from __future__ import annotations

from dataclasses import dataclass

from core.domain import Position
from core.experiments.execution import execute_scenario
from core.planning import Planner, plan
from core.simulation import (
    RunReason,
    RunResult,
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


def run_scenario(scenario: ScenarioDefinition, planner: Planner = plan) -> RunResult:
    result, _ = execute_scenario(scenario, planner, max_ticks=scenario.max_ticks)
    return result


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
