from __future__ import annotations

import hashlib
import re
import tempfile
import unittest
from pathlib import Path

from scripts.validate_prompt_records import PromptRecord, validate_record


def record_text(prompt_id: str = "PROMPT-0001", prompt: str = "Do the thing.") -> str:
    checksum = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return f"""# {prompt_id}: Test Prompt

## Prompt ID
{prompt_id}

## Prompt Type
fix-audit

## Date
2026-07-11

## Objective
Validate prompt records.

## Module
governance-finalization

## Requirement IDs
QUALITY-001

## Exact Prompt SHA-256
{checksum}

## Exact Prompt
````text
{prompt}
````

## In Scope
- Validation

## Out of Scope
- Product code

## Files Read
- README.md

## Files Changed
- scripts/validate_prompt_records.py

## Checks Run
- unit tests

## Sonar Status
Pending remote run

## Audit Status
Pending

## Final Outcome
Prompt validation completed.
"""


class PromptRecordValidatorTests(unittest.TestCase):
    def validate(self, name: str, text: str):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            return validate_record(PromptRecord(path=path, text=text))

    def test_valid_record(self):
        self.assertEqual([], self.validate("PROMPT-0001-test.md", record_text()))

    def test_malformed_fence(self):
        text = record_text().replace("````text\n", "``text\n")
        self.assertIn("missing valid exact prompt fenced block", self.validate("PROMPT-0001-test.md", text))

    def test_missing_checksum(self):
        text = record_text().replace("## Exact Prompt SHA-256\n" + hashlib.sha256(b"Do the thing.").hexdigest() + "\n\n", "")
        self.assertIn("missing required metadata: Exact Prompt SHA-256", self.validate("PROMPT-0001-test.md", text))

    def test_checksum_mismatch(self):
        text = record_text().replace(hashlib.sha256(b"Do the thing.").hexdigest(), "0" * 64)
        self.assertIn("checksum mismatch", self.validate("PROMPT-0001-test.md", text))

    def test_filename_metadata_mismatch(self):
        self.assertIn(
            "filename Prompt ID does not match metadata Prompt ID",
            self.validate("PROMPT-0002-test.md", record_text("PROMPT-0001")),
        )

    def test_missing_exact_prompt(self):
        text = record_text()
        text = re.sub(r"## Exact Prompt\n`{3,}text\nDo the thing\.\n`{3,}\n\n", "", text)
        self.assertIn("missing required metadata: Exact Prompt", self.validate("PROMPT-0001-test.md", text))

    def test_missing_required_metadata(self):
        text = record_text().replace("## Module\ngovernance-finalization\n\n", "")
        self.assertIn("missing required metadata: Module", self.validate("PROMPT-0001-test.md", text))


if __name__ == "__main__":
    unittest.main()
