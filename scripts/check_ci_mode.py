#!/usr/bin/env python3
"""Distinguish governance-only mode from product-code mode."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(".").resolve()
    backend = root / "backend"
    frontend = root / "frontend"
    product_mode = backend.exists() or frontend.exists()

    if not product_mode:
        print("CI_MODE=governance-only")
        return 0

    errors: list[str] = []
    if backend.exists():
        if not ((backend / "pyproject.toml").exists() or (backend / "requirements.txt").exists()):
            errors.append("backend exists but has no dependency/tooling manifest")
        if not (backend / "tests").exists():
            errors.append("backend exists but backend/tests is missing")
    if frontend.exists():
        if not (frontend / "package.json").exists():
            errors.append("frontend exists but package.json is missing")
        if not ((frontend / "src").exists() or (frontend / "app").exists()):
            errors.append("frontend exists but no src/ or app/ directory exists")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("CI_MODE=product-code")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
