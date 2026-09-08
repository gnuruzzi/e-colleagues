#!/usr/bin/env python3
"""Write the e-colleagues operating contract into a project.

Standard library only: this ships to machines the project does not control (§6). Roster data
comes from dist/team.json, rendered by tools/gen.py, because YAML is not available here.

Owns three things and nothing else:
  * the package region of AGENTS.md, between its markers
  * a two-line CLAUDE.md pointing at AGENTS.md [CC-14]
  * .e-colleagues/lock.json

Everything outside a marker pair belongs to the project and is never touched.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import sys

BEGIN = "<!-- e-colleagues:begin"
INDEX = "<!-- e-colleagues:index -->"
BINDINGS = "<!-- e-colleagues:project-bindings -->"
END = "<!-- e-colleagues:end -->"

# bootstrap.py --check FAILS above this. The bump to 65536 lives in the trust-gated project
# config, and an untrusted teammate never gets it [CX-11][CX-03].
AGENTS_MAX_BYTES = 30 * 1024
BLOCK_MAX_BYTES = 2 * 1024          # the package-owned region only
ANTIGRAVITY_CAUTION_CHARS = 12000   # printed as a caution, never enforced [AG-11]


def team_data(explicit: pathlib.Path | None) -> dict:
    if explicit:
        return json.loads(explicit.read_text())
    here = pathlib.Path(__file__).resolve()
    # the skill travels with the plugin, so the path is relative to this file, never
    # ${CLAUDE_PLUGIN_ROOT} or a hardcoded install location [CC-13][CX-10]
    for up in here.parents:
        cand = up / "dist" / "team.json"
        if cand.exists():
            return json.loads(cand.read_text())
    sys.exit("cannot find dist/team.json; pass --team-json")


def package_region(team: dict) -> str:
    """The package-owned region: rewritten on every update (§5.1)."""
    v, profile = team["version"], team["profile"]
    rows = ["| Colleague | Signature | Spawn name |", "|---|---|---|"]
    spawnable = []
    for name in team["roster"]:
        p = team["personas"][name]
        spawn = p["spawn_name"] or "(primary)"
        if p["spawn_name"]:
            spawnable.append(p["spawn_name"])
        rows.append(f"| {p['display']} | `{p['signature'].strip()}` | {spawn} |")
    return "\n".join([
        f"{BEGIN} v={v} profile={profile} -->",
        "## E-Colleagues",
        "",
        *rows,
        "",
        "The Tech-Lead delegates by spawning sub-agents of exactly these types: "
        + ", ".join(spawnable) + ". Specialists never spawn.",
        "Specialists never post externally: findings return to the Tech-Lead, who posts them.",
        "If no Tech-Lead persona is active in this session, invoke the `ec-tech-lead` skill first.",
        "",
    ])


def index_region(team: dict) -> str:
    """Audit-owned: scaffolded once, then rewritten only by an audit, never by an update."""
    lines = [INDEX, "| lens | where it lives | derived from |", "|---|---|---|"]
    for name in team["roster"]:
        lines.append(f"| {team['personas'][name]['lens']} | — | not yet audited |")
    lines.append("")
    return "\n".join(lines)


def bindings_region() -> str:
    """The team's own. Scaffolded once and never touched again (§5.1)."""
    return "\n".join([BINDINGS, "### Platforms and tools", "", "### Workflow and permissions", ""])


def build_block(team: dict) -> str:
    return package_region(team) + "\n" + index_region(team) + "\n" + bindings_region() + "\n" + END + "\n"


def splice(existing: str, team: dict) -> str:
    """Rewrite only the package region; preserve the index and the project's bindings.

    The block goes first because Codex truncates the TAIL once project_doc_max_bytes is
    spent, and the spawn sentence is load-bearing [CX-11][CX-05]. On an update the index is
    audit-owned and the bindings are the team's, so both are carried across verbatim (§5.1).
    """
    if BEGIN in existing and END in existing:
        head = existing[: existing.index(BEGIN)]
        tail = existing[existing.index(END) + len(END):]
        inner = existing[existing.index(BEGIN): existing.index(END)]
        # keep whatever the audit and the team have written in their own regions
        if INDEX in inner:
            keep_index = inner[inner.index(INDEX):]
            if BINDINGS in keep_index:
                idx = keep_index[: keep_index.index(BINDINGS)]
                binds = keep_index[keep_index.index(BINDINGS):]
            else:
                idx, binds = keep_index, bindings_region() + "\n"
        else:
            idx, binds = index_region(team) + "\n", bindings_region() + "\n"
        return head + package_region(team) + "\n" + idx.rstrip("\n") + "\n\n" \
            + binds.rstrip("\n") + "\n\n" + END + tail

    lines = existing.splitlines(keepends=True)
    at = 0
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            at = i + 1
            break
    while at < len(lines) and not lines[at].strip():
        at += 1
    return "".join(lines[:at]) + "\n" + build_block(team) + "\n" + "".join(lines[at:])


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def plan(root: pathlib.Path, team: dict, notes: list[str]) -> dict[pathlib.Path, str]:
    """The files this run owns, and what they should contain.

    `notes` collects things the project must do by hand, which this script will not do for it.
    """
    out = {}
    agents = root / "AGENTS.md"
    existing = agents.read_text() if agents.exists() else f"# AGENTS.md — {root.name}\n"
    out[agents] = splice(existing, team)

    claude = root / "CLAUDE.md"
    # never `/import codex`, which appends a copy of AGENTS.md into CLAUDE.md [CC-14][CC-16]
    if not claude.exists() or claude.read_text().strip() == "@AGENTS.md":
        out[claude] = "@AGENTS.md\n"
    elif "@AGENTS.md" not in claude.read_text():
        # The project owns this file, so it is not rewritten — but without the import Claude
        # never sees the contract, and that must not fail silently.
        notes.append("CLAUDE.md exists and does not import AGENTS.md. Claude Code will not "
                     "see the contract. Add a line reading `@AGENTS.md` to it — do not run "
                     "`/import codex`, which appends a whole copy [CC-14][CC-16].")

    lock = root / ".e-colleagues" / "lock.json"
    doc = {
        "package_version": team["version"],
        "profile": team["profile"],
        "roster": team["roster"],
        "written": {},
        "completed_lenses": [],
        "updated": datetime.date.today().isoformat(),
    }
    for path, content in sorted(out.items()):
        doc["written"][str(path.relative_to(root))] = sha(content)
    out[lock] = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    return out


def budgets(root: pathlib.Path, content: str, warn) -> list[str]:
    errs = []
    size = len(content.encode())
    if size > AGENTS_MAX_BYTES:
        errs.append(f"AGENTS.md is {size} bytes, over the {AGENTS_MAX_BYTES} limit "
                    f"[CX-11]: Codex truncates the tail and an untrusted teammate never "
                    f"gets the raised cap")
    m = re.search(re.escape(BEGIN) + r".*?" + re.escape(END), content, re.S)
    if m and len(m.group(0).encode()) > BLOCK_MAX_BYTES:
        errs.append(f"the managed block is {len(m.group(0).encode())} bytes, over "
                    f"{BLOCK_MAX_BYTES}")
    if len(content) > ANTIGRAVITY_CAUTION_CHARS:
        warn(f"AGENTS.md is {len(content)} characters; Antigravity documents a 12,000 "
             f"character limit for rules files and its application here is UNVERIFIED [AG-11]")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".", type=pathlib.Path)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--team-json", type=pathlib.Path)
    a = ap.parse_args()
    if not (a.write or a.check):
        ap.error("pass --write or --check")

    root = a.root.resolve()
    team = team_data(a.team_json)
    notes: list[str] = []
    files = plan(root, team, notes)

    warnings: list[str] = []
    errs = budgets(root, files[root / "AGENTS.md"], warnings.append)

    changed = []
    for path, content in sorted(files.items()):
        if not path.exists() or path.read_text() != content:
            changed.append(path.relative_to(root))

    for n in notes:
        print(f"action needed: {n}")
    for w in warnings:
        print(f"warning: {w}")
    for e in errs:
        print(f"error: {e}")
    if errs:
        return 1

    if a.check:
        if changed:
            print("would change:")
            for c in changed:
                print(f"  {c}")
            return 1
        print("up to date")
        return 0

    for path, content in sorted(files.items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print(f"wrote {len(files)} files, {len(changed)} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
