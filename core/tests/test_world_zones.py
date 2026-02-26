from __future__ import annotations

from core.domain import Position
from core.domain.world import World, ZoneType


def test_zone_expiration_restores_slow_cost() -> None:
    world = World(width=3, height=3)
    zone_id = world.add_zone(
        zone_type=ZoneType.SLOW,
        cells=(Position(1, 1),),
        current_tick=0,
        duration_ticks=2,
        extra_cost=4.0,
    )

    assert zone_id > 0
    assert world.get_extra_cost(Position(1, 1)) == 4.0

    no_changes = world.expire_zones(current_tick=1)
    assert no_changes.cost_cells_changed == set()

    changes = world.expire_zones(current_tick=2)
    assert changes.cost_cells_changed == {Position(1, 1)}
    assert world.get_extra_cost(Position(1, 1)) == 0.0


def test_zone_obstacle_blocks_until_expired() -> None:
    world = World(width=3, height=3)
    world.add_zone(
        zone_type=ZoneType.OBSTACLE,
        cells=(Position(1, 0),),
        current_tick=5,
        duration_ticks=1,
    )

    assert world.is_blocked(Position(1, 0)) is True

    changes = world.expire_zones(current_tick=6)

    assert changes.obstacle_cells_changed == {Position(1, 0)}
    assert world.is_blocked(Position(1, 0)) is False
