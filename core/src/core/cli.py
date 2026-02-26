from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from core.experiments.runner import run_scenario_experiment


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="path-planner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run-scenario", help="Run one scenario without frontend")
    run_parser.add_argument("--scenario", required=True)
    run_parser.add_argument("--planner", default="astar")
    run_parser.add_argument("--max-ticks", type=int, default=None)
    run_parser.add_argument("--metrics-out", required=True)
    run_parser.add_argument("--snapshot-out", default=None)
    run_parser.add_argument(
        "--include-ticks",
        action="store_true",
        help="Include per-tick metrics in JSON output",
    )
    return parser


def _write_json(path: str | Path, payload: dict[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "run-scenario":
        parser.error(f"Unsupported command: {args.command}")

    result = run_scenario_experiment(
        scenario_name=args.scenario,
        planner=args.planner,
        max_ticks=args.max_ticks,
        include_tick_data=args.include_ticks,
    )

    metrics_payload: dict[str, object] = {
        "summary": asdict(result.summary),
    }
    if args.include_ticks:
        metrics_payload["ticks"] = result.tick_metrics

    _write_json(args.metrics_out, metrics_payload)

    if args.snapshot_out:
        _write_json(args.snapshot_out, result.snapshot)

    print(
        " | ".join(
            [
                f"Scenario={result.summary.scenario}",
                f"Goal erreicht={result.summary.goal_reached}",
                f"Ticks={result.summary.ticks_executed}",
                f"Replans={result.summary.replans}",
                f"Kosten={result.summary.total_cost:.3f}",
            ],
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
