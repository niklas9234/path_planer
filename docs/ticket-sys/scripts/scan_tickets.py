#!/usr/bin/env python3
"""
scan_tickets.py

Scans the ticket directory and writes an index file with the highest used ticket
number per prefix. This enables auto-incrementing IDs when creating tickets.

Expected layout:
  docs/ticket-sys/
    scripts/
      scan_tickets.py
      create_ticket.py
      ticket_index.json   <- generated
    tickets/
      CORE-001-....
      FE-002-....

Run (from repo root):
  python3 docs/ticket-sys/scripts/scan_tickets.py

It will write:
  docs/ticket-sys/scripts/ticket_index.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

AREA_TO_PREFIX = {
    "core": "CORE",
    "be": "BE",
    "fe": "FE",
    "exp": "EXP",
    "doc": "DOC",
    "so": "SO",
}

TICKET_ID_RE = re.compile(r"^(CORE|BE|FE|EXP|DOC|SO)-(\d{3})-", re.IGNORECASE)


def scan_tickets(tickets_dir: Path) -> dict:
    """Return {PREFIX: max_number} for all known prefixes."""
    index = {prefix: 0 for prefix in AREA_TO_PREFIX.values()}

    if not tickets_dir.exists():
        raise FileNotFoundError(f"tickets directory not found: {tickets_dir}")

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
    parser = argparse.ArgumentParser(description="Scan tickets and write ticket_index.json")
    parser.add_argument(
        "--root",
        default=None,
        help="Ticket system root (defaults to docs/ticket-sys relative to script location).",
    )
    parser.add_argument(
        "--out",
        default="ticket_index.json",
        help="Output filename inside scripts/ (default: ticket_index.json).",
    )
    args = parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    default_root = script_path.parents[1]  # .../docs/ticket-sys
    root = Path(args.root).resolve() if args.root else default_root

    tickets_dir = root / "tickets"
    scripts_dir = root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    index = scan_tickets(tickets_dir)

    out_path = scripts_dir / args.out
    out_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Wrote index: {out_path}")
    for k in sorted(index.keys()):
        print(f"  {k}: {index[k]:03d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
