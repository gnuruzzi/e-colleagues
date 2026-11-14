"""fleet.py: config, naming, start. Standard library only, like the script."""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLEET = ROOT / "skills" / "ec-fleet" / "scripts" / "fleet.py"

FAKE = '''import json, os, sys
with open(os.environ["FAKE_LOG"], "a") as fh:
    fh.write(json.dumps(sys.argv[1:]) + "\\n")
d = os.environ["FAKE_DIR"]
if sys.argv[1] == "status":
    sys.stdout.write(open(os.path.join(d, "status.json")).read())
elif sys.argv[1] == "capture":
    sys.stdout.write(open(os.path.join(d, sys.argv[2] + ".screen")).read())
elif sys.argv[1] == "add" and os.path.exists(os.path.join(d, "fail")):
    sys.stderr.write("worktree already exists\\n"); sys.exit(3)
'''


def load():
    spec = importlib.util.spec_from_file_location("fleet", FLEET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.fake = self.dir / "fake.py"
        self.fake.write_text(FAKE)
        self.log = self.dir / "log"
        self.cfg = self.dir / "fleet.toml"

    def write_cfg(self, top="", extra=""):
        py, fake = json.dumps(sys.executable), json.dumps(str(self.fake))
        self.cfg.write_text(
            top + f'[launcher]\n'
            f'start = [{py}, {fake}, "add", "{{name}}", "--agent", "{{agent}}", "--prompt", "{{prompt}}"]\n'
            f'status = [{py}, {fake}, "status"]\n'
            f'capture = [{py}, {fake}, "capture", "{{name}}"]\n' + extra)

    def run_fleet(self, *args, config=True, env=None):
        e = {**os.environ, "FAKE_LOG": str(self.log), "FAKE_DIR": str(self.dir),
             "EC_FLEET_CONFIG": str(self.cfg if config else self.dir / "absent.toml")}
        e.pop("TMUX_PANE", None)
        e.update(env or {})
        return subprocess.run([sys.executable, str(FLEET), *args],
                              capture_output=True, text=True, env=e)

    def logged(self):
        return [json.loads(ln) for ln in self.log.read_text().splitlines()]


class TestSafeName(unittest.TestCase):
    def test_references_become_branch_safe_names(self):
        f = load()
        for ref, want in [("12", "issue-12"), ("#12", "issue-12"), ("ENG-123", "eng-123"),
                          ("owner/repo#12", "owner-repo-12"),
                          ("Fix the  parser!", "fix-the-parser"), ("--force", "force")]:
            self.assertEqual(f.safe_name(ref), want, ref)

    def test_nothing_usable_is_an_error(self):
        with self.assertRaises(ValueError):
            load().safe_name("#!/")


class TestStart(Base):
    def test_default_argv_is_plain_workmux(self):
        r = self.run_fleet("start", "12", "--host", "antigravity", "--dry-run", config=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), [
            "workmux", "add", "issue-12", "--background", "--agent", "agy --agent tech-lead",
            "--prompt", "Use the ec-fleet skill. Your assignment: issue 12."])

    def test_base_is_appended_with_the_launchers_flag(self):
        r = self.run_fleet("start", "12", "--host", "codex", "--base", "main", "--dry-run",
                           config=False)
        self.assertEqual(json.loads(r.stdout)[-2:], ["--base", "main"])

    def test_a_host_is_required_when_no_default_is_configured(self):
        r = self.run_fleet("start", "12", "--dry-run", config=False)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--host", r.stderr)

    def test_default_host_and_start_command_come_from_the_config(self):
        self.write_cfg(top='default_host = "antigravity"\n',
                       extra='[hosts.antigravity]\n'
                             'start = "agy --agent tech-lead --remote-control"\n')
        r = self.run_fleet("start", "ENG-123")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.logged(), [[
            "add", "eng-123", "--agent", "agy --agent tech-lead --remote-control",
            "--prompt", "Use the ec-fleet skill. Your assignment: issue ENG-123."]])

    def test_an_unknown_host_is_refused_with_the_known_ones(self):
        r = self.run_fleet("start", "12", "--host", "agy", "--dry-run", config=False)
        self.assertEqual(r.returncode, 2)
        self.assertIn("antigravity", r.stderr)

    def test_a_given_name_is_used_as_given(self):
        r = self.run_fleet("start", "12", "--name", "user/eng-12-parser", "--host", "claude",
                           "--dry-run", config=False)
        self.assertEqual(json.loads(r.stdout)[2], "user/eng-12-parser")

    def test_a_given_name_that_reads_as_an_option_is_refused(self):
        for bad in ("-x", "--force", "two words", ""):
            r = self.run_fleet("start", "12", f"--name={bad}", "--host", "claude", "--dry-run",
                               config=False)
            self.assertEqual(r.returncode, 2, bad)

    def test_a_mistyped_config_key_is_an_error_not_a_default(self):
        self.cfg.write_text('[launcer]\nstatus = ["x"]\n')
        r = self.run_fleet("start", "12", "--host", "claude", "--dry-run")
        self.assertEqual(r.returncode, 2)
        self.assertIn("launcer", r.stderr)

    def test_a_wrong_type_in_the_config_is_an_error(self):
        self.cfg.write_text('[launcher]\nstart = "workmux add"\n')
        r = self.run_fleet("start", "12", "--host", "claude", "--dry-run")
        self.assertEqual(r.returncode, 2)
        self.assertIn("launcher.start", r.stderr)

    def test_the_launchers_refusal_reaches_the_person(self):
        self.write_cfg()
        (self.dir / "fail").write_text("")
        r = self.run_fleet("start", "12", "--host", "claude")
        self.assertEqual(r.returncode, 3)
        self.assertIn("worktree already exists", r.stderr)

    def test_a_missing_launcher_is_named(self):
        self.cfg.write_text('[launcher]\nstart = ["no-such-launcher-xyz", "{name}"]\n')
        r = self.run_fleet("start", "12", "--host", "claude")
        self.assertEqual(r.returncode, 127)
        self.assertIn("no-such-launcher-xyz", r.stderr)


if __name__ == "__main__":
    unittest.main()
