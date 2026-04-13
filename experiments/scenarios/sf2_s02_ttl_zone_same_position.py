from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 2 – Szenario 2: TTL-zone, gleiche Position
#
# Ziel dieses Szenarios:
# - Dieselbe on-path Slow-Zone wie in F2S1 wird an derselben Position aktiviert,
#   bleibt aber nur für eine begrenzte Zeit bestehen.
# - Damit wird nicht nur die räumliche Relevanz, sondern zusätzlich die zeitliche
#   Persistenz der Kostenänderung untersucht.
# - Das Szenario soll zeigen, dass eine kostenbasierte Änderung nicht automatisch
#   dieselbe Reaktion rechtfertigt wie eine dauerhafte Verteuerung des Pfads.
# - Erwartet wird, dass event_based früh reagiert, periodic je nach Taktung
#   verzögert oder günstiger reagieren kann und path_affected nur dann replanned,
#   wenn die Zone den tatsächlich noch relevanten Pfadabschnitt betrifft.
#
# Umsetzung:
# - Gleiche Zellen, gleicher Zusatzkostensatz und gleicher Startzeitpunkt wie in F2S1.
# - Nur die Dauer der Zone wird reduziert, damit die Szenarien als Minimal-Pair
#   sauber vergleichbar bleiben.


ZONE_START_TICK = 2
ZONE_DURATION_TICKS = 10
ZONE_EXTRA_COST = 10.0

MIDDLE_PATH_SLOW_ZONE_CELLS = tuple(
    Position(x, 10)
    for x in range(9, 18)
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf2_s02_ttl_zone_same_position",
        policy_name="event_based",
        world_config=WorldConfig(width=WIDTH, height=HEIGHT),
        start=START,
        goal=GOAL,
        initial_obstacles=INITIAL_OBSTACLES,
        initial_zones=(),
        max_ticks=500,
        scheduled_events={
            ZONE_START_TICK: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=MIDDLE_PATH_SLOW_ZONE_CELLS,
                    duration_ticks=ZONE_DURATION_TICKS,
                    extra_cost=ZONE_EXTRA_COST,
                ),
            ),
        },
        expectation=ScenarioExpectation(
            min_replans=1,
        ),
    )
