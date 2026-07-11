# PROMPT-0003: Final Governance Cleanup

## Prompt ID
PROMPT-0003

## Prompt Type
fix-audit

## Date
2026-07-11

## Objective
Perform the final governance cleanup before product implementation by normalizing repository text policy, validating prompt records, finalizing the commit ledger, and keeping CI/SonarQube enforcement honest.

## Module
governance-finalization

## Requirement IDs
QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001

## Exact Prompt SHA-256
7b77b5a1bd8d7106bc8fdb81e6a7615a6f49c33b7df343b40b24a4037f7585fb

## Exact Prompt
`````text
You are performing the final governance cleanup before product implementation.

Do not implement product business logic.
Do not create database models, migrations, APIs, algorithms, or frontend screens.

# READ FIRST

Read:

* `README.md`
* all files under `docs/`
* all files under `prompts/`
* `.github/workflows/ci.yml`
* `sonar-project.properties`
* `.gitignore`
* current Git status
* recent Git history

# OBJECTIVE

Produce one clean, traceable corrective commit that resolves the final implementation-readiness blockers.

# 1. Normalize Repository Line Endings

The working tree currently shows many modified files caused primarily by line-ending or BOM normalization.

Create or update `.gitattributes` with an explicit policy:

```text
* text=auto
*.py text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
*.md text eol=lf
*.toml text eol=lf
*.json text eol=lf
*.properties text eol=lf
*.sh text eol=lf
```

Preserve legitimate UTF-8 Bengali content.

Normalize tracked files deliberately.

Do not modify content unnecessarily.

After normalization, the final working tree must be clean after the corrective commit.

# 2. Fix Prompt Record Format

Correct:

`prompts/history/PROMPT-0002-governance-hardening.md`

The exact prompt must be stored inside a valid fenced block:

````text
```text
<exact prompt>
````

````

Do not use:

```text
``text
````

Recalculate the SHA-256 checksum from the exact stored prompt text.

Ensure the recorded checksum matches.

# 3. Add Prompt Record Validation

Create:

`scripts/validate_prompt_records.py`

It must validate every file under:

`prompts/history/`

Check:

* valid Prompt ID
* required metadata exists
* exact prompt section exists
* valid fenced block
* checksum exists
* checksum matches exact prompt
* no obvious secret values
* filename Prompt ID matches metadata Prompt ID

Add unit tests covering:

1. valid record
2. malformed fence
3. missing checksum
4. checksum mismatch
5. filename/metadata mismatch
6. missing exact prompt
7. missing required metadata

Add this validator to the CI traceability job.

# 4. Finalize Commit Ledger

Update:

`docs/commit-ledger.md`

Replace the pending SHA for `PROMPT-0002` with:

`0f816689d63315501fde383699dbd82549ba784b`

Keep the SonarQube and Quality Gate values honest:

* `Pending remote run` until confirmed
* do not claim pass before remote evidence exists

Add a pending entry for the new corrective Prompt ID.

# 5. Create New Prompt Record

Create the next sequential record, expected:

`prompts/history/PROMPT-0003-final-governance-cleanup.md`

Store this exact prompt verbatim.

Include:

* Prompt ID
* Prompt type
* date
* objective
* module
* requirement IDs
* exact prompt
* SHA-256 checksum
* in scope
* out of scope
* files read
* files changed
* checks run
* Sonar status
* audit status
* final outcome

# 6. Remove Repository Noise

Ensure generated artifacts are not tracked:

* `__pycache__/`
* `*.pyc`
* coverage outputs
* test caches
* local environments

Update `.gitignore` where needed.

If tracked generated files exist, remove them from Git tracking.

# 7. Validate CI

Update `.github/workflows/ci.yml` so the traceability job also runs:

```text
python scripts/validate_prompt_records.py
```

Keep the existing order:

```text
traceability
→ backend-quality
→ frontend-quality
→ test-and-coverage
→ sonarqube
→ quality-gate
```

Do not weaken SonarQube enforcement.

# 8. Validation Required

Run:

* `python scripts/validate_commit_traceability.py` with a valid local test range
* `python scripts/validate_requirement_ids.py`
* `python scripts/validate_prompt_records.py`
* `python -m unittest discover tests/governance`
* YAML validation
* Git status review
* secret scan where practical

Report exact commands and results.

# 9. Commit

Prepare one focused commit:

```text
chore(governance): finalize clean traceable repository state

Requirement-IDs: QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001
Prompt-ID: PROMPT-0003
Module: governance-finalization
Tests: traceability, prompt-record, requirement-ID, YAML, and governance tests passed
```

After committing:

```text
git status --porcelain
```

must return no output.

# 10. Remote Validation

If remote push is available:

1. Push the commit.
2. Confirm all CI jobs pass.
3. Confirm SonarQube analysis completes.
4. Confirm Quality Gate passes.
5. Update the ledger in a later traceable commit if the run result must be persisted.

If remote push is unavailable:

* provide the exact push command
* keep remote Sonar and Quality Gate status as Pending

# OUT OF SCOPE

Do not implement:

* backend application code
* frontend application code
* database schema
* migrations
* analytics
* APIs
* authentication
* deployment infrastructure beyond existing governance configuration

# FINAL RESPONSE FORMAT

Return only:

## Prompt Record Created

## Files Created

## Files Updated

## Line Ending Normalization

## Prompt Validation

## Ledger Update

## Tests and Validation

## Commit Created

## Git Status

## Remote CI Result

## SonarQube Result

## Quality Gate Result

## Remaining Blockers

## Ready for Repository Foundation

Answer the final line only as:

`YES`

or

`NO`
`````

## Prompt Record Created

## Files Created

## Files Updated

## Line Ending Normalization

## Prompt Validation

## Ledger Update

## Tests and Validation

## Commit Created

## Git Status

## Remote CI Result

## SonarQube Result

## Quality Gate Result

## Remaining Blockers

## Ready for Repository Foundation

Answer the final line only as:

`YES`

or

`NO`
````

## Prompt Record Created

## Files Created

## Files Updated

## Line Ending Normalization

## Prompt Validation

## Ledger Update

## Tests and Validation

## Commit Created

## Git Status

## Remote CI Result

## SonarQube Result

## Quality Gate Result

## Remaining Blockers

## Ready for Repository Foundation

Answer the final line only as:

`YES`

or

`NO`
```

## In Scope
- Repository line-ending policy
- Prompt record fence and checksum correction
- Prompt record validation script and unit tests
- CI traceability job update
- Commit ledger update
- Generated artifact ignore policy
- Local validation and clean corrective commit

## Out of Scope
- Backend application code
- Frontend application code
- Database models or migrations
- APIs
- Business algorithms
- Authentication implementation
- Production deployment infrastructure

## Files Read
- README.md
- docs/*
- prompts/*
- .github/workflows/ci.yml
- sonar-project.properties
- .gitignore
- current Git status
- recent Git history
- attached governance cleanup prompt

## Files Changed
- .gitattributes
- .env.example
- .gitignore
- .github/workflows/ci.yml
- README.md
- sonar-project.properties
- docs/* line-ending normalization
- docs/commit-ledger.md
- prompts/templates/* line-ending normalization
- prompts/history/PROMPT-0001-finalize-selective-merge.md
- prompts/history/PROMPT-0002-governance-hardening.md
- prompts/history/PROMPT-0003-final-governance-cleanup.md
- scripts/* line-ending normalization
- scripts/validate_prompt_records.py
- tests/governance/* line-ending normalization
- tests/governance/test_validate_prompt_records.py
- tests/governance/test_validate_commit_traceability.py

## Checks Run
- python scripts/validate_prompt_records.py: passed
- python scripts/validate_requirement_ids.py: passed, 48 registry IDs traced
- python scripts/validate_commit_traceability.py --commits HEAD: passed, 1 commit checked
- python scripts/check_ci_mode.py: passed, governance-only mode
- python -m unittest discover tests/governance: passed, 17 tests
- YAML validation for .github/workflows/ci.yml: passed
- git diff --check: passed
- practical secret-value scan: passed
- remote initial-push CI inspection: failed before fix because legacy short SHA prefixes were not matched against full SHAs

## Sonar Status
Pending remote run.

## Audit Status
Local governance audit passed. Human review pending.

## Final Outcome
Corrective governance cleanup prepared and remote initial-push traceability issue identified for follow-up correction without product implementation. Remote SonarQube and Quality Gate remain pending until the clean repository passes traceability and required SonarQube secrets are configured.
