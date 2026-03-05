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
            "s01_corridor_baseline",
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
    assert summary["scenario"] == "s01_corridor_baseline"
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
            "s05_dynamic_obstacle_corridor",
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

    assert metrics_payload["summary"]["scenario"] == "s05_dynamic_obstacle_corridor"
    assert metrics_payload["summary"]["replans"] >= 1
    assert len(metrics_payload["ticks"]) == metrics_payload["summary"]["ticks_executed"]
    assert snapshot_payload["world"]["width"] == 12
    assert snapshot_payload["robot"]["position"]


def test_cli_accepts_policy_overrides_and_emits_policy_name(tmp_path) -> None:
    metrics_path = tmp_path / "metrics.json"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "core.cli",
            "run-scenario",
            "--scenario",
            "s01_corridor_baseline",
            "--planner",
            "astar",
            "--policy",
            "periodic",
            "--policy-param",
            "interval=5",
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
    assert payload["summary"]["policy_name"] == "periodic"
    assert payload["summary"]["policy_params"] == {"interval": 5}
    assert "Policy=periodic (interval=5)" in completed.stdout
