from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    width = 80
    height = 3

    # Force a 1-cell-wide corridor at y=1 by blocking y=0 and y=2.
    initial_obstacles = tuple(
        Position(x, y)
        for x in range(width)
        for y in (0, 2)
    )

    start = Position(0, 1)
    goal = Position(width - 1, 1)

    # We want ~20-30 replans: 14 zones with TTL=1 create 28 update ticks (+ initial plan).
    zones_count = 14
    start_tick = 2
    tick_step = 2          # put zones on even ticks -> their expiry hits odd ticks
    ahead_offset = 10      # place zone ahead of robot
    zone_len = 3           # 3 cells, makes path-affecting robust
    extra_cost = 10.0      # keep consistent with your other scenarios

    scheduled_events: dict[int, tuple[object, ...]] = {}

    for i in range(zones_count):
        tick = start_tick + i * tick_step

        # Place the zone segment ahead of the robot's expected position.
        # Clamp so that x0+zone_len-1 stays inside [0, width-1].
        x0 = min(tick + ahead_offset, (width - 1) - zone_len)
        cells = tuple(Position(x, 1) for x in range(x0, x0 + zone_len))

        scheduled_events[tick] = (
            AddZone(
                zone_type=ZoneType.SLOW,
                cells=cells,
                duration_ticks=1,
                extra_cost=extra_cost,
            ),
        )

    return ScenarioDefinition(
        name="s08_update_storm_corridor",
        policy_name="event_based",
        world_config=WorldConfig(width=width, height=height),
        start=start,
        goal=goal,
        initial_obstacles=initial_obstacles,
        initial_zones=(),
        max_ticks=250,
        scheduled_events=scheduled_events,
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks"),
            min_replans=1,
        ),
    )
