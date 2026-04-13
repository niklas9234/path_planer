from core.domain import AddObstacle, AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 4 – Szenario 3: Near-path zone + später zentrale Blockade
#
# Ziel dieses Szenarios:
# - Zunächst wird eine länger anhaltende Slow-Zone auf einer wahrscheinlichen
#   Alternativroute nahe des mittleren Bereichs aktiviert.
# - Der aktuelle Standardpfad wird dadurch zunächst nicht direkt ungültig.
# - Später wird das mittlere Tor der zentralen Doppelwand blockiert.
# - Das Szenario soll zeigen, dass die frühe Änderung zunächst nur potenziell
#   relevant ist, durch die spätere Blockade aber strategisch wichtig wird.
# - Erwartet wird, dass keine Strategie universell dominiert:
#   event_based reagiert früh auf die Near-path-Zone, path_affected ggf. erst
#   später, und periodic hängt vom Replan-Zeitpunkt ab.


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf4_s03_near_path_zone_then_central_blockade",
        policy_name="event_based",
        world_config=WorldConfig(width=WIDTH, height=HEIGHT),
        start=START,
        goal=GOAL,
        initial_obstacles=INITIAL_OBSTACLES,
        initial_zones=(),
        max_ticks=500,
        scheduled_events={
            # Frühe Near-path-Zone auf der oberen Passage / Alternativroute
            4: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=(
                        Position(11, 15),
                        Position(12, 15),
                        Position(13, 15),
                        Position(14, 15),
                        Position(15, 15),
                        Position(16, 15),
                        Position(11, 16),
                        Position(12, 16),
                        Position(13, 16),
                        Position(14, 16),
                        Position(15, 16),
                        Position(16, 16),
                    ),
                    duration_ticks=20,
                    extra_cost=10.0,
                ),
            ),
            # Spätere echte on-path-Änderung:
            # mittleres Tor der zentralen Doppelwand wird geschlossen
            14: (
                AddObstacle(position=Position(13, 10)),
                AddObstacle(position=Position(14, 10)),
            ),
        },
        expectation=ScenarioExpectation(
            min_replans=1,
        ),
    )