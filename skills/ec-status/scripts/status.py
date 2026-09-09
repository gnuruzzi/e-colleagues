#!/usr/bin/env python3
"""Report the contract's health: roster, lens coverage, and which lenses have gone stale.

Standard library only (§6).

Staleness is a `git diff`, not a feature (§5.2): each knowledge file records the commit it
was derived from and the paths that were read, so a lens is stale exactly when any recorded
path changed since that commit.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

STORE = ".e-colleagues/knowledge"
INDEX = "<!-- e-colleagues:index -->"
BINDINGS = "<!-- e-colleagues:project-bindings -->"


def git(root: pathlib.Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.returncode, (r.stdout or r.stderr).strip()


def parse_frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out: dict = {"derived_from": {}}
    for raw in m.group(1).splitlines():
        if not raw.strip():
            continue
        indented = raw.startswith("  ")
        key, _, val = raw.strip().partition(":")
        val = val.strip()
        if key == "derived_from":
            continue
        target = out["derived_from"] if indented else out
        if key == "paths":
            target[key] = [p.strip() for p in val.strip("[]").split(",") if p.strip()]
        else:
            target[key] = val
    return out


def stale_paths(root: pathlib.Path, commit: str, paths: list[str]) -> list[str] | None:
    """Which recorded paths changed since `commit`. None means the question is unanswerable."""
    rc, _ = git(root, "cat-file", "-e", f"{commit}^{{commit}}")
    if rc != 0:
        return None                      # the commit is gone: rebased, squashed, shallow clone
    rc, out = git(root, "diff", "--name-only", f"{commit}..HEAD", "--", *paths)
    if rc != 0:
        return None
    return [l for l in out.splitlines() if l.strip()]


def index_rows(root: pathlib.Path) -> dict[str, str]:
    agents = root / "AGENTS.md"
    if not agents.exists():
        return {}
    s = agents.read_text()
    if INDEX not in s or BINDINGS not in s:
        return {}
    region = s.split(INDEX, 1)[1].split(BINDINGS, 1)[0]
    rows = {}
    for ln in region.splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] not in ("lens", "---") and not set(cells[0]) <= {"-"}:
            rows[cells[0]] = cells[1]
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".", type=pathlib.Path)
    ap.add_argument("--fail-on-stale", action="store_true",
                    help="exit 1 if any lens is stale (for CI)")
    a = ap.parse_args()
    root = a.root.resolve()

    lock_path = root / ".e-colleagues" / "lock.json"
    if not lock_path.exists():
        print("no .e-colleagues/lock.json — this project is not bootstrapped. Run ec-init.")
        return 1
    lock = json.loads(lock_path.read_text())

    print(f"package {lock.get('package_version','?')}  profile {lock.get('profile','?')}")
    print(f"roster: {', '.join(lock.get('roster', []))}")

    rows = index_rows(root)
    completed = set(lock.get("completed_lenses", []))
    print(f"\nlenses ({len(rows)} in the index, {len(completed)} completed)")

    stale_count, unknown = 0, 0
    for lens, where in sorted(rows.items()):
        f = root / STORE / f"{lens}.md"
        if not f.exists():
            state = "not audited" if lens not in completed else f"indexed -> {where}"
            print(f"  {lens:<24} {state}")
            continue
        fm = parse_frontmatter(f.read_text())
        if not fm or not fm.get("derived_from", {}).get("commit"):
            print(f"  {lens:<24} PROVENANCE MISSING — cannot judge staleness")
            unknown += 1
            continue
        d = fm["derived_from"]
        changed = stale_paths(root, d["commit"], d.get("paths", []))
        if changed is None:
            print(f"  {lens:<24} commit {d['commit']} unreachable — re-audit to re-baseline")
            unknown += 1
        elif changed:
            stale_count += 1
            print(f"  {lens:<24} STALE since {d['commit']} — {len(changed)} recorded path(s) changed")
            for c in changed[:5]:
                print(f"      {c}")
            if len(changed) > 5:
                print(f"      … and {len(changed)-5} more")
        else:
            print(f"  {lens:<24} fresh at {d['commit']}")

    print(f"\n{stale_count} stale, {unknown} unknown, {len(rows)} total")
    if a.fail_on_stale and stale_count:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
