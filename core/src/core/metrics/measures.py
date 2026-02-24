from __future__ import annotations

from dataclasses import dataclass

from core.experiments.run_context import RunContext
from core.simulation.loop import RunResult


@dataclass(frozen=True, slots=True)
class RunMetrics:
    run_context: RunContext
    ticks_executed: int
    replans: int
    moves: int
    reason: str


def from_run_result(run_context: RunContext, run_result: RunResult) -> RunMetrics:
    return RunMetrics(
        run_context=run_context,
        ticks_executed=run_result.ticks_executed,
        replans=run_result.replans,
        moves=run_result.moves,
        reason=run_result.reason,
    )
