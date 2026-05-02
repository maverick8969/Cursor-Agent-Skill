#!/usr/bin/env python3
"""
Sync .cursor/agents/*.md from a local clone of VoltAgent/awesome-claude-code-subagents.

Transforms Claude Code-style frontmatter (tools, model: sonnet|opus|...) into Cursor format:
  name, description, model: inherit

Prepends an H1 title derived from the filename stem. Optionally rewrites ~/.claude/agents paths
to ~/.cursor/agents for this catalog layout.

Usage:
  git clone --depth 1 https://github.com/VoltAgent/awesome-claude-code-subagents.git _upstream-awesome
  python3 scripts/sync_agents_from_upstream.py

Or:
  python3 scripts/sync_agents_from_upstream.py --upstream /path/to/awesome-claude-code-subagents
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Do not overwrite Cursor-specific fork customizations.
SKIP_STEMS = frozenset({"agent-installer", "design-bridge"})


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_frontmatter_block(text: str) -> tuple[dict[str, str], str] | str:
    """Return (fields, body) or an error message string."""
    if not text.startswith("---\n"):
        return "must start with ---\\n"
    rest = text[4:]
    end = rest.find("\n---\n")
    if end == -1:
        return "unclosed frontmatter"
    block = rest[:end]
    body = rest[end + 5 :]  # after closing \n---\n
    fields: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            return f"invalid frontmatter line: {raw_line!r}"
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            return f"empty key: {raw_line!r}"
        fields[key] = value
    return (fields, body)


def normalize_description(raw: str) -> str:
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        inner = raw[1:-1]
        return inner.replace('\\"', '"')
    return raw


def title_from_stem(stem: str) -> str:
    return " ".join(part.capitalize() for part in stem.split("-"))


def cursor_body(body: str) -> str:
    """Normalize catalog paths for Cursor installs."""
    body = body.replace("~/.claude/agents", "~/.cursor/agents")
    body = body.replace(".claude/agents", ".cursor/agents")
    return body.rstrip() + "\n"


def upstream_to_cursor(upstream_text: str, stem: str) -> tuple[str | None, str | None]:
    parsed = parse_frontmatter_block(upstream_text)
    if isinstance(parsed, str):
        return None, parsed
    fields, body = parsed

    name = fields.get("name", "").strip()
    if name != stem:
        return None, f"name {name!r} != stem {stem!r}"
    desc = normalize_description(fields.get("description", ""))
    if not desc:
        return None, "empty description"

    title = title_from_stem(stem)
    out = (
        "---\n"
        f"name: {name}\n"
        f"description: {desc}\n"
        "model: inherit\n"
        "---\n\n"
        f"# {title}\n\n"
        f"{cursor_body(body)}"
    )
    return out, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upstream",
        type=Path,
        default=repo_root() / "_upstream-awesome",
        help="Path to awesome-claude-code-subagents clone (default: ./_upstream-awesome)",
    )
    args = parser.parse_args()
    root = repo_root()
    categories = args.upstream / "categories"
    if not categories.is_dir():
        print(f"error: categories not found: {categories}", file=sys.stderr)
        return 1

    agents_dir = root / ".cursor" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    md_paths = sorted(p for p in categories.rglob("*.md") if p.name != "README.md")
    written = 0
    skipped = 0
    errors: list[str] = []

    for path in md_paths:
        stem = path.stem
        if stem in SKIP_STEMS:
            skipped += 1
            continue
        text = path.read_text(encoding="utf-8")
        out, err = upstream_to_cursor(text, stem)
        if err:
            errors.append(f"{path.relative_to(args.upstream)}: {err}")
            continue
        assert out is not None
        (agents_dir / f"{stem}.md").write_text(out, encoding="utf-8")
        written += 1

    print(f"Wrote {written} agent file(s) to {agents_dir.relative_to(root)}")
    if skipped:
        print(f"Skipped {skipped} (fork-specific): {', '.join(sorted(SKIP_STEMS))}")
    if errors:
        print("Errors:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

