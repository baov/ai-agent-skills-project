#!/usr/bin/env python3
"""Brique B — pont test-cases <-> tests reels.

Verifie que chaque scenario documente sous docs/metier/test-cases/ pointe vers un
test automatise qui existe reellement, et signale les tests sans test-case.

Contrat harness (voir references/templates.md section 6) :
  --explain          decrit la regle sans rien verifier
  --root <chemin>    racine du projet (defaut : repertoire courant)
  sortie             path:line: [INV-NNN] message -- remediation
  code 0             tout est coherent
  code 1             au moins un covered_broken (severite error)
  code 2             uniquement des warns (pending, orphelins)

Aucune dependance externe : le front-matter est parse a la main pour que le
script tourne en CI minimale.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

INVARIANT_ID = "INV-002"

TEST_CASES_DIR = Path("docs/metier/test-cases")

# Ou chercher les tests reels, par ordre de frequence. Adapter au projet.
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
    """Retourne (champs, ligne de fin du front-matter).

    Parseur volontairement minimal : cles plates, valeurs scalaires, commentaires
    en fin de ligne ignores. Suffisant pour le front-matter des test-cases et
    evite une dependance YAML.
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
    """`tests/test_panier.py::test_ajout` -> ('tests/test_panier.py', 'test_ajout')."""
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
            f"{TEST_CASES_DIR}: [{INVARIANT_ID}] dossier de test-cases introuvable "
            f"-- lance `codebase-cartographer` ou desactive la brique B",
            file=sys.stderr,
        )
        return report

    referenced_files: set[str] = set()

    for case_path in sorted(cases_root.rglob("*.md")):
        relative = case_path.relative_to(root).as_posix()
        fields, end_line = parse_front_matter(case_path)

        if not fields:
            report.malformed.append(
                (relative, 1, "front-matter absent ou illisible")
            )
            continue

        status = fields.get("status", "").lower()
        if status not in VALID_STATUS:
            report.malformed.append(
                (relative, end_line or 1,
                 f"champ `status` invalide ({status or 'vide'})")
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
                 f"le fichier de test `{file_part}` n'existe pas")
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
                     f"le test `{test_name}` est introuvable dans `{file_part}`")
                )
                continue

        report.covered_ok.append(relative)

    for test_file in sorted(collect_test_files(root)):
        as_posix = test_file.as_posix()
        if as_posix not in referenced_files:
            report.orphans.append(as_posix)

    return report


# --------------------------------------------------------------------------- #
# Sortie
# --------------------------------------------------------------------------- #

def emit(report: Report) -> int:
    for path, line, reason in report.covered_broken:
        print(
            f"{path}:{line}: [{INVARIANT_ID}] test-case marque `covered` mais {reason} "
            f"-- corrige le champ `automated_test`, ou repasse le test-case en "
            f"`status: pending` si le test a ete supprime volontairement"
        )

    for path, line, reason in report.malformed:
        print(
            f"{path}:{line}: [{INVARIANT_ID}] {reason} "
            f"-- ajoute un front-matter conforme (voir references/templates.md section 2)"
        )

    for path, line in report.pending:
        print(
            f"{path}:{line}: [{INVARIANT_ID}] test-case sans test automatise "
            f"-- ecris le test puis renseigne `automated_test`, ou passe en "
            f"`status: manual` s'il ne sera jamais automatise"
        )

    for path in report.orphans:
        print(
            f"{path}:1: [{INVARIANT_ID}] fichier de test sans test-case associe "
            f"-- cree le test-case correspondant sous {TEST_CASES_DIR}/, ou ajoute "
            f"ce chemin aux exclusions s'il s'agit d'un test purement technique"
        )

    total = (
        len(report.covered_ok) + len(report.covered_broken)
        + len(report.pending) + len(report.manual) + len(report.malformed)
    )
    print(
        f"\n{total} test-cases : {len(report.covered_ok)} covered_ok, "
        f"{len(report.covered_broken)} covered_broken, {len(report.pending)} pending, "
        f"{len(report.manual)} manual, {len(report.malformed)} malformes. "
        f"{len(report.orphans)} test(s) orphelin(s).",
        file=sys.stderr,
    )

    if report.covered_broken or report.malformed:
        return 1
    if report.pending or report.orphans:
        return 2
    return 0


EXPLANATION = f"""\
[{INVARIANT_ID}] Pont test-cases <-> tests reels

Chaque scenario sous {TEST_CASES_DIR}/ porte un front-matter YAML dont le champ
`automated_test` designe le test qui le couvre, au format <chemin>::<nom du test>.

Ce script verifie que la reference pointe vers un fichier et un test qui existent
vraiment, et signale les fichiers de test qu'aucun test-case ne mentionne.

Severites :
  error  covered_broken (reference cassee), front-matter malforme
  warn   pending (scenario non automatise), test orphelin

Limite connue : ce check verifie l'EXISTENCE d'un test, jamais sa valeur. Un test
reference peut n'asserter rien du tout. C'est la brique D (mutation testing) qui
repond a cette question.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifie la coherence entre test-cases documentes et tests reels."
    )
    parser.add_argument("--explain", action="store_true",
                        help="decrit la regle sans rien verifier")
    parser.add_argument("--root", default=".",
                        help="racine du projet (defaut : repertoire courant)")
    args = parser.parse_args()

    if args.explain:
        print(EXPLANATION)
        return 0

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"racine introuvable : {root}", file=sys.stderr)
        return 1

    return emit(check(root))


if __name__ == "__main__":
    sys.exit(main())
