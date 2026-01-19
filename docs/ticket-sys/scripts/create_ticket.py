#!/usr/bin/env python3
"""
create_ticket.py (auto-numbering)

Creates a new Markdown ticket file by:
- taking only --area and --title (plus optional --prio)
- auto-determining the next free number per area/prefix
- generating ID as <PREFIX>-<NNN> (PREFIX uppercase)
- generating filename as <ID>-<slug>.md
- writing YAML frontmatter + a static template body

It also writes/updates an index file at:
  docs/ticket-sys/scripts/ticket_index.json

Usage (run from repo root):
  python3 docs/ticket-sys/scripts/create_ticket.py --area core --title "World model basics"
  python3 docs/ticket-sys/scripts/create_ticket.py --area fe --title "D3 path rendering" --prio P2
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ALLOWED_AREA = {"core", "be", "fe", "exp", "doc", "so"}
ALLOWED_PRIO = {"P0", "P1", "P2"}

AREA_TO_PREFIX = {
    "core": "CORE",
    "be": "BE",
    "fe": "FE",
    "exp": "EXP",
    "doc": "DOC",
    "so": "SO",
}

TEMPLATE_BODY = """# {id} – {title}

## Goal
Kurz und präzise beschreiben, **was** mit diesem Ticket erreicht werden soll.
Der Fokus liegt auf dem Ergebnis, nicht auf der Umsetzung.

## Context
(Optional) Kurze Einordnung:
- Warum ist dieses Ticket notwendig?
- Zu welchem größeren Ziel / Kapitel / Architekturteil gehört es?

## Tasks
Konkrete, überprüfbare Arbeitsschritte:
- Aufgabe 1
- Aufgabe 2
- Aufgabe 3

## Done when
Klare Abschlusskriterien. Das Ticket ist **fertig**, wenn:
- Kriterium 1 erfüllt ist
- Kriterium 2 erfüllt ist

## Out of Scope
(Optional) Dinge, die **bewusst nicht** Teil dieses Tickets sind.

## Notes
(Optional)
- Entscheidungen
- Links
- offene Fragen
- Hinweise für spätere Tickets
"""

TICKET_ID_RE = re.compile(r"^(CORE|BE|FE|EXP|DOC|SO)-(\d{3})-")


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "untitled"


def build_frontmatter(ticket_id: str, title: str, area: str, prio: str, created: str) -> str:
    safe_title = title.replace('"', '\\"')
    return (
        "---\n"
        f"id: {ticket_id}\n"
        f'title: "{safe_title}"\n'
        "status: backlog\n"
        f"area: {area}\n"
        f"prio: {prio}\n"
        f"created: {created}\n"
        "---\n"
    )


def scan_max_numbers(tickets_dir: Path) -> dict:
    index = {p: 0 for p in AREA_TO_PREFIX.values()}
    for p in tickets_dir.glob("*.md"):
        m = TICKET_ID_RE.match(p.name)
        if not m:
            continue
        prefix = m.group(1).upper()
        n = int(m.group(2))
        if prefix in index and n > index[prefix]:
            index[prefix] = n
    return index


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create a new Markdown ticket file (auto-numbering).")
    parser.add_argument("--area", required=True, help="Area: core|be|fe|exp|doc|so")
    parser.add_argument("--title", required=True, help="Ticket title (human readable)")
    parser.add_argument("--prio", default="P1", help="Priority: P0|P1|P2 (default: P1)")
    parser.add_argument(
        "--root",
        default=None,
        help="Ticket system root (defaults to docs/ticket-sys relative to script location).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite if the target file already exists (default: do not overwrite).",
    )
    args = parser.parse_args(argv)

    area = args.area.strip().lower()
    title = args.title.strip()
    prio = args.prio.strip().upper()

    if area not in ALLOWED_AREA:
        print(f"Error: invalid --area '{area}'. Allowed: {', '.join(sorted(ALLOWED_AREA))}", file=sys.stderr)
        return 2
    if not title:
        print("Error: --title must not be empty.", file=sys.stderr)
        return 2
    if prio not in ALLOWED_PRIO:
        print(f"Error: invalid --prio '{prio}'. Allowed: {', '.join(sorted(ALLOWED_PRIO))}", file=sys.stderr)
        return 2

    script_path = Path(__file__).resolve()
    default_root = script_path.parents[1]  # .../docs/ticket-sys
    root = Path(args.root).resolve() if args.root else default_root

    tickets_dir = root / "tickets"
    scripts_dir = root / "scripts"

    if not tickets_dir.exists():
        print(f"Error: tickets directory not found: {tickets_dir}", file=sys.stderr)
        return 2

    prefix = AREA_TO_PREFIX[area]

    # Helper step: scan tickets and persist index for transparency
    index = scan_max_numbers(tickets_dir)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    idx_path = scripts_dir / "ticket_index.json"
    idx_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    next_num = index.get(prefix, 0) + 1
    ticket_id = f"{prefix}-{next_num:03d}"

    slug = slugify(title)
    out_path = tickets_dir / f"{ticket_id}-{slug}.md"

    if out_path.exists() and not args.force:
        print(f"Error: ticket file already exists: {out_path}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 2

    created = date.today().isoformat()
    frontmatter = build_frontmatter(ticket_id, title, area, prio, created)
    body = TEMPLATE_BODY.format(id=ticket_id, title=title)
    out_path.write_text(frontmatter + "\n" + body, encoding="utf-8")

    print(f"Updated index: {idx_path}")
    print(f"Created ticket: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
