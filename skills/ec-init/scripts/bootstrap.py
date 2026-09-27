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
BLOCK_MAX_BYTES = 2 * 1024          # the package-owned region only, BEGIN..INDEX
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


def roster_of(team: dict, profile: str) -> list[str]:
    if profile not in team["profiles"]:
        sys.exit(f"unknown profile '{profile}'; choose one of "
                 f"{', '.join(sorted(team['profiles']))}")
    return team["profiles"][profile]


def package_region(team: dict, profile: str) -> str:
    """The package-owned region: rewritten on every update (§5.1)."""
    v = team["version"]
    rows = ["| Colleague | Signature | Spawn name |", "|---|---|---|"]
    spawnable = []
    for name in roster_of(team, profile):
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


def index_region(team: dict, profile: str) -> str:
    """Audit-owned: scaffolded once, then rewritten only by an audit, never by an update."""
    lines = [INDEX, "| lens | where it lives | derived from |", "|---|---|---|"]
    for name in roster_of(team, profile):
        lines.append(f"| {team['personas'][name]['lens']} | — | not yet audited |")
    lines.append("")
    return "\n".join(lines)


def index_lenses(content: str) -> list[str]:
    """The lens names the audit-owned index currently lists, in order."""
    if INDEX not in content:
        return []
    region = content.split(INDEX, 1)[1]
    region = region.split(BINDINGS, 1)[0] if BINDINGS in region else region
    lenses = []
    for ln in region.splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] != "lens" and not set(cells[0]) <= {"-"}:
            lenses.append(cells[0])
    return lenses


def bindings_region() -> str:
    """The team's own. Scaffolded once and never touched again (§5.1)."""
    return "\n".join([BINDINGS, "### Platforms and tools", "", "### Workflow and permissions", ""])


def build_block(team: dict, profile: str) -> str:
    return (package_region(team, profile) + "\n" + index_region(team, profile) + "\n"
            + bindings_region() + "\n" + END + "\n")


def splice(existing: str, team: dict, profile: str) -> str:
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
            idx, binds = index_region(team, profile) + "\n", bindings_region() + "\n"
        return head + package_region(team, profile) + "\n" + idx.rstrip("\n") + "\n\n" \
            + binds.rstrip("\n") + "\n\n" + END + tail

    lines = existing.splitlines(keepends=True)
    at = 0
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            at = i + 1
            break
    while at < len(lines) and not lines[at].strip():
        at += 1
    return "".join(lines[:at]) + "\n" + build_block(team, profile) + "\n" + "".join(lines[at:])


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def plan(root: pathlib.Path, team: dict, profile: str, notes: list[str]) -> dict[pathlib.Path, str]:
    """The files this run owns, and what they should contain.

    `notes` collects things the project must do by hand, which this script will not do for it.
    """
    out = {}
    agents = root / "AGENTS.md"
    existing = agents.read_text() if agents.exists() else f"# AGENTS.md — {root.name}\n"
    out[agents] = splice(existing, team, profile)

    roster = roster_of(team, profile)
    lenses = [team["personas"][n]["lens"] for n in roster]
    # The index is the audit's region and is carried across verbatim, so a profile change
    # can leave a row that no persona in the new roster will ever audit. That row reads as
    # "not yet audited" forever unless someone is told.
    orphaned = [l for l in index_lenses(out[agents]) if l not in lenses]
    if orphaned:
        notes.append(f"the index lists {', '.join(f'`{l}`' for l in orphaned)}, which no "
                     f"persona in the '{profile}' roster audits, so it can never complete. "
                     f"The index is the audit's, not this script's: remove the row by hand, "
                     f"or choose a profile whose roster includes that lens's persona.")

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
    # The lock has two owners, like AGENTS.md: this script owns the package fields, and the
    # audit owns `completed_lenses` and the knowledge entries under `written`. Rebuilding the
    # whole document wiped the audit's record, so an ec-init run after an ec-onboard made
    # every indexed lens report as "not audited".
    prior = {}
    if lock.exists():
        try:
            prior = json.loads(lock.read_text())
        except json.JSONDecodeError:
            prior = {}
    doc = {
        "package_version": team["version"],
        "profile": profile,
        "roster": roster,
        "lenses": lenses,
        "written": {},
        "completed_lenses": prior.get("completed_lenses", []),
    }
    # carry across anything the audit recorded, which this script does not author
    for rel, val in (prior.get("written") or {}).items():
        if rel.startswith(".e-colleagues/knowledge/"):
            doc["written"][rel] = val
    for path, content in sorted(out.items()):
        # Hash only what the package owns. AGENTS.md is mostly the project's, so hashing the
        # whole file made any edit to the project's own prose report the contract as out of
        # date — found by following the README as a stranger would.
        owned = content
        if path.name == "AGENTS.md":
            m = re.search(re.escape(BEGIN) + r".*?" + re.escape(INDEX), content, re.S)
            owned = m.group(0) if m else content
        doc["written"][str(path.relative_to(root))] = sha(owned)
    # `updated` means "when the contract last changed", so it moves only when something
    # else in the lock did. Stamping today's date unconditionally made --check exit 1 the
    # day after every bootstrap, on the calendar alone — a gate that is red for no reason
    # is a gate people learn to ignore.
    unchanged = all(prior.get(k) == doc[k] for k in doc)
    doc["updated"] = (prior.get("updated") if unchanged and prior.get("updated")
                      else datetime.date.today().isoformat())
    out[lock] = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    return out


def budgets(root: pathlib.Path, content: str, warn) -> list[str]:
    errs = []
    size = len(content.encode())
    if size > AGENTS_MAX_BYTES:
        errs.append(f"AGENTS.md is {size} bytes, over the {AGENTS_MAX_BYTES} limit "
                    f"[CX-11]: Codex truncates the tail and an untrusted teammate never "
                    f"gets the raised cap")
    # The 2 KB budget is the PACKAGE-owned region only (§5.1). The index grows one row per
    # lens and the project-bindings region is the team's to write; both are bounded by the
    # 30 KiB total, not by this.
    m = re.search(re.escape(BEGIN) + r".*?" + re.escape(INDEX), content, re.S)
    if m and len(m.group(0).encode()) > BLOCK_MAX_BYTES:
        errs.append(f"the package-owned region is {len(m.group(0).encode())} bytes, over "
                    f"{BLOCK_MAX_BYTES}")
    if len(content) > ANTIGRAVITY_CAUTION_CHARS:
        warn(f"AGENTS.md is {len(content)} characters; Antigravity documents a 12,000 "
             f"character limit for rules files and its application here is UNVERIFIED [AG-11]")
    return errs


def install_personas(dist: pathlib.Path, dest: pathlib.Path, roster: list[str],
                     dry_run: bool) -> tuple[list[str], list[str]]:
    """Copy the rendered role files to a Codex agents directory as REAL FILES.

    Never symlinks: Codex opens a role's config with O_NOFOLLOW at spawn, so a symlinked
    role is discovered and then fails with "agent type is currently not available"
    (docs/experiments.md E5), so any symlink-based install layout is silently broken.
    """
    written, skipped = [], []
    for name in roster:
        src = dist / f"{name}.toml"
        if not src.exists():          # the tech-lead is developer_instructions, not a role
            skipped.append(name)
            continue
        target = dest / f"{name}.toml"
        if target.is_symlink():
            # replacing a symlink in place would write through it; remove it first
            if not dry_run:
                target.unlink()
        if not dry_run:
            dest.mkdir(parents=True, exist_ok=True)
            target.write_text(src.read_text())
        written.append(name)
    return written, skipped


def install_user_scope(team: dict, a) -> int:
    """§9 route A: personas and the tech-lead profile, for this machine.

    Writes no project files: a per-user install and a per-project contract are different
    jobs. Never writes ~/.codex/config.toml — Codex rewrites that file itself.
    """
    here = pathlib.Path(__file__).resolve()
    dist = a.dist
    if dist is None:
        for up in here.parents:
            if (up / "dist" / "codex" / "agents").exists():
                dist = up / "dist" / "codex" / "agents"
                break
    if dist is None or not dist.exists():
        print("error: cannot find dist/codex/agents; pass --dist")
        return 1

    roster = roster_of(team, a.profile or "default")
    codex_home = pathlib.Path.home() / ".codex"
    dest = codex_home / "agents"

    if a.check:
        stale = []
        for name in roster:
            src = dist / f"{name}.toml"
            if not src.exists():
                continue
            t = dest / f"{name}.toml"
            if t.is_symlink():
                stale.append(f"{t.name} is a SYMLINK and cannot spawn [CX-02]")
            elif not t.exists() or t.read_text() != src.read_text():
                stale.append(f"{t.name} is missing or out of date")
        # The profile carries the tech-lead's whole body, so it goes stale whenever a
        # persona body changes. Checking only the agent files reported "up to date" while
        # the installed tech-lead was several revisions behind.
        profile_src = dist.parent / "e-colleagues.config.toml"
        profile_dst = codex_home / "e-colleagues.config.toml"
        if profile_src.exists():
            if not profile_dst.exists():
                stale.append("e-colleagues.config.toml is not installed")
            elif profile_dst.read_text() != profile_src.read_text():
                stale.append("e-colleagues.config.toml is out of date")
        for s_ in stale:
            print(f"  {s_}")
        print("up to date" if not stale else f"{len(stale)} file(s) need --write")
        return 1 if stale else 0

    written, skipped = install_personas(dist, dest, roster, dry_run=False)
    print(f"installed {len(written)} personas into ~/.codex/agents as real files: "
          f"{', '.join(written)}")
    if skipped:
        print(f"delivered as developer_instructions instead, not a role file: "
              f"{', '.join(skipped)} [CX-06]")

    profile_src = dist.parent / "e-colleagues.config.toml"
    if profile_src.exists():
        (codex_home / "e-colleagues.config.toml").write_text(profile_src.read_text())
        print("installed ~/.codex/e-colleagues.config.toml — run `codex --profile e-colleagues`")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".", type=pathlib.Path,
                    help="the project root; ignored with --scope user")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--team-json", type=pathlib.Path)
    ap.add_argument("--profile", default=None,
                    help="which roster to write; ec-init proposes it from evidence (D3). "
                         "Defaults to the profile recorded in lock.json, so a plain --write "
                         "never silently changes a project's roster")
    ap.add_argument("--scope", choices=("project", "user"), default="project",
                    help="project: write this repository's contract. user: install the "
                         "personas and the profile for this machine (§9 route A). They are "
                         "different jobs and are not combined")
    ap.add_argument("--dist", type=pathlib.Path,
                    help="dist/codex/agents directory; defaults to the one beside this skill")
    a = ap.parse_args()
    if not (a.write or a.check):
        ap.error("pass --write or --check")

    team = team_data(a.team_json)

    if a.scope == "user":
        return install_user_scope(team, a)

    root = a.root.resolve()
    notes: list[str] = []
    # A project's roster is its own decision. Honour what the lock already records, so a
    # plain --write after an ec-init does not quietly swap the roster back to the default.
    profile = a.profile
    if profile is None:
        lock_path = root / ".e-colleagues" / "lock.json"
        if lock_path.exists():
            try:
                profile = json.loads(lock_path.read_text()).get("profile")
            except json.JSONDecodeError:
                profile = None
        profile = profile or "default"
    files = plan(root, team, profile, notes)

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
