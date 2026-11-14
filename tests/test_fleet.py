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


BLOCK = """### RETURN
status: needs-decision
task: issue 15
changed: none
evidence: none
findings:
risks: none
follow-ups: none
questions: Keep the old flag as an alias, or remove it? I recommend removing it,
  since nothing in the repository reads it.
knowledge: none
"""

AGY_SCREEN = """  👨\u200d💻 Tech-Lead: Execution of the date shell command was declined by the user permission check.

    ### RETURN
    status: needs-decision
    task: probe-a
    changed: none
    evidence: date was declined
    findings: none
    risks: none
    follow-ups: none
    questions: Would you like me to retry running the shell command "date" (which requires your explicit permission approval in the prompt so that we can capture and verify the actual live system clock output from the shell environment     
    as originally requested), or should we skip executing the "date" command altogether (which avoids re-triggering the permission prompt and respects your previous denial while allowing us to conclude the probe-a task immediately 
    without shell timestamp output)?
    knowledge: none

\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2026
>
\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2026
? for shortcuts \u2026 tech-lead (Gemini 4 Argon \u00b7 high)  /agents
"""


class TestLastReturn(unittest.TestCase):
    def setUp(self):
        self.f = load()

    def test_reads_status_and_a_wrapped_question(self):
        got = self.f.last_return("some output\n" + BLOCK + "\n> ")
        self.assertEqual(got["status"], "needs-decision")
        self.assertEqual(got["questions"],
                         "Keep the old flag as an alias, or remove it? I recommend removing "
                         "it, since nothing in the repository reads it.")

    def test_an_antigravity_capture_is_read_and_the_interface_does_not_leak(self):
        got = self.f.last_return(AGY_SCREEN)
        self.assertEqual(got["status"], "needs-decision")
        self.assertTrue(got["questions"].startswith("Would you like me to retry running"))
        self.assertTrue(got["questions"].endswith("without shell timestamp output)?"))
        self.assertNotIn("  ", got["questions"])
        self.assertNotIn("shortcuts", got["questions"])

    def test_the_last_block_wins(self):
        older = BLOCK.replace("needs-decision", "partial")
        self.assertEqual(self.f.last_return(older + "\nmore work\n" + BLOCK)["status"],
                         "needs-decision")

    def test_a_framed_or_indented_block_is_read(self):
        framed = "\n".join("\u2502  " + ln for ln in BLOCK.splitlines())
        self.assertEqual(self.f.last_return(framed)["status"], "needs-decision")

    def test_a_block_cut_off_before_knowledge_is_unreadable(self):
        cut = "### RETURN\nstatus: partial\ntask: x\nquestions: Which one?\n>\n? for shortcuts\n"
        self.assertIsNone(self.f.last_return(cut))

    def test_a_newer_cut_off_block_does_not_fall_back_to_an_older_one(self):
        cut = "### RETURN\nstatus: partial\ntask: x\nquestions: Which one?\n>\n"
        self.assertIsNone(self.f.last_return(BLOCK + "\n" + cut))

    def test_a_continuation_that_starts_with_an_earlier_key_stays_in_the_question(self):
        def block(question):
            return ("### RETURN\nstatus: partial\ntask: x\nchanged: none\nevidence: none\n"
                    "findings: none\nrisks: none\nfollow-ups: none\n"
                    f"questions: {question}\nknowledge: none\n")
        got = self.f.last_return(block("Is this ok?\n  status: unclear to me"))
        self.assertEqual(got, {"status": "partial", "questions": "Is this ok? status: unclear to me"})
        got = self.f.last_return(block("Choose A or B,\n  risks: of A are high"))
        self.assertEqual(got["questions"], "Choose A or B, risks: of A are high")

    def test_a_block_cut_off_before_its_status_is_unreadable(self):
        self.assertIsNone(self.f.last_return("### RETURN\n"))

    def test_no_block_is_none(self):
        self.assertIsNone(self.f.last_return("all done, nothing else to say\n"))


class TestOverview(Base):
    def seed(self, agents):
        self.write_cfg()
        (self.dir / "status.json").write_text(json.dumps({"agents": agents}))

    def test_stopped_sessions_are_read_and_working_ones_are_not_captured(self):
        self.seed([
            {"worktree": "issue-12", "branch": "issue-12", "status": "working",
             "agent_kind": "agy", "updated_ts": 100, "pane_id": "%1"},
            {"worktree": "issue-15", "branch": "issue-15", "status": "done",
             "agent_kind": "agy", "updated_ts": 200, "pane_id": "%2"},
            {"worktree": "issue-19", "branch": "issue-19", "status": "waiting",
             "agent_kind": "codex", "updated_ts": 300, "pane_id": "%3"},
        ])
        (self.dir / "issue-15.screen").write_text(BLOCK)
        (self.dir / "issue-19.screen").write_text("Allow this command? [y/n]\n")
        r = self.run_fleet("overview", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = {row["name"]: row for row in json.loads(r.stdout)}
        self.assertEqual(set(rows["issue-12"]), {"name", "branch", "host", "state",
                                                 "updated_ts", "self", "return_status",
                                                 "questions"})
        self.assertIsNone(rows["issue-12"]["return_status"])
        self.assertEqual(rows["issue-15"]["return_status"], "needs-decision")
        self.assertTrue(rows["issue-15"]["questions"].startswith("Keep the old flag"))
        self.assertEqual(rows["issue-19"]["state"], "waiting")
        self.assertIsNone(rows["issue-19"]["return_status"])
        self.assertEqual([c for c in self.logged() if c[0] == "capture"],
                         [["capture", "issue-15"], ["capture", "issue-19"]])

    def test_the_callers_own_session_is_marked_and_not_captured(self):
        self.seed([{"worktree": "main", "status": "done", "pane_id": "%7"}])
        r = self.run_fleet("overview", "--json", env={"TMUX_PANE": "%7"})
        row = json.loads(r.stdout)[0]
        self.assertTrue(row["self"])
        self.assertEqual([c for c in self.logged() if c[0] == "capture"], [])

    def test_the_table_names_each_session_and_why_it_stopped(self):
        self.seed([{"worktree": "issue-15", "status": "done", "agent_kind": "agy",
                    "pane_id": "%2"}])
        (self.dir / "issue-15.screen").write_text(BLOCK)
        r = self.run_fleet("overview")
        self.assertIn("issue-15", r.stdout)
        self.assertIn("needs-decision", r.stdout)
        self.assertIn("Keep the old flag", r.stdout)

    def test_a_stopped_session_with_no_block_says_so(self):
        self.seed([{"worktree": "issue-19", "status": "done", "pane_id": "%3"}])
        (self.dir / "issue-19.screen").write_text("Allow this command? [y/n]\n")
        self.assertIn("no RETURN block on screen", self.run_fleet("overview").stdout)

    def test_no_sessions_is_not_an_error(self):
        self.seed([])
        r = self.run_fleet("overview")
        self.assertEqual(r.returncode, 0)
        self.assertIn("no sessions", r.stdout)

    def test_status_output_that_is_not_json_is_an_error(self):
        self.write_cfg()
        (self.dir / "status.json").write_text("workmux: not in a git repository\n")
        r = self.run_fleet("overview")
        self.assertEqual(r.returncode, 1)
        self.assertIn("not in a git repository", r.stderr)


if __name__ == "__main__":
    unittest.main()
