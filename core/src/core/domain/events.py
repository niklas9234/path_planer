from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from core.domain.position import Position
from core.domain.world import ZoneType


@dataclass(frozen=True, slots=True)
class InitWorld:
    """Initialize a new world grid and reset simulation-relevant state."""

    width: int
    height: int
    cell_size_m: float = 1.0
    base_cost: float = 1.0


@dataclass(frozen=True, slots=True)
class SetRobotPosition:
    """Set robot position to an absolute grid cell."""

    position: Position


@dataclass(frozen=True, slots=True)
class SetGoal:
    """Set or update the robot goal position."""

    goal: Position


@dataclass(frozen=True, slots=True)
class ClearGoal:
    """Clear the current robot goal."""


@dataclass(frozen=True, slots=True)
class AddObstacle:
    """Mark a grid cell as blocked."""

    position: Position


@dataclass(frozen=True, slots=True)
class RemoveObstacle:
    """Mark a grid cell as free."""

    position: Position


@dataclass(frozen=True, slots=True)
class SetExtraCost:
    """Set the additive traversal cost for a specific cell."""

    position: Position
    value: float


@dataclass(frozen=True, slots=True)
class ClearExtraCost:
    """Reset additive traversal cost for a specific cell to default."""

    position: Position


@dataclass(frozen=True, slots=True)
class AddZone:
    """Add a zone overlay with optional TTL in ticks."""

    zone_type: ZoneType
    cells: tuple[Position, ...]
    duration_ticks: int | None = None
    extra_cost: float = 0.0


@dataclass(frozen=True, slots=True)
class ResetSimulation:
    """Reset runtime simulation state; optional deterministic seed can be provided."""

    seed: int | None = None


DomainEvent: TypeAlias = (
    InitWorld
    | SetRobotPosition
    | SetGoal
    | ClearGoal
    | AddObstacle
    | RemoveObstacle
    | SetExtraCost
    | ClearExtraCost
    | AddZone
    | ResetSimulation
)


__all__ = [
    "InitWorld",
    "SetRobotPosition",
    "SetGoal",
    "ClearGoal",
    "AddObstacle",
    "RemoveObstacle",
    "SetExtraCost",
    "ClearExtraCost",
    "AddZone",
    "ResetSimulation",
    "DomainEvent",
]
