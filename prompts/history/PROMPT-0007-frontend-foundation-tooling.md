# PROMPT-0007: Frontend Foundation Tooling

## Prompt ID
PROMPT-0007

## Prompt Type
fix-foundation

## Date
2026-07-11

## Objective
Resolve the frontend foundation npm install/tooling blocker as far as the local environment allows, use command-line tooling, and preserve truthful reporting of any remaining foundation failure before the database module begins.

## Module
frontend-foundation-tooling

## Requirement IDs
QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001, DOC-002

## Exact Prompt SHA-256
6dbeb1b9d62623fcc272005b2e724515eb8309b74bf508e9246732bc3338a0a7

## Exact Prompt
```text
একটা গুরুত্বপূর্ণ note: latest foundation commit-এ frontend install/test local environment-এ npm offline cache এবং approval-layer সমস্যার কারণে blocked ছিল। Database module শুরু করার আগে Codex যেন existing CI result inspect করে এবং foundation failure থাকলে সেটা hide না করে।
 what said is this ok and use gitbash
```

## In Scope
- Inspect npm offline configuration and frontend dependency state.
- Use command-line tooling to run frontend install and available frontend checks.
- Add the generated frontend lockfile.
- Restore CI and Dockerfile to deterministic `npm ci` now that a lockfile exists.
- Record remaining worker-spawn or approval-layer blockers truthfully.

## Out of Scope
- Database schema and migrations.
- Product features.
- Hiding or marking failed/blocked checks as passed.

## Files Read
- frontend/package.json
- frontend/package-lock.json
- .github/workflows/ci.yml
- frontend/Dockerfile
- docs/commit-ledger.md

## Files Changed
- .github/workflows/ci.yml
- frontend/Dockerfile
- frontend/package-lock.json
- frontend formatting changes from Prettier
- docs/commit-ledger.md
- prompts/history/PROMPT-0007-frontend-foundation-tooling.md

## Checks Run
- `cmd /c "npm run format:check"` passed after formatting.
- `cmd /c "npm run lint"` passed.
- `cmd /c "npm run typecheck"` passed.
- `cmd /c "npm test"` blocked by `spawn EPERM`.
- `cmd /c "npm run build"` blocked by `spawn EPERM`.

## Sonar Status
Pending remote GitHub Actions run. SonarQube pass is not claimed locally.

## Audit Status
Human audit pending.

## Final Outcome
The npm offline-cache blocker was resolved enough to generate `package-lock.json`, install dependencies, and pass frontend format/lint/typecheck. Local frontend test/build remain blocked by sandbox worker process spawning and approval-layer failure, so remote CI must be inspected before the database module begins.
