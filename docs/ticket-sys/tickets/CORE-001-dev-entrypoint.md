---
id: CORE-001
title: "dev entrypoint"
status: done
area: core
prio: P1
created: 2026-02-12
change -status between - backlog | in_progress | done - 
change -prio between - P0 | P1 | P2 -
---

# CORE-001 – dev entrypoint

## Goal
einheitlicher Einstiegspunkt für Entwicklungs- und Testbefehle

## Tasks
- Makefile bzw. Dev-Entry-Point einführen mit folgenden Möglichkeiten:
```go
make backend-run     // startet Backend-Server
make frontend-run    // startet Frontend-Dev-Server
make dev             // startet Backend + Frontend (parallel)
make test            // führt Backend-Tests + Frontend-Tests aus
make format          // cleanup (z.B. mit black/ruff + prettier/eslint)
```


## Result

- [Makefile](../../../Makefile) wurde erstellt.
- make backend-rund funktioniert 
- künftige Überarbeitungen werden nicht zwingend mit neuen Tickets dokumentiert aber eventuell in diesem Ticket. 


## Updates
