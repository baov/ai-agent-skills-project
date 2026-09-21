#!/usr/bin/env python3
"""Block B -- test-case bridge to the real tests.

Checks that every scenario documented under docs/business/test-cases/ points at an
automated test that really exists, and reports tests with no test-case.

Harness contract (see references/templates.md section 6):
  --explain          describes the rule without checking anything
  --root <path>      project root (default: current directory)
  output             path:line: [INV-NNN] message -- remediation
  code 0             everything is consistent
  code 1             at least one covered_broken (severity error)
  code 2             warns only (pending, orphans)

No external dependency: the front-matter is parsed by hand so that the script
runs on a minimal CI.

This starter speaks English; the script generated for a project writes its
messages in that project's language.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

INVARIANT_ID = "INV-002"

TEST_CASES_DIR = Path("docs/business/test-cases")

# Where to look for the real tests, in order of frequency. Adapt to the project.
TEST_GLOBS = (
    "**/test_*.py",
    "**/*_test.py",
    "**/*.test.ts",
    "**/*.test.tsx",
    "**/*.test.js",
    "**/*.spec.ts",
    "**/*.spec.js",
    "**/src/test/**/*.java",
    "**/src/test/**/*.kt",
    "**/*_test.go",
    "**/*Test.cs",
)

IGNORED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "target", "build", "dist",
    "__pycache__", ".gradle", ".idea", "vendor", ".tox",
}

VALID_STATUS = {"covered", "pending", "manual"}


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def parse_front_matter(path: Path) -> tuple[dict[str, str], int]:
    """Returns (fields, line where the front-matter ends).

    A deliberately minimal parser: flat keys, scalar values, trailing comments
    ignored. Enough for the test-case front-matter, and it avoids a YAML
    dependency.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return {}, 0

    if not lines or lines[0].strip() != "---":
        return {}, 0

    fields: dict[str, str] = {}
    for index, raw in enumerate(lines[1:], start=2):
        if raw.strip() == "---":
            return fields, index
        match = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", raw)
        if not match:
            continue
        key, value = match.group(1), match.group(2)
        value = re.sub(r"\s+#.*$", "", value).strip().strip("'\"")
        fields[key] = value
    return fields, 0


def split_reference(reference: str) -> tuple[str, str | None]:
    """`tests/test_cart.py::test_add` -> ('tests/test_cart.py', 'test_add')."""
    if "::" in reference:
        file_part, _, test_part = reference.partition("::")
        return file_part.strip(), test_part.strip() or None
    return reference.strip(), None


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def collect_test_files(root: Path) -> set[Path]:
    found: set[Path] = set()
    for pattern in TEST_GLOBS:
        for path in root.glob(pattern):
            if path.is_file() and not is_ignored(path.relative_to(root)):
                found.add(path.relative_to(root))
    return found


# --------------------------------------------------------------------------- #
# Verification
# --------------------------------------------------------------------------- #

@dataclass
class Report:
    covered_ok: list[str] = field(default_factory=list)
    covered_broken: list[tuple[str, int, str]] = field(default_factory=list)
    pending: list[tuple[str, int]] = field(default_factory=list)
    manual: list[str] = field(default_factory=list)
    malformed: list[tuple[str, int, str]] = field(default_factory=list)
    orphans: list[str] = field(default_factory=list)


def check(root: Path) -> Report:
    report = Report()
    cases_root = root / TEST_CASES_DIR

    if not cases_root.is_dir():
        print(
            f"{TEST_CASES_DIR}: [{INVARIANT_ID}] test-cases folder not found "
            f"-- run `codebase-cartographer`, or turn block B off",
            file=sys.stderr,
        )
        return report

    referenced_files: set[str] = set()

    for case_path in sorted(cases_root.rglob("*.md")):
        relative = case_path.relative_to(root).as_posix()
        fields, end_line = parse_front_matter(case_path)

        if not fields:
            report.malformed.append(
                (relative, 1, "front-matter missing or unreadable")
            )
            continue

        status = fields.get("status", "").lower()
        if status not in VALID_STATUS:
            report.malformed.append(
                (relative, end_line or 1,
                 f"invalid `status` field ({status or 'empty'})")
            )
            continue

        if status == "manual":
            report.manual.append(relative)
            continue

        reference = fields.get("automated_test", "").strip()
        if status == "pending" or reference in ("", "null", "~"):
            report.pending.append((relative, end_line or 1))
            continue

        file_part, test_name = split_reference(reference)
        target = root / file_part

        if not target.is_file():
            report.covered_broken.append(
                (relative, end_line or 1,
                 f"the test file `{file_part}` does not exist")
            )
            continue

        referenced_files.add(file_part)

        if test_name:
            try:
                content = target.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                content = ""
            if test_name not in content:
                report.covered_broken.append(
                    (relative, end_line or 1,
                     f"the test `{test_name}` is nowhere to be found in `{file_part}`")
                )
                continue

        report.covered_ok.append(relative)

    for test_file in sorted(collect_test_files(root)):
        as_posix = test_file.as_posix()
        if as_posix not in referenced_files:
            report.orphans.append(as_posix)

    return report


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

def emit(report: Report) -> int:
    for path, line, reason in report.covered_broken:
        print(
            f"{path}:{line}: [{INVARIANT_ID}] test-case marked `covered` but {reason} "
            f"-- fix the `automated_test` field, or move the test-case back to "
            f"`status: pending` if the test was deleted on purpose"
        )

    for path, line, reason in report.malformed:
        print(
            f"{path}:{line}: [{INVARIANT_ID}] {reason} "
            f"-- add a conforming front-matter (see references/templates.md section 2)"
        )

    for path, line in report.pending:
        print(
            f"{path}:{line}: [{INVARIANT_ID}] test-case with no automated test "
            f"-- write the test then fill in `automated_test`, or move it to "
            f"`status: manual` if it will never be automated"
        )

    for path in report.orphans:
        print(
            f"{path}:1: [{INVARIANT_ID}] test file with no test-case attached "
            f"-- create the matching test-case under {TEST_CASES_DIR}/, or add "
            f"this path to the exclusions if it is a purely technical test"
        )

    total = (
        len(report.covered_ok) + len(report.covered_broken)
        + len(report.pending) + len(report.manual) + len(report.malformed)
    )
    print(
        f"\n{total} test-cases: {len(report.covered_ok)} covered_ok, "
        f"{len(report.covered_broken)} covered_broken, {len(report.pending)} pending, "
        f"{len(report.manual)} manual, {len(report.malformed)} malformed. "
        f"{len(report.orphans)} orphan test(s).",
        file=sys.stderr,
    )

    if report.covered_broken or report.malformed:
        return 1
    if report.pending or report.orphans:
        return 2
    return 0


EXPLANATION = f"""\
[{INVARIANT_ID}] Test-case bridge to the real tests

Every scenario under {TEST_CASES_DIR}/ carries a YAML front-matter whose
`automated_test` field names the test covering it, as <path>::<test name>.

This script checks that the reference points at a file and a test that really
exist, and reports the test files no test-case mentions.

Severities:
  error  covered_broken (broken reference), malformed front-matter
  warn   pending (scenario not automated), orphan test

Known limit: this check verifies that a test EXISTS, never what it is worth. A
referenced test may assert nothing at all. That question belongs to block D
(mutation testing).
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Checks the consistency between documented test-cases and real tests."
    )
    parser.add_argument("--explain", action="store_true",
                        help="describes the rule without checking anything")
    parser.add_argument("--root", default=".",
                        help="project root (default: current directory)")
    args = parser.parse_args()

    if args.explain:
        print(EXPLANATION)
        return 0

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"root not found: {root}", file=sys.stderr)
        return 1

    return emit(check(root))


if __name__ == "__main__":
    sys.exit(main())
