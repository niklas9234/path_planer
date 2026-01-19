#!/usr/bin/env python3
"""Generate docs/tickets/BOARD.md from Markdown tickets with YAML frontmatter.

Ticket format (YAML frontmatter at top of file):

---
id: TICKET-003
title: "Ticket UI erstellen"
status: backlog            # backlog | in_progress | done
area: sonstiges            # core | backend | frontend | ws | docs | exp | sonstiges
prio: P1                   # P0 | P1 | P2
created: 2026-01-19
---

The script scans recursively under docs/tickets (default) for *.md tickets,
parses the YAML frontmatter (a simple key: value format), and generates
an overview board at docs/tickets/BOARD.md.

Usage:
  python docs/tickets/scripts/build_board.py
  python docs/tickets/scripts/build_board.py --root docs/tickets

Notes:
- No external dependencies.
- If a file has no frontmatter or no 'id', it is ignored.
- BOARD.md itself is ignored.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


STATUSES_ORDER = ["backlog", "in_progress", "done"]
STATUS_TITLES = {
    "backlog": "Backlog",
    "in_progress": "In Progress",
    "done": "Done",
}


@dataclass(frozen=True)
class Ticket:
    id: str
    title: str
    status: str
    area: str
    prio: str
    created: str
    path: Path


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if (len(s) >= 2) and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        return s[1:-1]
    return s


def parse_frontmatter(md_text: str) -> Optional[Dict[str, str]]:
    """Parse YAML frontmatter delimited by leading '---' lines.

    This is intentionally minimal: supports only `key: value` pairs.
    Comments starting with `#` are stripped.
    """
    lines = md_text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return None

    # Find end delimiter
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None

    fm: Dict[str, str] = {}
    for raw in lines[1:end_idx]:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # strip inline comments
        if "#" in line:
            line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = _strip_quotes(v.strip())
        if k:
            fm[k] = v
    return fm


def read_ticket(path: Path) -> Optional[Ticket]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None

    fm = parse_frontmatter(text)
    if not fm:
        return None

    tid = fm.get("id", "").strip()
    if not tid:
        return None

    title = fm.get("title", "").strip() or tid
    status = (fm.get("status", "backlog") or "backlog").strip().lower()
    area = (fm.get("area", "") or "").strip() or "sonstiges"
    prio = (fm.get("prio", "P2") or "P2").strip().upper()
    created = (fm.get("created", "") or "").strip()

    # normalize
    if status not in STATUS_TITLES:
        status = "backlog"

    if not created:
        # Try to use file mtime for a sensible default
        try:
            created_dt = dt.datetime.fromtimestamp(path.stat().st_mtime)
            created = created_dt.date().isoformat()
        except Exception:
            created = ""

    return Ticket(
        id=tid,
        title=title,
        status=status,
        area=area,
        prio=prio,
        created=created,
        path=path,
    )


def collect_tickets(root: Path) -> List[Ticket]:
    tickets: List[Ticket] = []
    for p in root.rglob("*.md"):
        if p.name.upper() == "BOARD.MD":
            continue
        # ignore templates and scripts markdown if any
        if any(part in {"scripts", "templates"} for part in p.parts):
            continue
        t = read_ticket(p)
        if t:
            tickets.append(t)
    return tickets


def sort_key(ticket: Ticket) -> Tuple[int, str, str]:
    prio_order = {"P0": 0, "P1": 1, "P2": 2}
    return (prio_order.get(ticket.prio, 9), ticket.created or "9999-99-99", ticket.id)


def make_board_md(tickets: List[Ticket], root: Path) -> str:
    today = dt.date.today().isoformat()

    # group
    grouped: Dict[str, List[Ticket]] = {s: [] for s in STATUS_TITLES}
    for t in tickets:
        grouped[t.status].append(t)

    for s in grouped:
        grouped[s].sort(key=sort_key)

    total = len(tickets)
    done_count = len(grouped["done"])

    lines: List[str] = []
    lines.append("# Ticket Board")
    lines.append("")
    lines.append(f"Generated: {today}")
    lines.append("")
    lines.append(f"Progress: {done_count} / {total} done")
    lines.append("")
    lines.append("Legend: status = backlog | in_progress | done; prio = P0 (highest) .. P2")
    lines.append("")

    for status in STATUSES_ORDER:
        lines.append(f"## {STATUS_TITLES[status]}")
        lines.append("")
        lines.append("| ID | Title | Area | Prio | Created | File |")
        lines.append("|---|---|---|---|---|---|")

        for t in grouped[status]:
            rel = os.path.relpath(t.path, root)
            # Use a relative markdown link so it works on GitHub/GitLab.
            file_link = f"[{rel}]({rel})"
            safe_title = t.title.replace("|", "\\|")
            safe_area = t.area.replace("|", "\\|")
            lines.append(f"| {t.id} | {safe_title} | {safe_area} | {t.prio} | {t.created} | {file_link} |")

        if not grouped[status]:
            lines.append("| _none_ |  |  |  |  |  |")

        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build docs/ticket-sys/BOARD.md from ticket files")
    parser.add_argument(
        "--root",
        type=str,
        default=str(Path("docs") / "ticket-sys"),
        help="Root directory containing ticket markdown files (default: docs/tickets)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root directory does not exist: {root}")

    tickets = collect_tickets(root)
    board = make_board_md(tickets, root)

    out_path = root / "BOARD.md"
    out_path.write_text(board, encoding="utf-8")
    print(f"Wrote {out_path} ({len(tickets)} tickets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
