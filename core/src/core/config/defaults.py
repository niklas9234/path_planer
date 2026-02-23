from __future__ import annotations

from math import sqrt

# World/grid defaults
DEFAULT_CELL_SIZE_M: float = 1.0
DEFAULT_CONNECTIVITY: int = 8
DEFAULT_BASE_COST: float = 1.0
DEFAULT_EXTRA_COST: float = 0.0

# Geometric factors
CARDINAL_STEP_FACTOR: float = 1.0
DIAGONAL_STEP_FACTOR: float = sqrt(2.0)

# Robot/simulation defaults
DEFAULT_ROBOT_SPEED_MPS: float = 1.0
