from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Mapping

from core.experiments.results import ExperimentResult
from core.experiments.run_context import RunContext
from core.experiments.scenarios import ScenarioDefinition, run_scenario
from core.metrics.measures import from_run_result
from core.metrics.recorder import MetricsRecorder
from core.planning.astar import plan
from core.protocol.snapshots import SimulationSnapshot, SnapshotMeta


def _load_core_version() -> str:
    version_file = Path(__file__).resolve().parents[4] / "shared" / "protocol" / "VERSION"
    return version_file.read_text(encoding="utf-8").strip()


def run_experiment(
    scenario: ScenarioDefinition,
    *,
    seed: int,
    planner_name: str = "astar",
    planner_params: Mapping[str, Any] | None = None,
    world_params: Mapping[str, Any] | None = None,
    recorder: MetricsRecorder | None = None,
) -> ExperimentResult:
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

    run_result = run_scenario(scenario, planner=plan)
    metrics = from_run_result(context, run_result)

    target_recorder = recorder or MetricsRecorder()
    target_recorder.record(metrics)

    snapshot = SimulationSnapshot(
        meta=SnapshotMeta(run_id=context.run_id, tick=run_result.ticks_executed),
        robot_position=scenario.goal if run_result.reason == "goal_reached" else scenario.start,
        goal_position=scenario.goal,
    )
    return ExperimentResult(
        run_context=context,
        run_result=run_result,
        metrics=metrics,
        snapshots=(snapshot,),
    )
