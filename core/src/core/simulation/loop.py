from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.planning import Planner
from core.planning.astar import NoPath
from core.simulation.engine import SimulationEngine
from core.simulation.replan_policy import EventBasedReplanPolicy, ReplanPolicy

RunReason = Literal["running", "goal_reached", "stalled", "max_ticks"]


@dataclass(frozen=True, slots=True)
class TickResult:
    replanned: bool
    moved: bool
    at_goal: bool
    done: bool
    reason: RunReason


@dataclass(frozen=True, slots=True)
class RunResult:
    ticks_executed: int
    replans: int
    moves: int
    done: bool
    reason: RunReason
    run_metrics: dict[str, int | float | bool | str | None] | None = None


def run_tick(
    engine: SimulationEngine,
    planner: Planner,
    *,
    replan_policy: ReplanPolicy | None = None,
) -> TickResult:
    policy = replan_policy or EventBasedReplanPolicy()
    obstacle_cells, cost_cells = engine.process_tick_updates()
    engine.state.metrics.on_tick_start(
        tick=engine.state.tick,
        world=engine.state.world,
        robot=engine.state.robot,
        zone_expired_obstacle_cells=obstacle_cells,
        zone_expired_cost_cells=cost_cells,
    )

    should_replan, replan_reason = policy.should_replan(engine.state)
    if should_replan:
        try:
            replanned = engine.replan(planner, reason=replan_reason)
        except NoPath:
            engine.state.metrics.on_done(
                tick=engine.state.tick,
                world=engine.state.world,
                robot=engine.state.robot,
                reason="stalled",
            )
            return TickResult(
                replanned=True,
                moved=False,
                at_goal=False,
                done=True,
                reason="stalled",
            )
    else:
        replanned = False
        engine.state.metrics.on_replan(
            tick=engine.state.tick,
            replanned=False,
            found_path=bool(engine.state.robot.path),
            world=engine.state.world,
            robot=engine.state.robot,
            reason=None,
        )

    moved = engine.step()
    at_goal = engine.state.robot.at_goal()

    if at_goal:
        engine.state.metrics.on_done(
            tick=engine.state.tick,
            world=engine.state.world,
            robot=engine.state.robot,
            reason="goal_reached",
        )
        return TickResult(replanned=replanned, moved=moved, at_goal=True, done=True, reason="goal_reached")

    if not moved:
        engine.state.metrics.on_done(
            tick=engine.state.tick,
            world=engine.state.world,
            robot=engine.state.robot,
            reason="stalled",
        )
        return TickResult(replanned=replanned, moved=False, at_goal=False, done=True, reason="stalled")

    return TickResult(replanned=replanned, moved=True, at_goal=False, done=False, reason="running")


def run_until_done(
    engine: SimulationEngine,
    planner: Planner,
    *,
    max_ticks: int = 1000,
    replan_policy: ReplanPolicy | None = None,
) -> RunResult:
    if max_ticks <= 0:
        raise ValueError(f"max_ticks must be > 0, got {max_ticks}.")

    replans = 0
    moves = 0

    for _ in range(max_ticks):
        tick = run_tick(engine, planner, replan_policy=replan_policy)
        if tick.replanned:
            replans += 1
        if tick.moved:
            moves += 1

        if tick.done:
            return RunResult(
                ticks_executed=engine.state.tick,
                replans=replans,
                moves=moves,
                done=True,
                reason=tick.reason,
                run_metrics=engine.state.metrics.finalize_run_metrics(),
            )

    engine.state.metrics.on_done(
        tick=engine.state.tick,
        world=engine.state.world,
        robot=engine.state.robot,
        reason="max_ticks",
    )
    return RunResult(
        ticks_executed=engine.state.tick,
        replans=replans,
        moves=moves,
        done=False,
        reason="max_ticks",
        run_metrics=engine.state.metrics.finalize_run_metrics(),
    )
