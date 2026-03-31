from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 2 – Szenario 1: Persistent on-path slow zone
#
# Ziel dieses Szenarios:
# - Der aktuell naheliegende mittlere Standardpfad bleibt formal begehbar,
#   wird aber durch eine lang anhaltende Slow-Zone gezielt verteuert.
# - Im Unterschied zu Familie 1 wird der Pfad also nicht invalidiert,
#   sondern nur kostenmäßig unattraktiver.
# - Das Szenario dient als Kernfall für kostenbasierte Relevanz: Replanning
#   ist hier nicht zwingend wegen Unlösbarkeit, sondern potenziell sinnvoll,
#   weil eine alternative Route günstiger werden kann.
# - Erwartet wird, dass adaptive Strategien den verteuerten Mittelpfad
#   zugunsten einer oberen oder unteren Alternative verlassen können,
#   während static_once auf dem ursprünglich geplanten Pfad verbleibt.
#
# Umsetzung:
# - Die Zone wird kurz nach der Initialplanung aktiviert.
# - Sie liegt direkt auf dem mittleren Durchgang und dem zugehörigen
#   Anlaufkorridor, sodass der Referenzpfad gezielt betroffen ist.
# - Die Dauer ist so gewählt, dass die Kostenänderung für den gesamten
#   relevanten Missionsabschnitt bestehen bleibt.


ZONE_START_TICK = 2
ZONE_DURATION_TICKS = 200
ZONE_EXTRA_COST = 10.0

MIDDLE_PATH_SLOW_ZONE_CELLS = tuple(
    Position(x, 10)
    for x in range(9, 18)
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf2_s01_persistent_on_path_slow_zone",
        # Platzhalter: wird im Experimentlauf durch die jeweilige Policy ersetzt.
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
