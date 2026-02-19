from dataclasses import dataclass

from domain.Position import Position
from Typing import List


@dataclass
class PlanResult(frozen=True):
  path: List[Position]
  total_cost: int
