"""Report translated pages that are missing or older than their English source.

Translations live under docs/<locale>/ with the same paths as the English pages
(see TRANSLATING.md). A translation counts as outdated when its English source
has commits after the translation's last commit.

Usage: python3 scripts/check-translations.py [--locale pt-br] [--strict]
--strict exits with status 1 when anything is missing or outdated.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
LOCALES = ("pt-br",)
# Generated from English docstrings by Sphinx autodoc, so never translated.
UNTRANSLATED_DIRS = ("api", "_build", "_static", "_templates")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def last_commit(path: Path) -> tuple[str, int] | None:
    out = git("log", "-1", "--format=%H %ct", "--", str(path.relative_to(ROOT)))
    if not out:
        return None
    sha, timestamp = out.split()
    return sha, int(timestamp)


def english_pages() -> list[Path]:
    skip = set(LOCALES) | set(UNTRANSLATED_DIRS)
    return sorted(p for p in DOCS.rglob("*.md") if p.relative_to(DOCS).parts[0] not in skip)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--locale", default="pt-br", choices=LOCALES)
    parser.add_argument("--strict", action="store_true", help="exit with status 1 when anything needs work")
    args = parser.parse_args()

    missing: list[str] = []
    outdated: list[tuple[str, list[str]]] = []
    uncommitted: list[str] = []
    pages = english_pages()

    for source in pages:
        rel = source.relative_to(DOCS)
        target = DOCS / args.locale / rel
        if not target.exists():
            missing.append(str(rel))
            continue
        source_commit, target_commit = last_commit(source), last_commit(target)
        if target_commit is None:
            uncommitted.append(str(rel))
            continue
        if source_commit and source_commit[1] > target_commit[1]:
            newer = git("log", "--format=%h %s", f"{target_commit[0]}..HEAD", "--", str(source.relative_to(ROOT)))
            outdated.append((str(rel), newer.splitlines() or [f"{source_commit[0][:7]} (newer than the translation)"]))

    done = len(pages) - len(missing) - len(outdated)
    print(f"{args.locale}: {done}/{len(pages)} pages translated and up to date")
    if uncommitted:
        print(f"\nNot committed yet ({len(uncommitted)}), counted as up to date:")
        for rel in uncommitted:
            print(f"  {rel}")
    if missing:
        print(f"\nMissing ({len(missing)}):")
        for rel in missing:
            print(f"  {rel}")
    if outdated:
        print(f"\nOutdated ({len(outdated)}): the English page changed after the translation")
        for rel, commits in outdated:
            print(f"  {rel}")
            for line in commits:
                print(f"      {line}")

    return 1 if args.strict and (missing or outdated) else 0


if __name__ == "__main__":
    sys.exit(main())
