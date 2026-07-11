# Code Quality and Commit Policy

## Mandatory Commit Format
```text
<type>(<scope>): <summary>

Requirement-IDs: <IDs>
Prompt-ID: <PROMPT-ID>
Module: <module-name>
Tests: <result>
```

## Rules
- One focused task per commit.
- One exact prompt record per implementation or fix commit.
- Prompt record must be committed with the related changes.
- Every pushed commit runs CI and SonarQube.
- Failed Quality Gate blocks accepted completion.
- Security Hotspots require human review.
- `NOSONAR` and Sonar exclusions require documented approval.
- Sonar rules must not be disabled to hide issues.
