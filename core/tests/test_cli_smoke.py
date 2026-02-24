from __future__ import annotations

import json
import os
import subprocess
import sys


def _cli_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "core/src"
    return env


def test_cli_run_scenario_writes_machine_readable_summary(tmp_path) -> None:
    metrics_path = tmp_path / "metrics.json"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "core.cli",
            "run-scenario",
            "--scenario",
            "empty_world_reaches_goal",
            "--seed",
            "7",
            "--planner",
            "astar",
            "--max-ticks",
            "20",
            "--metrics-out",
            str(metrics_path),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=_cli_env(),
    )

    payload = json.loads(metrics_path.read_text(encoding="utf-8"))

    summary = payload["summary"]
    assert summary["scenario"] == "empty_world_reaches_goal"
    assert summary["seed"] == 7
    assert summary["reason"] == "goal_reached"
    assert summary["ticks_executed"] > 0
    assert "Goal erreicht=True" in completed.stdout


def test_cli_optionally_emits_ticks_and_snapshot(tmp_path) -> None:
    metrics_path = tmp_path / "metrics.json"
    snapshot_path = tmp_path / "snapshot.json"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "core.cli",
            "run-scenario",
            "--scenario",
            "replan_after_obstacle",
            "--seed",
            "19",
            "--planner",
            "astar",
            "--max-ticks",
            "20",
            "--metrics-out",
            str(metrics_path),
            "--snapshot-out",
            str(snapshot_path),
            "--include-ticks",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=_cli_env(),
    )

    metrics_payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    snapshot_payload = json.loads(snapshot_path.read_text(encoding="utf-8"))

    assert metrics_payload["summary"]["scenario"] == "replan_after_obstacle"
    assert metrics_payload["summary"]["seed"] == 19
    assert metrics_payload["summary"]["replans"] >= 1
    assert len(metrics_payload["ticks"]) == metrics_payload["summary"]["ticks_executed"]
    assert snapshot_payload["world"]["width"] == 5
    assert snapshot_payload["robot"]["position"]
