from __future__ import annotations

from dataclasses import dataclass, field

from core.metrics.measures import RunMetrics


@dataclass(slots=True)
class MetricsRecorder:
    records: list[RunMetrics] = field(default_factory=list)

    def record(self, metrics: RunMetrics) -> None:
        self.records.append(metrics)
