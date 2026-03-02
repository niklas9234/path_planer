from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.domain import AddObstacle, AddZone, DomainEvent, Position, ZoneType
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
    world_config: WorldConfig
    start: Position
    goal: Position
    initial_obstacles: tuple[Position, ...]
    initial_zones: tuple[ZoneDefinition, ...]
    max_ticks: int
    scheduled_events: dict[int, tuple[DomainEvent, ...]]
    expectation: ScenarioExpectation
    replan_mode: Literal["dynamic_event", "static_once"] = "dynamic_event"


@dataclass(frozen=True, slots=True)
class WorldConfig:
    width: int
    height: int
    base_cost: float = 1.0
    cell_size_m: float = 1.0


@dataclass(frozen=True, slots=True)
class ZoneDefinition:
    zone_type: ZoneType
    cells: tuple[Position, ...]
    duration_ticks: int | None = None
    extra_cost: float = 0.0


def run_scenario(scenario: ScenarioDefinition, planner: Planner = plan) -> RunResult:
    result, _ = execute_scenario(scenario, planner, max_ticks=scenario.max_ticks)
    return result


def required_scenarios() -> tuple[ScenarioDefinition, ...]:
    return (
        ScenarioDefinition(
            name="empty_world_reaches_goal",
            world_config=WorldConfig(width=5, height=5),
            start=Position(0, 0),
            goal=Position(4, 4),
            initial_obstacles=(),
            initial_zones=(),
            max_ticks=20,
            scheduled_events={},
            expectation=ScenarioExpectation(
                allowed_reasons=("goal_reached",),
                min_moves=1,
            ),
        ),
        ScenarioDefinition(
            name="blocked_goal_stalls",
            world_config=WorldConfig(width=3, height=3),
            start=Position(0, 0),
            goal=Position(2, 2),
            initial_obstacles=(
                Position(1, 1),
                Position(1, 0),
                Position(0, 1),
            ),
            initial_zones=(),
            max_ticks=10,
            scheduled_events={},
            expectation=ScenarioExpectation(
                allowed_reasons=("stalled",),
                min_moves=0,
                max_moves=0,
            ),
        ),
        ScenarioDefinition(
            name="replan_after_obstacle",
            world_config=WorldConfig(width=5, height=3),
            start=Position(0, 0),
            goal=Position(4, 0),
            initial_obstacles=(),
            initial_zones=(),
            max_ticks=20,
            scheduled_events={1: (AddObstacle(position=Position(2, 0)),)},
            expectation=ScenarioExpectation(
                allowed_reasons=("goal_reached", "stalled"),
                min_replans=1,
            ),
        ),
        ScenarioDefinition(
            name="temporary_slow_zone_expires",
            world_config=WorldConfig(width=6, height=3),
            start=Position(0, 1),
            goal=Position(5, 1),
            initial_obstacles=(),
            initial_zones=(),
            max_ticks=20,
            scheduled_events={
                0: (
                    AddZone(
                        zone_type=ZoneType.SLOW,
                        cells=(Position(1, 1), Position(2, 1)),
                        duration_ticks=2,
                        extra_cost=3.0,
                    ),
                ),
            },
            expectation=ScenarioExpectation(
                allowed_reasons=("goal_reached",),
                min_replans=1,
            ),
        ),
        ScenarioDefinition(
            name="max_ticks_guard",
            world_config=WorldConfig(width=5, height=5),
            start=Position(0, 0),
            goal=Position(4, 4),
            initial_obstacles=(),
            initial_zones=(),
            max_ticks=1,
            scheduled_events={},
            expectation=ScenarioExpectation(
                allowed_reasons=("max_ticks",),
            ),
        ),
        ScenarioDefinition(
            name="testpath_20x20_image_map",
            world_config=WorldConfig(width=20, height=20),
            start=Position(3, 19),
            goal=Position(12, 0),
            initial_obstacles=(
                Position(3, 0),
                Position(7, 0),
                Position(13, 0),
                Position(7, 1),
                Position(7, 2),
                Position(13, 2),
                Position(17, 2),
                Position(7, 3),
                Position(19, 3),
                Position(3, 4),
                Position(4, 5),
                Position(19, 5),
                Position(5, 6),
                Position(14, 6),
                Position(6, 7),
                Position(10, 7),
                Position(13, 7),
                Position(6, 8),
                Position(11, 8),
                Position(0, 9),
                Position(1, 9),
                Position(2, 9),
                Position(7, 9),
                Position(3, 10),
                Position(8, 10),
                Position(4, 11),
                Position(15, 11),
                Position(16, 12),
                Position(17, 13),
                Position(7, 14),
                Position(13, 14),
                Position(19, 14),
                Position(4, 15),
                Position(8, 15),
                Position(14, 15),
                Position(5, 16),
                Position(14, 16),
                Position(6, 17),
                Position(14, 17),
                Position(12, 18),
                Position(13, 18),
                Position(12, 19),
            ),
            initial_zones=(
                ZoneDefinition(zone_type=ZoneType.SLOW, cells=(Position(3, 1), Position(3, 2), Position(3, 3)), extra_cost=3.0),
                ZoneDefinition(zone_type=ZoneType.SLOW, cells=(Position(7, 4),), extra_cost=3.0),
                ZoneDefinition(zone_type=ZoneType.SLOW, cells=(Position(9, 5), Position(10, 6)), extra_cost=3.0),
                ZoneDefinition(zone_type=ZoneType.SLOW, cells=(Position(15, 5), Position(16, 5), Position(17, 5), Position(18, 5)), extra_cost=3.0),
                ZoneDefinition(zone_type=ZoneType.SLOW, cells=(Position(14, 2), Position(15, 2), Position(16, 2)), extra_cost=3.0),
                ZoneDefinition(zone_type=ZoneType.SLOW, cells=(Position(3, 8), Position(4, 8), Position(5, 8)), extra_cost=3.0),
                ZoneDefinition(zone_type=ZoneType.SLOW, cells=(Position(10, 11), Position(11, 12), Position(12, 13)), extra_cost=3.0),
                ZoneDefinition(zone_type=ZoneType.SLOW, cells=(Position(10, 16), Position(11, 17)), extra_cost=3.0),
            ),
            max_ticks=400,
            scheduled_events={
                8: (AddZone(zone_type=ZoneType.SLOW, cells=(Position(14, 1), Position(15, 1), Position(16, 1)), duration_ticks=8, extra_cost=5.0),),
                9: (AddObstacle(position=Position(15, 2)),),
            },
            expectation=ScenarioExpectation(
                allowed_reasons=("goal_reached", "stalled", "max_ticks"),
                min_moves=0,
                min_replans=1,
            ),
        ),
    )


__all__ = [
    "ScenarioDefinition",
    "ScenarioExpectation",
    "WorldConfig",
    "ZoneDefinition",
    "required_scenarios",
    "run_scenario",
]
