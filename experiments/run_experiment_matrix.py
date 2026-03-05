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
    if str(core_src) not in sys.path:
        sys.path.insert(0, str(core_src))


_bootstrap_pythonpath()

from core.experiments.runner import run_scenario_experiment
from core.experiments.scenarios import required_scenarios


DEFAULT_POLICIES = ("static_once", "event_based", "periodic", "path_affected")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run all required scenarios against selected policies and export "
            "a consolidated result table (CSV + JSON)."
        ),
    )
    parser.add_argument(
        "--out-dir",
        default="experiments/runs/matrix",
        help="Output directory for per-run files and aggregated table.",
    )
    parser.add_argument(
        "--planner",
        default="astar",
        help="Planner name (currently only 'astar' is supported).",
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=None,
        help="Optional max tick budget override for each run.",
    )
    parser.add_argument(
        "--policies",
        nargs="+",
        default=list(DEFAULT_POLICIES),
        help="Policies to execute (default: static_once event_based periodic path_affected).",
    )
    parser.add_argument(
        "--periodic-interval",
        type=int,
        default=None,
        help=(
            "Interval passed to policy 'periodic' as interval=<n>. "
            "Must be set explicitly when periodic is selected."
        ),
    )
    parser.add_argument(
        "--path-affected-threshold",
        type=float,
        default=0.0,
        help="Threshold passed to policy 'path_affected' as cost_delta_threshold=<x>.",
    )
    return parser


def _policy_params(policy: str, args: argparse.Namespace) -> dict[str, object]:
    if policy == "periodic":
        if args.periodic_interval is None:
            raise ValueError(
                "Policy 'periodic' requires --periodic-interval to be set explicitly."
            )
        return {"interval": args.periodic_interval}
    if policy == "path_affected":
        return {"cost_delta_threshold": args.path_affected_threshold}
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
        for policy in args.policies:
            try:
                params = _policy_params(policy, args)
            except ValueError as exc:
                parser.error(str(exc))
            result = run_scenario_experiment(
                scenario_name=scenario.name,
                planner=args.planner,
                policy_name=policy,
                policy_params=params,
                max_ticks=args.max_ticks,
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
            _write_json(out_dir / filename, {"summary": summary, "snapshot": result.snapshot})

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
