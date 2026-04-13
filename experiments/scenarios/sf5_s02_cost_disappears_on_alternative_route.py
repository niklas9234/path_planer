from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 5 – Szenario 2: Cost disappears on alternative route
#
# Ziel dieses Szenarios:
# - Eine potenziell attraktive Alternativroute wird kurz nach Simulationsbeginn
#   durch eine zeitlich begrenzte Slow-Zone künstlich unattraktiv gemacht.
# - Der aktuell gewählte Pfad bleibt dabei gültig.
# - Nach Ablauf der Zone wird die Alternativroute wieder günstig.
# - Dadurch entsteht später eine neue Opportunity, ohne dass der bisherige Pfad
#   direkt blockiert oder beschädigt wird.
# - Das Szenario dient als Gegenbeispiel zur reinen Betroffenheitslogik:
#   Eine Strategie, die nur auf direkte Betroffenheit des aktuellen Pfads schaut,
#   könnte die verbesserte Alternativroute nach Auslaufen der Zone verpassen.


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf5_s02_cost_disappears_on_alternative_route",
        policy_name="event_based",
        world_config=WorldConfig(width=WIDTH, height=HEIGHT),
        start=START,
        goal=GOAL,
        initial_obstacles=INITIAL_OBSTACLES,
        initial_zones=(),
        max_ticks=500,
        scheduled_events={
            # Die obere rechte Alternativroute wird früh unattraktiv gemacht.
            0: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=(
                        Position(20, 14),
                        Position(21, 14),
                        Position(20, 15),
                        Position(21, 15),
                        Position(20, 16),
                        Position(21, 16),
                    ),
                    duration_ticks=20,
                    extra_cost=10.0,
                ),
            ),
        },
        expectation=ScenarioExpectation(
            min_replans=1,
        ),
    )