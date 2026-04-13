from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 3 – Szenario 1: Single off-path zone
#
# Ziel dieses Szenarios:
# - Eine einzelne Slow-Zone wird in einem abgelegenen Kartenbereich platziert,
#   der den aktuellen Standardpfad nicht direkt betrifft.
# - Das Szenario dient dazu, unnötigen Replan-Overhead sichtbar zu machen.
# - Erwartet wird, dass globale Trigger (z. B. event_based) eher reagieren,
#   während pfadnahe Trigger (z. B. path_affected) diese Änderung eher ignorieren
#   können, sofern sie für den tatsächlich genutzten Pfad nicht relevant ist.


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf3_s01_single_off_path_zone",
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
                        Position(20, 4),
                        Position(21, 4),
                        Position(20, 5),
                        Position(21, 5),
                    ),
                    duration_ticks=20,
                    extra_cost=10.0,
                ),
            ),
        },
        expectation=ScenarioExpectation(
            min_replans=0,
        ),
    )