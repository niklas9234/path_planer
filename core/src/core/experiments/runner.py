from __future__ import annotations

import random
from dataclasses import dataclass

from core.domain.events import AddObstacle, SetGoal
from core.metrics.recorder import RunMetricsRecorder
from core.planning.astar import plan
from core.planning.interface import Planner
from core.simulation.engine import SimulationEngine
from core.simulation.loop import RunReason, run_tick
from core.simulation.state import SimulationState

from .scenarios import ScenarioDefinition, required_scenarios


@dataclass(frozen=True, slots=True)
class ScenarioRunSummary:
    scenario: str
    planner: str
    seed: int
    goal_reached: bool
    reason: RunReason
    ticks_executed: int
    replans: int
    moves: int
    total_cost: float


@dataclass(frozen=True, slots=True)
class ScenarioRunOutput:
    summary: ScenarioRunSummary
    tick_metrics: list[dict[str, object]]
    snapshot: dict[str, object]


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


def _snapshot(engine: SimulationEngine) -> dict[str, object]:
    blocked = [
        [int(engine.state.world.blocked[y][x]) for x in range(engine.state.world.width)]
        for y in range(engine.state.world.height)
    ]
    return {
        "tick": engine.state.tick,
        "robot": {
            "position": [engine.state.robot.position.x, engine.state.robot.position.y],
            "goal": [engine.state.robot.goal.x, engine.state.robot.goal.y]
            if engine.state.robot.goal is not None
            else None,
        },
        "world": {
            "width": engine.state.world.width,
            "height": engine.state.world.height,
            "blocked": blocked,
        },
    }


def _resolve_planner(planner: str | Planner) -> tuple[str, Planner]:
    if callable(planner):
        return getattr(planner, "__name__", "custom"), planner

    planners: dict[str, Planner] = {
        "astar": plan,
    }
    if planner not in planners:
        allowed = ", ".join(sorted(planners))
        raise ValueError(f"Unknown planner '{planner}'. Allowed values: {allowed}.")
    return planner, planners[planner]


def run_scenario_experiment(
    *,
    scenario_name: str,
    seed: int,
    planner: str | Planner = "astar",
    max_ticks: int | None = None,
    include_tick_data: bool = True,
) -> ScenarioRunOutput:
    random.seed(seed)

    scenarios = {scenario.name: scenario for scenario in required_scenarios()}
    if scenario_name not in scenarios:
        available = ", ".join(sorted(scenarios))
        raise ValueError(f"Unknown scenario '{scenario_name}'. Available: {available}.")

    scenario = scenarios[scenario_name]
    effective_max_ticks = scenario.max_ticks if max_ticks is None else max_ticks
    if effective_max_ticks <= 0:
        raise ValueError(f"max_ticks must be > 0, got {effective_max_ticks}.")

    planner_name, planner_fn = _resolve_planner(planner)

    engine = _make_engine(scenario)
    recorder = RunMetricsRecorder()

    replans = 0
    moves = 0
    done = False
    reason: RunReason = "max_ticks"

    for _ in range(effective_max_ticks):
        for obstacle in scenario.dynamic_obstacles_by_tick.get(engine.state.tick, ()):
            engine.apply(AddObstacle(position=obstacle))

        previous_position = engine.state.robot.position
        tick = run_tick(engine, planner_fn)

        if tick.replanned:
            replans += 1
        if tick.moved:
            moves += 1

        recorder.record_tick(
            tick=engine.state.tick,
            world=engine.state.world,
            previous_position=previous_position,
            current_position=engine.state.robot.position,
            moved=tick.moved,
            replanned=tick.replanned,
            at_goal=tick.at_goal,
            reason=tick.reason,
        )

        if tick.done:
            done = True
            reason = tick.reason
            break

    if not done:
        reason = "max_ticks"

    summary = ScenarioRunSummary(
        scenario=scenario_name,
        planner=planner_name,
        seed=seed,
        goal_reached=reason == "goal_reached",
        reason=reason,
        ticks_executed=engine.state.tick,
        replans=replans,
        moves=moves,
        total_cost=recorder.total_cost,
    )

    return ScenarioRunOutput(
        summary=summary,
        tick_metrics=recorder.ticks_as_dict() if include_tick_data else [],
        snapshot=_snapshot(engine),
    )
