from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
from typing import Any

from core.experiments.result_store import save_json, stable_filename
from core.experiments.runner import run_scenario_experiment


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="path-planner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run-scenario", help="Run one scenario without frontend")
    run_parser.add_argument("--scenario", required=True)
    run_parser.add_argument("--planner", default="astar")
    run_parser.add_argument(
        "--policy",
        choices=("static_once", "event_based", "periodic", "path_affected"),
        default=None,
    )
    run_parser.add_argument(
        "--policy-param",
        action="append",
        default=[],
        metavar="key=value",
        help="Policy parameter as key=value (can be passed multiple times)",
    )
    run_parser.add_argument(
        "--periodic-interval",
        type=int,
        default=None,
        help="Convenience alias for --policy-param interval=<n>",
    )
    run_parser.add_argument("--max-ticks", type=int, default=None)
    run_parser.add_argument("--metrics-out", required=True)
    run_parser.add_argument("--snapshot-out", default=None)
    run_parser.add_argument(
        "--include-ticks",
        action="store_true",
        help="Include per-tick metrics in JSON output",
    )
    return parser


def _coerce_cli_value(raw: str) -> object:
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"

    try:
        return int(raw)
    except ValueError:
        pass

    try:
        return float(raw)
    except ValueError:
        return raw


def _parse_policy_params(raw_items: list[str], periodic_interval: int | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for item in raw_items:
        if "=" not in item:
            raise ValueError(f"Invalid --policy-param '{item}'. Expected key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid --policy-param '{item}'. Key must not be empty.")
        params[key] = _coerce_cli_value(value.strip())

    if periodic_interval is not None:
        params["interval"] = periodic_interval
    return params


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "run-scenario":
        parser.error(f"Unsupported command: {args.command}")

    try:
        cli_policy_params = _parse_policy_params(args.policy_param, args.periodic_interval)
        result = run_scenario_experiment(
            scenario_name=args.scenario,
            planner=args.planner,
            policy_name=args.policy,
            policy_params=cli_policy_params,
            max_ticks=args.max_ticks,
            include_tick_data=args.include_ticks,
        )
    except ValueError as exc:
        parser.error(str(exc))

    metrics_payload: dict[str, object] = {
        "summary": asdict(result.summary),
    }
    if args.include_ticks:
        metrics_payload["ticks"] = result.tick_metrics

    metrics_out = Path(args.metrics_out)
    save_json(
        metrics_payload,
        metrics_out.parent,
        filename_strategy=stable_filename(metrics_out.name),
    )

    if args.snapshot_out:
        snapshot_out = Path(args.snapshot_out)
        save_json(
            result.snapshot,
            snapshot_out.parent,
            filename_strategy=stable_filename(snapshot_out.name),
        )

    print(
        " | ".join(
            [
                f"Scenario={result.summary.scenario}",
                f"Goal erreicht={result.summary.goal_reached}",
                f"Ticks={result.summary.ticks_executed}",
                f"Replans={result.summary.replans}",
                f"Policy={result.summary.policy_name}",
                f"Kosten={result.summary.total_cost:.3f}",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
