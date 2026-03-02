from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.experiments.run_context import RunContext
from core.metrics.measures import RunMetrics
from core.protocol.snapshots import SimulationSnapshot
from core.simulation.loop import RunResult


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    run_context: RunContext
    run_result: RunResult
    metrics: RunMetrics
    snapshots: tuple[SimulationSnapshot, ...]

    def to_export_dict(self) -> dict[str, Any]:
        return {
            "run_context": {
                "run_id": self.run_context.run_id,
                "scenario_name": self.run_context.scenario_name,
                "planner_name": self.run_context.planner_name,
                "planner_params": dict(self.run_context.planner_params),
                "world_params": dict(self.run_context.world_params),
                "started_at": self.run_context.started_at.isoformat(),
                "core_version": self.run_context.core_version,
            },
            "run_result": self.run_result.to_dict(),
            "metrics": {
                "run_id": self.metrics.run_context.run_id,
                "ticks_executed": self.metrics.ticks_executed,
                "replans": self.metrics.replans,
                "moves": self.metrics.moves,
                "reason": self.metrics.reason,
            },
            "snapshots": [
                {
                    "meta": {
                        "run_id": snapshot.meta.run_id,
                        "tick": snapshot.meta.tick,
                    },
                    "robot_position": {
                        "x": snapshot.robot_position.x,
                        "y": snapshot.robot_position.y,
                    },
                    "goal_position": None
                    if snapshot.goal_position is None
                    else {
                        "x": snapshot.goal_position.x,
                        "y": snapshot.goal_position.y,
                    },
                }
                for snapshot in self.snapshots
            ],
        }
