from core.domain import Position, RemoveObstacle, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
    ZoneDefinition,
)

from experiments.scenarios.base_map import GOAL, HEIGHT, INITIAL_OBSTACLES, START, WIDTH

# Szenariofamilie 5 – Szenario 1: Shortcut opens
#
# Ziel dieses Szenarios:
# - Der aktuell gewählte Pfad bleibt zunächst gültig.
# - Eine lokal blockierte Verbindung im rechten Kartenbereich verhindert anfangs
#   eine günstigere Fortsetzung.
# - Gleichzeitig ist eine obere Alternativroute durch eine initiale Slow-Zone
#   unattraktiv gemacht.
# - Später öffnet sich die blockierte Verbindung wieder und erzeugt damit eine
#   neue, bessere Opportunität, obwohl der bisherige Pfad nicht ungültig wird.
# - Das Szenario dient als Gegenbeispiel zur reinen Betroffenheitslogik:
#   Eine Strategie, die nur prüft, ob der aktuelle Pfad direkt betroffen ist,
#   könnte die neu entstandene bessere Route verpassen.


def build() -> ScenarioDefinition:
    extra_initial_obstacles = (
        # Lokale Sperre im rechten Mittelbereich.
        # Diese Verbindung soll sich später als Shortcut öffnen.
        Position(24, 10),
        Position(25, 10),
    )

    initial_shortcut_detour_zone = (
        ZoneDefinition(
            zone_type=ZoneType.SLOW,
            cells=(
                Position(20, 14),
                Position(21, 14),
                Position(20, 15),
                Position(21, 15),
                Position(20, 16),
                Position(21, 16),
            ),
            extra_cost=10.0,
        ),
    )

    return ScenarioDefinition(
        name="sf5_s01_shortcut_opens",
        policy_name="event_based",
        world_config=WorldConfig(width=WIDTH, height=HEIGHT),
        start=START,
        goal=GOAL,
        initial_obstacles=INITIAL_OBSTACLES + extra_initial_obstacles,
        initial_zones=initial_shortcut_detour_zone,
        max_ticks=500,
        scheduled_events={
            # Die lokale Sperre wird nach der Initialplanung entfernt.
            22: (
                RemoveObstacle(position=Position(24, 10)),
                RemoveObstacle(position=Position(25, 10)),
            ),
        },
        expectation=ScenarioExpectation(
            min_replans=1,
        ),
    )