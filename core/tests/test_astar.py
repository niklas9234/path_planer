from __future__ import annotations

from math import isclose

import pytest

from core.domain import Position, World
from core.planning import NoPath, plan


def test_plan_returns_direct_diagonal_path_in_empty_world() -> None:
    world = World(width=5, height=5)
    start = Position(0, 0)
    goal = Position(2, 2)

    result = plan(world, start, goal)

    assert result.path == [Position(0, 0), Position(1, 1), Position(2, 2)]
    assert isclose(result.total_cost, 2 * (2**0.5), rel_tol=1e-9)
    assert result.expanded_nodes > 0
    assert result.heap_pops >= result.expanded_nodes


def test_plan_avoids_blocked_cell_and_finds_alternative_route() -> None:
    world = World(width=4, height=4)
    world.add_obstacle(Position(1, 1))

    start = Position(0, 0)
    goal = Position(2, 2)

    result = plan(world, start, goal)

    assert result.path[0] == start
    assert result.path[-1] == goal
    assert Position(1, 1) not in result.path
    assert isclose(result.total_cost, 1 + (2**0.5) + 1, rel_tol=1e-9)


def test_plan_raises_nopath_if_goal_is_not_reachable() -> None:
    world = World(width=3, height=3)
    goal = Position(2, 2)
    world.add_obstacle(Position(1, 1))
    world.add_obstacle(Position(1, 2))
    world.add_obstacle(Position(2, 1))

    with pytest.raises(NoPath):
        plan(world, Position(0, 0), goal)
