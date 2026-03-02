from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

FilenameStrategy = Callable[[dict[str, Any]], str]


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip())
    return normalized.strip("_") or "unknown"


def timestamped_filename(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    scenario = _slugify(str(summary.get("scenario", "scenario")))
    policy = _slugify(str(summary.get("planner", summary.get("policy", "policy"))))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{scenario}__{policy}__{timestamp}.json"


def stable_filename(filename: str) -> FilenameStrategy:
    def _strategy(_: dict[str, Any]) -> str:
        target = Path(filename)
        return target.name

    return _strategy


def _normalize_payload(run_result: Any) -> dict[str, Any]:
    if is_dataclass(run_result):
        return asdict(run_result)
    if isinstance(run_result, Mapping):
        return dict(run_result)
    raise TypeError("run_result must be a mapping or dataclass instance")


def save_json(
    run_result: Any,
    out_dir: str | Path,
    filename_strategy: FilenameStrategy = timestamped_filename,
) -> Path:
    payload = _normalize_payload(run_result)
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)

    target = directory / filename_strategy(payload)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def save_csv(rows: Iterable[Mapping[str, Any]], out_path: str | Path) -> Path:
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    iterator = iter(rows)
    try:
        first = next(iterator)
    except StopIteration:
        target.write_text("", encoding="utf-8")
        return target

    fieldnames = list(first.keys())
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(dict(first))
        for row in iterator:
            writer.writerow(dict(row))
    return target
