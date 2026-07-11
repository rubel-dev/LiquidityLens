# Code Quality and Commit Policy

## Mandatory Commit Format
```text
<type>(<scope>): <summary>

Requirement-IDs: <IDs>
Prompt-ID: <PROMPT-ID>
Module: <module-name>
Tests: <result>
```

## Enforcement Rules
- One focused task per commit.
- One exact prompt record per implementation or fix commit.
- Prompt record must be committed with the related changes.
- Every pushed commit runs CI and SonarQube.
- Every non-exempt commit after the governance-hardening commit must include Requirement-IDs, Prompt-ID, Module, Tests, and a matching prompt file.
- Failed Quality Gate blocks accepted completion.
- Security Hotspots require human review.
- `NOSONAR` and Sonar exclusions require documented approval.
- Sonar rules must not be disabled to hide issues.

## Narrow Exemptions
The only allowed exemptions are:
- automatic merge commits,
- unavoidable GitHub-generated commits,
- legacy commits explicitly recorded in docs/commit-ledger.md.

## Legacy Pre-Enforcement Exceptions
Recent shared history contains non-compliant commits such as `Delete prompts directory`, `Delete frontend directory`, `Delete scripts directory`, and older planning commits. These are recorded in docs/commit-ledger.md and must not be used as examples for future commits.

All commits after the governance-hardening commit are subject to mandatory enforcement.

## Governance-Only vs Product-Code Mode
Governance-only mode may pass without backend/frontend product source. Once `backend/` or `frontend/` is scaffolded, CI enters product-code mode and these checks become mandatory:

Backend:
- Ruff format check
- Ruff lint
- MyPy or Pyright
- Pytest
- coverage generation

Frontend:
- formatter check
- ESLint
- TypeScript type check
- unit tests
- production build
- coverage generation

Do not continue using optional `--if-present` checks after repository foundation is scaffolded.
