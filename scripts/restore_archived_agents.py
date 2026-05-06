#!/usr/bin/env python3
"""
Restore archived Cursor agents from .cursor/agents-archive back into .cursor/agents.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=repo_root() / ".cursor" / "agents-archive",
        help="Directory containing archived agent markdown files",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=repo_root() / ".cursor" / "agents",
        help="Directory to restore active agent markdown files into",
    )
    parser.add_argument(
        "--agent",
        action="append",
        help="Agent name to restore (repeatable, without .md extension)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Restore all archived agent files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing destination files if they differ",
    )
    args = parser.parse_args()
    if not args.all and not args.agent:
        parser.error("choose one of --all or --agent")
    return args


def archived_agents(archive_dir: Path) -> dict[str, Path]:
    files = {}
    for path in archive_dir.glob("*.md"):
        if path.name == "README.md":
            continue
        files[path.stem] = path
    return files


def restore_file(source: Path, destination: Path, force: bool) -> None:
    if destination.exists() and not force:
        raise RuntimeError(f"destination exists (use --force to overwrite): {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> int:
    args = parse_args()
    archive_dir = args.archive_dir.resolve()
    target_dir = args.target_dir.resolve()

    if not archive_dir.is_dir():
        print(f"error: archive directory not found: {archive_dir}", file=sys.stderr)
        return 1

    source_map = archived_agents(archive_dir)
    if not source_map:
        print("No archived agents found.")
        return 0

    if args.all:
        selected = sorted(source_map.keys())
    else:
        requested = sorted(set(args.agent or []))
        unknown = [name for name in requested if name not in source_map]
        if unknown:
            print(f"error: unknown archived agent(s): {', '.join(unknown)}", file=sys.stderr)
            return 1
        selected = requested

    restored = 0
    for name in selected:
        source = source_map[name]
        dest = target_dir / source.name
        restore_file(source, dest, args.force)
        restored += 1

    print(f"Restored agents: {restored}")
    print(f"Archive source: {archive_dir}")
    print(f"Active target: {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
