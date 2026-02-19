---
id: CORE-004
title: "Domain-Types"
status: backlog
area: core
prio: P1
created: 2026-02-18
change -status between - backlog | in_progress | done - 
change -prio between - P0 | P1 | P2 -
---

# CORE-004 – Domain-Types


## Context
We need small domain types that can be shared across planning/simulation and stay independent from IO.

## Scope / Deliverables

- Position(x:int, y:int):

- immutable, hashable (usable in sets/dicts)

- helper .as_tuple() is fine

## RobotState:

- position: Position

- goal: Position | None

- path: list[Position] + path_index

- basic helpers: set_goal, set_path, next_waypoint, advance_waypoint, at_goal, clear_plan

- No World dependency inside RobotState (bounds checks belong to World/Engine)