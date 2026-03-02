from __future__ import annotations

from core.domain import Position
from core.experiments.policies import (
    EventBasedReplanPolicy,
    PathAffectedReplanPolicy,
    PeriodicReplanPolicy,
    PolicyContext,
    StaticOnceReplanPolicy,
)


def make_context(**overrides: object) -> PolicyContext:
    base = {
        "tick": 0,
        "has_goal": True,
        "dirty_replan": False,
        "robot_position": Position(0, 0),
        "goal_position": Position(2, 2),
        "path": (Position(0, 0), Position(1, 0), Position(2, 0)),
        "path_index": 1,
    }
    base.update(overrides)
    return PolicyContext(**base)


def test_event_based_replan_policy_replans_for_dirty_goal_context() -> None:
    policy = EventBasedReplanPolicy()

    decision = policy.decide(make_context(dirty_replan=True))

    assert decision.replan is True
    assert decision.reason == "event"


def test_event_based_replan_policy_does_not_replan_without_goal() -> None:
    policy = EventBasedReplanPolicy()

    decision = policy.decide(make_context(dirty_replan=True, has_goal=False))

    assert decision.replan is False
    assert decision.reason == ""


def test_event_based_replan_policy_does_not_replan_without_dirty_flag() -> None:
    policy = EventBasedReplanPolicy()

    decision = policy.decide(make_context(dirty_replan=False, has_goal=True))

    assert decision.replan is False
    assert decision.reason == ""


def test_static_once_replan_policy_replans_only_once() -> None:
    policy = StaticOnceReplanPolicy()

    first = policy.decide(make_context())
    second = policy.decide(make_context(tick=1))

    assert first.replan is True
    assert first.reason == "initial_static"
    assert second.replan is False


def test_periodic_replan_policy_respects_interval() -> None:
    policy = PeriodicReplanPolicy(interval_ticks=3)

    replan_tick = policy.decide(make_context(tick=6))
    no_replan_tick = policy.decide(make_context(tick=7))

    assert replan_tick.replan is True
    assert replan_tick.reason == "periodic"
    assert no_replan_tick.replan is False


def test_path_affected_replan_policy_detects_changed_remaining_path_cells() -> None:
    policy = PathAffectedReplanPolicy()

    decision = policy.decide(
        make_context(
            obstacle_cells_changed=frozenset({Position(1, 0)}),
            path_index=1,
        ),
    )

    assert decision.replan is True
    assert decision.reason == "path_affected"
