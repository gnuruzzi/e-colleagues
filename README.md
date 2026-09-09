# e-colleagues

A team of AI personas that installs into your coding agent, learns your project from several angles, and works to the rules your project already has.

Six personas — **tech-lead, developer, reviewer, security, designer, platform** — authored once and rendered into each host's own dialect. The tech-lead is your single point of contact: it plans, delegates to the specialists, checks their work against acceptance criteria, and is the only one that posts anywhere public. Reviewer and security cannot edit your files, and on Codex that is enforced by the sandbox rather than by asking nicely.

Two things it does to a repository:

- **`ec-init`** establishes the operating contract — who is on the team, which platforms and tools the project uses, the branching and merge rules, who may push or tag. Interview-derived, because only a human knows those. It lands as one small managed block at the top of your `AGENTS.md`, and your own content is never restructured.
- **`ec-onboard`** learns the project. Each persona audits from its own angle — architecture, build and test reality, coverage and standards, security posture, design system, CI/CD and infrastructure — and **indexes what your project already documents first**, authoring a knowledge file only where there is no home for that angle. Every file records the commit and the paths it was derived from, so going stale is detectable with a `git diff`.

## Status

**M0–M5 complete.** All six personas are rendered into four host dialects from a single
source, behind a drift gate and 43 tests. What is verified is recorded: see
[`docs/experiments.md`](docs/experiments.md) for 23 experiments against the installed tools,
and [`docs/SUPPORT-MATRIX.md`](docs/SUPPORT-MATRIX.md) for which claim was last confirmed at
which version. [`docs/design.md`](docs/design.md) is the decision record.

Publishing is M6, so the install lines below assume you have the repository locally.

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

### opencode

There is no bundle format, so `ec-init` writes the files into the project:
`.opencode/agents/*.md` plus an `opencode.json` carrying `default_agent: tech-lead`.

### Antigravity

```bash
agy plugin install /path/to/e-colleagues        # or a https://github.com/... URL
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

## Why the research directory is here

`docs/research/` holds 58 independently fact-checked claims about how Claude Code, Codex, opencode and Antigravity actually load agents, skills, plugins and instruction files — 50 confirmed, 8 refuted with corrections — plus 67 explicit "unknown, do not assume" gaps and the vendor documentation as it read at research time. Every path, key and command in the design cites a claim id, or says UNVERIFIED.

It is kept because the tools move fast enough that an unsourced design rots quietly. Four of the five targets moved within a day of the research being written, and one version gate had already flipped.

## Licence

MIT. See [LICENSE](LICENSE).
