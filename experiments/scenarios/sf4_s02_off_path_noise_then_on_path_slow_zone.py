from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 4 – Szenario 2: Off-path noise + spätere on-path slow zone
#
# Ziel dieses Szenarios:
# - Zunächst treten mehrere kurzlebige Slow-Zones in einem abgelegenen Bereich
#   der Karte auf, der den angenommenen Standardpfad nicht direkt betrifft.
# - Später wird der mittlere Standardpfad durch eine länger anhaltende Slow-Zone
#   teurer, aber nicht unbenutzbar.
# - Das Szenario soll zeigen, dass frühes Off-path-Noise bei globalen Triggern
#   bereits Overhead auslösen kann, bevor eine tatsächlich pfadrelevante, aber
#   nur kostenbasierte Änderung eintritt.
# - Erwartet wird, dass static_once das Ziel weiter erreicht, aber unter Umständen
#   auf einer nun teureren Route bleibt, während adaptive Strategien auf die
#   spätere Bewertungsänderung reagieren können.


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf4_s02_off_path_noise_then_on_path_slow_zone",
        policy_name="event_based",
        world_config=WorldConfig(width=WIDTH, height=HEIGHT),
        start=START,
        goal=GOAL,
        initial_obstacles=INITIAL_OBSTACLES,
        initial_zones=(),
        max_ticks=500,
        scheduled_events={
            # Frühes Off-path-Noise in der unteren rechten Ecke
            2: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=(
                        Position(20, 5),
                        Position(21, 5),
                        Position(20, 6),
                        Position(21, 6),
                    ),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            6: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=tuple(
                        Position(x, y)
                        for x in range(21, 25)   # 21-24
                        for y in range(4, 6)     # 4-5
                    ),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            10: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=tuple(
                        Position(x, y)
                        for x in range(24, 26)   # 24-25
                        for y in range(2, 5)     # 2-4
                    ),
                    duration_ticks=1,
                    extra_cost=10.0,
                ),
            ),
            # Spätere echte on-path-Änderung:
            # mittlerer Standardpfad wird teurer, aber bleibt gültig
            14: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=tuple(
                        Position(x, 10)
                        for x in range(9, 18)    # 9-17 entlang des mittleren Korridors
                    ),
                    duration_ticks=12,
                    extra_cost=10.0,
                ),
            ),
        },
        expectation=ScenarioExpectation(
            min_replans=0,
        ),
    )