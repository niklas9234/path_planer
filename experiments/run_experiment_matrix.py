#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


def _bootstrap_pythonpath() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    core_src = repo_root / "core" / "src"
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    if str(core_src) not in sys.path:
        sys.path.insert(0, str(core_src))


_bootstrap_pythonpath()

from core.experiments.runner import run_scenario_experiment
from core.experiments.scenarios import required_scenarios


DEFAULT_POLICIES = ("static_once", "event_based", "periodic", "path_affected")
DEFAULT_PERIODIC_INTERVAL = 5
DEFAULT_PATH_AFFECTED_THRESHOLD = 0.0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run all required scenarios against the fixed policy matrix and export "
            "a consolidated result table (CSV + JSON)."
        ),
    )
    parser.add_argument(
        "--out-dir",
        default="experiments/runs/matrix",
        help="Output directory for per-run files and aggregated table.",
    )
    return parser


def _policy_params(policy: str) -> dict[str, object]:
    if policy == "periodic":
        return {"interval": DEFAULT_PERIODIC_INTERVAL}
    if policy == "path_affected":
        return {"cost_delta_threshold": DEFAULT_PATH_AFFECTED_THRESHOLD}
    return {}


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []

    for scenario in required_scenarios():
        for policy in DEFAULT_POLICIES:
            params = _policy_params(policy)
            result = run_scenario_experiment(
                scenario_name=scenario.name,
                planner="astar",
                policy_name=policy,
                policy_params=params,
                max_ticks=None,
                include_tick_data=False,
            )

            summary = asdict(result.summary)
            row = {
                "Scenario": summary["scenario"],
                "Policy": summary["policy_name"],
                "total_cost": summary["total_cost"],
                "ticks": summary["ticks_executed"],
                "replans": summary["replans"],
                "goal_reached": summary["goal_reached"],
            }
            rows.append(row)

            filename = f"{summary['scenario']}__{summary['policy_name']}.json"
            _write_json(
                out_dir / filename,
                {
                    "summary": summary,
                    "snapshot": result.snapshot,
                    "trajectory": result.trajectory,
                },
            )

    csv_path = out_dir / "matrix_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["Scenario", "Policy", "total_cost", "ticks", "replans", "goal_reached"],
        )
        writer.writeheader()
        writer.writerows(rows)

    _write_json(out_dir / "matrix_summary.json", rows)

    print(f"Wrote {len(rows)} runs to: {out_dir}")
    print("Columns: Scenario, Policy, total_cost, ticks, replans, goal_reached")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
