#!/usr/bin/env python3
"""Validate prompt-to-commit traceability for every introduced commit."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ZERO_SHA = "0" * 40
PROMPT_RE = re.compile(r"^Prompt-ID:\s*(PROMPT-\d{4})\b", re.MULTILINE)
REQ_RE = re.compile(r"^Requirement-IDs:\s*.+", re.MULTILINE)
MODULE_RE = re.compile(r"^Module:\s*.+", re.MULTILINE)
TESTS_RE = re.compile(r"^Tests:\s*.+", re.MULTILINE)


@dataclass
class CommitRecord:
    sha: str
    message: str
    parents: int = 1
    author: str = ""


def run_git(args: list[str], repo: Path) -> str:
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def commit_message(repo: Path, sha: str) -> str:
    return run_git(["log", "-1", "--pretty=%B", sha], repo)


def parent_count(repo: Path, sha: str) -> int:
    line = run_git(["rev-list", "--parents", "-n", "1", sha], repo)
    return max(0, len(line.split()) - 1)


def commit_author(repo: Path, sha: str) -> str:
    return run_git(["log", "-1", "--pretty=%an <%ae>", sha], repo)


def commits_for_event(repo: Path, event_name: str, before: str, sha: str, base: str, head: str) -> list[str]:
    event_name = event_name or "manual"
    if event_name == "pull_request":
        if not base or not head:
            raise ValueError("pull_request validation requires base and head SHAs")
        return rev_list(repo, f"{base}..{head}")
    if event_name == "push":
        if not sha:
            raise ValueError("push validation requires github.sha")
        if not before or before == ZERO_SHA:
            return rev_list(repo, sha)
        return rev_list(repo, f"{before}..{sha}")
    if before and sha:
        return rev_list(repo, f"{before}..{sha}")
    return [run_git(["rev-parse", "HEAD"], repo)]


def rev_list(repo: Path, revision: str) -> list[str]:
    output = run_git(["rev-list", "--reverse", revision], repo)
    return [line for line in output.splitlines() if line.strip()]


def load_legacy_shas(repo: Path) -> set[str]:
    ledger = repo / "docs" / "commit-ledger.md"
    legacy: set[str] = set()
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if "| LEGACY" in line or "| Legacy" in line:
                parts = [part.strip() for part in line.strip("|").split("|")]
                if parts:
                    legacy.add(parts[0])
    env = os.environ.get("TRACEABILITY_LEGACY_SHAS", "")
    legacy.update(sha.strip() for sha in env.split(",") if sha.strip())
    return legacy


def is_exempt(commit: CommitRecord, legacy_shas: set[str]) -> bool:
    if commit.sha in legacy_shas:
        return True
    first_line = commit.message.splitlines()[0] if commit.message else ""
    if commit.parents > 1 and first_line.startswith("Merge "):
        return True
    if "github-actions" in commit.author.lower() and first_line.startswith("Merge "):
        return True
    return False


def matching_prompt_exists(repo: Path, prompt_id: str) -> bool:
    return any((repo / "prompts" / "history").glob(f"{prompt_id}-*.md"))


def validate_commit(repo: Path, commit: CommitRecord, legacy_shas: set[str]) -> list[str]:
    if is_exempt(commit, legacy_shas):
        return []
    errors: list[str] = []
    if not REQ_RE.search(commit.message):
        errors.append("missing Requirement-IDs")
    prompt_match = PROMPT_RE.search(commit.message)
    if not prompt_match:
        errors.append("missing Prompt-ID")
    elif not matching_prompt_exists(repo, prompt_match.group(1)):
        errors.append(f"missing prompt file for {prompt_match.group(1)}")
    if not MODULE_RE.search(commit.message):
        errors.append("missing Module")
    if not TESTS_RE.search(commit.message):
        errors.append("missing Tests")
    return errors


def validate_records(repo: Path, records: list[CommitRecord], legacy_shas: set[str] | None = None) -> dict[str, list[str]]:
    legacy_shas = legacy_shas or set()
    failures: dict[str, list[str]] = {}
    for record in records:
        errors = validate_commit(repo, record, legacy_shas)
        if errors:
            failures[record.sha] = errors
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--event-name", default=os.environ.get("GITHUB_EVENT_NAME", "manual"))
    parser.add_argument("--before", default=os.environ.get("GITHUB_EVENT_BEFORE", ""))
    parser.add_argument("--sha", default=os.environ.get("GITHUB_SHA", ""))
    parser.add_argument("--base", default=os.environ.get("GITHUB_BASE_SHA", ""))
    parser.add_argument("--head", default=os.environ.get("GITHUB_HEAD_SHA", ""))
    parser.add_argument("--commits", nargs="*", help="Explicit commit SHAs for local validation")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    try:
        shas = args.commits or commits_for_event(repo, args.event_name, args.before, args.sha, args.base, args.head)
        legacy = load_legacy_shas(repo)
        records = [
            CommitRecord(sha=s, message=commit_message(repo, s), parents=parent_count(repo, s), author=commit_author(repo, s))
            for s in shas
        ]
        failures = validate_records(repo, records, legacy)
    except Exception as exc:
        print(f"traceability validator error: {exc}", file=sys.stderr)
        return 2

    if failures:
        for sha, errors in failures.items():
            print(f"{sha}: {', '.join(errors)}", file=sys.stderr)
        return 1
    print(f"traceability ok: {len(shas)} commit(s) checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
