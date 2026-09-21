#!/usr/bin/env python3
"""Validates this repository's skills against the Agent Skills specification.

Reference: https://agentskills.io/specification

The official `skills-ref` validator declares itself demo-only and installs from
a git checkout: unusable in pre-commit. This script replaces it while honoring
the contract in `references/templates.md` (section 6): `--explain`, `--root`,
one line per violation, no auto-fix, no dependency to install.
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
MAX_BODY_LINES = 500  # a spec recommendation, not a rule: severity warn

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

RULES = [
    ("INV-SKILL-001", "error", "Every skill folder holds a SKILL.md"),
    ("INV-SKILL-002", "error", "SKILL.md opens on a YAML frontmatter delimited by ---"),
    ("INV-SKILL-003", "error", f"`name`: 1-{MAX_NAME} characters, [a-z0-9-], no leading/trailing or double hyphen"),
    ("INV-SKILL-004", "error", "`name` matches the parent folder name"),
    ("INV-SKILL-005", "error", f"`description` present, non-empty, <= {MAX_DESCRIPTION} characters"),
    ("INV-SKILL-006", "error", f"`compatibility`, if present, <= {MAX_COMPATIBILITY} characters"),
    ("INV-SKILL-007", "warn", f"The SKILL.md body stays under {MAX_BODY_LINES} lines"),
]


def explain() -> None:
    print("Validating skills against the Agent Skills specification")
    print("Scope: every subfolder of skills/ holding a SKILL.md\n")
    for code, severity, statement in RULES:
        print(f"  {code} [{severity:5}] {statement}")
    print("\nExit codes: 0 conformant - 1 error violation - 2 warnings only")


def read_frontmatter(lines):
    """Returns (fields, end_line), or (None, 0) if the frontmatter is missing.

    Deliberately minimal parser: the spec defines only scalars and a flat
    `metadata`. Handles `>` and `|` blocks and indented continuations.
    """
    if not lines or lines[0].strip() != "---":
        return None, 0

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, 0

    fields, current_key = {}, None
    for line in lines[1:end]:
        header = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):[ \t]*(.*)$", line)
        if header:
            current_key = header.group(1)
            value = header.group(2).strip()
            fields[current_key] = "" if value in (">", "|", ">-", "|-") else value
        elif current_key and line.strip() and line[:1] in (" ", "\t"):
            continuation = line.strip()
            fields[current_key] = f"{fields[current_key]} {continuation}".strip()
        elif not line.strip():
            continue
        else:
            current_key = None

    return fields, end


def count_characters(text: str) -> int:
    """Counts NFC-normalized Unicode characters, never bytes."""
    return len(unicodedata.normalize("NFC", text))


def validate_skill(folder: Path, root: Path, violations: list) -> None:
    relative = folder.relative_to(root)
    skill_md = folder / "SKILL.md"

    if not skill_md.is_file():
        violations.append((
            "error", f"{relative}/: [INV-SKILL-001] skill folder without a SKILL.md"
            f" — add {relative}/SKILL.md with a `name` and `description` frontmatter"
        ))
        return

    path = skill_md.relative_to(root)
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    fields, frontmatter_end = read_frontmatter(lines)

    if fields is None:
        violations.append((
            "error", f"{path}:1: [INV-SKILL-002] YAML frontmatter missing or never closed"
            " — line 1 must be `---`, then the fields, then a closing `---`"
        ))
        return

    name = fields.get("name", "").strip().strip("\"'")
    if not name:
        violations.append((
            "error", f"{path}:2: [INV-SKILL-003] `name` field missing"
            f" — add `name: {folder.name}`"
        ))
    else:
        if count_characters(name) > MAX_NAME or not NAME_PATTERN.match(name):
            violations.append((
                "error", f"{path}:2: [INV-SKILL-003] `name: {name}` is invalid"
                f" — 1 to {MAX_NAME} characters from [a-z0-9-], no leading or trailing hyphen,"
                " no double hyphen"
            ))
        if name != folder.name:
            violations.append((
                "error", f"{path}:2: [INV-SKILL-004] `name: {name}` != folder `{folder.name}`"
                f" — rename the field to `{folder.name}`, or rename the folder to `{name}`"
            ))

    description = fields.get("description", "").strip().strip("\"'")
    if not description:
        violations.append((
            "error", f"{path}:3: [INV-SKILL-005] `description` field missing or empty"
            " — say what the skill does AND when to use it: it is the only text"
            " loaded at startup, so it is the only trigger"
        ))
    else:
        size = count_characters(description)
        if size > MAX_DESCRIPTION:
            violations.append((
                "error", f"{path}:3: [INV-SKILL-005] `description` is {size} characters"
                f" (max {MAX_DESCRIPTION}) — cut {size - MAX_DESCRIPTION} characters,"
                " starting with the redundant triggers"
            ))

    compatibility = fields.get("compatibility", "").strip().strip("\"'")
    if compatibility:
        size = count_characters(compatibility)
        if size > MAX_COMPATIBILITY:
            violations.append((
                "error", f"{path}:4: [INV-SKILL-006] `compatibility` is {size} characters"
                f" (max {MAX_COMPATIBILITY}) — cut {size - MAX_COMPATIBILITY} characters"
            ))

    body = len(lines) - (frontmatter_end + 1)
    if body > MAX_BODY_LINES:
        violations.append((
            "warn", f"{path}:{frontmatter_end + 2}: [INV-SKILL-007] body is {body} lines"
            f" (recommended <= {MAX_BODY_LINES}) — move the detail into references/:"
            " the whole body is loaded into context the moment the skill activates"
        ))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validates skills against the Agent Skills spec.")
    parser.add_argument("--explain", action="store_true", help="describe the rules without checking anything")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    arguments = parser.parse_args()

    if arguments.explain:
        explain()
        return 0

    root = Path(arguments.root).resolve()
    skills_folder = root / "skills"
    if not skills_folder.is_dir():
        print(f"{arguments.root}: no skills/ folder — nothing to validate", file=sys.stderr)
        return 1

    violations: list = []
    folders = sorted(d for d in skills_folder.iterdir() if d.is_dir())
    for folder in folders:
        validate_skill(folder, root, violations)

    for severity, message in violations:
        print(message)

    errors = sum(1 for severity, _ in violations if severity == "error")
    warnings = len(violations) - errors

    if not violations:
        print(f"{len(folders)} skills validated, no violation.")
        return 0

    print(f"\n{len(folders)} skills validated — {errors} error, {warnings} warn.", file=sys.stderr)
    return 1 if errors else 2


if __name__ == "__main__":
    sys.exit(main())
