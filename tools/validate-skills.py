#!/usr/bin/env python3
"""Valide les skills du dépôt contre la spécification Agent Skills.

Référence : https://agentskills.io/specification

Le validateur officiel `skills-ref` se déclare réservé à la démonstration et
s'installe depuis un checkout git : inaccessible en pre-commit. Ce script le
remplace en respectant le contrat de `references/templates.md` (section 6) :
`--explain`, `--root`, une ligne par violation, aucun auto-fix, aucune
dépendance à installer.
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
MAX_BODY_LINES = 500  # recommandation du spec, pas une règle : sévérité warn

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

REGLES = [
    ("INV-SKILL-001", "error", "Chaque dossier de skill contient un SKILL.md"),
    ("INV-SKILL-002", "error", "SKILL.md ouvre sur un frontmatter YAML délimité par ---"),
    ("INV-SKILL-003", "error", f"`name` : 1-{MAX_NAME} caractères, [a-z0-9-], sans tiret en tête/fin ni double tiret"),
    ("INV-SKILL-004", "error", "`name` est identique au nom du dossier parent"),
    ("INV-SKILL-005", "error", f"`description` présente, non vide, ≤ {MAX_DESCRIPTION} caractères"),
    ("INV-SKILL-006", "error", f"`compatibility`, si présent, ≤ {MAX_COMPATIBILITY} caractères"),
    ("INV-SKILL-007", "warn", f"Le corps de SKILL.md reste sous {MAX_BODY_LINES} lignes"),
]


def expliquer() -> None:
    print("Validation des skills contre la spécification Agent Skills")
    print("Périmètre : tout sous-dossier de skills/ contenant un SKILL.md\n")
    for code, severite, enonce in REGLES:
        print(f"  {code} [{severite:5}] {enonce}")
    print("\nCodes de sortie : 0 conforme · 1 violation error · 2 uniquement des warn")


def lire_frontmatter(lignes):
    """Retourne (champs, ligne_de_fin) ou (None, 0) si le frontmatter est absent.

    Parseur volontairement minimal : le spec ne définit que des scalaires et un
    `metadata` plat. Gère les blocs `>` et `|` et les continuations indentées.
    """
    if not lignes or lignes[0].strip() != "---":
        return None, 0

    fin = None
    for i in range(1, len(lignes)):
        if lignes[i].strip() == "---":
            fin = i
            break
    if fin is None:
        return None, 0

    champs, cle_courante = {}, None
    for ligne in lignes[1:fin]:
        entete = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):[ \t]*(.*)$", ligne)
        if entete:
            cle_courante = entete.group(1)
            valeur = entete.group(2).strip()
            champs[cle_courante] = "" if valeur in (">", "|", ">-", "|-") else valeur
        elif cle_courante and ligne.strip() and ligne[:1] in (" ", "\t"):
            suite = ligne.strip()
            champs[cle_courante] = f"{champs[cle_courante]} {suite}".strip()
        elif not ligne.strip():
            continue
        else:
            cle_courante = None

    return champs, fin


def compter_caracteres(texte: str) -> int:
    """Compte en caractères Unicode normalisés NFC, jamais en octets."""
    return len(unicodedata.normalize("NFC", texte))


def valider_skill(dossier: Path, racine: Path, violations: list) -> None:
    relatif = dossier.relative_to(racine)
    skill_md = dossier / "SKILL.md"

    if not skill_md.is_file():
        violations.append((
            "error", f"{relatif}/: [INV-SKILL-001] dossier de skill sans SKILL.md"
            f" — ajoute {relatif}/SKILL.md avec un frontmatter `name` et `description`"
        ))
        return

    chemin = skill_md.relative_to(racine)
    lignes = skill_md.read_text(encoding="utf-8").splitlines()
    champs, fin_frontmatter = lire_frontmatter(lignes)

    if champs is None:
        violations.append((
            "error", f"{chemin}:1: [INV-SKILL-002] frontmatter YAML absent ou non refermé"
            " — la première ligne doit être `---`, suivie des champs, puis d'un `---` de fermeture"
        ))
        return

    nom = champs.get("name", "").strip().strip("\"'")
    if not nom:
        violations.append((
            "error", f"{chemin}:2: [INV-SKILL-003] champ `name` absent"
            f" — ajoute `name: {dossier.name}`"
        ))
    else:
        if compter_caracteres(nom) > MAX_NAME or not NAME_PATTERN.match(nom):
            violations.append((
                "error", f"{chemin}:2: [INV-SKILL-003] `name: {nom}` invalide"
                f" — 1 à {MAX_NAME} caractères parmi [a-z0-9-], sans tiret en tête ou en fin,"
                " sans double tiret"
            ))
        if nom != dossier.name:
            violations.append((
                "error", f"{chemin}:2: [INV-SKILL-004] `name: {nom}` ≠ dossier `{dossier.name}`"
                f" — renomme le champ en `{dossier.name}` ou renomme le dossier en `{nom}`"
            ))

    description = champs.get("description", "").strip().strip("\"'")
    if not description:
        violations.append((
            "error", f"{chemin}:3: [INV-SKILL-005] champ `description` absent ou vide"
            " — décris ce que fait le skill ET quand l'utiliser : c'est le seul texte"
            " chargé au démarrage, donc le seul déclencheur"
        ))
    else:
        taille = compter_caracteres(description)
        if taille > MAX_DESCRIPTION:
            violations.append((
                "error", f"{chemin}:3: [INV-SKILL-005] `description` de {taille} caractères"
                f" (max {MAX_DESCRIPTION}) — retire {taille - MAX_DESCRIPTION} caractères,"
                " en coupant d'abord les déclencheurs redondants"
            ))

    compatibility = champs.get("compatibility", "").strip().strip("\"'")
    if compatibility:
        taille = compter_caracteres(compatibility)
        if taille > MAX_COMPATIBILITY:
            violations.append((
                "error", f"{chemin}:4: [INV-SKILL-006] `compatibility` de {taille} caractères"
                f" (max {MAX_COMPATIBILITY}) — retire {taille - MAX_COMPATIBILITY} caractères"
            ))

    corps = len(lignes) - (fin_frontmatter + 1)
    if corps > MAX_BODY_LINES:
        violations.append((
            "warn", f"{chemin}:{fin_frontmatter + 2}: [INV-SKILL-007] corps de {corps} lignes"
            f" (recommandé ≤ {MAX_BODY_LINES}) — déporte le détail dans references/ :"
            " le corps entier est chargé en contexte dès que le skill s'active"
        ))


def main() -> int:
    parseur = argparse.ArgumentParser(description="Valide les skills contre la spec Agent Skills.")
    parseur.add_argument("--explain", action="store_true", help="décrit les règles sans rien vérifier")
    parseur.add_argument("--root", default=".", help="racine du dépôt (défaut : répertoire courant)")
    arguments = parseur.parse_args()

    if arguments.explain:
        expliquer()
        return 0

    racine = Path(arguments.root).resolve()
    dossier_skills = racine / "skills"
    if not dossier_skills.is_dir():
        print(f"{arguments.root}: aucun dossier skills/ — rien à valider", file=sys.stderr)
        return 1

    violations: list = []
    dossiers = sorted(d for d in dossier_skills.iterdir() if d.is_dir())
    for dossier in dossiers:
        valider_skill(dossier, racine, violations)

    for severite, message in violations:
        print(message)

    erreurs = sum(1 for severite, _ in violations if severite == "error")
    avertissements = len(violations) - erreurs

    if not violations:
        print(f"{len(dossiers)} skills validés, aucune violation.")
        return 0

    print(f"\n{len(dossiers)} skills validés — {erreurs} error, {avertissements} warn.", file=sys.stderr)
    return 1 if erreurs else 2


if __name__ == "__main__":
    sys.exit(main())
