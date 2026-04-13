from core.domain import AddObstacle, Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 1 – Szenario 3: Same Event, Later Timing
#
# Ziel dieses Szenarios:
# - Es wird dieselbe harte On-Path-Änderung wie in Szenario 2 verwendet:
#   Der mittlere Durchgang der zentralen Torwand wird blockiert.
# - Im Unterschied zu Szenario 2 tritt die Blockade später ein.
# - Dadurch kann untersucht werden, wie stark der Zeitpunkt einer ansonsten
#   identischen Pfadinvalidierung das Replan-Verhalten beeinflusst.
# - Das Szenario dient damit als Timing-Variante innerhalb derselben
#   Szenariofamilie bei unveränderter Karten- und Ereignisstruktur.
#
# Umsetzung:
# - Die Blockade erfolgt bei Tick 6 und damit später als im frühen
#   Mitteltor-Szenario, aber noch vor dem geplanten Passieren des Tors.
# - Wie in Szenario 2 werden beide Zellen des mittleren Tors blockiert,
#   damit der Durchgang zuverlässig geschlossen ist.


MIDDLE_GATE_BLOCK_TICK = 12
MIDDLE_GATE_CELLS = (
    Position(13, 10),
    Position(14, 10),
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf1_s03_same_event_later_timing",
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
