from __future__ import annotations

"""Deprecated compatibility layer for policy imports.

Policy implementations live exclusively in ``core.simulation.replan_policy``.
This module intentionally re-exports those symbols so older imports continue
working without introducing a second implementation source.
"""

from core.simulation.replan_policy import (
    EventBasedReplanPolicy,
    PathAffectedReplanPolicy,
    PeriodicReplanPolicy,
    PolicyContext,
    ReplanPolicy,
    StaticOnceReplanPolicy,
)
from core.simulation.replan_policy import (
    PolicyDecision as ReplanDecision,
)

__all__ = [
    "ReplanDecision",
    "PolicyContext",
    "ReplanPolicy",
    "EventBasedReplanPolicy",
    "StaticOnceReplanPolicy",
    "PeriodicReplanPolicy",
    "PathAffectedReplanPolicy",
]
