#!/usr/bin/env python3
"""Validate prompt history records and exact-prompt checksums."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PROMPT_ID_RE = re.compile(r"^PROMPT-\d{4}$")
FILENAME_RE = re.compile(r"^(PROMPT-\d{4})-[a-z0-9-]+\.md$")
CHECKSUM_RE = re.compile(r"^[0-9a-f]{64}$")
FENCE_RE = re.compile(r"## Exact Prompt\s*\n(?P<fence>`{3,})text\n(?P<prompt>.*?)\n(?P=fence)", re.DOTALL)
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SECRET_PATTERNS = [
    re.compile(r"(?i)(secret|token|password|api[_-]?key)\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{16,})"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"sonar_[A-Za-z0-9_\-.]{20,}", re.IGNORECASE),
]
PLACEHOLDER_VALUES = {"placeholder", "example", "changeme", "redacted", "<token>", "<secret>"}
REQUIRED_METADATA = {
    "Prompt ID": ("Prompt ID",),
    "Prompt Type": ("Prompt Type",),
    "Date": ("Date",),
    "Objective": ("Objective",),
    "Module": ("Module",),
    "Requirement IDs": ("Requirement IDs",),
    "Exact Prompt SHA-256": ("Exact Prompt SHA-256",),
    "Exact Prompt": ("Exact Prompt",),
    "In Scope": ("In Scope",),
    "Out of Scope": ("Out of Scope",),
    "Files Read": ("Files Read",),
    "Files Changed": ("Files Changed",),
    "Checks Run": ("Checks Run", "Tests/Checks Run", "Validation Performed"),
    "Sonar Status": ("Sonar Status", "SonarQube Status"),
    "Audit Status": ("Audit Status", "Human Audit Status"),
    "Final Outcome": ("Final Outcome",),
}


@dataclass
class PromptRecord:
    path: Path
    text: str


def headings(text: str) -> set[str]:
    return {match.group(1).strip() for match in HEADING_RE.finditer(text)}


def canonical_heading(actual_headings: set[str], canonical: str) -> str | None:
    for candidate in REQUIRED_METADATA[canonical]:
        if candidate in actual_headings:
            return candidate
    return None


def heading_value(text: str, heading: str) -> str | None:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s+|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def prompt_text(text: str) -> str | None:
    match = FENCE_RE.search(text)
    if not match:
        return None
    return match.group("prompt")


def has_obvious_secret(text: str) -> bool:
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(match.lastindex or 0).strip().strip("'\"")
            normalized = value.lower()
            if normalized in PLACEHOLDER_VALUES or normalized.startswith("<"):
                continue
            return True
    return False


def validate_record(record: PromptRecord) -> list[str]:
    errors: list[str] = []
    filename_match = FILENAME_RE.fullmatch(record.path.name)
    if not filename_match:
        errors.append("filename must start with PROMPT-XXXX and use a kebab-case suffix")

    actual_headings = headings(record.text)
    for canonical in REQUIRED_METADATA:
        if canonical_heading(actual_headings, canonical) is None:
            errors.append(f"missing required metadata: {canonical}")

    prompt_heading = canonical_heading(actual_headings, "Prompt ID") or "Prompt ID"
    metadata_id = heading_value(record.text, prompt_heading)
    if not metadata_id:
        errors.append("missing Prompt ID value")
    elif not PROMPT_ID_RE.fullmatch(metadata_id):
        errors.append("invalid Prompt ID value")
    elif filename_match and metadata_id != filename_match.group(1):
        errors.append("filename Prompt ID does not match metadata Prompt ID")

    exact = prompt_text(record.text)
    if exact is None:
        errors.append("missing valid exact prompt fenced block")
    checksum_heading = canonical_heading(actual_headings, "Exact Prompt SHA-256") or "Exact Prompt SHA-256"
    checksum = heading_value(record.text, checksum_heading)
    if not checksum:
        errors.append("missing checksum")
    elif not CHECKSUM_RE.fullmatch(checksum):
        errors.append("invalid checksum format")
    elif exact is not None and hashlib.sha256(exact.encode("utf-8")).hexdigest() != checksum:
        errors.append("checksum mismatch")

    if has_obvious_secret(record.text):
        errors.append("record appears to contain an obvious secret value")
    return errors


def validate_history(root: Path) -> dict[Path, list[str]]:
    history = root / "prompts" / "history"
    records = sorted(history.glob("PROMPT-*.md"))
    failures: dict[Path, list[str]] = {}
    if not records:
        failures[history] = ["no prompt records found"]
        return failures
    for path in records:
        errors = validate_record(PromptRecord(path=path, text=path.read_text(encoding="utf-8-sig")))
        if errors:
            failures[path] = errors
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args(argv)
    failures = validate_history(Path(args.repo).resolve())
    if failures:
        for path, errors in failures.items():
            print(f"{path}: {', '.join(errors)}", file=sys.stderr)
        return 1
    print("prompt records ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
