# e-colleagues

A team of AI personas that installs into your coding agent, learns your project from several angles, and works to the rules your project already has.

Six personas — **tech-lead, developer, reviewer, security, designer, platform** — authored once and rendered into each host's own dialect. The tech-lead is your single point of contact: it plans, delegates to the specialists, checks their work against acceptance criteria, and is the only one that posts anywhere public. Reviewer and security cannot edit your files, and on Codex that is enforced by the sandbox rather than by asking nicely.

Two things it does to a repository:

- **`ec-init`** establishes the operating contract — who is on the team, which platforms and tools the project uses, the branching and merge rules, who may push or tag. Interview-derived, because only a human knows those. It lands as one small managed block at the top of your `AGENTS.md`, and your own content is never restructured.
- **`ec-onboard`** learns the project. Each persona audits from its own angle — architecture, build and test reality, coverage and standards, security posture, design system, CI/CD and infrastructure — and **indexes what your project already documents first**, authoring a knowledge file only where there is no home for that angle. Every file records the commit and the paths it was derived from, so going stale is detectable with a `git diff`.

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
    (10**17, 3)-> 9.7e+16             float   # integer precision lost
The shipped test passes only because 900 == 900.0 is True in Python and 1000 × 10 / 100
happens to divide exactly. …

The fix needs a decision from you, not just code: which rounding applies to fractional
cents? Floor, round-half-even, or round-half-up … …

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

## What works today

Version 0.1.0. Six personas, rendered from one source into four host dialects.

| host | minimum version | the tech-lead is primary by | "cannot edit" is enforced by |
|---|---|---|---|
| OpenAI Codex CLI | 0.153.4 | `developer_instructions` (prose) | **the sandbox** — the only host where it is a filesystem guarantee |
| Claude Code | 2.1.263 | `--agent` (mechanical) | the tool list; the shell can still write |
| opencode | 1.18.29 | `default_agent` (mechanical) | permissions; bash narrowed by patterns |
| Google Antigravity | agy 1.1.27 | `mainAgent` (mechanical) | the tool list; `run_command` can still write |

Known limits, stated because a guarantee that is really a request is worth naming:
Codex's read-only sandbox blocks **every** write including `/tmp`, so a project whose tests
write anything needs an explicit override; Antigravity and opencode have no per-project
roster from this package, both being installed per machine, and an Antigravity re-install
merges rather than replaces; and `AGENTS.md` never reaches an Antigravity agent, so
its personas carry the contract in their own bodies. The full list, with what each rests on,
is in [`docs/acceptance.md`](docs/acceptance.md).

## Install

Nothing here needs network access beyond cloning.

### Codex CLI

```bash
codex plugin marketplace add /path/to/e-colleagues
codex plugin add e-colleagues@e-colleagues          # the four skills
python3 skills/ec-init/scripts/bootstrap.py --scope user --write   # the personas, as real files
```

The second line installs `ec-init`, `ec-onboard`, `ec-status` and `ec-tech-lead`. The third
writes `~/.codex/agents/*.toml` and `~/.codex/e-colleagues.config.toml`; run
`codex --profile e-colleagues` to make the tech-lead primary. They must be **real files** —
Codex opens a role file with `O_NOFOLLOW` at spawn, so a symlinked persona is discovered and
then fails with `agent type is currently not available`.

### Claude Code

```bash
claude plugin marketplace add /path/to/e-colleagues
claude plugin install e-colleagues@e-colleagues
claude --agent tech-lead
```

Delegation uses the qualified name — `e-colleagues:reviewer`, not `reviewer`. A bare name
resolves for the `--agent` flag but not for the `Agent` tool's `subagent_type`.

Both lines are needed even when a repository's own `.claude/settings.json` declares this
marketplace and enables the plugin: trusting such a clone registers and fetches the
marketplace but does not load the plugin, and nothing on screen says so
(`docs/experiments.md`, E23 addendum).

### opencode

```bash
python3 skills/ec-init/scripts/bootstrap.py --scope user --write   # ~/.config/opencode/agents/*.md
opencode run --agent tech-lead
```

opencode has no bundle format and no plugin route for agents — a plugin can add commands
and skills, not agents (`docs/experiments.md`, E25) — so the agents are installed per
machine, as real files, for the chosen profile. Your global opencode config is never
written: in the TUI pick the tech-lead with Tab, or set `default_agent: tech-lead` yourself.

### Antigravity

```bash
agy plugin install https://github.com/gnuruzzi/e-colleagues     # or a local path
agy --agent tech-lead
```

A **global** install is the only route that delivers agents — no workspace directory does at
agy 1.1.27 — so the roster is per-user rather than per-project there. A re-install merges
rather than replaces, so uninstall first when the roster shrinks.

## Bootstrap a project

```bash
python3 skills/ec-init/scripts/bootstrap.py /path/to/project --write --profile default
python3 skills/ec-status/scripts/status.py  /path/to/project
```

Profiles are `default` (all six), `library` (no designer, for projects with no user
interface) and `minimal`. `--check` exits non-zero when the contract is out of date or
`AGENTS.md` would exceed 30 KiB — above that Codex truncates the tail, and the raised cap
lives in a trust-gated config an untrusted teammate never gets.

## How this was built

Every path, key and command in the design cites a fact-checked claim, or says UNVERIFIED. The
claims are stated in full in [`docs/SUPPORT-MATRIX.md`](docs/SUPPORT-MATRIX.md), together with
the version each was last confirmed at and whether it was exercised at runtime or rests on
documentation alone.

They are not taken on faith. [`docs/experiments.md`](docs/experiments.md) records 25
experiments run against the installed tools, with the exact command, the version and the raw
output — and where an experiment contradicts a claim, the experiment wins. That discipline
paid for itself: seven tool names the Antigravity documentation lists are absent from its tool
registry and abort an agent at startup, so a renderer built from the documentation would have
produced agents that could not start on that host at all.

It is worth the ceremony because these tools move fast. Four of the five targets released a
new version within a day of the research being written, and one version gate had already
flipped by the time it was checked.

## Licence

MIT. See [LICENSE](LICENSE).
