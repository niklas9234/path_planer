from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 3 – Szenario 2: Repeated off-path updates
#
# Ziel dieses Szenarios:
# - Mehrere kurzlebige Slow-Zones werden nacheinander in demselben abgelegenen
#   Kartenbereich platziert, ohne den aktuellen Standardpfad direkt zu betreffen.
# - Das Szenario soll zeigen, dass globale Trigger bei wiederholten irrelevanten
#   Änderungen unnötigen Replan-Overhead erzeugen können.
# - Erwartet wird, dass event_based häufiger replanned, während path_affected
#   solche Updates weitgehend ignorieren kann, sofern der genutzte Pfad nicht
#   tatsächlich betroffen ist.


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf3_s02_repeated_off_path_updates",
        # Platzhalter: wird im Experimentlauf durch die jeweilige Policy ersetzt.
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
                    cells=(
                        Position(20, 5),
                        Position(21, 5),
                        Position(20, 6),
                        Position(21, 6),
                    ),
                    duration_ticks=4,
                    extra_cost=10.0,
                ),
            ),
            8: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=tuple(
                        Position(x, y)
                        for x in range(21, 25)   # 21-24
                        for y in range(4, 6)     # 4-5
                    ),
                    duration_ticks=4,
                    extra_cost=10.0,
                ),
            ),
            14: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=tuple(
                        Position(x, y)
                        for x in range(24, 26)   # 24-25
                        for y in range(2, 5)     # 2-4
                    ),
                    duration_ticks=4,
                    extra_cost=10.0,
                ),
            ),
            20: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=tuple(
                        Position(x, y)
                        for x in range(25, 27)   # 25-26
                        for y in range(1, 3)     # 1-2
                    ),
                    duration_ticks=4,
                    extra_cost=10.0,
                ),
            ),
        },
        expectation=ScenarioExpectation(
            min_replans=0,
        ),
    )
