from core.domain import AddObstacle, AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    width = 26
    height = 18

    obstacles: set[tuple[int, int]] = set()

    def rect(x0: int, y0: int, x1: int, y1: int) -> None:
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                obstacles.add((x, y))

    # ------------------------------------------------------------------
    # Kartenmodell: grobe Rekonstruktion des Bildes
    # ------------------------------------------------------------------
    #
    # Idee:
    # - Start unten links
    # - Ziel oben rechts
    # - zentrale Trennstruktur mit zwei möglichen Übergängen:
    #     * oberer Übergang bleibt offen
    #     * mittlerer/pinker Übergang wird nach der Initialplanung blockiert
    # - zusätzliche Hindernisse orientieren sich an den schwarzen Formen im Bild
    #
    # Koordinatenursprung: (0, 0) links oben
    # ------------------------------------------------------------------

    # Zentrale vertikale Trennung zwischen linker und rechter Hälfte.
    # Zwei Öffnungen:
    # - y=3   -> dauerhafter oberer Umweg
    # - y=11  -> anfangs offener "pinker" Durchgang, der später blockiert wird
    for y in range(height):
        if y not in (3, 11):
            obstacles.add((12, y))

    # Linke obere / mittlere schwarze Struktur
    rect(0, 5, 8, 5)
    rect(8, 3, 8, 11)
    rect(0, 8, 8, 8)

    # Linke untere schwarze Struktur
    rect(0, 13, 6, 13)
    rect(6, 13, 6, 14)
    rect(7, 16, 7, 17)

    # Rechte obere schwarze Struktur
    rect(18, 1, 18, 5)

    # Rechte mittlere / untere schwarze Struktur
    rect(15, 11, 21, 12)
    rect(20, 9, 21, 12)
    rect(14, 16, 20, 16)

    start = Position(3, 16)
    goal = Position(22, 2)

    scheduled_events: dict[int, list[object]] = {}

    def add_event(tick: int, event: object) -> None:
        scheduled_events.setdefault(tick, []).append(event)

    # ------------------------------------------------------------------
    # Pinker Bereich aus dem Bild:
    # nach der ersten Planung wird der zentrale Übergang blockiert.
    #
    # Ich nehme hier AddObstacle(position=...) an.
    # Falls deine Event-Klasse stattdessen z. B. "cell=" verwendet,
    # musst du nur diese eine Zeile anpassen.
    # ------------------------------------------------------------------
    add_event(
        2,
        AddObstacle(
            position=Position(12, 11),
        ),
    )

    # ------------------------------------------------------------------
    # Gelbe Felder aus dem Bild als temporäre Slow-Zones
    # Großteils bewusst abseits des späteren Umwegs.
    # Eine Zone liegt näher am oberen Umweg, damit path_affected
    # nicht nur wegen der Brückensperrung replanned.
    # ------------------------------------------------------------------

    zone_duration = 3
    extra_cost = 10.0

    # Oben links
    add_event(
        4,
        AddZone(
            zone_type=ZoneType.SLOW,
            cells=(
                Position(3, 2),
                Position(3, 3),
                Position(4, 2),
                Position(4, 3),
            ),
            duration_ticks=zone_duration,
            extra_cost=extra_cost,
        ),
    )

    # Oben mittig
    add_event(
        7,
        AddZone(
            zone_type=ZoneType.SLOW,
            cells=(
                Position(10, 1),
                Position(10, 2),
                Position(11, 1),
                Position(11, 2),
            ),
            duration_ticks=zone_duration,
            extra_cost=extra_cost,
        ),
    )

    # Oben rechts
    add_event(
        10,
        AddZone(
            zone_type=ZoneType.SLOW,
            cells=(
                Position(16, 0),
                Position(17, 0),
            ),
            duration_ticks=zone_duration,
            extra_cost=extra_cost,
        ),
    )

    # Rechts oben / mittig
    add_event(
        13,
        AddZone(
            zone_type=ZoneType.SLOW,
            cells=(
                Position(16, 5),
                Position(17, 5),
            ),
            duration_ticks=zone_duration,
            extra_cost=extra_cost,
        ),
    )

    # Linke mittlere vertikale Zone
    add_event(
        16,
        AddZone(
            zone_type=ZoneType.SLOW,
            cells=(
                Position(9, 6),
                Position(9, 7),
            ),
            duration_ticks=zone_duration,
            extra_cost=extra_cost,
        ),
    )

    # Untere vertikale Zone
    add_event(
        19,
        AddZone(
            zone_type=ZoneType.SLOW,
            cells=(
                Position(15, 13),
                Position(15, 14),
            ),
            duration_ticks=zone_duration,
            extra_cost=extra_cost,
        ),
    )

    # Eine Zone nahe des oberen Umwegs, damit path_affected
    # hier typischerweise noch 1-2 zusätzliche Replans bekommt.
    add_event(
        22,
        AddZone(
            zone_type=ZoneType.SLOW,
            cells=(
                Position(16, 3),
                Position(17, 3),
            ),
            duration_ticks=2,
            extra_cost=12.0,
        ),
    )

    initial_obstacles = tuple(
        Position(x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) in obstacles
    )

    return ScenarioDefinition(
        name="s09_bridge_cutoff_offpath_noise",
        policy_name="event_based",
        world_config=WorldConfig(width=width, height=height),
        start=start,
        goal=goal,
        initial_obstacles=initial_obstacles,
        initial_zones=(),
        max_ticks=300,
        scheduled_events={
            tick: tuple(events)
            for tick, events in scheduled_events.items()
        },
        expectation=ScenarioExpectation(
            min_replans=1,
        ),
    )
