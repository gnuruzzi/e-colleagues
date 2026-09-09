#!/usr/bin/env python3
"""Static gates for the generated tree and the persona source.

Every check here exists because some host fails open. In particular `check.py` owns the
[CC-07] Claude frontmatter guard: `claude plugin validate` does NOT catch a malformed agent
frontmatter when the value contains a colon, and every routing sentence has one
(docs/experiments.md E15).
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import tomllib

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("check.py needs PyYAML: pip install pyyaml")

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAILS: list[str] = []


def fail(msg: str) -> None:
    FAILS.append(msg)


def ok(label: str) -> None:
    print(f"  ok   {label}")


# --------------------------------------------------------------------------- team + personas
def check_personas():
    team = yaml.safe_load((ROOT / "team.yaml").read_text())
    catalog, sigs = set(team["catalog"]), team["signatures"]
    if catalog != set(sigs):
        fail(f"team.yaml: catalog and signatures disagree: {catalog ^ set(sigs)}")
    for prof, names in team["profiles"].items():
        if not set(names) <= catalog:
            fail(f"team.yaml: profile {prof} names personas outside the catalog")
        if names[0] != "tech-lead":
            fail(f"team.yaml: profile {prof} must start with tech-lead")

    seen_lenses, primaries = set(), []
    for f in sorted((ROOT / "personas").glob("*.yaml")):
        p = yaml.safe_load(f.read_text())
        n = p["name"]
        if n not in catalog:
            fail(f"{f.name}: {n} is not in the catalog")
        if n in ("default", "worker", "explorer"):
            fail(f"{f.name}: {n} collides with a Codex built-in [CX-02]")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", n):
            fail(f"{f.name}: name must be kebab-case [CC-03]")
        if ":" in n:
            fail(f"{f.name}: an agent name may not contain ':' [CC-03]")
        if p["signature"] != sigs[n]:
            fail(f"{f.name}: signature differs from team.yaml")
        # the routing sentence every host uses to decide delegation
        d = " ".join(p["description"].split())
        if "Use " not in d or "not use" not in d.lower():
            fail(f"{f.name}: description must be a routing sentence saying when NOT to use it")
        # D6: only the tech-lead may post externally
        if p["external_post"] != (p["role"] == "primary"):
            fail(f"{f.name}: external_post must be true only for the primary (D6)")
        # D7 + flat team: only the primary may delegate
        if p["capabilities"]["delegate"] and p["role"] != "primary":
            fail(f"{f.name}: a specialist may not delegate")
        lens = p["lens"]["name"]
        if lens in seen_lenses:
            fail(f"{f.name}: duplicate lens {lens}")
        seen_lenses.add(lens)
        if p["role"] == "primary":
            primaries.append(n)
        body = (ROOT / "personas" / p["prompt"]).read_text()
        if "r4:" not in body.split("---")[1]:
            fail(f"{p['prompt']}: missing r4 frontmatter")
    if primaries != ["tech-lead"]:
        fail(f"exactly one primary expected, got {primaries}")
    ok(f"personas ({len(catalog)}) and team.yaml consistent")


# --------------------------------------------------------------------------- codex dialect
def check_codex():
    host = yaml.safe_load((ROOT / "hosts" / "codex.yaml").read_text())
    allowed = set(host["agent_file"]["allowed_keys"])
    required = host["agent_file"]["required_keys"]
    files = sorted((ROOT / "dist" / "codex" / "agents").glob("*.toml"))
    if not files:
        fail("dist/codex/agents: no role files rendered")
    for f in files:
        if f.is_symlink():
            fail(f"{f.name}: a role file must be a real file, never a symlink (E5)")
        try:
            d = tomllib.loads(f.read_bytes().decode())
        except tomllib.TOMLDecodeError as e:
            fail(f"{f.name}: does not parse: {e}")
            continue
        extra = set(d) - allowed
        if extra:
            fail(f"{f.name}: keys outside the whitelist would drop the agent silently: {extra} [CX-02]")
        for k in required:
            if not str(d.get(k, "")).strip():
                fail(f"{f.name}: {k} is required and must be non-blank [CX-02]")
        # the guarantee this design rests on
        p = yaml.safe_load((ROOT / "personas" / f"{d['name']}.yaml").read_text())
        if not p["capabilities"]["edit"]:
            if d.get("sandbox_mode") != "read-only":
                fail(f"{f.name}: a read-only persona must set sandbox_mode = \"read-only\"")
            if d.get("approval_policy") != "never":
                fail(f"{f.name}: read-only needs approval_policy = \"never\", or the sandbox "
                     f"is bypassable [CX-02]")
        if "sandbox_mode" not in d:
            fail(f"{f.name}: sandbox_mode must always be written; an omitted key inherits "
                 f"the session sandbox [CX-02]")
    ok(f"codex role files ({len(files)}) parse, whitelisted, sandbox pairs correct")


# --------------------------------------------------------------------------- claude fail-open
CLAUDE_ALLOWED = {"name", "description", "model", "effort", "maxTurns", "tools",
                  "disallowedTools", "skills", "memory", "background", "isolation"}
CLAUDE_FORBIDDEN = {"permissionMode", "hooks", "mcpServers"}


def check_claude_agents():
    """The [CC-07] guard. `claude plugin validate` does not do this (E15)."""
    d = ROOT / "dist" / "claude" / "agents"
    files = sorted(d.glob("*.md")) if d.exists() else []
    if not files:
        print("  skip claude agents (not rendered until M5)")
        return
    for f in files:
        text = f.read_text()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            fail(f"{f.name}: no frontmatter block")
            continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            fail(f"{f.name}: frontmatter does not parse, and validate would not catch it: {e}")
            continue
        if not isinstance(fm, dict):
            fail(f"{f.name}: frontmatter is not a mapping")
            continue
        unknown = set(fm) - CLAUDE_ALLOWED
        if unknown:
            fail(f"{f.name}: unknown frontmatter keys {unknown}")
        present = set(fm) & CLAUDE_FORBIDDEN
        if present:
            fail(f"{f.name}: {present} are silently ignored in plugin agents [CC-07]")
        if ":" in str(fm.get("name", "")):
            fail(f"{f.name}: an agent name may not contain ':' [CC-03]")
        if not str(fm.get("description", "")).strip():
            fail(f"{f.name}: description is required")
        p = yaml.safe_load((ROOT / "personas" / f"{fm['name']}.yaml").read_text())
        if not p["capabilities"]["edit"] and fm.get("memory"):
            fail(f"{f.name}: memory re-enables Write and Edit on a read-only persona [CC-07]")
    ok(f"claude agents ({len(files)}) frontmatter parsed and whitelisted")


# --------------------------------------------------------------------------- skills
BANNED_TOKENS = ["$ARGUMENTS", "${CLAUDE_SKILL_DIR}", "${CLAUDE_PLUGIN_ROOT}"]


def check_skills():
    files = sorted((ROOT / "skills").rglob("SKILL.md"))
    if not files:
        fail("skills/: none found")
    for f in files:
        text = f.read_text()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            fail(f"{f}: no frontmatter")
            continue
        fm = yaml.safe_load(m.group(1))
        extra = set(fm) - {"name", "description", "metadata"}
        if extra:
            fail(f"{f}: frontmatter keys outside {{name, description, metadata}}: {extra}")
        if "compatibility" in fm:
            fail(f"{f}: Codex's bundled validator omits `compatibility` [STD-01]")
        if fm.get("name") != f.parent.name:
            fail(f"{f}: name must equal the directory ({f.parent.name})")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fm.get("name", "")):
            fail(f"{f}: name must be kebab-case")
        if len(fm.get("description", "")) > 1024:
            fail(f"{f}: description over 1024 characters")
        body = text[m.end():]
        for tok in BANNED_TOKENS:
            if tok in body:
                fail(f"{f}: {tok} reaches the model literally on Codex and Antigravity "
                     f"[CX-12][AG-10]")
        if re.search(r"(?m)^!", body):
            fail(f"{f}: a leading `!` command is Claude-only [CX-12]")
        if len(body.encode()) > 7 * 1024:
            fail(f"{f}: body over 7 KB")
    ok(f"skills ({len(files)}) frontmatter and portability clean")


# --------------------------------------------------------------------------- persona bodies
def check_rendered_bodies():
    """Every specialist body carries the §4 skeleton and the RETURN block verbatim."""
    ret = (ROOT / "personas" / "_shared" / "return.md").read_text()
    block = ret[ret.index("### RETURN"): ret.rindex("```")].strip()
    n = 0
    for f in sorted((ROOT / "dist" / "codex" / "agents").glob("*.toml")):
        d = tomllib.loads(f.read_bytes().decode())
        body = d["developer_instructions"]
        for section in ("Position in the tree", "Operating rules", "R4 — Side effects",
                        "Your audit lens", "Addressing the team"):
            if section not in body:
                fail(f"{f.name}: body is missing the '{section}' section")
        if block not in body:
            fail(f"{f.name}: the RETURN block is not present verbatim")
        if "never post" not in body.lower():
            fail(f"{f.name}: R5 (never post externally) missing (D6)")
        n += 1
    ok(f"rendered specialist bodies ({n}) carry the skeleton and RETURN verbatim")


# --------------------------------------------------------------------------- knowledge store
KNOWLEDGE_KEYS = {"lens", "persona", "derived_from", "package_version", "confidence"}
DERIVED_KEYS = {"commit", "paths", "at"}


def check_knowledge(root: pathlib.Path | None = None):
    """§13 item 8. The shipped readers parse this shape by hand because they are stdlib-only;
    here it is validated with a real YAML parser, and the index is cross-checked against disk.
    """
    root = root or ROOT
    store = root / ".e-colleagues" / "knowledge"
    agents = root / "AGENTS.md"
    if not store.exists():
        print("  skip knowledge store (this repository has none)")
        return
    lenses = {p.stem for p in store.glob("*.md")}
    for f in sorted(store.glob("*.md")):
        text = f.read_text()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            fail(f"{f.name}: no provenance frontmatter (§5.2)")
            continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            fail(f"{f.name}: provenance does not parse: {e}")
            continue
        missing = KNOWLEDGE_KEYS - set(fm)
        if missing:
            fail(f"{f.name}: provenance missing {missing}")
            continue
        if fm["lens"] != f.stem:
            fail(f"{f.name}: lens '{fm['lens']}' does not match the filename")
        d = fm.get("derived_from") or {}
        if DERIVED_KEYS - set(d):
            fail(f"{f.name}: derived_from missing {DERIVED_KEYS - set(d)}")
        if not d.get("paths"):
            fail(f"{f.name}: derived_from.paths is empty, so staleness cannot be computed")
        if fm.get("confidence") not in ("high", "medium", "low"):
            fail(f"{f.name}: confidence must be high, medium or low")
    # the index must correspond one-to-one with what is on disk
    if agents.exists():
        s = agents.read_text()
        if "<!-- e-colleagues:index -->" in s and "<!-- e-colleagues:project-bindings -->" in s:
            region = s.split("<!-- e-colleagues:index -->", 1)[1] \
                      .split("<!-- e-colleagues:project-bindings -->", 1)[0]
            indexed = set()
            for ln in region.splitlines():
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                if len(cells) == 3 and cells[0] not in ("lens",) and not set(cells[0]) <= {"-"}:
                    if ".e-colleagues/knowledge/" in cells[1]:
                        indexed.add(pathlib.Path(cells[1]).stem)
            if indexed - lenses:
                fail(f"index names knowledge files that do not exist: {indexed - lenses}")
            if lenses - indexed:
                fail(f"knowledge files not named in the index: {lenses - indexed}")
    ok(f"knowledge store ({len(lenses)}) provenance valid and index consistent")


# --------------------------------------------------------------------------- drift
def check_drift():
    sys.path.insert(0, str(ROOT / "tools"))
    import gen  # noqa: E402
    stale = [rel for rel, content in gen.build().items()
             if not (ROOT / rel).exists() or (ROOT / rel).read_text() != content]
    if stale:
        fail("generated tree is stale, run tools/gen.py: " + ", ".join(sorted(stale)))
    else:
        ok("no drift between personas/ and the generated tree")


def main():
    ap = argparse.ArgumentParser()
    for flag in ("personas", "codex", "claude", "skills", "bodies", "knowledge", "drift"):
        ap.add_argument(f"--{flag}", action="store_true")
    a = ap.parse_args()
    chosen = {k for k, v in vars(a).items() if v}
    run_all = not chosen
    print("check.py")
    if run_all or "personas" in chosen: check_personas()
    if run_all or "codex" in chosen: check_codex()
    if run_all or "claude" in chosen: check_claude_agents()
    if run_all or "skills" in chosen: check_skills()
    if run_all or "bodies" in chosen: check_rendered_bodies()
    if run_all or "knowledge" in chosen: check_knowledge()
    if run_all or "drift" in chosen: check_drift()
    if FAILS:
        print("\nFAILED:")
        for f in FAILS:
            print("  " + f)
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
