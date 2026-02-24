from __future__ import annotations

from dataclasses import dataclass

from core.domain import Position, RobotState, World


@dataclass(slots=True)
class SimulationState:
    world: World
    robot: RobotState
    dirty_replan: bool = False
    tick: int = 0

    @classmethod
    def create(
        cls,
        *,
        width: int,
        height: int,
        robot_position: Position,
        cell_size_m: float = 1.0,
        base_cost: float = 1.0,
    ) -> SimulationState:
        world = World(
            width=width,
            height=height,
            cell_size_m=cell_size_m,
            base_cost=base_cost,
        )
        world.assert_in_bounds(robot_position.x, robot_position.y)
        robot = RobotState(position=robot_position)
        return cls(world=world, robot=robot)
