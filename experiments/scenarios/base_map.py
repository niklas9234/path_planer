from core.domain import Position

# Base Map
# Gemeinsame Kartenbasis für mehrere Szenarien.
# Diese Datei enthält nur die Map-Struktur und gemeinsam genutzte Konstanten,
# damit einzelne Szenariodateien dieselbe Karte importieren können.

WIDTH = 28
HEIGHT = 20

START = Position(1, 1)
GOAL = Position(25, 18)


def _rect_cells(x1: int, y1: int, x2: int, y2: int) -> tuple[Position, ...]:
    """Inclusive rectangle helper."""
    return tuple(
        Position(x, y)
        for x in range(x1, x2 + 1)
        for y in range(y1, y2 + 1)
    )


def _central_wall_cells() -> tuple[Position, ...]:
    ys = (19, 18, 17, 14, 13, 12, 11, 9, 8, 7, 6, 5, 2, 1, 0)
    return tuple(Position(x, y) for x in (13, 14) for y in ys)


INITIAL_OBSTACLES: tuple[Position, ...] = (
    # Linker Bereich: Regal-Strukturen
    *_rect_cells(3, 12, 4, 18),
    *_rect_cells(3, 1, 4, 7),
    *_rect_cells(7, 9, 8, 16),
    *_rect_cells(7, 0, 8, 6),

    # Linke Nischen / Sackgassen
    *_rect_cells(0, 16, 1, 17),
    *_rect_cells(0, 3, 1, 4),

    # Zentrale Doppelwand mit drei Toren
    *_central_wall_cells(),

    # Rechter Bereich
    *_rect_cells(18, 13, 19, 18),
    *_rect_cells(18, 1, 19, 9),
    *_rect_cells(22, 8, 23, 16),
    *_rect_cells(26, 3, 27, 11),

    # Untere Barriere
    *_rect_cells(16, 0, 24, 1),

    # Obere Inseln
    *_rect_cells(16, 18, 19, 19),
)
