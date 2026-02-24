from __future__ import annotations

import json

from core.experiments.runner import ARTIFACT_SCHEMA_VERSION, run_experiments
from core.experiments.scenarios import required_scenarios


def test_run_experiments_persists_schema_fields(tmp_path) -> None:
    run_id = "schema-check"

    payload = run_experiments(
        run_id=run_id,
        persist_artifact=True,
        output_dir=tmp_path,
        include_snapshots=True,
    )

    artifact_path = tmp_path / f"run_{run_id}.json"
    assert artifact_path.exists()

    on_disk = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert on_disk == payload

    assert payload["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert set(payload.keys()) == {
        "schema_version",
        "run_context",
        "summary_metrics",
        "snapshots",
    }

    run_context = payload["run_context"]
    assert run_context["run_id"] == run_id
    assert run_context["scenario_count"] == len(required_scenarios())
    assert isinstance(run_context["scenario_names"], list)

    summary = payload["summary_metrics"]
    assert {
        "total_scenarios",
        "completed_scenarios",
        "failed_scenarios",
        "total_ticks",
        "total_replans",
        "total_moves",
        "reasons",
    }.issubset(summary.keys())

    snapshots = payload["snapshots"]
    assert isinstance(snapshots, list)
    assert snapshots
    assert {
        "scenario_name",
        "done",
        "reason",
        "ticks_executed",
        "replans",
        "moves",
    }.issubset(snapshots[0].keys())


def test_summary_metrics_are_stable_for_identical_inputs() -> None:
    scenarios = required_scenarios()

    first = run_experiments(
        run_id="first",
        scenarios=scenarios,
        persist_artifact=False,
        include_snapshots=True,
    )
    second = run_experiments(
        run_id="second",
        scenarios=scenarios,
        persist_artifact=False,
        include_snapshots=True,
    )

    assert first["summary_metrics"] == second["summary_metrics"]
