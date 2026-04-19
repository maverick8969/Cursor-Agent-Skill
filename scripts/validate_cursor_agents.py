#!/usr/bin/env python3
"""
Validate Cursor subagent markdown files under .cursor/agents/.

Each agent must:
  - Start with YAML frontmatter delimited by --- lines
  - Include non-empty name, description, and model keys
  - Use name equal to the filename stem (e.g. api-designer.md -> name: api-designer)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / ".cursor" / "agents"

# Cursor allows inherit, fast, or specific model IDs; repo standard is inherit.
ALLOWED_MODEL_VALUES = {"inherit", "fast"}


def parse_frontmatter(content: str) -> tuple[dict[str, str] | None, str | None]:
    """Return (fields dict, error message). fields is None on failure."""
    if not content.startswith("---\n"):
        return None, "file must start with YAML frontmatter (---\\n)"

    rest = content[4:]
    end = rest.find("\n---\n")
    if end == -1:
        return None, "unclosed frontmatter (missing closing --- before body)"

    block = rest[:end]
    fields: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            return None, f"invalid frontmatter line (expected key: value): {raw_line!r}"
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            return None, f"empty key in frontmatter: {raw_line!r}"
        fields[key] = value

    return fields, None


def validate_agent(path: Path) -> list[str]:
    errors: list[str] = []
    stem = path.stem
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"{path.relative_to(REPO_ROOT)}: cannot read file: {e}"]

    fields, fm_err = parse_frontmatter(text)
    if fm_err:
        return [f"{path.relative_to(REPO_ROOT)}: {fm_err}"]

    assert fields is not None

    for key in ("name", "description", "model"):
        if key not in fields:
            errors.append(f"{path.relative_to(REPO_ROOT)}: frontmatter missing required key {key!r}")
        elif not fields[key].strip():
            errors.append(f"{path.relative_to(REPO_ROOT)}: frontmatter key {key!r} must be non-empty")

    if "name" in fields and fields["name"].strip() != stem:
        errors.append(
            f"{path.relative_to(REPO_ROOT)}: name {fields['name']!r} must match filename stem {stem!r}"
        )

    if "model" in fields and fields["model"].strip():
        m = fields["model"].strip()
        # Allow inherit/fast or typical model id patterns (letters, digits, hyphens).
        if m not in ALLOWED_MODEL_VALUES and not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", m):
            errors.append(
                f"{path.relative_to(REPO_ROOT)}: model {m!r} does not look like a valid value "
                f"(use inherit, fast, or a documented model id)"
            )

    return errors


def main() -> int:
    if not AGENTS_DIR.is_dir():
        print(f"error: agents directory not found: {AGENTS_DIR}", file=sys.stderr)
        return 1

    md_files = sorted(AGENTS_DIR.glob("*.md"))
    if not md_files:
        print(f"error: no .md files under {AGENTS_DIR}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for path in md_files:
        all_errors.extend(validate_agent(path))

    if all_errors:
        print("Cursor agent validation failed:\n", file=sys.stderr)
        for msg in all_errors:
            print(f"  {msg}", file=sys.stderr)
        print(f"\n{len(all_errors)} error(s) in {len(md_files)} agent file(s).", file=sys.stderr)
        return 1

    print(f"OK: validated {len(md_files)} agent file(s) under .cursor/agents/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
