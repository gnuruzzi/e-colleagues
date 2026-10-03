# e-colleagues

A team of AI personas that installs into your coding agent, learns your project from
several angles, and works to the rules your project already has.

Six personas, **tech-lead, developer, reviewer, security, designer, platform**, authored once
and rendered for OpenAI Codex CLI, Claude Code, opencode and Google Antigravity. The tech-lead
is your single point of contact; the reviewer and security personas cannot edit your files.

## Why

A coding agent arrives as one voice holding every tool. Ask it to implement a change and
review it, and the same model, in the same thread, with the same write access, does both,
then reports on its own work in its own words. The rules of your project, who may push, what
gets reviewed, where findings go, live in someone's head or in a prompt retyped every session.

e-colleagues splits that one voice into a team whose roles hold:

- **One point of contact.** The tech-lead plans, delegates each piece with a brief, checks
  what comes back against acceptance criteria, and is the only persona that speaks to you or
  posts anywhere. Specialists return findings; they never touch your tracker.
- **Roles the host enforces, where it can.** The reviewer and the security persona have no
  edit tools on any host. On Codex the sandbox makes that a filesystem guarantee; elsewhere it
  is the tool list, and the table below says which is which, because the difference matters.
- **Rules that live in the repository.** `ec-init` writes the operating contract into your
  `AGENTS.md` as one managed block, so every session, on every host, on every teammate's
  machine, starts from the same rules.
- **Knowledge that knows when it is stale.** `ec-onboard` indexes what your project already
  documents before writing anything, and every file it does write records the commit and the
  paths it came from, so staleness is a `git diff`, not a feeling.

It is for teams and solo developers already using Codex, Claude Code, opencode or Antigravity
who want that structure without changing tools: one install per machine, one block in one
file per project.

## At a glance

| | |
|---|---|
| **Six personas, one source** | Authored once in `personas/`, rendered into Codex, Claude Code, opencode and Antigravity dialects by `tools/gen.py`; a drift gate fails when the rendered tree and the source disagree |
| **One external voice** | Only the tech-lead speaks to you or posts to a tracker; specialists hand back structured findings (design §0, D6) |
| **Read-only roles that hold** | Reviewer and security have no edit tools on any host; on Codex the read-only sandbox blocks every write, measured (E4) |
| **The contract in your repository** | `ec-init` interviews you once and writes one managed block in `AGENTS.md`; idempotent, and `--check` guards it in CI |
| **A six-angle audit that indexes first** | `ec-onboard` records where your project already documents each angle and writes a knowledge file only where nothing does |
| **Staleness as a `git diff`** | Every knowledge file records the commit and paths it came from; `ec-status` reports which lenses went stale and which no persona can ever audit |
| **Install once per machine** | A plugin for Codex, Claude Code and Antigravity; `bootstrap.py --scope user` for the Codex roles and the opencode agents |
| **Every claim measured** | 25 experiments against the installed tools, 52 claims each stamped with the version it was last confirmed at, re-verified as one snapshot in September 2026 |

## See it in action

Both excerpts are unedited output from headless runs on 2026-10-03, cut with `…` where noted.

**The tech-lead delegating a review, Claude Code 2.1.284.** A four-file demo repository: a
one-line pricing helper, one test, and a bug the test does not catch. The prompt was *"Review
the change in the last commit for correctness before we merge it. Delegate the review to the
reviewer and report back."*

```text
👨‍💻 Tech-Lead: Both spot-checks confirm the Reviewer's evidence — I have what I need,
no further lookups required. Here's the report.

## Verdict: do not merge yet — REQUEST CHANGES
Reviewed: commit fbc32cd "add discount helper" on master (4 new files, 17 lines).
Reviewer: 🕵️ e-colleagues:reviewer, read-only, no files touched.

### Blocking — src/pricing.py:5 returns a float, never an int
`return price_cents - price_cents * percent / 100` uses true division, so the function
violates its own `-> int` annotation and the docstring's "in cents" on every input.
I reproduced the Reviewer's probe myself:
    (1000, 10) -> 900.0               float
    (999, 33)  -> 669.3299999999999   float
The shipped test passes only because 900 == 900.0 is True in Python. …
The fix needs a decision from you, not just code: which rounding applies to fractional
cents? …

### Recommended next step
Tell me the rounding policy (and whether negative prices are valid). I'll then brief the
Developer to fix the arithmetic and extend the tests, and send it back through the
Reviewer before I call it done.
```

**The reviewer's sandbox on Codex 0.154.0, no model turn.** The reviewer's role file sets
`sandbox_mode = "read-only"` and `approval_policy = "never"`. The project's test suite runs;
a write does not, anywhere, including `/tmp`:

```console
$ codex sandbox -c sandbox_mode=read-only -c approval_policy=never -- make test
Ran 2 tests in 0.000s
OK
$ codex sandbox -c sandbox_mode=read-only -c approval_policy=never -- sh -c "echo note > REVIEW.md"
sh: line 1: REVIEW.md: Read-only file system
```

## Quick start

**1. Install once per machine.** Clone this repository and follow the four lines for your
tool under [Install](#install). Then start the tech-lead: `codex --profile e-colleagues`,
`claude --agent tech-lead`, `opencode run --agent tech-lead`, or `agy --agent tech-lead`.

**2. Set up a project.** In your project, existing or empty, ask the tech-lead to run
`ec-init`: `$ec-init` on Codex, `/e-colleagues:ec-init` on Claude Code, `/ec-init` on
Antigravity. It proposes a roster from what the repository contains, asks you the few things
only a human knows (where work is tracked, who may merge, how to build and test), and writes
one managed block at the top of `AGENTS.md`. An empty repository gets a fresh `AGENTS.md`; an
existing one is never restructured. opencode carries no skills, so there run the script and
fill in the two headings it leaves you:

```bash
python3 ~/e-colleagues/skills/ec-init/scripts/bootstrap.py . --write
```

**3. Let the team learn the project.** Run `ec-onboard` the same way. Each persona audits
its own angle, indexes what you already document, and writes a knowledge file only where
nothing covers that angle. Later, `ec-status` says which of that knowledge has gone stale:

```bash
python3 ~/e-colleagues/skills/ec-status/scripts/status.py .
```

Profiles pick the roster: `default` is all six, `library` drops the designer, `minimal` is
tech-lead, developer and reviewer. `ec-init` proposes one; the scripts take `--profile`.

## Install

```bash
git clone https://github.com/gnuruzzi/e-colleagues ~/e-colleagues && cd ~/e-colleagues
```

**Codex CLI.** The plugin carries the four skills; the script writes the personas as real
files under `~/.codex/`, because a symlinked role is found and then fails at spawn (E5).

```bash
codex plugin marketplace add "$PWD"
codex plugin add e-colleagues@e-colleagues
python3 skills/ec-init/scripts/bootstrap.py --scope user --write
```

**Claude Code.** Both lines are needed even for a repository whose own settings declare this
marketplace: trust registers it but does not load the plugin, silently (E23 addendum).
Delegation uses the qualified name `e-colleagues:reviewer`.

```bash
claude plugin marketplace add "$PWD"
claude plugin install e-colleagues@e-colleagues
```

**opencode.** No bundle or plugin route for agents exists (E25), so the agents install per
machine as real files. Your global config is never written: use `--agent`, Shift+Tab in the
TUI, or set `default_agent` yourself.

```bash
python3 skills/ec-init/scripts/bootstrap.py --scope user --write
```

**Antigravity.** Only a global install delivers agents, so the roster is per machine. A
re-install merges rather than replaces; uninstall first when the roster shrinks (E8).

```bash
agy plugin install https://github.com/gnuruzzi/e-colleagues
```

To update, `git pull` in the clone and re-run the lines for your tool;
`bootstrap.py --scope user --check` reports what is out of date.

## Hosts and guarantees

Version 0.1.0. Every claim below was measured at the version shown.

| host | floor | re-verified at | tech-lead is primary by | "cannot edit" is enforced by |
|---|---|---|---|---|
| Codex CLI | 0.153.4 | 0.154.0 | `developer_instructions` (prose) | **the sandbox**: the one filesystem guarantee |
| Claude Code | 2.1.263 | 2.1.284 | `--agent` (mechanical) | the tool list; the shell can still write |
| opencode | 1.18.29 | 2.0.18 | `default_agent` (mechanical) | permissions; the shell narrowed by patterns |
| Antigravity | agy 1.1.27 | agy 1.2.10, desktop 2.17.0 | `mainAgent` (mechanical) | the tool list; `run_command` can still write |

Known limits, because a guarantee that is really a request is worth naming:

- Codex's read-only sandbox blocks **every** write, `/tmp` included, so a test suite that
  writes anything needs an explicit override.
- Antigravity and opencode have no per-project roster from this package; both install per
  machine.
- `AGENTS.md` never reaches an Antigravity agent, so its personas carry the contract in
  their own bodies.

The full list, and what each rests on, is in [`docs/acceptance.md`](docs/acceptance.md).

## How this was built

Every path, key and command in the design cites a fact-checked claim or says UNVERIFIED.
[`docs/SUPPORT-MATRIX.md`](docs/SUPPORT-MATRIX.md) states all 52 claims with the version each
was last confirmed at, and [`docs/experiments.md`](docs/experiments.md) holds the 25
experiments behind them, exact command and raw output included; an experiment outranks any
claim it contradicts. The design is [`docs/design.md`](docs/design.md).

## Licence

MIT. See [LICENSE](LICENSE).
