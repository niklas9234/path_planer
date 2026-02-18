---
id: CORE-003
title: "World-Grid"
status: backlog
area: core
prio: P1
created: 2026-02-18
change -status between - backlog | in_progress | done - 
change -prio between - P0 | P1 | P2 -
---

# CORE-003 – World-Grid

## Context
We need a stable grid world as the single source of truth for planning + simulation.

## Scope / Deliverables

- World(width, height, cell_size_m=..., connectivity=8, base_cost=...)

- Internal layers:

- blocked[y][x] -> bool

- extra_cost[y][x] -> float (>= 0)

## Core APIs:

- in_bounds(x,y)

- is_blocked(x,y)

- set_obstacle/add_obstacle/remove_obstacle

- set_extra_cost/add_cost/clear_extra_cost

- neighbors(x,y) returns reachable neighbors with step cost (diag factor)

- Movement: 8-connectivity with diagonal factor sqrt(2)

