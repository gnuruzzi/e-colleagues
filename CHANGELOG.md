# Changelog

Notable changes to e-colleagues. Format follows [Keep a Changelog](https://keepachangelog.com/);
this project uses semantic versioning from 0.1.0 onward.

## [0.1.0] — 2026-09-09

First release. Six personas, four hosts, rendered from one source.

### Added

- **Six personas** — tech-lead, developer, reviewer, security, designer, platform — authored
  once in `personas/` as host-neutral YAML plus a Markdown body, and rendered into each
  host's own dialect. Tool vocabulary lives only in `hosts/*.yaml`.
- **Four host dialects**: Codex role TOMLs, Claude plugin agents, opencode agents with an
  `opencode.json`, and Antigravity `agent.md` files, plus the three plugin manifests that
  coexist in one repository.
- **`ec-init`** — establishes the operating contract as a managed block in `AGENTS.md`, with
  three regions and three owners: the package's, the audit's, and the team's. An update
  rewrites only the package's.
- **`ec-onboard`** — the multi-angle audit. Indexes what a project already documents and
  authors a knowledge file only where there is no home for that lens.
- **`ec-status`** — staleness as a `git diff`. Every knowledge file records the commit and
  the paths it was derived from, so a lens is stale exactly when a recorded path changed.
- **`ec-tech-lead`** — the portable floor: the tech-lead as a skill, for hosts or clones
  where the personas cannot load.
- **`tools/check.py`** — nine gates, every one negative-tested.
- 43 tests, standard library only, like the scripts they cover.

### Verified rather than assumed

`docs/experiments.md` records 23 experiments against the installed tools, and
`docs/SUPPORT-MATRIX.md` maps each of 52 claims to the version it was last confirmed at.
Findings that changed the design before any code depended on them:

- **Seven Antigravity tool names in the vendor documentation are not in the tool registry**
  and abort an agent at startup. Rendered from that list, every Antigravity agent would have
  failed to start.
- **`claude plugin validate` does not catch the frontmatter fail-open it appeared to.** A
  colon in the value — which every routing sentence has — makes malformed frontmatter pass,
  so `check.py` owns that guard.
- **A symlinked Codex role file is discovered and then fails at spawn**, so personas are
  installed as real files.
- **Codex's `read-only` sandbox blocks every write**, including `/tmp` and `$HOME`. Tests run,
  but a suite that writes anything needs an explicit override.
- **Bare `subagent_type` names do not resolve on Claude**; the qualified form is required.
- **A project `.claude/settings.json` `agent` key is not trust-gated** and replaces the whole
  system prompt.

### Known limitations

See [`docs/acceptance.md`](docs/acceptance.md). In short: Antigravity has no per-project
roster and its re-install merges rather than replaces; `AGENTS.md` reaches no Antigravity
agent; and "cannot edit" is a filesystem guarantee only on Codex.
