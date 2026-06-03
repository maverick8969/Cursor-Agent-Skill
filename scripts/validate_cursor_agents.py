#!/usr/bin/env python3
"""
Validate Cursor subagent markdown files under .cursor/agents/.

Each agent must:
  - Start with YAML frontmatter delimited by --- lines
  - Include non-empty name, description, and model keys
  - Use name equal to the filename stem (e.g. api-designer.md -> name: api-designer)
"""

from __future__ import annotations

import json
import re
import sys
from argparse import ArgumentParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / ".cursor" / "agents"
DEFAULT_CATALOG_DIR = REPO_ROOT / ".cursor" / "_catalog" / "wshobson"

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
    last_key: str | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if last_key and (line.startswith(" ") or line.startswith("\t")):
            continuation = stripped
            if continuation:
                previous = fields.get(last_key, "")
                fields[last_key] = f"{previous} {continuation}".strip()
            continue
        line = stripped
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
        last_key = key

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


def validate_skill_dir(path: Path, *, require_name_matches_dir: bool = False) -> list[str]:
    errors: list[str] = []
    skill_md = path / "SKILL.md"
    if not skill_md.is_file():
        return [f"{path.relative_to(REPO_ROOT)}: missing SKILL.md"]

    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as e:
        return [f"{skill_md.relative_to(REPO_ROOT)}: cannot read file: {e}"]

    fields, fm_err = parse_frontmatter(text)
    if fm_err:
        return [f"{skill_md.relative_to(REPO_ROOT)}: {fm_err}"]
    assert fields is not None

    for key in ("name", "description"):
        if key not in fields or not fields[key].strip():
            errors.append(f"{skill_md.relative_to(REPO_ROOT)}: frontmatter key {key!r} must be non-empty")

    if require_name_matches_dir and "name" in fields and fields["name"].strip() != path.name:
        errors.append(
            f"{skill_md.relative_to(REPO_ROOT)}: name {fields['name']!r} must match directory {path.name!r}"
        )

    return errors


def validate_catalog(catalog_dir: Path) -> list[str]:
    if not catalog_dir.exists():
        return []

    errors: list[str] = []
    index_file = catalog_dir / "plugin-index.json"
    if not index_file.is_file():
        return [f"{index_file.relative_to(REPO_ROOT)}: missing plugin-index.json"]

    try:
        index = json.loads(index_file.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{index_file.relative_to(REPO_ROOT)}: invalid JSON: {e}"]

    plugins = index.get("plugins")
    if not isinstance(plugins, list):
        errors.append(f"{index_file.relative_to(REPO_ROOT)}: 'plugins' must be a list")
        return errors

    for plugin in plugins:
        if not isinstance(plugin, dict):
            errors.append(f"{index_file.relative_to(REPO_ROOT)}: plugin entry must be an object")
            continue
        if not plugin.get("supported"):
            continue

        name = str(plugin.get("name", "")).strip() or "<unknown>"
        for agent_name in plugin.get("agents", []):
            candidate = catalog_dir / "agents" / f"{agent_name}.md"
            if not candidate.is_file():
                errors.append(f"{index_file.relative_to(REPO_ROOT)}: plugin {name!r} missing agent {agent_name!r}")
        for skill_name in plugin.get("skills", []):
            candidate = catalog_dir / "skills" / str(skill_name)
            if not candidate.is_dir():
                errors.append(f"{index_file.relative_to(REPO_ROOT)}: plugin {name!r} missing skill {skill_name!r}")

    agents_dir = catalog_dir / "agents"
    skills_dir = catalog_dir / "skills"
    if not agents_dir.is_dir():
        errors.append(f"{agents_dir.relative_to(REPO_ROOT)}: missing agents directory")
        return errors
    if not skills_dir.is_dir():
        errors.append(f"{skills_dir.relative_to(REPO_ROOT)}: missing skills directory")
        return errors

    for agent_file in sorted(agents_dir.glob("*.md")):
        errors.extend(validate_agent(agent_file))
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        errors.extend(validate_skill_dir(skill_dir, require_name_matches_dir=False))

    return errors


def validate_project_skills() -> list[str]:
    skills_dir = REPO_ROOT / ".cursor" / "skills"
    if not skills_dir.is_dir():
        return []
    errors: list[str] = []
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        errors.extend(validate_skill_dir(skill_dir, require_name_matches_dir=True))
    return errors


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument(
        "--catalog-dir",
        type=Path,
        default=DEFAULT_CATALOG_DIR,
        help="Optional generated catalog directory to validate when present",
    )
    args = parser.parse_args()

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
    all_errors.extend(validate_project_skills())
    all_errors.extend(validate_catalog(args.catalog_dir.resolve()))

    if all_errors:
        print("Cursor agent validation failed:\n", file=sys.stderr)
        for msg in all_errors:
            print(f"  {msg}", file=sys.stderr)
        print(f"\n{len(all_errors)} error(s) in {len(md_files)} agent file(s).", file=sys.stderr)
        return 1

    print(f"OK: validated {len(md_files)} agent file(s) under .cursor/agents/")
    if args.catalog_dir.exists():
        print(f"OK: validated generated catalog under {args.catalog_dir.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
