from __future__ import annotations

from dataclasses import dataclass

from core.domain.position import Position


@dataclass(frozen=True, slots=True)
class SnapshotMeta:
    run_id: str
    tick: int


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    meta: SnapshotMeta
    robot_position: Position
    goal_position: Position | None


__all__ = ["SnapshotMeta", "SimulationSnapshot"]
