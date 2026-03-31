from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 1 – Szenario 1: Baseline / Referenzfall
#
# Ziel dieses Szenarios:
# - Referenzlauf auf der gemeinsamen Basiskarte ohne dynamische Änderungen.
# - Alle Strategien werden unter identischen Ausgangsbedingungen verglichen.
# - Das Szenario dient als Nullfall, um spätere Unterschiede eindeutig auf
#   Szenario-Events und Replan-Trigger zurückführen zu können.
# - Erwartet wird, dass nach der Initialplanung keine zusätzlichen Replans
#   erforderlich sind und alle Strategien denselben grundlegenden Pfad finden.


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="sf1_s01_baseline_reference",
        policy_name="event_based",
        world_config=WorldConfig(width=WIDTH, height=HEIGHT),
        start=START,
        goal=GOAL,
        initial_obstacles=INITIAL_OBSTACLES,
        initial_zones=(),
        max_ticks=500,
        scheduled_events={},
        expectation=ScenarioExpectation(
            min_replans=0,
        ),
    )