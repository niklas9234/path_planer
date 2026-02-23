from __future__ import annotations

from math import inf, isclose

from core.domain.Position import Position
from core.domain.world import WorldSnapshot
from core.planning.astar import plan


def test_plan_returns_direct_diagonal_path_in_empty_world() -> None:
    world = WorldSnapshot(width=5, height=5)
    start = Position(0, 0)
    goal = Position(2, 2)

    result = plan(world, start, goal)

    assert result.path == [Position(0, 0), Position(1, 1), Position(2, 2)]
    assert isclose(result.total_cost, 2 * (2**0.5), rel_tol=1e-9)


def test_plan_avoids_blocked_cell_and_finds_alternative_route() -> None:
    world = WorldSnapshot(width=4, height=4)
    world.add_obstacle(Position(1, 1))

    start = Position(0, 0)
    goal = Position(2, 2)

    result = plan(world, start, goal)

    assert result.path[0] == start
    assert result.path[-1] == goal
    assert Position(1, 1) not in result.path
    assert isclose(result.total_cost, 1 + (2**0.5) + 1, rel_tol=1e-9)


def test_plan_returns_empty_path_if_goal_is_not_reachable() -> None:
    world = WorldSnapshot(width=3, height=3)
    goal = Position(2, 2)
    world.add_obstacle(Position(1, 1))
    world.add_obstacle(Position(1, 2))
    world.add_obstacle(Position(2, 1))

    result = plan(world, Position(0, 0), goal)

    assert result.path == []
    assert result.total_cost == inf
