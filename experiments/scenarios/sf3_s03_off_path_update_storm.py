from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 3 – Szenario 3: Distributed off-path update storm
#
# Ziel dieses Szenarios:
# - Viele sehr kurzlebige Slow-Zones werden über mehrere abgelegene Bereiche
#   der Karte verteilt ausgelöst.
# - Der Kartenursprung wird hier als (0, 0) unten links verstanden.
# - Keine der Zonen liegt gezielt auf dem angenommenen Standardpfad.
# - Das Szenario soll zeigen, dass globale Trigger bei häufigen, räumlich
#   verteilten irrelevanten Änderungen deutlichen Replan-Overhead erzeugen
#   können, während pfadnahe Trigger diese Änderungen weitgehend ignorieren.
#
# Verwendete Off-path-Bereiche:
# A  unten rechts: x 20-21, y 5-6
# B  unten rechts: x 21-24, y 4-5
# C  unten rechts: x 24-25, y 2-4
# D  unten rechts: x 25-26, y 1-2
# E  oben links:   x 0-1,   y 18-19
# F  links oben:   x 5-6,   y 17-18
# G  links Mitte:  x 5-6,   y 8-9
# H  oben Mitte:   x 9-10,  y 17-18


def _zone_a() -> tuple[Position, ...]:
    return tuple(
        Position(x, y)
        for x in range(20, 22)   # 20-21
        for y in range(5, 7)     # 5-6
    )


def _zone_b() -> tuple[Position, ...]:
    return tuple(
        Position(x, y)
        for x in range(21, 25)   # 21-24
        for y in range(4, 6)     # 4-5
    )


def _zone_c() -> tuple[Position, ...]:
    return tuple(
        Position(x, y)
        for x in range(24, 26)   # 24-25
        for y in range(2, 5)     # 2-4
    )


def _zone_d() -> tuple[Position, ...]:
    return tuple(
        Position(x, y)
        for x in range(25, 27)   # 25-26
        for y in range(1, 3)     # 1-2
    )


def _zone_e() -> tuple[Position, ...]:
    return tuple(
        Position(x, y)
        for x in range(0, 2)     # 0-1
        for y in range(18, 20)   # 18-19
    )


def _zone_f() -> tuple[Position, ...]:
    return tuple(
        Position(x, y)
        for x in range(5, 7)     # 5-6
        for y in range(17, 19)   # 17-18
    )


def _zone_g() -> tuple[Position, ...]:
    return tuple(
        Position(x, y)
        for x in range(5, 7)     # 5-6
        for y in range(8, 10)    # 8-9
    )


def _zone_h() -> tuple[Position, ...]:
    return tuple(
        Position(x, y)
        for x in range(9, 11)    # 9-10
        for y in range(17, 19)   # 17-18
    )


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf3_s03_distributed_off_path_update_storm",
        policy_name="event_based",
        world_config=WorldConfig(width=WIDTH, height=HEIGHT),
        start=START,
        goal=GOAL,
        initial_obstacles=INITIAL_OBSTACLES,
        initial_zones=(),
        max_ticks=500,
        scheduled_events={
            2: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_e(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            4: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_a(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            6: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_f(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            8: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_b(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            10: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_g(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            12: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_c(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            14: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_h(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            16: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_d(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            18: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_a(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            20: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=_zone_f(),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
        },
        expectation=ScenarioExpectation(
            min_replans=0,
        ),
    )