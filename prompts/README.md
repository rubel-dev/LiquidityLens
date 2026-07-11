# Prompt History

This directory contains the AI prompt logs for this project, committed alongside every code change.

## Convention

| File | Contents |
|---|---|
| `YYYY-MM-DD.md` | All prompts sent to Claude AI on that date |

## Why?

This is a requirement from the hackathon judges:
> *"Push prompts with every commit"*

Every prompt file is committed in the same commit as the code it produced, providing a full audit trail of AI-assisted development.

## Format

Each entry includes:
- Timestamp
- Session ID (for tracing back to a specific Claude CLI session)
- The exact prompt text as sent

## How to update

Before committing new code, run:

```bash
# This script auto-extracts today's SUST_Onsite prompts from Claude CLI history
python scripts/export_prompts.py
git add prompts/
```
