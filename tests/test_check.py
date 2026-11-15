"""Negative tests for the opencode gate in tools/check.py.

A gate that has never failed is not yet a gate (design §15). These run the gate against a
copy of the rendered tree, break one thing at a time, and require the gate to say so.
check.py needs PyYAML, so this file skips itself where the library is absent.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parent.parent


@unittest.skipUnless(yaml, "check.py needs PyYAML")
class TestOpencodeGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.root / "tools").mkdir()
        shutil.copy(ROOT / "tools" / "check.py", self.root / "tools" / "check.py")
        for d in ("hosts", "personas", "dist/opencode"):
            shutil.copytree(ROOT / d, self.root / d)
        self.agents = self.root / "dist" / "opencode" / "agents"
        self.config = self.root / "dist" / "opencode" / "opencode.json"

    def check(self):
        return subprocess.run([sys.executable, str(self.root / "tools" / "check.py"),
                               "--opencode"], capture_output=True, text=True)

    def frontmatter(self, name):
        text = (self.agents / f"{name}.md").read_text()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        return yaml.safe_load(m.group(1)), m.group(2)

    def write_frontmatter(self, name, fm, body):
        (self.agents / f"{name}.md").write_text(
            "---\n" + yaml.safe_dump(fm, sort_keys=False).rstrip("\n") + "\n---\n" + body)

    def test_the_rendered_tree_passes(self):
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("opencode agents", r.stdout)

    def test_a_permission_key_in_neither_list_fails(self):
        fm, body = self.frontmatter("reviewer")
        fm["permission"]["taks"] = {"*": "deny"}          # the misspelling opencode would swallow
        self.write_frontmatter("reviewer", fm, body)
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("taks", r.stdout)
        self.assertIn("not one of", r.stdout)

    def test_the_schema_name_alone_fails(self):
        fm, body = self.frontmatter("tech-lead")
        del fm["permission"]["subagent"]
        self.write_frontmatter("tech-lead", fm, body)
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("`task` and its 2.x name `subagent`", r.stdout)

    def test_the_runtime_name_alone_fails(self):
        fm, body = self.frontmatter("reviewer")
        del fm["permission"]["bash"]
        self.write_frontmatter("reviewer", fm, body)
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("`bash` and its 2.x name `shell`", r.stdout)

    def test_the_pair_must_carry_identical_rules(self):
        fm, body = self.frontmatter("reviewer")
        fm["permission"]["shell"] = {"*": "allow"}          # the deny patterns dropped from one spelling
        self.write_frontmatter("reviewer", fm, body)
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("identical", r.stdout)

    def test_a_schema_change_fails_the_gate(self):
        p = self.root / "hosts" / "opencode-config.schema.json"
        schema = json.loads(p.read_text())
        obj = next(v for v in schema["$defs"]["PermissionConfig"]["anyOf"]
                   if v.get("type") == "object")
        obj["properties"]["sandbox"] = obj["properties"].pop("lsp")   # a key renamed upstream
        p.write_text(json.dumps(schema))
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("drifted from the vendored schema", r.stdout)
        self.assertIn("sandbox", r.stdout)

    def test_a_key_list_change_fails_the_gate(self):
        p = self.root / "hosts" / "opencode.yaml"
        text = p.read_text()
        self.assertIn(" doom_loop,", text)
        p.write_text(text.replace(" doom_loop,", ""))
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("drifted from the vendored schema", r.stdout)
        self.assertIn("doom_loop", r.stdout)

    def test_the_config_needs_both_spellings_too(self):
        cfg = json.loads(self.config.read_text())
        del cfg["permission"]["subagent"]
        self.config.write_text(json.dumps(cfg, indent=2) + "\n")
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("opencode.json: permission `task`", r.stdout)


@unittest.skipUnless(yaml, "check.py needs PyYAML")
class TestVersionStamp(unittest.TestCase):
    """The renderer stamps dist/team.json; VERSION and the four manifests are source files,
    and a release bump missed them once. The personas gate now checks all five."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.root / "tools").mkdir()
        shutil.copy(ROOT / "tools" / "check.py", self.root / "tools" / "check.py")
        for f in ("team.yaml", "VERSION", "plugin.json"):
            shutil.copy(ROOT / f, self.root / f)
        for d in ("personas", ".codex-plugin", ".claude-plugin"):
            shutil.copytree(ROOT / d, self.root / d)

    def check(self):
        return subprocess.run([sys.executable, str(self.root / "tools" / "check.py"),
                               "--personas"], capture_output=True, text=True)

    def test_a_consistent_tree_passes(self):
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("stamped everywhere", r.stdout)

    def test_a_manifest_left_behind_fails(self):
        p = self.root / ".claude-plugin" / "marketplace.json"
        doc = json.loads(p.read_text())
        doc["plugins"][0]["version"] = "0.0.0"               # the nested entry, easiest to miss
        p.write_text(json.dumps(doc, indent=2) + "\n")
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("marketplace.json: version 0.0.0 but team.yaml says", r.stdout)

    def test_a_stale_VERSION_file_fails(self):
        (self.root / "VERSION").write_text("0.0.0\n")
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("VERSION: version 0.0.0", r.stdout)


@unittest.skipUnless(yaml, "check.py needs PyYAML")
class TestSkillsGate(unittest.TestCase):
    """A skill that quotes the RETURN block must quote the one the personas use."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.root / "tools").mkdir()
        shutil.copy(ROOT / "tools" / "check.py", self.root / "tools" / "check.py")
        for d in ("personas", "skills"):
            shutil.copytree(ROOT / d, self.root / d)
        self.skill = self.root / "skills" / "ec-fleet" / "SKILL.md"

    def check(self):
        return subprocess.run([sys.executable, str(self.root / "tools" / "check.py"),
                               "--skills"], capture_output=True, text=True)

    def test_the_shipped_skills_pass(self):
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_return_block_that_drifted_fails(self):
        self.skill.write_text(self.skill.read_text().replace(
            "status: done | partial | blocked | needs-decision", "status: done | blocked"))
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("ec-fleet", r.stdout)
        self.assertIn("the RETURN block differs from personas/_shared/return.md", r.stdout)



class TestAgyValidatorGate(unittest.TestCase):
    """agy 1.5.3 passes a plugin with a missing or invalid name and only warns (E32), so the gate
    reads the warnings. A stub stands in for the binary."""

    def run_with(self, output: str):
        with tempfile.TemporaryDirectory() as tmp:
            stub = pathlib.Path(tmp) / "agy"
            stub.write_text(f"#!{sys.executable}\nprint({output!r})\n")
            stub.chmod(0o755)
            return subprocess.run([sys.executable, str(ROOT / "tools" / "check.py"), "--hosts"],
                                  capture_output=True, text=True, env={"PATH": tmp})

    def test_the_known_warning_passes(self):
        r = self.run_with("  ⚠ AGENTS.md: never loaded: plugins load rules only from rules/.\n"
                          "✔ Validation passed with 1 warning")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("agy plugin validate passes", r.stdout)

    def test_any_other_warning_fails(self):
        r = self.run_with("  ⚠ AGENTS.md: never loaded: plugins load rules only from rules/.\n"
                          "  ⚠ agents/x/agent.md: missing name\n"
                          "✔ Validation passed with 2 warnings")
        self.assertEqual(r.returncode, 1)
        self.assertIn("missing name", r.stdout)

    def test_the_older_ok_line_still_passes(self):
        self.assertEqual(self.run_with("  [ok]    e-colleagues").returncode, 0)


class TestAgyToolsGate(unittest.TestCase):
    """At agy 1.5.3 some tool names still load and give the agent nothing (E32). The gate
    passes only names that deliver a tool."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.root / "tools").mkdir()
        shutil.copy(ROOT / "tools" / "check.py", self.root / "tools" / "check.py")
        for d in ("personas", "hosts", "agents"):
            shutil.copytree(ROOT / d, self.root / d)
        self.agent = self.root / "agents" / "reviewer" / "agent.md"

    def check(self):
        return subprocess.run([sys.executable, str(self.root / "tools" / "check.py"),
                               "--agy-tools"], capture_output=True, text=True)

    def test_the_rendered_agents_pass(self):
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_name_that_gives_no_tool_fails(self):
        for name in ("grep_search", "list_dir", "read_url_content", "command_status"):
            text = (ROOT / "agents" / "reviewer" / "agent.md").read_text()
            self.agent.write_text(text.replace("tools:\n", f"tools:\n  - {name}\n", 1))
            r = self.check()
            self.assertEqual(r.returncode, 1, name)
            self.assertIn(name, r.stdout)

    def test_no_rendered_agent_lists_such_a_name(self):
        dead = {"grep_search", "find_by_name", "list_dir", "multi_replace_file_content",
                "read_url_content", "command_status"}
        for f in sorted((ROOT / "agents").glob("*/agent.md")):
            fm = f.read_text().split("---")[1]
            self.assertFalse(dead & set(re.findall(r"^  - (\S+)$", fm, re.M)), f.parent.name)


class TestPostingRule(unittest.TestCase):
    """D6: a specialist posts externally only where the project's contract grants it. Every
    rendered body must say so, and none may still say it never posts."""

    def test_every_rendered_body_carries_the_rule(self):
        files = (sorted((ROOT / "dist").rglob("*.md")) + sorted((ROOT / "dist").rglob("*.toml"))
                 + sorted((ROOT / "agents").rglob("*.md"))
                 + [ROOT / "skills" / "ec-tech-lead" / "SKILL.md"])
        bodies = [f for f in files if "R4 — Side effects" in f.read_text()]
        self.assertGreaterEqual(len(bodies), 20)
        for f in bodies:
            text = f.read_text()
            self.assertIn("R5 — External posting.", text, f.name)
            self.assertIn("only where `AGENTS.md` grants it to your role", text, f.name)
            self.assertNotIn("never post", text.lower(), f.name)


class TestClaudeDenylistGate(unittest.TestCase):
    """D6: every sub-agent reaches MCP tools. On Claude Code a `tools` allowlist strips them
    and no pattern re-admits every server (E33), so no persona carries one. A specialist names
    what it must not have in `disallowedTools`, and inherits everything else (E36)."""

    EVERY = ["Agent", "SendMessage", "EnterWorktree", "ExitWorktree", "CronCreate", "CronDelete",
             "RemoteTrigger", "PushNotification", "ShareOnboardingGuide", "DesignSync"]
    READ_ONLY = ["Write", "Edit", "NotebookEdit", "Monitor"]
    NO_WEB = ["WebFetch", "WebSearch"]

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.root / "tools").mkdir()
        shutil.copy(ROOT / "tools" / "check.py", self.root / "tools" / "check.py")
        for d in ("personas", "hosts"):
            shutil.copytree(ROOT / d, self.root / d)
        shutil.copytree(ROOT / "dist" / "claude", self.root / "dist" / "claude")

    def check(self):
        return subprocess.run([sys.executable, str(self.root / "tools" / "check.py"),
                               "--claude"], capture_output=True, text=True)

    @staticmethod
    def denied(path):
        fm = path.read_text().split("---")[1]
        m = re.search(r"(?m)^disallowedTools: (.*)$", fm)
        return (m.group(1).split(", ") if m else []), fm

    def test_the_rendered_agents_pass(self):
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_each_rendered_persona_denies_what_its_capabilities_say(self):
        want = {"reviewer": self.EVERY + self.READ_ONLY + self.NO_WEB,
                "security": self.EVERY + self.READ_ONLY + self.NO_WEB,
                "developer": self.EVERY + self.NO_WEB,
                "platform": self.EVERY + self.NO_WEB,
                "designer": self.EVERY}
        for name, names in want.items():
            got, fm = self.denied(ROOT / "dist" / "claude" / "agents" / f"{name}.md")
            self.assertEqual(got, names, name)
            self.assertNotRegex(fm, r"(?m)^tools:", name)
        got, fm = self.denied(ROOT / "dist" / "claude" / "agents" / "tech-lead.md")
        self.assertEqual(got, [])
        self.assertNotRegex(fm, r"(?m)^tools:")

    def test_a_tools_allowlist_fails_on_any_persona(self):
        for name in ("reviewer", "developer", "tech-lead"):
            agent = self.root / "dist" / "claude" / "agents" / f"{name}.md"
            keep = agent.read_text()
            agent.write_text(keep.replace("model: inherit\n",
                                          "model: inherit\ntools: Read, Grep, Glob, Bash\n", 1))
            r = self.check()
            agent.write_text(keep)
            self.assertEqual(r.returncode, 1, name)
            self.assertIn("strips every MCP tool", r.stdout, name)

    def test_a_denylist_missing_one_name_fails(self):
        for name in ("reviewer", "developer", "designer"):
            agent = self.root / "dist" / "claude" / "agents" / f"{name}.md"
            keep = agent.read_text()
            names, _ = self.denied(agent)
            for tool in names:
                line = "disallowedTools: " + ", ".join(t for t in names if t != tool) + "\n"
                agent.write_text(re.sub(r"(?m)^disallowedTools: .*\n", line, keep, count=1))
                r = self.check()
                self.assertEqual(r.returncode, 1, (name, tool))
                self.assertIn(tool, r.stdout, (name, tool))
            agent.write_text(keep)


class TestOpencodeReadOnlyShell(unittest.TestCase):
    """opencode matches a shell rule against each simple command of a line, redirections
    included, and the last matching rule decides (E35). So the order below is the rule set:
    it is the one that refused sixteen write forms of sixteen and kept a reviewer's commands."""

    RULES = [("*", "allow"), ("*>*", "deny"), ("*2>&1*", "allow"), ("*2>/dev/null*", "allow"),
             ("*>*>*", "deny"), ("*> /dev/null 2>&1", "allow"), ("*>/dev/null 2>&1", "allow"),
             ("*>*>*>*", "deny"), ("git commit*", "deny"), ("git stash*", "deny"),
             ("git init*", "deny"), ("sed -i*", "deny"), ("tee*", "deny"), ("cp *", "deny"),
             ("mv *", "deny"), ("rm *", "deny"), ("rmdir*", "deny"), ("mkdir*", "deny"),
             ("touch*", "deny")]

    @staticmethod
    def permission(name):
        import yaml
        text = (ROOT / "dist" / "opencode" / "agents" / f"{name}.md").read_text()
        return yaml.safe_load(text.split("---")[1])["permission"]

    def test_the_read_only_personas_carry_the_measured_rules_in_order(self):
        for name in ("reviewer", "security"):
            perm = self.permission(name)
            for key in ("bash", "shell"):
                self.assertEqual(list(perm[key].items()), self.RULES, (name, key))

    def test_a_writer_has_no_shell_rules(self):
        for name in ("developer", "platform", "designer"):
            perm = self.permission(name)
            self.assertNotIn("bash", perm, name)
            self.assertNotIn("shell", perm, name)

    def test_the_tech_lead_is_told_both_names_of_the_delegation_tool(self):
        text = (ROOT / "dist" / "opencode" / "agents" / "tech-lead.md").read_text()
        self.assertIn("use the `subagent` tool with `agent` exactly one of:", text)
        self.assertIn("`task` with `subagent_type`", text)
