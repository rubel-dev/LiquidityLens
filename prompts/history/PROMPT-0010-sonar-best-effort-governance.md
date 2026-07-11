# PROMPT-0010: Sonar Best-Effort Governance

## Prompt ID
PROMPT-0010

## Prompt Type
governance-update

## Date
2026-07-11

## Objective
Update governance and CI policy so SonarQube analysis and Quality Gate are best-effort and non-blocking per the latest judge instruction, while preserving mandatory prompt traceability and local validation.

## Module
sonar-best-effort-governance

## Requirement IDs
QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001, DOC-002, DOC-003

## Exact Prompt SHA-256
c6af5d19e9c70a72634ff259cea6d73dabfe81087d1401d31a6a4474e1638a45

## Exact Prompt
```text
Update the project governance and CI policy based on the latest judge instruction.

The judges have explicitly allowed teams to continue when SonarQube or CI analysis fails because of tool, environment, configuration, or integration problems.

Apply these changes:

1. Keep prompt-to-commit traceability mandatory.
2. Keep local testing mandatory.
3. Make SonarQube analysis best-effort and non-blocking.
4. A SonarQube error or failed Quality Gate must not block implementation, commits, merging, or demo preparation.
5. Do not delete the SonarQube configuration if it already exists.
6. Continue attempting SonarQube analysis when practical.
7. Record SonarQube results honestly as:

   * Passed
   * Failed
   * Skipped
   * Unavailable
   * Configuration Error
8. Never claim SonarQube passed unless it actually passed.
9. When SonarQube fails, record:

   * error summary
   * likely cause
   * attempts made
   * known code-quality risk
   * local checks used as fallback
10. Local fallback checks must include, where applicable:

* formatter
* linter
* type checker
* unit tests
* integration tests
* coverage
* security/safety validation

Update:

* `.github/workflows/ci.yml`
* any SonarQube workflow
* `docs/12-decision-log.md`
* `docs/13-known-risks.md`
* `docs/15-code-quality-and-commit-policy.md`
* `docs/commit-ledger.md`
* `README.md`

The SonarQube job should use non-blocking behavior such as `continue-on-error: true`, while still publishing the result when available.

Do not weaken prompt traceability.
Do not remove tests.
Do not hide errors.
Do not claim full CI compliance when remote checks were skipped.

After updating, continue with the current implementation module using local Git Bash validation.

Return:

* files changed
* final CI policy
* SonarQube fallback behavior
* local validation commands
* remaining risks
```

## In Scope
- Make SonarQube analysis and Quality Gate non-blocking in CI.
- Preserve existing SonarQube configuration.
- Add governance documentation for honest SonarQube status reporting.
- Keep prompt traceability and local quality checks mandatory.
- Record local fallback checks and risks.

## Out of Scope
- Removing SonarQube.
- Weakening prompt/commit traceability.
- Removing local tests, formatter, linter, type checker, coverage, or security/safety validation.
- Claiming remote CI, SonarQube, or Quality Gate passed without evidence.

## Files Read
- .github/workflows/ci.yml
- README.md
- docs/12-decision-log.md
- docs/13-known-risks.md
- docs/15-code-quality-and-commit-policy.md
- docs/commit-ledger.md
- sonar-project.properties

## Files Changed
- .github/workflows/ci.yml
- README.md
- docs/12-decision-log.md
- docs/13-known-risks.md
- docs/15-code-quality-and-commit-policy.md
- docs/commit-ledger.md
- prompts/history/PROMPT-0010-sonar-best-effort-governance.md

## Checks Run
- Git Bash validation attempted with `C:\Users\Rubel\AppData\Local\Programs\Git\usr\bin\bash.exe`; blocked by `CreateFileMapping ... Win32 error 5`.
- `python scripts\validate_prompt_records.py` passed.
- `python scripts\validate_requirement_ids.py` passed.
- `python -m unittest discover tests/governance` passed.
- `python scripts\check_ci_mode.py` passed.
- `python -m pytest` from `backend/` passed with 16 passed, 2 skipped, and 97.21% coverage.
- `python -m pytest tests\integration\test_domain_migration_postgres.py -q` passed with 2 tests against local PostgreSQL `hacathon_db`.
- `cmd /c "npm run format:check && npm run lint && npm run typecheck"` passed.
- `cmd /c "npm test"` remained blocked locally by sandbox `spawn EPERM`.
- `git diff --check` passed.

## Sonar Status
Best-effort/non-blocking policy configured. Remote result pending.

## Audit Status
Human audit pending.

## Final Outcome
CI and governance policy were updated so SonarQube and Quality Gate are best-effort/non-blocking while prompt traceability and local fallback checks remain mandatory. Local validation passed except Git Bash and frontend Vitest, both blocked by sandbox permission/process-spawn errors.
