from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from core.experiments.execution import execute_scenario
from core.experiments.results import ExperimentResult
from core.experiments.run_context import RunContext
from core.experiments.scenarios import ScenarioDefinition, required_scenarios
from core.metrics.measures import from_run_result
from core.metrics.recorder import TickMetrics
from core.planning import plan
from core.protocol.snapshots import SimulationSnapshot, SnapshotMeta
from core.simulation import SimulationEngine
from core.simulation.loop import RunResult


def _load_core_version() -> str:
    version_file = Path(__file__).resolve().parents[4] / "shared" / "protocol" / "VERSION"
    return version_file.read_text(encoding="utf-8").strip()


@dataclass(frozen=True, slots=True)
class CliRunSummary:
    scenario: str
    seed: int
    planner: str
    ticks_executed: int
    replans: int
    moves: int
    reason: str
    goal_reached: bool
    total_cost: float


@dataclass(frozen=True, slots=True)
class ScenarioExperimentResult:
    summary: CliRunSummary
    tick_metrics: list[dict[str, int | float | bool | str | None]]
    snapshot: dict[str, object]


def _scenario_by_name(name: str) -> ScenarioDefinition:
    scenarios = {scenario.name: scenario for scenario in required_scenarios()}
    try:
        return scenarios[name]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario: {name}") from exc


def _run_scenario_with_engine(
    scenario: ScenarioDefinition,
    *,
    max_ticks: int | None,
) -> tuple[RunResult, SimulationEngine]:
    tick_budget = scenario.max_ticks if max_ticks is None else max_ticks
    return execute_scenario(scenario, plan, max_ticks=tick_budget)


def _tick_to_dict(item: TickMetrics) -> dict[str, int | float | bool | str | None]:
    return {
        "tick": item.tick,
        "replan_count": item.replan_count,
        "replan_trigger_reason": item.replan_trigger_reason,
        "path_length_current": item.path_length_current,
        "path_cost_current": item.path_cost_current,
        "steps_taken": item.steps_taken,
        "goal_reached": item.goal_reached,
        "ticks_to_goal": item.ticks_to_goal,
        "no_path_events": item.no_path_events,
        "obstacle_changes": item.obstacle_changes,
    }


def run_scenario_experiment(
    *,
    scenario_name: str,
    seed: int,
    planner: str = "astar",
    max_ticks: int | None = None,
    include_tick_data: bool = False,
) -> ScenarioExperimentResult:
    random.seed(seed)
    if planner != "astar":
        raise ValueError(f"Unsupported planner: {planner}")

    scenario = _scenario_by_name(scenario_name)
    run_result, engine = _run_scenario_with_engine(scenario, max_ticks=max_ticks)
    finalized = engine.state.metrics.finalize_run_metrics()

    summary = CliRunSummary(
        scenario=scenario.name,
        seed=seed,
        planner=planner,
        ticks_executed=run_result.ticks_executed,
        replans=run_result.replans,
        moves=run_result.moves,
        reason=run_result.reason,
        goal_reached=run_result.reason == "goal_reached",
        total_cost=float(finalized.get("steps_taken", 0)),
    )

    tick_metrics = [_tick_to_dict(item) for item in engine.state.metrics.ticks if item.tick > 0]

    snapshot: dict[str, object] = {
        "meta": {"tick": run_result.ticks_executed, "scenario": scenario.name, "seed": seed},
        "world": {"width": scenario.width, "height": scenario.height},
        "robot": {
            "position": {"x": engine.state.robot.position.x, "y": engine.state.robot.position.y},
            "goal": None
            if engine.state.robot.goal is None
            else {"x": engine.state.robot.goal.x, "y": engine.state.robot.goal.y},
        },
    }

    return ScenarioExperimentResult(
        summary=summary,
        tick_metrics=tick_metrics if include_tick_data else [],
        snapshot=snapshot,
    )


def run_experiment(
    scenario: ScenarioDefinition,
    *,
    seed: int,
    planner_name: str = "astar",
    planner_params: Mapping[str, Any] | None = None,
    world_params: Mapping[str, Any] | None = None,
    recorder: object | None = None,
) -> ExperimentResult:
    del recorder
    random.seed(seed)

    context = RunContext.create(
        scenario_name=scenario.name,
        seed=seed,
        planner_name=planner_name,
        planner_params=planner_params,
        world_params=world_params,
        core_version=_load_core_version(),
    )

    if planner_name != "astar":
        raise ValueError(f"Unsupported planner_name: {planner_name}")

    run_result, engine = _run_scenario_with_engine(scenario, max_ticks=None)
    metrics = from_run_result(context, run_result)

    snapshot = SimulationSnapshot(
        meta=SnapshotMeta(run_id=context.run_id, tick=run_result.ticks_executed),
        robot_position=engine.state.robot.position,
        goal_position=engine.state.robot.goal,
    )
    return ExperimentResult(
        run_context=context,
        run_result=run_result,
        metrics=metrics,
        snapshots=(snapshot,),
    )
