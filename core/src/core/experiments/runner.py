"""Experiment-runner with optional JSON artifact export.

Artifact schema (`schema_version=1`):
- `schema_version` (int): Version of this artifact JSON schema.
- `run_context` (object): Metadata for the execution context.
  - `run_id` (str)
  - `scenario_count` (int)
  - `scenario_names` (list[str])
- `summary_metrics` (object): Aggregated metrics across all scenarios.
  - `total_scenarios`, `completed_scenarios`, `failed_scenarios`
  - `total_ticks`, `total_replans`, `total_moves`
  - `reasons` (object with reason->count)
- `snapshots` (optional list[object]): Per-scenario run snapshots.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.experiments.scenarios import (
    ScenarioDefinition,
    required_scenarios,
    run_scenario,
)
from core.planning.astar import plan
from core.planning.interface import Planner

ARTIFACT_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class ScenarioSnapshot:
    scenario_name: str
    done: bool
    reason: str
    ticks_executed: int
    replans: int
    moves: int


@dataclass(frozen=True, slots=True)
class ExperimentRunArtifact:
    schema_version: int
    run_context: dict[str, Any]
    summary_metrics: dict[str, Any]
    snapshots: list[dict[str, Any]] | None = None


def _build_summary_metrics(snapshots: list[ScenarioSnapshot]) -> dict[str, Any]:
    reasons: dict[str, int] = {}
    for snapshot in snapshots:
        reasons[snapshot.reason] = reasons.get(snapshot.reason, 0) + 1

    total_scenarios = len(snapshots)
    completed_scenarios = sum(1 for snapshot in snapshots if snapshot.done)

    return {
        "total_scenarios": total_scenarios,
        "completed_scenarios": completed_scenarios,
        "failed_scenarios": total_scenarios - completed_scenarios,
        "total_ticks": sum(snapshot.ticks_executed for snapshot in snapshots),
        "total_replans": sum(snapshot.replans for snapshot in snapshots),
        "total_moves": sum(snapshot.moves for snapshot in snapshots),
        "reasons": dict(sorted(reasons.items())),
    }


def _artifact_to_json_dict(artifact: ExperimentRunArtifact) -> dict[str, Any]:
    payload = {
        "schema_version": artifact.schema_version,
        "run_context": artifact.run_context,
        "summary_metrics": artifact.summary_metrics,
    }
    if artifact.snapshots is not None:
        payload["snapshots"] = artifact.snapshots
    return payload


def run_experiments(
    *,
    run_id: str,
    scenarios: tuple[ScenarioDefinition, ...] | None = None,
    planner: Planner = plan,
    persist_artifact: bool = False,
    output_dir: str | Path = "experiments/runs",
    include_snapshots: bool = False,
) -> dict[str, Any]:
    scenario_list = scenarios if scenarios is not None else required_scenarios()

    snapshots = [
        ScenarioSnapshot(
            scenario_name=scenario.name,
            done=result.done,
            reason=result.reason,
            ticks_executed=result.ticks_executed,
            replans=result.replans,
            moves=result.moves,
        )
        for scenario in scenario_list
        for result in [run_scenario(scenario, planner)]
    ]

    artifact = ExperimentRunArtifact(
        schema_version=ARTIFACT_SCHEMA_VERSION,
        run_context={
            "run_id": run_id,
            "scenario_count": len(scenario_list),
            "scenario_names": [scenario.name for scenario in scenario_list],
        },
        summary_metrics=_build_summary_metrics(snapshots),
        snapshots=(
            [asdict(snapshot) for snapshot in snapshots] if include_snapshots else None
        ),
    )
    payload = _artifact_to_json_dict(artifact)

    if persist_artifact:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        artifact_path = output_path / f"run_{run_id}.json"
        artifact_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return payload


__all__ = ["ARTIFACT_SCHEMA_VERSION", "run_experiments"]
