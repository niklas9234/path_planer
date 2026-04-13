from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 2 – Szenario 3: Pulse-zone, gleiche Position
#
# Ziel dieses Szenarios:
# - Dieselbe on-path Slow-Zone wie in F2S1 und F2S2 wird verwendet, aber nur
#   als sehr kurzer Puls aktiviert.
# - Der mittlere Standardpfad bleibt durchgehend begehbar und wird nur für
#   einen sehr kurzen Zeitraum verteuert.
# - Das Szenario dient dazu, unnötiges oder überreaktives Replanning von
#   wirklich relevanten Kostenänderungen zu trennen.
# - Erwartet wird, dass event_based die Änderung sofort verarbeitet, periodic
#   sie je nach Takt teilweise "übersehen" kann und path_affected nur dann
#   replanned, wenn die Zone für den noch ausstehenden Pfadabschnitt in genau
#   diesem Zeitfenster tatsächlich relevant ist.
#
# Umsetzung:
# - Gleiche Position wie F2S1 und F2S2, damit nur die Persistenz variiert.
# - Gleicher Starttick und gleicher Zusatzkostenwert.
# - Die Zone existiert nur für einen Tick und bildet damit den Kurzzeitfall.

ZONE_START_TICK = 2
ZONE_DURATION_TICKS = 1
ZONE_EXTRA_COST = 10.0

MIDDLE_PATH_SLOW_ZONE_CELLS = tuple(
    Position(x, 10)
    for x in range(9, 18)
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf2_s03_pulse_zone_same_position",
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
