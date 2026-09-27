#!/usr/bin/env python3
"""Static gates for the generated tree and the persona source.

Every check here exists because some host fails open. In particular `check.py` owns the
[CC-07] Claude frontmatter guard: `claude plugin validate` does NOT catch a malformed agent
frontmatter when the value contains a colon, and every routing sentence has one
(docs/experiments.md E15).
"""
from __future__ import annotations

import argparse
import json
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
        print("  skip claude agents (none rendered)")
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


# --------------------------------------------------------------------------- opencode
def check_opencode():
    """opencode agents fail OPEN: an unknown key is silently moved into `options`, so a
    misspelled `permision:` yields a reviewer with full default permissions [OC-01][OC-02].
    Only this gate stands between that and a shipped agent."""
    host = yaml.safe_load((ROOT / "hosts" / "opencode.yaml").read_text())
    allowed = set(host["agent_file"]["allowed_keys"])
    perm_keys = set(host["permission_keys"])
    aliases = host.get("permission_aliases", {})

    def both_spellings(label: str, perm: dict) -> None:
        # The 2.x runtime renamed `task` and `bash`; the schema still lists the old names.
        # Either alone is a silent fail-open on the version that knows only the other.
        for old, new in aliases.items():
            a, b = perm.get(old), perm.get(new)
            if (a is None) != (b is None) or (a is not None and a != b):
                fail(f"{label}: permission `{old}` and its 2.x name `{new}` must both be "
                     f"present with identical rules [OC-02]")

    # The key lists above were transcribed from the published schema; the vendored copy is
    # what makes a later change to that schema fail this gate instead of going unnoticed.
    schema_path = ROOT / "hosts" / host["schema_file"]
    defs = json.loads(schema_path.read_text())["$defs"]
    schema_agent_keys = set(defs["AgentConfig"]["properties"])
    schema_perm_keys = set(next(v for v in defs["PermissionConfig"]["anyOf"]
                               if v.get("type") == "object")["properties"])
    cmd = defs["Config"]["properties"]["command"]["additionalProperties"]
    schema_cmd_keys, schema_cmd_required = set(cmd["properties"]), set(cmd.get("required", []))
    drift = []
    # `name` is accepted by the loader though absent from the schema [OC-02]; the 2.x
    # runtime names are accepted though absent from the schema (E20 addendum).
    if allowed - {"name"} != schema_agent_keys:
        drift.append(f"agent keys {sorted((allowed - {'name'}) ^ schema_agent_keys)}")
    if perm_keys - set(aliases.values()) != schema_perm_keys:
        drift.append(f"permission keys "
                     f"{sorted((perm_keys - set(aliases.values())) ^ schema_perm_keys)}")
    if (set(host["config"]["command_keys"]) != schema_cmd_keys
            or set(host["config"]["command_required"]) != schema_cmd_required):
        drift.append("command keys")
    if drift:
        fail(f"hosts/opencode.yaml drifted from the vendored schema {schema_path.name}: "
             f"{'; '.join(drift)} — refresh the copy or the lists, and re-derive (E16 C3)")

    d = ROOT / "dist" / "opencode" / "agents"
    files = sorted(d.glob("*.md")) if d.exists() else []
    if not files:
        print("  skip opencode agents (not rendered)")
        return
    for f in files:
        m = re.match(r"^---\n(.*?)\n---\n", f.read_text(), re.S)
        if not m:
            fail(f"{f.name}: no frontmatter")
            continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            fail(f"{f.name}: frontmatter does not parse: {e}")
            continue
        unknown = set(fm) - allowed
        if unknown:
            fail(f"{f.name}: {unknown} is outside KNOWN_KEYS and would vanish into "
                 f"`options` with full default permissions [OC-02]")
        if "options" in fm:
            fail(f"{f.name}: `options` content means a key was silently swallowed [OC-02]")
        for k in host["agent_file"]["required_keys"]:
            if not fm.get(k):
                fail(f"{f.name}: {k} is required")
        if fm.get("mode") not in ("primary", "subagent", "all"):
            fail(f"{f.name}: mode must be primary, subagent or all [OC-03]")
        for k in (fm.get("permission") or {}):
            if k not in perm_keys:
                fail(f"{f.name}: permission key '{k}' is not one of opencode's {len(perm_keys)}")
            if k != k.lower():
                fail(f"{f.name}: permission keys are lowercase; '{k}' is Claude's spelling")
        name = f.stem
        p = yaml.safe_load((ROOT / "personas" / f"{name}.yaml").read_text())
        perm = fm.get("permission") or {}
        if not p["capabilities"]["edit"] and perm.get("edit") != "deny":
            fail(f"{f.name}: a read-only persona needs permission.edit = deny")
        if p["capabilities"]["delegate"] and "task" not in perm:
            fail(f"{f.name}: a delegating persona needs a permission.task allowlist [OC-05]")
        both_spellings(f.name, perm)
        if p["role"] == "primary" and fm.get("mode") != "primary":
            fail(f"{f.name}: the primary needs mode: primary [OC-03]")

    cfg_path = ROOT / "dist" / "opencode" / "opencode.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text())
        both_spellings("opencode.json", cfg.get("permission") or {})
        da = cfg.get("default_agent")
        if da and not (d / f"{da}.md").exists():
            fail(f"opencode.json: default_agent '{da}' does not resolve — a hard config "
                 f"error for every user of the repository [OC-03]")
        for cname, c in (cfg.get("command") or {}).items():
            extra = set(c) - set(host["config"]["command_keys"])
            if extra:
                fail(f"opencode.json: command '{cname}' has keys outside the schema: {extra}")
            for req in host["config"]["command_required"]:
                if req not in c:
                    fail(f"opencode.json: command '{cname}' is missing required '{req}'")
    ok(f"opencode agents ({len(files)}) use opencode's own vocabulary; config resolves; "
       f"key lists match the vendored schema")


# --------------------------------------------------------------------------- antigravity
def check_agy_tools():
    """Every emitted tool name must be in the MEASURED registry.

    A name outside it aborts the agent at startup with `unknown component: tool "<name>" not
    found in registry` (experiments.md E17). Seven names AG-06 lists are invalid. The list
    must be re-derived by running one agent per name; grepping the binary yields a superset
    and reported all seven as present (E16 C1, superseded).
    """
    host = yaml.safe_load((ROOT / "hosts" / "antigravity.yaml").read_text())
    registry = set(host["tool_registry"])
    rejected = set(host["rejected_at_1_1_27"])
    if registry & rejected:
        fail(f"hosts/antigravity.yaml: {registry & rejected} is in both lists")
    d = ROOT / "agents"
    files = sorted(d.glob("*/agent.md")) if d.exists() else []
    if not files:
        print("  skip antigravity agents (not rendered)")
        return
    for f in files:
        m = re.match(r"^---\n(.*?)\n---\n", f.read_text(), re.S)
        if not m:
            fail(f"{f.parent.name}/agent.md: no frontmatter")
            continue
        fm = yaml.safe_load(m.group(1))
        unknown = set(fm) - set(host["agent_file"]["allowed_keys"])
        if unknown:
            fail(f"{f.parent.name}/agent.md: unknown frontmatter keys {unknown}")
        for never in host["agent_file"]["never_emit"]:
            if never in fm:
                fail(f"{f.parent.name}/agent.md: `{never}` exists in agy 1.1.27 but not in "
                     f"desktop 2.12.2 (E16); do not emit it")
        tools = fm.get("tools") or []
        if not tools:
            fail(f"{f.parent.name}/agent.md: an omitted or empty `tools` list means no tools "
                 f"[AG-06]")
        bad = [t for t in tools if t not in registry]
        if bad:
            fail(f"{f.parent.name}/agent.md: {bad} not in the measured registry — the agent "
                 f"would abort at startup (E17)")
        name = fm.get("name")
        p = yaml.safe_load((ROOT / "personas" / f"{name}.yaml").read_text())
        if not p["capabilities"]["edit"] and (set(tools) & set(host["capabilities"]["edit"])):
            fail(f"{f.parent.name}/agent.md: a read-only persona carries a write tool")
        if not p["capabilities"]["delegate"] and "invoke_subagent" in tools:
            fail(f"{f.parent.name}/agent.md: a specialist carries invoke_subagent")
        if p["capabilities"]["delegate"] and "invoke_subagent" not in tools:
            fail(f"{f.parent.name}/agent.md: the primary needs invoke_subagent")
    ok(f"antigravity agents ({len(files)}) use only the {len(registry)} measured registry names")


# --------------------------------------------------------------------------- vendor validators
# This repository is simultaneously a plugin AND a project bootstrapped with itself, so its
# own CLAUDE.md sits at the plugin root. Claude warns that a plugin-root CLAUDE.md is not
# loaded as project context — true, and irrelevant here: that file exists for the project
# role, not the plugin role. It is the one warning this gate tolerates, by exact text.
KNOWN_CLAUDE_WARNINGS = ["CLAUDE.md at the plugin root is not loaded as project context"]


def check_hosts():
    """Run the vendors' own validators. Skips cleanly where a binary is absent, so CI on a
    bare runner reports honestly instead of passing vacuously."""
    import shutil
    import subprocess

    if shutil.which("claude"):
        runs = [("agents dir", ["./dist/claude/agents"]),
                ("plugin manifest", [".claude-plugin/plugin.json"]),
                ("marketplace", [".claude-plugin/marketplace.json"])]
        for label, args in runs:
            r = subprocess.run(["claude", "plugin", "validate", "--strict", *args],
                               capture_output=True, text=True, cwd=ROOT)
            out = r.stdout + r.stderr
            if r.returncode != 0:
                # Claude prints a separate "Found 1 warning" block per issue, so counting
                # blocks is not enough. Tolerate only when EVERY complaint is a known one.
                complaints = [c.strip() for c in re.findall(r"❯\s*(.+)", out)]
                unknown = [c for c in complaints
                           if not any(k in c for k in KNOWN_CLAUDE_WARNINGS)]
                has_errors = re.search(r"Found \d+ error", out) is not None
                if complaints and not unknown and not has_errors:
                    ok(f"claude validate {label}: passes but for the known plugin-root "
                       f"CLAUDE.md warning")
                else:
                    fail(f"claude plugin validate --strict {' '.join(args)} failed: "
                         f"{out.strip().splitlines()[-1] if out.strip() else '(no output)'}")
            else:
                ok(f"claude validate {label}")
    else:
        print("  skip claude plugin validate (claude not on PATH)")

    if shutil.which("agy"):
        r = subprocess.run(["agy", "plugin", "validate", "."], capture_output=True,
                           text=True, cwd=ROOT)
        if r.returncode != 0 or "[ok]" not in (r.stdout + r.stderr):
            fail(f"agy plugin validate did not report [ok]: {(r.stdout + r.stderr).strip()[:120]}")
        else:
            ok("agy plugin validate reports [ok]")
    else:
        print("  skip agy plugin validate (agy not on PATH)")


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
    for flag in ("personas", "codex", "claude", "opencode", "agy-tools", "skills",
                 "bodies", "knowledge", "hosts", "drift"):
        ap.add_argument(f"--{flag}", action="store_true")
    a = ap.parse_args()
    chosen = {k for k, v in vars(a).items() if v}
    run_all = not chosen
    print("check.py")
    if run_all or "personas" in chosen: check_personas()
    if run_all or "codex" in chosen: check_codex()
    if run_all or "claude" in chosen: check_claude_agents()
    if run_all or "opencode" in chosen: check_opencode()
    if run_all or "agy_tools" in chosen: check_agy_tools()
    if run_all or "skills" in chosen: check_skills()
    if run_all or "bodies" in chosen: check_rendered_bodies()
    if run_all or "knowledge" in chosen: check_knowledge()
    if run_all or "hosts" in chosen: check_hosts()
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
