from __future__ import annotations

from dataclasses import asdict

from core.domain import AddObstacle, Position, SetGoal
from core.planning import plan
from core.simulation import (
    EventBasedReplanPolicy,
    SimulationEngine,
    SimulationState,
    StaticOnceReplanPolicy,
    run_tick,
)


def _run_with_policy(policy_name: str) -> dict[str, object]:
    scheduled_events = {5: (AddObstacle(position=Position(6, 1)),)}

    engine = SimulationEngine(
        SimulationState.create(
            width=8,
            height=3,
            robot_position=Position(0, 1),
        ),
    )
    engine.apply(SetGoal(goal=Position(7, 1)))

    if policy_name == "static_once":
        policy = StaticOnceReplanPolicy()
    elif policy_name == "event_based":
        policy = EventBasedReplanPolicy()
    else:
        raise AssertionError(f"Unsupported policy_name in test: {policy_name}")

    replans = 0
    moves = 0
    reason = "max_ticks"

    for _ in range(30):
        events = scheduled_events.get(engine.state.tick, ())
        for event in events:
            engine.apply(event)

        tick = run_tick(engine, plan, replan_policy=policy)
        if tick.replanned:
            replans += 1
        if tick.moved:
            moves += 1

        if tick.done:
            reason = tick.reason
            break

    return {
        "result": {
            "reason": reason,
            "replans": replans,
            "moves": moves,
            "ticks": engine.state.tick,
        },
        "position": asdict(engine.state.robot.position),
        "goal": asdict(engine.state.robot.goal) if engine.state.robot.goal is not None else None,
    }


def test_policy_selection_event_based_outperforms_static_once_when_path_is_cut() -> None:
    static_once_first = _run_with_policy("static_once")
    event_based_first = _run_with_policy("event_based")

    assert static_once_first["result"]["replans"] == 1, (
        "Expected static_once to replan exactly once (initial planning only), "
        f"got {static_once_first['result']['replans']}."
    )
    assert static_once_first["result"]["reason"] == "stalled", (
        "Expected static_once to stall after the scheduled obstacle cuts the original path at tick 5; "
        f"got reason={static_once_first['result']['reason']}."
    )

    assert event_based_first["result"]["replans"] >= 2, (
        "Expected event_based to replan at least twice (initial plan + event-triggered replan), "
        f"got {event_based_first['result']['replans']}."
    )
    assert event_based_first["result"]["reason"] == "goal_reached", (
        "Expected event_based to reach the goal via available detour after obstacle insertion at tick 5; "
        f"got reason={event_based_first['result']['reason']}."
    )

    static_once_second = _run_with_policy("static_once")
    event_based_second = _run_with_policy("event_based")

    assert static_once_first == static_once_second, (
        "Determinism failure for static_once: repeated run produced different outcome. "
        f"first={static_once_first}, second={static_once_second}"
    )
    assert event_based_first == event_based_second, (
        "Determinism failure for event_based: repeated run produced different outcome. "
        f"first={event_based_first}, second={event_based_second}"
    )
