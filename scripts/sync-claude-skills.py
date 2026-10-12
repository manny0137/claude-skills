#!/usr/bin/env python3
"""
Sync Claude Skills - expose every skill in this repo as a Claude Code project skill.

Claude Code discovers project skills at .claude/skills/<name>/SKILL.md and uses
the folder name as the skill's /command name. This script creates one relative
directory symlink per skill, so the skill's scripts/, references/ and assets/
resolve exactly as they do in the source tree. Nothing is copied.

Skills are taken from the same canonical tree scripts/derive_counters.py counts
(generated mirrors such as .gemini/ and .codex/ are excluded). Name handling:

- Dual-published copies (same folder name, identical contents) are linked once.
- Different skills that share a folder name are both prefixed with their
  plugin folder (e.g. agenthub-run, autoresearch-agent-run).
- A name already taken by a Claude Code built-in or by .claude/commands/ is
  prefixed the same way, so the repo never shadows them.

Only symlinks this script manages (links that resolve inside the repo) are
created or removed; real directories in .claude/skills/ are left alone.

Usage:
    python scripts/sync-claude-skills.py            # create/update links
    python scripts/sync-claude-skills.py --dry-run  # show what would change
    python scripts/sync-claude-skills.py --check    # exit 1 if links are stale
"""

import argparse
import filecmp
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

# Names Claude Code ships as built-in skills/commands. A repo skill with one of
# these names would shadow or be shadowed by the built-in, so it gets prefixed.
RESERVED_NAMES = {
    "batch", "claude-api", "code-review", "debug", "fewer-permission-prompts",
    "init", "keybindings-help", "loop", "plugin-authoring", "review", "run",
    "security-review", "session-start-hook", "simplify", "update-config",
}

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def load_canonical_walk(repo_root: Path):
    """Reuse derive_counters.canonical_walk so both scripts agree on what a skill is."""
    path = repo_root / "scripts" / "derive_counters.py"
    spec = importlib.util.spec_from_file_location("derive_counters", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.canonical_walk


def same_tree(a: Path, b: Path) -> bool:
    """True when two skill directories have identical contents (recursively)."""
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__"])
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    if mismatch or errors:
        return False
    return all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def plugin_prefix(skill_dir: Path, repo_root: Path) -> str:
    """Nearest ancestor that tells the skill apart: skips `skills/` and folders named like the skill."""
    for parent in skill_dir.relative_to(repo_root).parents:
        if parent.name and parent.name not in ("skills", skill_dir.name):
            return parent.name
    return "repo"


def find_skills(repo_root: Path) -> List[Dict]:
    canonical_walk = load_canonical_walk(repo_root)
    skill_dirs = sorted(
        p.parent for p in canonical_walk(repo_root) if p.name == "SKILL.md" and p.parent != repo_root
    )

    reserved = set(RESERVED_NAMES)
    commands_dir = repo_root / ".claude" / "commands"
    if commands_dir.is_dir():
        reserved.update(p.stem for p in commands_dir.glob("*.md"))
        reserved.update(p.name for p in commands_dir.iterdir() if p.is_dir())

    # Group by folder name, drop identical dual-published copies.
    groups: Dict[str, List[Path]] = {}
    for skill_dir in skill_dirs:
        bucket = groups.setdefault(skill_dir.name, [])
        if any(same_tree(kept, skill_dir) for kept in bucket):
            continue
        bucket.append(skill_dir)

    skills, taken = [], set()
    for base, dirs in sorted(groups.items()):
        needs_prefix = len(dirs) > 1 or base in reserved
        for skill_dir in dirs:
            name = f"{plugin_prefix(skill_dir, repo_root)}-{base}" if needs_prefix else base
            if name in taken or name in reserved:
                n = 2
                while f"{name}-{n}" in taken:
                    n += 1
                name = f"{name}-{n}"
            if not NAME_PATTERN.match(name):
                raise SystemExit(f"error: derived skill name {name!r} for {skill_dir} is not a valid skill name")
            taken.add(name)
            skills.append({"name": name, "source": skill_dir.relative_to(repo_root).as_posix()})

    return sorted(skills, key=lambda s: s["name"])


def is_managed_link(link: Path, repo_root: Path) -> bool:
    """A symlink this script owns: it points somewhere inside the repo (or is dangling)."""
    if not link.is_symlink():
        return False
    target = (link.parent / os.readlink(link)).resolve()
    return target == repo_root or repo_root in target.parents


def plan(repo_root: Path, skills: List[Dict]) -> Dict[str, List]:
    skills_dir = repo_root / ".claude" / "skills"
    wanted = {}
    for skill in skills:
        link = skills_dir / skill["name"]
        wanted[skill["name"]] = os.path.relpath(repo_root / skill["source"], skills_dir)

    create, update, conflict = [], [], []
    for name, target in wanted.items():
        link = skills_dir / name
        if link.is_symlink():
            if os.readlink(link) != target:
                update.append((name, target))
        elif link.exists():
            conflict.append(name)
        else:
            create.append((name, target))

    remove = []
    if skills_dir.is_dir():
        for entry in sorted(skills_dir.iterdir()):
            if entry.name not in wanted and is_managed_link(entry, repo_root.resolve()):
                remove.append(entry.name)

    return {"create": create, "update": update, "remove": remove, "conflict": conflict}


def apply(repo_root: Path, changes: Dict[str, List]) -> None:
    skills_dir = repo_root / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for name in changes["remove"]:
        (skills_dir / name).unlink()
    for name, target in changes["update"]:
        (skills_dir / name).unlink()
        (skills_dir / name).symlink_to(target, target_is_directory=True)
    for name, target in changes["create"]:
        (skills_dir / name).symlink_to(target, target_is_directory=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Link every repo skill into .claude/skills/ for Claude Code.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="show what would change without writing")
    mode.add_argument("--check", action="store_true", help="exit 1 if .claude/skills/ is out of date")
    parser.add_argument("--json", action="store_true", help="print the skill list as JSON")
    parser.add_argument("--verbose", action="store_true", help="list every change")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    skills = find_skills(repo_root)
    changes = plan(repo_root, skills)

    if args.json:
        print(json.dumps(skills, indent=2))
        return 0

    pending = len(changes["create"]) + len(changes["update"]) + len(changes["remove"])
    if args.verbose or args.dry_run or args.check:
        for name, target in changes["create"]:
            print(f"  + {name} -> {target}")
        for name, target in changes["update"]:
            print(f"  ~ {name} -> {target}")
        for name in changes["remove"]:
            print(f"  - {name}")
    for name in changes["conflict"]:
        print(f"  ! {name}: a real directory already exists in .claude/skills/, left untouched", file=sys.stderr)

    if args.check:
        if pending:
            print(f"{pending} change(s) pending; run: python scripts/sync-claude-skills.py")
            return 1
        print(f"Claude skills in sync: {len(skills)} skills linked in .claude/skills/")
        return 0

    if not args.dry_run:
        apply(repo_root, changes)

    verb = "Would link" if args.dry_run else "Linked"
    print(
        f"{verb} {len(skills)} skills in .claude/skills/ "
        f"({len(changes['create'])} new, {len(changes['update'])} updated, {len(changes['remove'])} removed)"
    )
    return 1 if changes["conflict"] else 0


if __name__ == "__main__":
    sys.exit(main())
