---
id: CORE-005
title: "Planner interface + A_star"
status: backlog
area: core
prio: P1
created: 2026-02-19
change -status between - backlog | in_progress | done - 
change -prio between - P0 | P1 | P2 -
---

# CORE-005 – Planner interface + A_star

## Context
We need one working planner (A*) to enable replanning + evaluation pipeline.

## Scope / Deliverables

- Planner interface/protocol: plan(world, start, goal) -> PlanResult

- PlanResult includes:

  - path: list[Position]

  - total_cost: float

expanded_nodes: int

success: bool (or infer from path)

AStarPlanner:

uses world.neighbors(...)

supports weighted costs + 8-dir

Heuristic:

Octile distance (matches 8-dir + diag factor)