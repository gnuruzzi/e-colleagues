#!/usr/bin/env python3
"""Bootstrap tests (§13 item 10).

Standard library only, like the script under test. §13 says "pytest, stdlib only"; unittest
is the stdlib test runner, so these run with `python3 -m unittest` and need nothing installed.
"""
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
TEAM = ROOT / "dist" / "team.json"

BEGIN, INDEX, BINDINGS, END = (
    "<!-- e-colleagues:begin", "<!-- e-colleagues:index -->",
    "<!-- e-colleagues:project-bindings -->", "<!-- e-colleagues:end -->")


def run(root, *args):
    return subprocess.run(
        [sys.executable, str(BOOTSTRAP), str(root), *args, "--team-json", str(TEAM)],
        capture_output=True, text=True)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def seed(self, **files):
        for rel, text in files.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)

    @property
    def agents(self):
        return (self.root / "AGENTS.md").read_text()


class TestFreshRepo(Base):
    def test_creates_the_three_owned_files(self):
        self.seed(**{"AGENTS.md": "# proj\n\nProject prose.\n"})
        self.assertEqual(run(self.root, "--write").returncode, 0)
        for rel in ("AGENTS.md", "CLAUDE.md", ".e-colleagues/lock.json"):
            self.assertTrue((self.root / rel).exists(), rel)

    def test_block_is_placed_directly_after_the_h1(self):
        # Codex truncates the TAIL, so the spawn sentence must be near the top [CX-11]
        self.seed(**{"AGENTS.md": "# proj\n\nProject prose.\n"})
        run(self.root, "--write")
        lines = self.agents.splitlines()
        self.assertTrue(lines[0].startswith("# "))
        begin = next(i for i, l in enumerate(lines) if l.startswith(BEGIN))
        prose = next(i for i, l in enumerate(lines) if "Project prose." in l)
        self.assertLess(begin, prose, "the block must precede the project's own prose")

    def test_claude_md_is_the_two_line_pointer(self):
        # never a copy of AGENTS.md, which is what /import codex produces [CC-14][CC-16]
        self.seed(**{"AGENTS.md": "# proj\n"})
        run(self.root, "--write")
        self.assertEqual((self.root / "CLAUDE.md").read_text().strip(), "@AGENTS.md")

    def test_lock_records_version_roster_and_hashes(self):
        self.seed(**{"AGENTS.md": "# proj\n"})
        run(self.root, "--write")
        lock = json.loads((self.root / ".e-colleagues/lock.json").read_text())
        team = json.loads(TEAM.read_text())
        self.assertEqual(lock["package_version"], team["version"])
        self.assertEqual(lock["roster"], team["roster"])
        self.assertIn("AGENTS.md", lock["written"])


class TestIdempotence(Base):
    def test_second_write_is_a_no_op(self):
        self.seed(**{"AGENTS.md": "# proj\n\nProse.\n"})
        run(self.root, "--write")
        first = self.agents
        run(self.root, "--write")
        self.assertEqual(first, self.agents)

    def test_check_is_clean_after_write(self):
        self.seed(**{"AGENTS.md": "# proj\n"})
        run(self.root, "--write")
        self.assertEqual(run(self.root, "--check").returncode, 0)

    def test_check_fails_before_write(self):
        self.seed(**{"AGENTS.md": "# proj\n"})
        self.assertEqual(run(self.root, "--check").returncode, 1)


class TestRegionOwnership(Base):
    """§5.1: three regions, three owners. An update rewrites only the package region."""

    def bootstrapped_with_edits(self):
        self.seed(**{"AGENTS.md": "# proj\n\nProject prose.\n"})
        run(self.root, "--write")
        s = self.agents
        s = s.replace("### Platforms and tools\n",
                      "### Platforms and tools\n\nGitLab board 'X'. Post as MR comments.\n")
        s = s.replace("| architecture | — | not yet audited |",
                      "| architecture | docs/adr/ | a3f91e2 |")
        (self.root / "AGENTS.md").write_text(s)

    def test_update_preserves_the_teams_bindings(self):
        self.bootstrapped_with_edits()
        run(self.root, "--write")
        self.assertIn("GitLab board 'X'", self.agents)

    def test_update_preserves_an_audit_written_index_row(self):
        self.bootstrapped_with_edits()
        run(self.root, "--write")
        self.assertIn("docs/adr/ | a3f91e2", self.agents)

    def test_update_preserves_project_prose_outside_the_markers(self):
        self.bootstrapped_with_edits()
        run(self.root, "--write")
        self.assertIn("Project prose.", self.agents)

    def test_roster_change_rewrites_only_the_package_region(self):
        self.bootstrapped_with_edits()
        team = json.loads(TEAM.read_text())
        team["profile"] = "minimal"
        team["roster"] = ["tech-lead", "developer", "reviewer"]
        team["personas"] = {k: v for k, v in team["personas"].items() if k in team["roster"]}
        alt = self.root / "team-minimal.json"
        alt.write_text(json.dumps(team))
        subprocess.run([sys.executable, str(BOOTSTRAP), str(self.root), "--write",
                        "--team-json", str(alt)], capture_output=True, text=True)
        spawn = re.search(r"exactly these types: ([^.]*)", self.agents).group(1)
        self.assertEqual(spawn, "developer, reviewer")
        self.assertIn("GitLab board 'X'", self.agents)   # bindings survive a roster change


class TestForeignFilesUntouched(Base):
    """Nothing outside the owned files and markers may change (§13 item 10)."""

    OTHERS = {
        ".claude/settings.json": '{\n  "permissions": {\n    "allow": ["Read"]\n  }\n}\n',
        "opencode.json": '{\n  "$schema": "https://opencode.ai/config.json"\n}\n',
        ".codex/config.toml": 'model = "gpt-5.5"\n',
        "README.md": "# readme\n",
    }

    def test_other_config_files_are_byte_identical_after_write(self):
        self.seed(**{"AGENTS.md": "# proj\n"}, **self.OTHERS)
        run(self.root, "--write")
        for rel, original in self.OTHERS.items():
            self.assertEqual((self.root / rel).read_text(), original, rel)

    def test_an_existing_claude_md_with_project_content_is_not_overwritten(self):
        self.seed(**{"AGENTS.md": "# proj\n",
                     "CLAUDE.md": "# project's own CLAUDE.md\n\nHand-written guidance.\n"})
        run(self.root, "--write")
        self.assertIn("Hand-written guidance.", (self.root / "CLAUDE.md").read_text())


class TestBudgets(Base):
    """[CX-11]: over 30 KiB the tail is truncated and an untrusted teammate never gets the
    raised cap, so --check FAILS rather than warns."""

    def test_over_budget_fails_check(self):
        self.seed(**{"AGENTS.md": "# big\n\n" + ("padding. " * 8 + "\n") * 500})
        r = run(self.root, "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("over the", r.stdout)

    def test_over_budget_write_refuses_and_writes_nothing(self):
        self.seed(**{"AGENTS.md": "# big\n\n" + ("padding. " * 8 + "\n") * 500})
        self.assertEqual(run(self.root, "--write").returncode, 1)
        self.assertNotIn(BEGIN, self.agents)
        self.assertFalse((self.root / ".e-colleagues/lock.json").exists())

    def test_a_realistic_large_file_still_fits(self):
        # the shape of a real, mature AGENTS.md: ~23.5 KB before the block
        self.seed(**{"AGENTS.md": "# proj\n\n" + ("Realistic prose line. " * 5 + "\n") * 205})
        size = len((self.root / "AGENTS.md").read_bytes())
        self.assertGreater(size, 20 * 1024)
        self.assertEqual(run(self.root, "--write").returncode, 0)
        self.assertIn(BEGIN, self.agents)

    def test_the_managed_block_stays_under_2kb(self):
        self.seed(**{"AGENTS.md": "# proj\n"})
        run(self.root, "--write")
        block = re.search(re.escape(BEGIN) + r".*?" + re.escape(END), self.agents, re.S)
        self.assertLess(len(block.group(0).encode()), 2048)


class TestBlockContent(Base):
    def test_block_carries_the_literal_spawn_sentence(self):
        # Codex spawns only when asked by name [CX-05]
        self.seed(**{"AGENTS.md": "# proj\n"})
        run(self.root, "--write")
        self.assertIn("spawning sub-agents of exactly these types", self.agents)

    def test_block_names_the_floor_skill_for_untrusted_clones(self):
        # project agents need trust, project skills do not (E12)
        self.seed(**{"AGENTS.md": "# proj\n"})
        run(self.root, "--write")
        self.assertIn("ec-tech-lead", self.agents)

    def test_block_states_the_no_external_posting_rule(self):
        self.seed(**{"AGENTS.md": "# proj\n"})
        run(self.root, "--write")
        self.assertIn("never post externally", self.agents)

    def test_signatures_match_team_json_exactly(self):
        self.seed(**{"AGENTS.md": "# proj\n"})
        run(self.root, "--write")
        for p in json.loads(TEAM.read_text())["personas"].values():
            self.assertIn(p["signature"].strip(), self.agents)


if __name__ == "__main__":
    unittest.main(verbosity=2)
