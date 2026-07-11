#!/usr/bin/env python3
"""Validate requirement registry and traceability consistency."""

from __future__ import annotations

import re
import sys
from pathlib import Path

VALID_STATUSES = {"Documented", "Approved", "In Progress", "Implemented", "Verified", "Deferred", "Blocked"}
REGISTRY_PREFIXES = ("FR", "NFR", "DATA", "ARCH", "API", "DB", "SEC", "SAFE", "MET", "DOC", "QUALITY", "CI", "DEMO")
ID_RE = re.compile(r"\b([A-Z]+)-(\d{3})\b")
RANGE_RE = re.compile(r"\b[A-Z]+-\d{3}\.\.\d{3}\b")


def rows(markdown: str) -> list[list[str]]:
    parsed: list[list[str]] = []
    for line in markdown.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or set(cells[0]) <= {"-"}:
            continue
        parsed.append(cells)
    return parsed


def registry_ids(requirements: str) -> set[str]:
    ids: set[str] = set()
    in_registry = False
    for line in requirements.splitlines():
        if line.startswith("## Requirement Registry"):
            in_registry = True
            continue
        if in_registry and line.startswith("## "):
            break
        if in_registry:
            match = re.match(r"\|\s*([A-Z]+-\d{3})\s*\|", line)
            if match and match.group(1).split("-")[0] in REGISTRY_PREFIXES:
                ids.add(match.group(1))
    return ids


def traceability_ids(traceability: str) -> tuple[set[str], list[str]]:
    ids: set[str] = set()
    statuses: list[str] = []
    for row in rows(traceability):
        if row[0] == "Requirement ID" or row[0].startswith("---"):
            continue
        if ID_RE.fullmatch(row[0]):
            ids.add(row[0])
            if len(row) >= 10:
                statuses.append(row[9])
    return ids, statuses


def all_defined_ids(requirements: str) -> set[str]:
    return {m.group(0) for m in ID_RE.finditer(requirements)}


def main() -> int:
    root = Path(".")
    req = (root / "docs" / "01-requirements.md").read_text(encoding="utf-8")
    trace = (root / "docs" / "11-requirement-traceability.md").read_text(encoding="utf-8")
    docs_text = "\n".join(p.read_text(encoding="utf-8") for p in (root / "docs").glob("*.md"))
    errors: list[str] = []

    if RANGE_RE.search(docs_text):
        errors.append("range syntax such as MET-009..011 is not allowed")

    reg = registry_ids(req)
    trace_ids, statuses = traceability_ids(trace)
    missing = sorted(reg - trace_ids)
    if missing:
        errors.append("registry IDs missing from traceability: " + ", ".join(missing))

    for status in statuses:
        if status not in VALID_STATUSES:
            errors.append(f"invalid traceability status: {status}")

    defined = all_defined_ids(req) | {"AC-" + f"{i:03d}" for i in range(1, 100)} | {"WF-" + f"{i:03d}" for i in range(1, 100)}
    referenced = {m.group(0) for m in ID_RE.finditer(trace)}
    undefined = sorted(id_ for id_ in referenced if id_.split("-")[0] not in {"AC", "WF"} and id_ not in defined)
    if undefined:
        errors.append("undefined IDs referenced in traceability: " + ", ".join(undefined))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"requirement IDs ok: {len(reg)} registry IDs traced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
