#!/usr/bin/env python3
"""
Build a Cursor-friendly catalog from a local clone of wshobson/agents.

Outputs:
  - .cursor/_catalog/wshobson/agents/*.md
  - .cursor/_catalog/wshobson/skills/<skill-name>/**
  - .cursor/_catalog/wshobson/plugin-index.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REWRITE_PATHS = (
    ("~/.claude/agents", "~/.cursor/agents"),
    ("~/.claude/skills", "~/.cursor/skills"),
    (".claude/agents", ".cursor/agents"),
    (".claude/skills", ".cursor/skills"),
)


@dataclass(frozen=True)
class AgentFile:
    name: str
    plugin: str
    source_path: Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_frontmatter_block(text: str) -> tuple[dict[str, str], str] | str:
    if not text.startswith("---\n"):
        return "must start with ---\\n"
    rest = text[4:]
    end = rest.find("\n---\n")
    if end == -1:
        return "unclosed frontmatter"
    block = rest[:end]
    body = rest[end + 5 :]
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
            return f"invalid frontmatter line: {raw_line!r}"
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            return f"empty key in frontmatter: {raw_line!r}"
        fields[key] = value
        last_key = key
    return fields, body


def normalize_description(raw: str) -> str:
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        return raw[1:-1].replace('\\"', '"')
    return raw


def rewrite_text(text: str) -> str:
    for old, new in REWRITE_PATHS:
        text = text.replace(old, new)
    return text


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_commit_sha(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.strip() or None


def build_cursor_agent(
    upstream_text: str,
    *,
    agent_name: str,
    plugin_name: str,
    source_rel: str,
    model_overrides: dict[str, str],
    keep_upstream_model: bool,
) -> tuple[str | None, str | None]:
    parsed = parse_frontmatter_block(upstream_text)
    if isinstance(parsed, str):
        return None, parsed

    fields, body = parsed
    fm_name = fields.get("name", "").strip()
    if not fm_name:
        return None, "missing name in frontmatter"
    if fm_name != agent_name:
        return None, f"name {fm_name!r} != filename stem {agent_name!r}"

    description = normalize_description(fields.get("description", ""))
    if not description:
        return None, "missing description in frontmatter"

    selected_model = model_overrides.get(agent_name)
    if selected_model is None:
        selected_model = fields.get("model", "inherit").strip() if keep_upstream_model else "inherit"
    if not selected_model:
        selected_model = "inherit"

    rendered = (
        "---\n"
        f"name: {agent_name}\n"
        f"description: {description}\n"
        f"model: {selected_model}\n"
        "---\n\n"
        f"<!-- source: wshobson/agents plugin={plugin_name} path={source_rel} -->\n\n"
        f"{rewrite_text(body).rstrip()}\n"
    )
    return rendered, None


def copy_skill_tree(skill_dir: Path, output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(skill_dir, output_dir)

    for path in output_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        path.write_text(rewrite_text(text), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upstream",
        type=Path,
        default=repo_root() / "_upstream-wshobson",
        help="Path to a local clone of wshobson/agents (default: ./_upstream-wshobson)",
    )
    parser.add_argument(
        "--catalog-dir",
        type=Path,
        default=repo_root() / ".cursor" / "_catalog" / "wshobson",
        help="Output catalog directory (default: ./.cursor/_catalog/wshobson)",
    )
    parser.add_argument(
        "--model-overrides",
        type=Path,
        help="Optional JSON map of {agent-name: model-id}",
    )
    parser.add_argument(
        "--keep-upstream-model",
        action="store_true",
        help="Keep upstream model values when no override is provided (default: force inherit)",
    )
    parser.add_argument(
        "--fail-on-collision",
        action="store_true",
        help="Fail when duplicate agent or skill names resolve to different source content",
    )
    args = parser.parse_args()

    upstream = args.upstream.resolve()
    marketplace = upstream / ".claude-plugin" / "marketplace.json"
    plugins_root = upstream / "plugins"

    if not marketplace.is_file():
        print(f"error: marketplace.json not found: {marketplace}", file=sys.stderr)
        return 1
    if not plugins_root.is_dir():
        print(f"error: plugins directory not found: {plugins_root}", file=sys.stderr)
        return 1

    model_overrides: dict[str, str] = {}
    if args.model_overrides:
        model_overrides = json.loads(args.model_overrides.read_text(encoding="utf-8"))

    catalog_dir = args.catalog_dir.resolve()
    agents_out = catalog_dir / "agents"
    skills_out = catalog_dir / "skills"
    if catalog_dir.exists():
        shutil.rmtree(catalog_dir)
    agents_out.mkdir(parents=True, exist_ok=True)
    skills_out.mkdir(parents=True, exist_ok=True)

    data = read_json(marketplace)
    plugins = data.get("plugins", [])
    if not isinstance(plugins, list):
        print("error: marketplace plugins is not a list", file=sys.stderr)
        return 1

    warnings: list[str] = []
    errors: list[str] = []

    by_agent_hash: dict[str, str] = {}
    by_skill_hash: dict[str, str] = {}
    agent_plugins: dict[str, list[str]] = {}
    skill_plugins: dict[str, list[str]] = {}
    command_plugins: dict[str, list[str]] = {}
    plugin_entries: list[dict] = []

    for plugin in plugins:
        name = str(plugin.get("name", "")).strip()
        if not name:
            warnings.append("Skipping plugin with empty name")
            continue

        category = str(plugin.get("category", "")).strip()
        source_value = plugin.get("source")
        source_rel: str | None = None
        if isinstance(source_value, str) and source_value.startswith("./plugins/"):
            source_rel = source_value.removeprefix("./")
        else:
            plugin_entries.append(
                {
                    "name": name,
                    "category": category,
                    "source": source_value,
                    "agents": [],
                    "skills": [],
                    "commands": [],
                    "supported": False,
                    "notes": ["unsupported or external source"],
                }
            )
            warnings.append(f"{name}: unsupported source, skipping content sync")
            continue

        plugin_path = upstream / source_rel
        agents_dir = plugin_path / "agents"
        skills_dir = plugin_path / "skills"
        commands_dir = plugin_path / "commands"

        plugin_agent_names: list[str] = []
        plugin_skill_names: list[str] = []
        plugin_command_names: list[str] = []

        if agents_dir.is_dir():
            for agent_path in sorted(agents_dir.glob("*.md")):
                stem = agent_path.stem
                upstream_text = agent_path.read_text(encoding="utf-8")
                rendered, err = build_cursor_agent(
                    upstream_text,
                    agent_name=stem,
                    plugin_name=name,
                    source_rel=str(agent_path.relative_to(upstream)),
                    model_overrides=model_overrides,
                    keep_upstream_model=args.keep_upstream_model,
                )
                if err:
                    errors.append(f"{agent_path.relative_to(upstream)}: {err}")
                    continue
                assert rendered is not None
                payload = rendered.encode("utf-8")
                digest = sha256_bytes(payload)

                existing = by_agent_hash.get(stem)
                if existing and existing != digest:
                    msg = f"agent collision with different content: {stem} ({name})"
                    if args.fail_on_collision:
                        errors.append(msg)
                        continue
                    warnings.append(msg)
                    continue

                if not existing:
                    by_agent_hash[stem] = digest
                    (agents_out / f"{stem}.md").write_bytes(payload)
                plugin_agent_names.append(stem)
                agent_plugins.setdefault(stem, []).append(name)

        if skills_dir.is_dir():
            for skill_path in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
                skill_name = skill_path.name
                skill_marker = skill_path / "SKILL.md"
                if not skill_marker.is_file():
                    msg = f"{skill_path.relative_to(upstream)} missing SKILL.md"
                    if args.fail_on_collision:
                        errors.append(msg)
                    else:
                        warnings.append(msg)
                    continue

                skill_bytes = skill_marker.read_bytes()
                digest = sha256_bytes(skill_bytes)
                existing = by_skill_hash.get(skill_name)
                if existing and existing != digest:
                    msg = f"skill collision with different SKILL.md: {skill_name} ({name})"
                    if args.fail_on_collision:
                        errors.append(msg)
                        continue
                    warnings.append(msg)
                    continue

                if not existing:
                    by_skill_hash[skill_name] = digest
                    copy_skill_tree(skill_path, skills_out / skill_name)
                plugin_skill_names.append(skill_name)
                skill_plugins.setdefault(skill_name, []).append(name)

        if commands_dir.is_dir():
            for command_path in sorted(commands_dir.glob("*.md")):
                command_name = command_path.stem
                plugin_command_names.append(command_name)
                command_plugins.setdefault(command_name, []).append(name)

        plugin_entries.append(
            {
                "name": name,
                "category": category,
                "source": source_value,
                "agents": plugin_agent_names,
                "skills": plugin_skill_names,
                "commands": plugin_command_names,
                "supported": True,
            }
        )

    if errors:
        print("Sync failed with errors:", file=sys.stderr)
        for entry in errors:
            print(f"  - {entry}", file=sys.stderr)
        return 1

    index_payload = {
        "source_repository": "wshobson/agents",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "upstream_path": str(upstream),
        "upstream_commit": git_commit_sha(upstream),
        "catalog_version": "1",
        "plugins": plugin_entries,
        "agents": {
            name: {"path": f"agents/{name}.md", "plugins": sorted(set(agent_plugins.get(name, [])))}
            for name in sorted(by_agent_hash.keys())
        },
        "skills": {
            name: {"path": f"skills/{name}", "plugins": sorted(set(skill_plugins.get(name, [])))}
            for name in sorted(by_skill_hash.keys())
        },
        "commands": {
            name: {"plugins": sorted(set(command_plugins.get(name, [])))}
            for name in sorted(command_plugins.keys())
        },
        "warnings": warnings,
    }
    (catalog_dir / "plugin-index.json").write_text(
        json.dumps(index_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Catalog generated at: {catalog_dir}")
    print(f"Agents: {len(by_agent_hash)}")
    print(f"Skills: {len(by_skill_hash)}")
    print(f"Plugins indexed: {len(plugin_entries)}")
    if warnings:
        print(f"Warnings: {len(warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
