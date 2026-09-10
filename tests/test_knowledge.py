#!/usr/bin/env python3
"""Knowledge store and staleness tests (§13 item 8). Standard library only."""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOTSTRAP = ROOT / "skills" / "ec-init" / "scripts" / "bootstrap.py"
KNOWLEDGE = ROOT / "skills" / "ec-onboard" / "scripts" / "knowledge.py"
STATUS = ROOT / "skills" / "ec-status" / "scripts" / "status.py"
TEAM = ROOT / "dist" / "team.json"


def sh(*args, cwd=None):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, cwd=cwd)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.root / ".github/workflows").mkdir(parents=True)
        (self.root / "src").mkdir()
        (self.root / "AGENTS.md").write_text("# demo\n\nProse.\n")
        (self.root / ".github/workflows/ci.yml").write_text("name: ci\non: [push]\n")
        (self.root / "Dockerfile").write_text("FROM alpine\n")
        (self.root / "src/calc.py").write_text("def add(a, b): return a + b\n")
        self.git("init", "-q")
        self.commit("init")
        sh(sys.executable, BOOTSTRAP, self.root, "--write", "--team-json", TEAM)
        self.body = self.root / "body.md"
        self.body.write_text("The pipeline is one GitHub Actions workflow.\n")

    def git(self, *args):
        return sh("git", "-C", self.root, *args)

    def commit(self, msg):
        self.git("add", "-A")
        return sh("git", "-C", self.root, "-c", "user.email=a@b", "-c", "user.name=c",
                  "commit", "-qm", msg)

    def audit(self, lens="ci-cd-and-infra", persona="platform",
              paths=".github/workflows/ci.yml,Dockerfile"):
        return sh(sys.executable, KNOWLEDGE, self.root, "--lens", lens, "--persona", persona,
                  "--paths", paths, "--body-file", self.body)

    def status(self, *extra):
        return sh(sys.executable, STATUS, self.root, *extra)

    @property
    def agents(self):
        return (self.root / "AGENTS.md").read_text()


class TestAuthoring(Base):
    def test_writes_the_file_with_provenance(self):
        self.assertEqual(self.audit().returncode, 0)
        f = self.root / ".e-colleagues/knowledge/ci-cd-and-infra.md"
        self.assertTrue(f.exists())
        fm = f.read_text().split("---")[1]
        for key in ("lens:", "persona:", "commit:", "paths:", "package_version:", "confidence:"):
            self.assertIn(key, fm)

    def test_records_the_head_commit(self):
        self.audit()
        head = self.git("rev-parse", "--short", "HEAD").stdout.strip()
        self.assertIn(f"commit: {head}",
                      (self.root / ".e-colleagues/knowledge/ci-cd-and-infra.md").read_text())

    def test_updates_the_index_row(self):
        self.audit()
        self.assertRegex(self.agents, r"\| ci-cd-and-infra \| \.e-colleagues/knowledge/")

    def test_records_the_lens_in_the_lock_so_a_pass_resumes(self):
        self.audit()
        lock = json.loads((self.root / ".e-colleagues/lock.json").read_text())
        self.assertIn("ci-cd-and-infra", lock["completed_lenses"])

    def test_refuses_without_paths_because_staleness_needs_them(self):
        r = sh(sys.executable, KNOWLEDGE, self.root, "--lens", "x", "--persona", "y",
               "--body-file", self.body)
        self.assertNotEqual(r.returncode, 0)

    def test_refuses_a_path_that_does_not_exist(self):
        r = self.audit(paths="does/not/exist.yml")
        self.assertNotEqual(r.returncode, 0)

    def test_index_only_authors_nothing(self):
        r = sh(sys.executable, KNOWLEDGE, self.root, "--lens", "architecture",
               "--persona", "tech-lead", "--index-only", "docs/adr/")
        self.assertEqual(r.returncode, 0)
        self.assertFalse((self.root / ".e-colleagues/knowledge/architecture.md").exists())
        self.assertIn("| architecture | docs/adr/ |", self.agents)

    def test_the_index_region_stays_well_formed(self):
        self.audit()
        region = self.agents.split("<!-- e-colleagues:index -->")[1] \
                            .split("<!-- e-colleagues:project-bindings -->")[0]
        self.assertTrue(region.startswith("\n|"))
        self.assertTrue(region.endswith("\n\n"))
        for ln in [l for l in region.splitlines() if l.strip()]:
            self.assertEqual(ln.count("|"), 4, ln)


class TestLockOwnership(Base):
    """The lock has two owners: ec-init owns the package fields, the audit owns
    completed_lenses and the knowledge entries. Rebuilding the whole document wiped the
    audit's record, so every indexed lens reported as "not audited" after an ec-init run."""

    def test_ec_init_does_not_wipe_the_audits_record(self):
        self.audit()
        before = json.loads((self.root / ".e-colleagues/lock.json").read_text())
        self.assertIn("ci-cd-and-infra", before["completed_lenses"])
        sh(sys.executable, BOOTSTRAP, self.root, "--write", "--team-json", TEAM)
        after = json.loads((self.root / ".e-colleagues/lock.json").read_text())
        self.assertIn("ci-cd-and-infra", after["completed_lenses"])

    def test_ec_init_keeps_the_knowledge_entries(self):
        self.audit()
        sh(sys.executable, BOOTSTRAP, self.root, "--write", "--team-json", TEAM)
        written = json.loads((self.root / ".e-colleagues/lock.json").read_text())["written"]
        self.assertIn(".e-colleagues/knowledge/ci-cd-and-infra.md", written)

    def test_status_still_reports_a_lens_indexed_after_an_ec_init_run(self):
        sh(sys.executable, KNOWLEDGE, self.root, "--lens", "architecture",
           "--persona", "tech-lead", "--index-only", "docs/")
        sh(sys.executable, BOOTSTRAP, self.root, "--write", "--team-json", TEAM)
        self.assertIn("indexed", self.status().stdout)


class TestStaleness(Base):
    """Staleness is a git diff over the recorded paths (§5.2)."""

    def setUp(self):
        super().setUp()
        self.audit()
        self.commit("bootstrap + audit")

    def test_fresh_immediately_after_an_audit(self):
        self.assertIn("fresh at", self.status().stdout)
        self.assertEqual(self.status("--fail-on-stale").returncode, 0)

    def test_a_change_to_an_UNRECORDED_path_leaves_it_fresh(self):
        # the control that makes the next test meaningful
        (self.root / "src/calc.py").write_text("def sub(a, b): return a - b\n")
        self.commit("unrelated")
        self.assertIn("fresh at", self.status().stdout)

    def test_a_change_to_a_RECORDED_path_makes_it_stale(self):
        (self.root / ".github/workflows/ci.yml").write_text("name: ci\non: [push, pull_request]\n")
        self.commit("ci change")
        out = self.status().stdout
        self.assertIn("STALE", out)
        self.assertIn(".github/workflows/ci.yml", out)
        self.assertEqual(self.status("--fail-on-stale").returncode, 1)

    def test_re_auditing_rebaselines_to_fresh(self):
        (self.root / "Dockerfile").write_text("FROM debian\n")
        self.commit("base image")
        self.assertIn("STALE", self.status().stdout)
        self.audit()
        self.commit("re-audit")
        self.assertIn("fresh at", self.status().stdout)

    def test_an_unreachable_commit_is_unknown_not_fresh(self):
        f = self.root / ".e-colleagues/knowledge/ci-cd-and-infra.md"
        f.write_text(re.sub(r"commit: \w+", "commit: deadbee", f.read_text()))
        out = self.status().stdout
        self.assertIn("unreachable", out)
        self.assertNotIn("fresh at", out)

    def test_missing_provenance_is_unknown_not_fresh(self):
        (self.root / ".e-colleagues/knowledge/ci-cd-and-infra.md").write_text("no frontmatter\n")
        out = self.status().stdout
        self.assertIn("PROVENANCE MISSING", out)

    def test_status_on_an_unbootstrapped_project_says_so(self):
        with tempfile.TemporaryDirectory() as d:
            r = sh(sys.executable, STATUS, d)
            self.assertEqual(r.returncode, 1)
            self.assertIn("not bootstrapped", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
