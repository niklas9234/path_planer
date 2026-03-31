from core.domain import AddObstacle, Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 1 – Szenario 2: On-Path Obstacle at Middle Gate
#
# Ziel dieses Szenarios:
# - Der im Referenzfall naheliegende mittlere Durchgang der zentralen Torwand
#   wird kurz nach der Initialplanung blockiert.
# - Dadurch wird ein zuvor sinnvoller bzw. geplanter Pfad gezielt invalidiert.
# - Das Szenario dient als erster Kernfall für harte On-Path-Änderungen.
# - Erwartet wird, dass adaptive Strategien replannen müssen, während die
#   statische Einmalplanung klar benachteiligt ist.
#
# Umsetzung:
# - Die Blockade erfolgt bei Tick 2, also nach der Initialplanung,
#   aber früh genug, damit der Roboter den mittleren Durchgang noch nicht
#   passiert hat.
# - Um den mittleren Durchgang zuverlässig zu schließen, werden beide Zellen
#   des Tors blockiert.


MIDDLE_GATE_BLOCK_TICK = 2
MIDDLE_GATE_CELLS = (
    Position(13, 10),
    Position(14, 10),
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf1_s02_on_path_obstacle_middle_gate",
        # Platzhalter: wird im Experimentlauf durch die jeweilige Policy ersetzt.
        policy_name="event_based",
        world_config=WorldConfig(width=WIDTH, height=HEIGHT),
        start=START,
        goal=GOAL,
        initial_obstacles=INITIAL_OBSTACLES,
        initial_zones=(),
        max_ticks=500,
        scheduled_events={
            MIDDLE_GATE_BLOCK_TICK: tuple(
                AddObstacle(position=cell) for cell in MIDDLE_GATE_CELLS
            ),
        },
        expectation=ScenarioExpectation(
            min_replans=1,
        ),
    )
