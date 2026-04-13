from core.domain import AddObstacle, AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 4 – Szenario 1: Off-path noise + später echter on-path obstacle
#
# Ziel dieses Szenarios:
# - Zunächst treten mehrere kurzlebige Slow-Zones in einem abgelegenen Bereich
#   der Karte auf, der den angenommenen Standardpfad nicht direkt betrifft.
# - Später wird das mittlere Tor der zentralen Doppelwand blockiert.
# - Das Szenario soll zeigen, dass globale Trigger bereits durch irrelevantes
#   Noise Replan-Overhead aufbauen können, bevor eine tatsächlich pfadrelevante
#   Änderung eintritt.
# - Erwartet wird, dass event_based früher und häufiger replanned, während
#   path_affected zunächst ruhiger bleibt, bei der späteren echten Blockade
#   aber ebenfalls reagieren muss.


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf4_s01_off_path_noise_then_on_path_obstacle",
        # Platzhalter: wird im Experimentlauf durch die jeweilige Policy ersetzt.
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