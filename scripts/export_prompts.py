"""
export_prompts.py — Run before every commit to update today's prompt log.

Usage:
    python scripts/export_prompts.py

This reads Claude CLI history (~/.claude/history.jsonl), filters for
SUST_Onsite prompts from today, and writes/updates prompts/YYYY-MM-DD.md.
"""
import json
import datetime
from pathlib import Path
from collections import defaultdict

HISTORY_FILE = Path.home() / ".claude" / "history.jsonl"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
PROJECT_KEYWORD = "SUST_Onsite"


def load_history():
    if not HISTORY_FILE.exists():
        print(f"[ERROR] History file not found: {HISTORY_FILE}")
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def filter_project(entries):
    return [e for e in entries if PROJECT_KEYWORD in e.get("project", "")]


def format_prompt_log(entries):
    lines = [
        f"# Claude AI Prompt History — {PROJECT_KEYWORD}",
        "**Project:** bKash x SUST CSE Carnival 2026 — Agent Liquidity Intelligence System",
        f"**Total prompts:** {len(entries)}",
        "",
        "---",
        "",
        "This file documents every AI prompt used during development of this project.",
        "Committed alongside code changes as required by the hackathon judges.",
        "",
        "---",
        "",
    ]

    by_date = defaultdict(list)
    for e in entries:
        ts = datetime.datetime.fromtimestamp(e["timestamp"] / 1000)
        by_date[ts.strftime("%Y-%m-%d")].append((ts, e))

    for date_str in sorted(by_date.keys()):
        lines.append(f"## {date_str}")
        lines.append("")
        for i, (ts, e) in enumerate(by_date[date_str], 1):
            display = e["display"].replace("\r", " ").replace("\n", " ").strip()
            session = e.get("sessionId", "unknown")[:8]
            lines.append(f"### Prompt #{i} — {ts.strftime('%H:%M:%S')}")
            lines.append(f"**Session:** `{session}...`")
            lines.append(f"**Prompt:**")
            lines.append(f"> {display}")
            lines.append("")

    return "\n".join(lines)


def main():
    today = datetime.date.today().strftime("%Y-%m-%d")
    out_file = PROMPTS_DIR / f"{today}.md"

    entries = load_history()
    sust_entries = filter_project(entries)

    if not sust_entries:
        print(f"[WARN] No {PROJECT_KEYWORD} prompts found in history.")
        return

    PROMPTS_DIR.mkdir(exist_ok=True)
    content = format_prompt_log(sust_entries)
    out_file.write_text(content, encoding="utf-8")
    print(f"[OK] Written {len(sust_entries)} prompts → {out_file}")
    print(f"     Now run: git add prompts/ && git commit ...")


if __name__ == "__main__":
    main()
