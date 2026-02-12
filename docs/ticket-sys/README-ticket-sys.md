# Ticket System – Project Task Tracking

## Ziel

Dieses Ticketsystem dient der **strukturierten, nachvollziehbaren Planung und Umsetzung**
der Bachelorarbeit.
Es ersetzt klassische Projektmanagement-Tools durch ein **leichtgewichtiges,
versionskontrolliertes System**, das direkt im Repository lebt.

Ziele des Systems:
- klare Strukturierung der Arbeitsschritte
- saubere Trennung nach Architektur-Schichten (Frontend, Backend, Core, etc.)
- vollständige Nachvollziehbarkeit über Git
- minimaler organisatorischer Overhead (Solo-Projekt)
- langfristig lern- und wiederverwendbar

---

## Grundidee

- **Jedes Ticket ist eine eigene Markdown-Datei**
- Metadaten werden über **YAML Frontmatter** definiert
- Der Ticket-Status (`backlog`, `in_progress`, `done`) ist maschinenlesbar
- Eine zentrale Datei (`BOARD.md`) zeigt alle Tickets gruppiert nach Status
- `BOARD.md` wird **automatisch generiert**, nicht manuell gepflegt

Dieses System ist bewusst einfach gehalten und verzichtet auf externe Tools
(Jira, Trello, Notion), um Fokus und Reproduzierbarkeit zu gewährleisten.

---

## Ordnerstruktur

```text
docs/ticket-sys/
├─ BOARD.md            # Generierte Ticket-Übersicht (UI)
├─ README.md           # Diese Datei
├─ scripts/
│  └─ build_board.py   # Generator für BOARD.md
└─ tickets/
   ├─ CORE-001-...
   ├─ FE-002-...
   └─ ...
```

---

## Ticket-Dateinamen

### Format

```
<PREFIX>-<NNN>-<slug>.md
```

### Beispiele

- CORE-001-world-model.md
- BE-002-ws-message-router.md
- FE-003-d3-path-rendering.md
- DOC-004-architecture-diagrams.md
- SO-005-ticket-ui.md

### Prefixe und Bedeutung

| Prefix | Bedeutung |
|------|----------|
| CORE | Core / Domain / Simulation |
| BE   | Backend / Application / Adapter |
| FE   | Frontend |
| EXP  | Experimente / Auswertung |
| DOC  | Dokumentation |
| SO   | Sonstiges (Setup, Tools, Repo) |

### Nummerierung

- Die Nummer ist immer **dreistellig** (`001`, `002`, …)
- Die Nummerierung erfolgt **pro Prefix**
- Das Ticket wird primär über `<PREFIX>-<NNN>` identifiziert

---

## Schreibweise (Slug)

- ausschließlich Kleinbuchstaben
- Wörter mit Bindestrich (`-`) trennen
- keine Sonderzeichen oder Umlaute
- maximal 4–5 Wörter

Beispiele:
- ws-message-codec
- dynamic-replanning-trigger
- ticket-board-generator

---

## Ticket-Format (Pflicht)

Jede Ticket-Datei **muss** YAML Frontmatter enthalten:

```yaml
---
id: CORE-001
title: "World model basics"
status: backlog        # backlog | in_progress | done
area: core             # core | be | fe | exp | doc | so
prio: P1               # P0 | P1 | P2
created: 2026-01-19
---
```

### Status-Werte

- `backlog` – geplant, noch nicht begonnen
- `in_progress` – aktuell in Bearbeitung
- `done` – abgeschlossen

### Prioritäten

- `P0` – kritisch / blocker
- `P1` – normal
- `P2` – optional / nice-to-have

---

## Empfohlene Ticket-Struktur (Inhalt)

Nach dem Frontmatter folgt freier Markdown-Text:

```md
## Goal
Kurzbeschreibung des Ziels.

## Tasks
- [ ] Teilaufgabe 1
- [ ] Teilaufgabe 2

## Done when
- klare, überprüfbare Abschlusskriterien

## Notes
Optionale Gedanken, Links, Entscheidungen.
```

---

## Ticket-Workflow

1. **Neues Ticket anlegen**
   - Datei in `docs/ticket-sys/tickets/`
   - `status: backlog`

2. **Ticket starten**
   - Status auf `in_progress` ändern

3. **Ticket abschließen**
   - Status auf `done` ändern

4. **Ticket Board aktualisieren**
   - Script ausführen (siehe unten)

5. **Commit**
   - Commit-Nachricht referenziert Ticket-ID  
     Beispiel: `CORE: implement world model (CORE-001)`

---

## Ticket Board (UI)

Die Datei `BOARD.md` stellt alle Tickets gruppiert nach Status dar:

- Backlog
- In Progress
- Done

⚠️ **Wichtig:**
- `BOARD.md` wird automatisch generiert
- Änderungen an `BOARD.md` sollten **nicht manuell** vorgenommen werden
- Die Datei ist ein abgeleitetes Artefakt

---

## Script ausführen (Board generieren)

### Vom Repository-Root aus:

```bash
python3 docs/ticket-sys/scripts/build_board.py
```

### Ergebnis:

- `docs/ticket-sys/BOARD.md` wird neu erzeugt oder aktualisiert
- Alle Tickets werden anhand ihres `status` gruppiert

---

## Design-Entscheidungen

- kein externes Projektmanagement-Tool
- Tickets sind Teil der Versionsgeschichte (Git)
- klare Architektur-Zuordnung über Prefixe
- Fokus auf Nachvollziehbarkeit statt Management
- geeignet für Einzelarbeit und wissenschaftliche Projekte

Dieses Ticketsystem ist bewusst pragmatisch gestaltet und
bildet die Grundlage für eine strukturierte, reproduzierbare Entwicklung
im Rahmen der Bachelorarbeit.



## Ticket-Erstellung per Kommandozeile

Zur Vereinfachung und Standardisierung der Ticket-Erstellung steht ein
CLI-Skript (`create_ticket.py`) zur Verfügung.  
Das Skript erzeugt neue Ticket-Dateien automatisch auf Basis eines
vordefinierten Templates und stellt sicher, dass alle Metadaten
einheitlich und korrekt gesetzt werden.

Beim Ausführen des Skripts werden die benötigten Informationen per
Kommandozeilenparameter übergeben. Auf Basis dieser Parameter wird
eine neue Markdown-Datei im Ordner `docs/ticket-sys/tickets/` erstellt.
Standardwerte wie der Ticket-Status (`backlog`) sowie das Erstellungsdatum
werden automatisch gesetzt.

### Verwendung

```bash
python3 docs/ticket-sys/scripts/create_ticket.py \
  --area be \
  --title "World model basics"

```
### Parameter

```bash
--area
# AREA - SIEHE "Prefixe und Bedeutung"

--title
# Titel - Lesbarer Titel des Tickets. Der Titel wird zusätzlich zur Generierung des Dateinamens (Slug) verwendet.

--area 
# Bereich - (optional) Bereich des Tickets (core, be, fe, exp, doc, so). Wird nicht explizit angegeben, leitet das Skript den Bereich automatisch aus dem Prefix der Ticket-ID ab.

--prio 
# Priorität - (optional) Priorität des Tickets (P0, P1, P2). Standardwert ist P1.

--force 
# Überschreiben - (optional) Überschreibt eine bereits existierende Ticket-Datei.
```


