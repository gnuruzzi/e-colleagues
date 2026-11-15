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
