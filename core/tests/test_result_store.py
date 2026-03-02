from __future__ import annotations

import json
from dataclasses import dataclass

from core.experiments.result_store import save_csv, save_json, stable_filename, timestamped_filename


@dataclass(frozen=True)
class _RunSummary:
    scenario: str
    planner: str


@dataclass(frozen=True)
class _ResultPayload:
    summary: _RunSummary


def test_save_json_with_stable_filename(tmp_path) -> None:
    payload = {"summary": {"scenario": "simple", "planner": "astar"}, "value": 1}

    out = save_json(payload, tmp_path, filename_strategy=stable_filename("metrics.json"))

    assert out == tmp_path / "metrics.json"
    assert json.loads(out.read_text(encoding="utf-8"))["summary"]["scenario"] == "simple"


def test_save_json_accepts_dataclass_and_timestamped_name(tmp_path) -> None:
    payload = _ResultPayload(summary=_RunSummary(scenario="demo world", planner="a*"))

    out = save_json(payload, tmp_path, filename_strategy=timestamped_filename)

    assert out.parent == tmp_path
    assert out.suffix == ".json"
    assert "demo_world__a" in out.name


def test_save_csv_writes_header_and_rows(tmp_path) -> None:
    out = save_csv([
        {"tick": 1, "cost": 1.0},
        {"tick": 2, "cost": 2.0},
    ], tmp_path / "ticks.csv")

    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "tick,cost"
    assert lines[1] == "1,1.0"
    assert lines[2] == "2,2.0"
