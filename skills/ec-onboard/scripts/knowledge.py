#!/usr/bin/env python3
"""Write one knowledge file, record its provenance, and update the index and the lock.

Standard library only: this ships to machines the project does not control (§6).

Provenance is what makes staleness detection a `git diff` rather than a feature (§5.2), so
every file records the commit it was derived from and the paths that were read.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

INDEX = "<!-- e-colleagues:index -->"
BINDINGS = "<!-- e-colleagues:project-bindings -->"
STORE = ".e-colleagues/knowledge"
CONFIDENCE = ("high", "medium", "low")


def git(root: pathlib.Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def frontmatter(lens, persona, commit, paths, version, confidence) -> str:
    """The §5.2 schema. Kept to one deliberately simple shape so the shipped reader needs
    no YAML library; `check.py --knowledge` validates it with a real parser in CI."""
    lines = [
        "---",
        f"lens: {lens}",
        f"persona: {persona}",
        "derived_from:",
        f"  commit: {commit}",
        "  paths: [" + ", ".join(paths) + "]",
        f"  at: {datetime.date.today().isoformat()}",
        f"package_version: {version}",
        f"confidence: {confidence}",
        "---",
    ]
    return "\n".join(lines) + "\n"


def parse_frontmatter(text: str) -> dict | None:
    """Read back exactly the shape written above. Returns None if it is not that shape."""
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


def update_index(root: pathlib.Path, lens: str, where: str, derived: str) -> bool:
    """Rewrite this lens's row in the AGENTS.md index region. Audit-owned (§5.1)."""
    agents = root / "AGENTS.md"
    if not agents.exists():
        sys.exit("no AGENTS.md; run ec-init first")
    s = agents.read_text()
    if INDEX not in s or BINDINGS not in s:
        sys.exit("AGENTS.md has no index region; run ec-init first")
    head, rest = s.split(INDEX, 1)
    region, tail = rest.split(BINDINGS, 1)
    row = f"| {lens} | {where} | {derived} |"
    lines, replaced = [], False
    for ln in region.splitlines():
        if re.match(rf"^\|\s*{re.escape(lens)}\s*\|", ln):
            lines.append(row)
            replaced = True
        else:
            lines.append(ln)
    if not replaced:                      # a lens the block did not scaffold
        at = max(i for i, l in enumerate(lines) if l.startswith("|")) + 1
        lines.insert(at, row)
    body = "\n".join(l for l in lines if l.strip())
    agents.write_text(head + INDEX + "\n" + body + "\n\n" + BINDINGS + tail)
    return replaced


def update_lock(root: pathlib.Path, lens: str, rel: str | None) -> None:
    lock = root / ".e-colleagues" / "lock.json"
    doc = json.loads(lock.read_text()) if lock.exists() else {}
    doc.setdefault("completed_lenses", [])
    if lens not in doc["completed_lenses"]:
        doc["completed_lenses"].append(lens)      # so an interrupted audit resumes (§5.3)
    if rel:
        doc.setdefault("written", {})[rel] = "authored"
    doc["updated"] = datetime.date.today().isoformat()
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=pathlib.Path)
    ap.add_argument("--lens", required=True)
    ap.add_argument("--persona", required=True)
    ap.add_argument("--paths", default="", help="comma-separated paths this lens was derived from")
    ap.add_argument("--confidence", default="high", choices=CONFIDENCE)
    ap.add_argument("--body-file", type=pathlib.Path,
                    help="the knowledge body; omit with --index-only")
    ap.add_argument("--index-only", metavar="WHERE",
                    help="the project already documents this lens; record where and author nothing")
    a = ap.parse_args()
    root = a.root.resolve()

    if a.index_only:
        # Rule 1 of the lens contract: point at the project's own documentation, never copy it
        update_index(root, a.lens, a.index_only, "— (the project's own)")
        update_lock(root, a.lens, None)
        print(f"indexed {a.lens} -> {a.index_only} (nothing authored)")
        return 0

    if not a.body_file:
        ap.error("--body-file is required unless --index-only is given")
    paths = [p.strip() for p in a.paths.split(",") if p.strip()]
    if not paths:
        ap.error("--paths is required: without it staleness cannot be computed")
    for p in paths:
        if not (root / p.rstrip("/")).exists():
            sys.exit(f"recorded path does not exist: {p}")

    commit = git(root, "rev-parse", "--short", "HEAD")
    version = "0.0.0"
    lock = root / ".e-colleagues" / "lock.json"
    if lock.exists():
        version = json.loads(lock.read_text()).get("package_version", version)

    body = a.body_file.read_text().strip()
    out = root / STORE / f"{a.lens}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(frontmatter(a.lens, a.persona, commit, paths, version, a.confidence)
                   + "\n" + body + "\n")
    rel = str(out.relative_to(root))
    update_index(root, a.lens, rel, f"{commit} · {datetime.date.today().isoformat()}")
    update_lock(root, a.lens, rel)
    print(f"wrote {rel} (commit {commit}, {len(paths)} paths recorded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
