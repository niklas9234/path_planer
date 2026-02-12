---
id: CORE-002
title: "shared-protocol"
status: backlog
area: core
prio: P1
created: 2026-02-12
change -status between - backlog | in_progress | done - 
change -prio between - P0 | P1 | P2 -
---

# CORE-002 – shared-protocol

## Goal
Definition einer gemeinsamen, versionierten Protokollstruktur für WebSocket-Messages.
- Vermeidung von „undefined data“-Fehlern
- Klare Vertragsdefinition zwischen Frontend und Backend
- saubere Schnittstellendefinition

## Tasks
Konkrete, überprüfbare Arbeitsschritte:
- Erstellen eines festen Verzeichniss für JSON protocoll-Schemata
- Möglichkeit der Versionierung 

## Regeln

- Frontend darf nichts aus Backend importieren
- Backend darf nichts aus Frontend importieren