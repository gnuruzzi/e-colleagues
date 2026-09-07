# e-colleagues

A team of AI personas that installs into your coding agent, learns your project from several angles, and works to the rules your project already has.

Six personas — **tech-lead, developer, reviewer, security, designer, platform** — authored once and rendered into each host's own dialect. The tech-lead is your single point of contact: it plans, delegates to the specialists, checks their work against acceptance criteria, and is the only one that posts anywhere public. Reviewer and security cannot edit your files, and on Codex that is enforced by the sandbox rather than by asking nicely.

Two things it does to a repository:

- **`ec-init`** establishes the operating contract — who is on the team, which platforms and tools the project uses, the branching and merge rules, who may push or tag. Interview-derived, because only a human knows those. It lands as one small managed block at the top of your `AGENTS.md`, and your own content is never restructured.
- **`ec-onboard`** learns the project. Each persona audits from its own angle — architecture, build and test reality, coverage and standards, security posture, design system, CI/CD and infrastructure — and **indexes what your project already documents first**, authoring a knowledge file only where there is no home for that angle. Every file records the commit and the paths it was derived from, so going stale is detectable with a `git diff`.

## Status

**Design revision 3 complete; implementation not started.** Codex CLI is the first target; Claude Code, opencode and Antigravity follow at M5. See [`docs/design.md`](docs/design.md) for the design, [`docs/experiments.md`](docs/experiments.md) for what has been verified against the installed tools, and [`docs/handoff.md`](docs/handoff.md) for provenance.

Install instructions land at M6. There is nothing to install yet.

## Why the research directory is here

`docs/research/` holds 58 independently fact-checked claims about how Claude Code, Codex, opencode and Antigravity actually load agents, skills, plugins and instruction files — 50 confirmed, 8 refuted with corrections — plus 67 explicit "unknown, do not assume" gaps and the vendor documentation as it read at research time. Every path, key and command in the design cites a claim id, or says UNVERIFIED.

It is kept because the tools move fast enough that an unsourced design rots quietly. Four of the five targets moved within a day of the research being written, and one version gate had already flipped.

## Licence

MIT. See [LICENSE](LICENSE).
