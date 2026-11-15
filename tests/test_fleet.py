"""fleet.py: config, naming, start, overview. Standard library only, like the script."""
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
elif sys.argv[1] == "where":
    if os.path.exists(os.path.join(d, "where.out")):
        sys.stdout.write(open(os.path.join(d, "where.out")).read())
        sys.exit(int(os.path.exists(os.path.join(d, "where.fail"))))
    else:
        sys.stderr.write("no such repository\\n"); sys.exit(3)
elif sys.argv[1] == "add" and os.path.exists(os.path.join(d, "fail")):
    sys.stderr.write("worktree already exists\\n"); sys.exit(3)
elif sys.argv[1] == "add" and os.path.exists(os.path.join(d, "exit")):
    code = int(open(os.path.join(d, "exit")).read())
    if code < 0:
        os.kill(os.getpid(), -code)
    sys.exit(code)
elif sys.argv[1] == "add" and os.path.exists(os.path.join(d, "read-stdin")):
    open(os.path.join(d, "stdin.log"), "w").write(sys.stdin.read())
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
        (self.dir / "xdg").mkdir()

    def write_cfg(self, top="", extra=""):
        py, fake = json.dumps(sys.executable), json.dumps(str(self.fake))
        self.cfg.write_text(
            top + f'[launcher]\n'
            f'start = [{py}, {fake}, "add", "{{name}}", "--agent", "{{agent}}", "--prompt", "{{prompt}}"]\n'
            f'status = [{py}, {fake}, "status"]\n'
            f'capture = [{py}, {fake}, "capture", "{{name}}"]\n'
            f'where = [{py}, {fake}, "where", "{{name}}"]\n' + extra)

    def run_fleet(self, *args, config=True, env=None, stdin=None, cwd=None):
        e = {**os.environ, "FAKE_LOG": str(self.log), "FAKE_DIR": str(self.dir)}
        if config:
            e["EC_FLEET_CONFIG"] = str(self.cfg)
        else:
            e.pop("EC_FLEET_CONFIG", None)
            e["XDG_CONFIG_HOME"] = str(self.dir / "xdg")
        e.pop("TMUX_PANE", None)
        e.update(env or {})
        return subprocess.run([sys.executable, str(FLEET), *args],
                              capture_output=True, text=True, env=e, input=stdin, cwd=cwd)

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
            "workmux", "add", "issue-12", "--background", "--agent",
            "agy --agent tech-lead --settings '{\"trustedWorkspaces\":[\"{worktree}\"]}'",
            "--prompt", "Use the ec-fleet skill. Your assignment: issue 12."])

    def test_opencode_is_given_the_tech_lead_through_a_config_file_beside_the_script(self):
        """opencode's TUI takes no --agent at 2.2.7; a config file named in the environment
        chooses the agent, and a private server makes the session read it (E30)."""
        copy = self.dir.resolve() / "scripts"
        copy.mkdir()
        (copy / "fleet.py").write_text(FLEET.read_text())
        e = {**os.environ, "XDG_CONFIG_HOME": str(self.dir / "xdg")}
        e.pop("EC_FLEET_CONFIG", None)
        r = subprocess.run([sys.executable, str(copy / "fleet.py"), "start", "12", "--host",
                            "opencode", "--dry-run"], capture_output=True, text=True, env=e)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)[5],
                         f"env OPENCODE_CONFIG={copy}/opencode-tech-lead.json opencode --standalone")
        shipped = FLEET.parent / "opencode-tech-lead.json"
        self.assertEqual(json.loads(shipped.read_text()), {"default_agent": "tech-lead"})

    def test_a_script_path_the_launcher_would_break_is_refused_for_such_a_start(self):
        moved = self.dir / "my skills" / "scripts"
        moved.mkdir(parents=True)
        (moved / "fleet.py").write_text(FLEET.read_text())
        e = {**os.environ, "XDG_CONFIG_HOME": str(self.dir / "xdg")}
        e.pop("EC_FLEET_CONFIG", None)
        run = lambda host: subprocess.run(
            [sys.executable, str(moved / "fleet.py"), "start", "12", "--host", host, "--dry-run"],
            capture_output=True, text=True, env=e)
        r = run("opencode")
        self.assertEqual(r.returncode, 2)
        self.assertIn("[hosts.opencode]", r.stderr)
        self.assertEqual(run("claude").returncode, 0)

    def project(self, files):
        root = self.dir / "project"
        (root / ".git").mkdir(parents=True)
        (root / "src").mkdir()
        for rel, name in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(f"---\nname: {name}\ndescription: x\n---\nbody\n")
        return root

    def test_a_project_agent_that_would_replace_the_tech_lead_is_named(self):
        """At agy 1.5.3 a workspace agent runs in place of the installed one of the same
        name, by its frontmatter name and not its folder's (E32)."""
        root = self.project({".agents/agents/anything/agent.md": "tech-lead",
                             "_agents/plugins/p/agents/lead.md": '"tech-lead"',
                             ".agents/agents/reviewer/agent.md": "reviewer"})
        self.write_cfg()
        (self.dir / "where.out").write_text("Worktree: /w/issue-12\n")
        r = self.run_fleet("start", "12", "--host", "antigravity", cwd=root / "src")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "started issue-12\n")
        self.assertIn("fleet: this repository has its own agent named 'tech-lead'", r.stderr)
        self.assertIn(".agents/agents/anything/agent.md", r.stderr)
        self.assertIn("_agents/plugins/p/agents/lead.md", r.stderr)
        self.assertNotIn("reviewer", r.stderr)

    def test_no_such_warning_without_such_an_agent_or_on_another_host(self):
        self.write_cfg()
        (self.dir / "where.out").write_text("Worktree: /w/issue-12\n")
        plain = self.project({".agents/agents/reviewer/agent.md": "reviewer"})
        self.assertEqual(self.run_fleet("start", "12", "--host", "antigravity",
                                        cwd=plain).stderr, "")
        (plain / ".agents/agents/tl").mkdir()
        (plain / ".agents/agents/tl/agent.md").write_text("---\nname: tech-lead\n---\n")
        self.assertEqual(self.run_fleet("start", "12", "--host", "claude", cwd=plain).stderr, "")

    def test_base_is_appended_with_the_launchers_flag(self):
        r = self.run_fleet("start", "12", "--host", "codex", "--base", "main", "--dry-run",
                           config=False)
        self.assertEqual(json.loads(r.stdout)[-2:], ["--base", "main"])

    def test_a_host_is_required_when_no_default_is_configured(self):
        r = self.run_fleet("start", "12", "--dry-run", config=False)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--host", r.stderr)
        # The skill tells the dispatcher to retry on exactly this text.
        self.assertIn("no host chosen", r.stderr)
        skill = (ROOT / "skills" / "ec-fleet" / "SKILL.md").read_text()
        self.assertIn("`no host chosen`", skill)

    def test_default_host_and_start_command_come_from_the_config(self):
        self.write_cfg(top='default_host = "antigravity"\n',
                       extra='[hosts.antigravity]\n'
                             'start = "agy --agent tech-lead --remote-control"\n')
        (self.dir / "where.out").write_text("Worktree: /w/repo__worktrees/eng-123\nBranch:   eng-123\n")
        r = self.run_fleet("start", "ENG-123")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr, "")
        self.assertEqual(self.logged(), [["where", "eng-123"], [
            "add", "eng-123", "--agent",
            "agy --agent tech-lead --remote-control "
            "--settings '{\"trustedWorkspaces\":[\"/w/repo__worktrees/eng-123\"]}'",
            "--prompt", "Use the ec-fleet skill. Your assignment: issue ENG-123."]])

    TRUST = '[hosts.h]\nstart = "h run"\ntrust = "--trust {worktree}"\n'

    def test_codex_gets_its_own_trust_for_the_worktree(self):
        self.write_cfg()
        (self.dir / "where.out").write_text("Worktree: /w/my repo__worktrees/issue-12\n")
        r = self.run_fleet("start", "12", "--host", "codex")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(
            self.logged()[-1][3],
            "codex --profile e-colleagues "
            "-c 'projects={\"/w/my repo__worktrees/issue-12\"={trust_level=\"trusted\"}}'")

    def test_a_bare_path_from_where_is_read_too(self):
        self.write_cfg(extra=self.TRUST)
        (self.dir / "where.out").write_text("\n/w/issue-12\n")
        r = self.run_fleet("start", "12", "--host", "h")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.logged()[-1][3], "h run --trust /w/issue-12")

    def test_a_path_with_a_space_is_filled_only_inside_quotes(self):
        (self.dir / "where.out").write_text("Worktree: /w/a --flag b/issue-12\n")
        for template, want in (
                ("--trust {worktree}", "h run"),
                ("--trust '{worktree}'", "h run --trust '/w/a --flag b/issue-12'"),
                ('--trust \\"{worktree}\\"', 'h run --trust "/w/a --flag b/issue-12"'),
                ("--a 'x' --trust {worktree}", "h run")):
            self.write_cfg(extra=f'[hosts.h]\nstart = "h run"\ntrust = "{template}"\n')
            self.log.unlink(missing_ok=True)
            r = self.run_fleet("start", "12", "--host", "h")
            self.assertEqual(r.returncode, 0, (template, r.stderr))
            self.assertEqual(self.logged()[-1][3], want, template)

    def test_a_launcher_of_ones_own_is_not_asked_through_workmux(self):
        """The default where command is workmux's; it knows nothing of another launcher."""
        py, fake = json.dumps(sys.executable), json.dumps(str(self.fake))
        self.cfg.write_text(f'[launcher]\nstart = [{py}, {fake}, "add", "{{name}}", "{{agent}}"]\n')
        stub = self.dir / "bin"
        stub.mkdir()
        (stub / "workmux").write_text("#!/bin/sh\necho 'Worktree: /stub/path'\n")
        (stub / "workmux").chmod(0o755)
        r = self.run_fleet("start", "12", "--host", "antigravity",
                           env={"PATH": f"{stub}{os.pathsep}{os.environ['PATH']}"})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.logged(), [["add", "issue-12", "agy --agent tech-lead"]])
        self.assertIn("fleet: could not learn the worktree's path", r.stderr)

    def test_without_the_worktrees_path_the_start_goes_ahead_untrusted_and_says_so(self):
        self.write_cfg(extra=self.TRUST)
        outputs = [None, "", "Worktree: relative/issue-12\n", "Worktree: /w/it's/issue-12\n",
                   'Worktree: /w/a"b/issue-12\n', "Worktree: /w/a\\b/issue-12\n",
                   "Worktree: /w/a\x1bb/issue-12\n", "Worktree: /w/a\x7fb/issue-12\n",
                   "FAILS:Worktree: /w/issue-12\n"]
        for out in outputs:
            self.log.unlink(missing_ok=True)
            for name in ("where.out", "where.fail"):
                (self.dir / name).unlink(missing_ok=True)
            if out is not None and out.startswith("FAILS:"):
                out = out[len("FAILS:"):]
                (self.dir / "where.fail").write_text("")
            if out is not None:
                (self.dir / "where.out").write_text(out)
            r = self.run_fleet("start", "12", "--host", "h")
            self.assertEqual(r.returncode, 0, (out, r.stderr))
            self.assertEqual(r.stdout, "started issue-12\n", out)
            self.assertIn("fleet: could not learn the worktree's path", r.stderr, out)
            self.assertEqual(self.logged()[-1][3], "h run", out)

    def test_a_where_command_that_cannot_run_does_not_stop_the_start(self):
        self.write_cfg(extra=self.TRUST)
        lines = ['where = ["no-such-launcher-xyz", "{name}"]' if ln.startswith("where = ") else ln
                 for ln in self.cfg.read_text().splitlines()]
        self.cfg.write_text("\n".join(lines) + "\n")
        r = self.run_fleet("start", "12", "--host", "h")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("fleet: could not learn the worktree's path", r.stderr)
        self.assertEqual(self.logged(), [["add", "issue-12", "--agent", "h run", "--prompt",
                                          "Use the ec-fleet skill. Your assignment: issue 12."]])

    def test_where_runs_only_for_a_host_whose_trust_needs_the_path(self):
        self.write_cfg(extra='[hosts.antigravity]\ntrust = ""\n'
                             '[hosts.fixed]\nstart = "f run"\ntrust = "--yes"\n')
        for host, agent in (("claude", "claude --agent tech-lead"),
                            ("antigravity", "agy --agent tech-lead"), ("fixed", "f run --yes")):
            self.log.unlink(missing_ok=True)
            r = self.run_fleet("start", "12", "--host", host)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stderr, "", host)
            self.assertEqual([c[0] for c in self.logged()], ["add"], host)
            self.assertEqual(self.logged()[0][3], agent, host)

    def test_a_dry_run_runs_nothing_and_leaves_the_path_unfilled(self):
        self.write_cfg(extra=self.TRUST)
        r = self.run_fleet("start", "12", "--host", "h", "--dry-run")
        self.assertEqual(json.loads(r.stdout)[5], "h run --trust {worktree}")
        self.assertFalse(self.log.exists())

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

    def test_a_base_that_reads_as_an_option_is_refused(self):
        for bad in ("-x", "two words", ""):
            r = self.run_fleet("start", "12", f"--base={bad}", "--host", "claude", "--dry-run",
                               config=False)
            self.assertEqual(r.returncode, 2, bad)
            self.assertIn("--base", r.stderr)

    def test_an_empty_reference_is_refused(self):
        for bad in ("", "  "):
            r = self.run_fleet("start", bad, "--name", "x", "--host", "claude", "--dry-run",
                               config=False)
            self.assertEqual(r.returncode, 2, repr(bad))

    def test_placeholders_inside_a_value_are_never_expanded(self):
        r = self.run_fleet("start", "12 {name}", "--host", "claude", "--dry-run", config=False)
        self.assertEqual(json.loads(r.stdout)[-1],
                         "Use the ec-fleet skill. Your assignment: issue 12 {name}.")
        r = self.run_fleet("start", "12", "--name", "a{prompt}b", "--host", "claude",
                           "--dry-run", config=False)
        self.assertEqual(json.loads(r.stdout)[2], "a{prompt}b")

    def test_a_missing_explicit_config_is_an_error_not_a_default(self):
        r = self.run_fleet("start", "12", "--host", "claude", "--dry-run")
        self.assertEqual(r.returncode, 2)
        self.assertIn(f"{self.cfg}: no such config file", r.stderr)
        absent = self.dir / "absent.toml"
        r = self.run_fleet("--config", str(absent), "start", "12", "--host", "claude",
                           "--dry-run", config=False)
        self.assertEqual(r.returncode, 2)
        self.assertIn(str(absent), r.stderr)

    def test_an_empty_launcher_command_is_an_error(self):
        for key in ("start", "status", "capture", "where"):
            self.cfg.write_text(f"[launcher]\n{key} = []\n")
            r = self.run_fleet("start", "12", "--host", "claude", "--dry-run")
            self.assertEqual(r.returncode, 2, key)
            self.assertIn(f"launcher.{key}: expected a non-empty list", r.stderr)

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

    def test_a_launcher_that_fails_silently_still_says_so(self):
        self.write_cfg()
        for code, want in (("4", 4), ("-15", 1)):
            (self.dir / "exit").write_text(code)
            r = self.run_fleet("start", "12", "--host", "claude")
            self.assertEqual(r.returncode, want, code)
            self.assertIn(f"fleet: launcher exited with {code}", r.stderr)

    def test_the_launcher_gets_no_input(self):
        self.write_cfg()
        (self.dir / "read-stdin").write_text("")
        r = self.run_fleet("start", "12", "--host", "claude", stdin="y\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.dir / "stdin.log").read_text(), "")

    def test_a_launcher_that_cannot_run_is_named(self):
        launcher = self.dir / "not-executable"
        launcher.write_text("#!/bin/sh\n")
        launcher.chmod(0o644)
        argv0 = json.dumps(str(launcher))
        self.cfg.write_text(f'[launcher]\nstart = [{argv0}, "{{name}}"]\nstatus = [{argv0}]\n')
        for args in (("start", "12", "--host", "claude"), ("overview",)):
            r = self.run_fleet(*args)
            self.assertEqual(r.returncode, 126, args)
            self.assertIn(f"fleet: cannot run launcher {launcher}: ", r.stderr)
            self.assertNotIn("Traceback", r.stderr)

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

# Cut from real captures (E29, E31): each host bullets the reply and adds lines of its own.
CODEX_SCREEN = """\u2022 \U0001f468\u200d\U0001f4bb Tech-Lead: The first touch command was declined.

  ### RETURN
  status: needs-decision
  task: issue 16
  changed: none
  evidence: touch was declined
  findings: none
  risks: none
  follow-ups: none
  questions: Would you like me to retry the declined command with a fresh request for escalated permissions so that we
  can verify creation at the originally requested path, or skip it because the replacement command already exited
  successfully?
  knowledge: none

  Worked for 11s \u2022 9:23 AM

\u203a Ask Codex to do anything

  GPT-6.1-Sol high \u00b7 <tmp>/repo__worktrees/issue-16 \u00b7 Reply ready
  \u2190 for agents \u00b7 ? for shortcuts
"""

CLAUDE_SCREEN = """\u25cf \U0001f468\u200d\U0001f4bb Tech-Lead: This is a parser probe.

  ### RETURN
  status: partial
  task: issue-14
  changed: none
  evidence: none
  findings:
    - severity: blocking
      path: README.md
      line: 1
      body: the title says probe
    - severity: nit
      path: -
      line: -
      body: questions: is a word that also names a field
  risks: none
  follow-ups: none
  questions: Should the parser probe continue (yes or no)?
  knowledge: none

\u273b Worked for 4s \u00b7 done 9:25

\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
\u276f yes
\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  \u23f5\u23f5 auto mode on (shift+tab to cycle) \u00b7 \u2190 1 agent
"""

# opencode draws a sidebar to the right of the conversation, on the same screen rows (E30).
PAD = " " * 60
OPENCODE_SCREEN = f"""     Reading .env was rejected, so I have no line count to report.
{PAD}{PAD}Readiness check
     ### RETURN{PAD}Session
     status: needs-decision{PAD}Context
     task: issue-17{PAD}14,020 tokens
     changed: none{PAD}21% used
     evidence: the read of .env was rejected
     findings: none{PAD}MCP
     risks: none{PAD}\u2022 a server
     follow-ups: none
     questions: Do you want me to retry reading `.env` so I can report its line count, or{PAD}LSP
     should I skip it entirely?
     knowledge: none

     Tech-Lead \u00b7 <local model>{PAD}\u00b7 12.7s
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

    def test_a_codex_capture_is_read_and_its_footer_does_not_leak(self):
        got = self.f.last_return(CODEX_SCREEN)
        self.assertEqual(got["status"], "needs-decision")
        self.assertTrue(got["questions"].startswith("Would you like me to retry"))
        self.assertTrue(got["questions"].endswith("successfully?"))

    def test_a_claude_capture_with_a_nested_finding_is_read(self):
        got = self.f.last_return(CLAUDE_SCREEN)
        self.assertEqual(got, {"status": "partial",
                               "questions": "Should the parser probe continue (yes or no)?"})

    def test_an_opencode_capture_is_read_past_its_sidebar(self):
        got = self.f.last_return(OPENCODE_SCREEN)
        self.assertEqual(got, {
            "status": "needs-decision",
            "questions": "Do you want me to retry reading `.env` so I can report its line count, "
                         "or should I skip it entirely?"})

    def test_the_last_block_wins(self):
        older = BLOCK.replace("needs-decision", "partial")
        self.assertEqual(self.f.last_return(older + "\nmore work\n" + BLOCK)["status"],
                         "needs-decision")

    def test_a_framed_or_indented_block_is_read(self):
        framed = "\n".join("\u2502  " + ln for ln in BLOCK.splitlines())
        self.assertEqual(self.f.last_return(framed)["status"], "needs-decision")

    def test_only_a_line_that_is_the_heading_starts_a_block(self):
        self.assertIsNone(self.f.last_return(BLOCK.replace("### RETURN", "### RETURNS")))
        quoted = BLOCK.replace("Keep the old flag", "Is the ### RETURN block right? Keep the flag")
        self.assertEqual(self.f.last_return(quoted)["status"], "needs-decision")
        for head in ("\u25cf ### RETURN \u2502", "\u25cf Tech-Lead: ### RETURN"):
            self.assertEqual(self.f.last_return(BLOCK.replace("### RETURN", head))["status"],
                             "needs-decision", head)

    def test_text_is_cut_at_eight_spaces_and_a_padded_frame_is_not(self):
        gap = lambda n: BLOCK.replace("status: needs-decision",
                                      "status: needs-decision" + " " * n + "Context")
        self.assertEqual(self.f.last_return(gap(8))["status"], "needs-decision")
        self.assertIsNone(self.f.last_return(gap(7)))
        framed = "\n".join("\u2502" + " " * 10 + ln for ln in BLOCK.splitlines())
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

    def test_the_four_statuses_are_read(self):
        for status in ("done", "partial", "blocked", "needs-decision"):
            got = self.f.last_return(BLOCK.replace("status: needs-decision", f"status: {status}"))
            self.assertEqual(got["status"], status)

    def test_a_status_that_is_not_one_of_the_four_is_unreadable(self):
        for line in ("status: done | partial | blocked | needs-decision", "**status:** done"):
            self.assertIsNone(self.f.last_return(BLOCK.replace("status: needs-decision", line)),
                              line)

    def test_a_block_cut_off_before_its_status_is_unreadable(self):
        self.assertIsNone(self.f.last_return("### RETURN\n"))

    def test_no_block_is_none(self):
        self.assertIsNone(self.f.last_return("all done, nothing else to say\n"))


class TestOverview(Base):
    def seed(self, agents):
        self.write_cfg()
        (self.dir / "status.json").write_text(json.dumps({"agents": agents}))

    def test_stopped_sessions_are_read_and_busy_ones_are_not_captured(self):
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
                         [["capture", "issue-15"]])

    def test_a_session_waiting_at_an_approval_is_not_read_for_an_old_block(self):
        self.seed([{"worktree": "issue-15", "status": "waiting", "agent_kind": "codex",
                    "pane_id": "%2"}])
        (self.dir / "issue-15.screen").write_text(BLOCK)
        r = self.run_fleet("overview")
        self.assertEqual(r.stdout.splitlines()[1].split(), ["issue-15", "waiting", "codex"])
        self.assertEqual([c[0] for c in self.logged()], ["status"])

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

    def test_a_long_question_is_cut_to_one_hundred_characters(self):
        self.seed([{"worktree": "issue-15", "status": "done", "agent_kind": "agy",
                    "pane_id": "%2"}])
        (self.dir / "issue-15.screen").write_text(
            BLOCK.replace("Keep the old flag", "Keep " + "very " * 40 + "old flag"))
        line = self.run_fleet("overview").stdout.splitlines()[1]
        question = line[line.index("Keep"):]
        self.assertEqual(len(question), 100)
        self.assertTrue(question.endswith("\u2026"))

    def test_the_skill_names_every_text_the_table_can_show(self):
        skill = (ROOT / "skills" / "ec-fleet" / "SKILL.md").read_text()
        f = load()
        for text in (f.NO_BLOCK, f.NO_SCREEN, "(this session)"):
            self.assertIn(f"`{text}`", skill)

    def test_a_stopped_session_with_no_block_says_so(self):
        self.seed([{"worktree": "issue-19", "status": "done", "pane_id": "%3"}])
        (self.dir / "issue-19.screen").write_text("Allow this command? [y/n]\n")
        self.assertIn("no RETURN block on screen", self.run_fleet("overview").stdout)

    def test_a_screen_that_cannot_be_read_says_so(self):
        self.seed([{"worktree": "issue-19", "status": "done", "pane_id": "%3"},
                   {"worktree": "issue-12", "status": "working", "pane_id": "%1"}])
        r = self.run_fleet("overview")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertTrue(lines[1].endswith("could not read its screen"), lines[1])
        self.assertEqual(lines[2].split(), ["issue-12", "working"])
        row = json.loads(self.run_fleet("overview", "--json").stdout)[0]
        self.assertIsNone(row["return_status"])
        self.assertIsNone(row["questions"])

    def test_a_row_without_a_usable_name_is_not_captured(self):
        self.seed([{"status": "done", "pane_id": "%2"},
                   {"worktree": "-x", "status": "done", "pane_id": "%3"}])
        r = self.run_fleet("overview")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([c for c in self.logged() if c[0] == "capture"], [])
        self.assertEqual(r.stdout.count("could not read its screen"), 2)

    def test_a_cell_that_is_not_text_is_shown_as_text(self):
        self.seed([{"worktree": "issue-15", "status": "done", "agent_kind": 7, "pane_id": "%2"}])
        (self.dir / "issue-15.screen").write_text(BLOCK)
        r = self.run_fleet("overview")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[1].split()[:3], ["issue-15", "done", "7"])

    def test_status_items_that_are_not_sessions_are_an_error(self):
        self.write_cfg()
        (self.dir / "status.json").write_text(json.dumps({"agents": ["x"]}))
        r = self.run_fleet("overview")
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stderr.startswith("fleet: "), r.stderr)

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
        self.assertTrue(r.stderr.startswith("fleet: "), r.stderr)
        self.assertIn("not in a git repository", r.stderr)


if __name__ == "__main__":
    unittest.main()
