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
