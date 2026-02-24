from __future__ import annotations

import heapq
from dataclasses import dataclass
from math import inf, sqrt

from core.domain.position import Position
from core.domain.world import World
from core.planning.interface import NoPath


@dataclass(frozen=True)
class PlanResult:
    path: list[Position]
    total_cost: float


def _octile(a: Position, b: Position) -> float:
    dx = abs(a.x - b.x)
    dy = abs(a.y - b.y)
    return (dx + dy) + (sqrt(2.0) - 2.0) * min(dx, dy)


def _reconstruct_path(
    came_from: dict[Position, Position],
    current: Position,
) -> list[Position]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def plan(world: World, start: Position, goal: Position) -> PlanResult:
    """Compute a shortest path with A* as a pure input/output function.

    The function does not mutate ``world``, ``start`` or ``goal``. It either
    returns a path-inclusive ``PlanResult`` or raises ``NoPath`` when no route
    exists between the provided endpoints.
    """
    if world.is_blocked(start):
        raise ValueError(f"Start position is blocked: {start}")
    if world.is_blocked(goal):
        raise ValueError(f"Goal position is blocked: {goal}")

    open_heap: list[tuple[float, int, Position]] = []
    push_count = 0
    heapq.heappush(open_heap, (_octile(start, goal), push_count, start))

    came_from: dict[Position, Position] = {}
    g_score: dict[Position, float] = {start: 0.0}
    closed: set[Position] = set()

    while open_heap:
        _, _, current = heapq.heappop(open_heap)

        if current in closed:
            continue
        if current == goal:
            return PlanResult(path=_reconstruct_path(came_from, current), total_cost=g_score[current])

        closed.add(current)

        for neighbor_pos, step_cost in world.neighbors(current):
            if neighbor_pos in closed:
                continue

            tentative = g_score[current] + step_cost
            if tentative < g_score.get(neighbor_pos, inf):
                came_from[neighbor_pos] = current
                g_score[neighbor_pos] = tentative
                push_count += 1
                f_score = tentative + _octile(neighbor_pos, goal)
                heapq.heappush(open_heap, (f_score, push_count, neighbor_pos))

    raise NoPath(f"No path from {start} to {goal}.")
