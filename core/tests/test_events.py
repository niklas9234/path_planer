from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from core.domain import (
    AddObstacle,
    ClearExtraCost,
    ClearGoal,
    DomainEvent,
    InitWorld,
    Position,
    RemoveObstacle,
    ResetSimulation,
    SetExtraCost,
    SetGoal,
    SetRobotPosition,
)


def test_event_payloads_are_dataclasses_and_frozen() -> None:
    event = SetGoal(goal=Position(3, 4))

    assert event.goal == Position(3, 4)
    with pytest.raises(FrozenInstanceError):
        event.goal = Position(0, 0)  # type: ignore[misc]


def test_all_expected_event_types_match_domain_event_alias() -> None:
    events: list[DomainEvent] = [
        InitWorld(width=10, height=8),
        SetRobotPosition(position=Position(0, 0)),
        SetGoal(goal=Position(7, 7)),
        ClearGoal(),
        AddObstacle(position=Position(1, 1)),
        RemoveObstacle(position=Position(1, 1)),
        SetExtraCost(position=Position(2, 2), value=2.5),
        ClearExtraCost(position=Position(2, 2)),
        ResetSimulation(seed=42),
    ]

    assert len(events) == 9
