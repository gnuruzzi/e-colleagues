# Changelog

Notable changes to e-colleagues. Format follows [Keep a Changelog](https://keepachangelog.com/);
this project uses semantic versioning from 0.1.0 onward.

## [0.1.1] — 2026-10-03

Every host moved past the version its claims were confirmed at; this release re-verifies all
of them, closes the questions the first sweep left open, delivers opencode per machine, and
puts a front door on the README. Nothing a 0.1.0 install depends on changed shape.

### Added

- **opencode, per machine.** `bootstrap.py --scope user` installs the roster's agents and the
  four skills under `~/.config/opencode/`, as real files, and reports them stale on `--check`.
  Measured end to end: the tech-lead loads from there and runs; the skills are listed and run
  when asked for by name. No bundle or plugin route for agents exists at opencode 2.0.18 (E25).
- **The opencode schema, vendored.** `check.py --opencode` fails when the key lists in
  `hosts/opencode.yaml` drift from `hosts/opencode-config.schema.json`; refreshing the copy is
  one `curl`. Six negative tests in `tests/test_check.py` break the gate one way each.
- **Both spellings of the opencode permissions.** The 2.x runtime names `task` as `subagent`
  and `bash` as `shell` and accepts either; the renderer now emits both with identical rules,
  and the gate requires the pair, so a dropped alias is a gate failure and not a fail-open.
- **A lens no persona audits is flagged.** The lock records the roster's lens names;
  `ec-status` prints `NO PERSONA` for an index row nobody in the roster can ever audit, and
  `bootstrap.py` reports it as an action needed. Found on this repository's own `AGENTS.md`.
- **README.** A real review as the opening demo, a diagram of the team tree, the roster as a
  catalog you can shrink or extend, one collapsible block per tool from install to first
  request, and the honesty table.

### Changed

- The raw research and the previous package left the tree before publication; every claim id
  now resolves inside the repository, and the documents are written for a stranger building
  on this rather than for whoever built it.
- Design §10 says what `--write` produces, three files, and names the per-host project files
  it never wrote. Route B is marked a design sketch, not code.
- `docs/experiments.md` gains E24 (the snapshot sweep) and E25 (the opencode plugin route),
  plus addenda to E8, E17, E19, E20 and E23.

### Fixed

- `bootstrap.py --check` no longer fails on the lock timestamp alone, and `--scope user
  --check` catches a stale tech-lead profile, not only stale agent files.
- Two documents still said the repository was unpublished; design §10 pointed the
  github-source question at publication rather than at its issue.

### Verified rather than assumed

- Every runtime claim re-run at Codex 0.154.0, Claude Code 2.1.283, agy 1.2.10 and desktop
  2.17.0 (E24), and the opencode dialect at 2.0.18 (E20 addendum). All reproduced.
- Four corrections: Antigravity desktop 2.17.0 carries the `agents:` tag it lacked at 2.12.2;
  Claude Code reads `AGENTS.md` natively at 2.1.283, so the `CLAUDE.md` import is no longer the
  only route; the opencode TUI's agent cycle is Shift+Tab, not Tab, and its file-form commands
  load from `.opencode/command/`, singular; `agy plugin install` parses `plugin@marketplace`
  but resolves it against nothing a user can register.
- Two nuances: with no role installed anywhere the Codex spawn tool has no `agent_type`
  parameter, so the loud `unknown agent_type` error presupposes one; and the rendered Claude
  reviewer now suppresses bytecode writes on its own initiative while its shell can still write.
- A github-sourced self-marketplace is registered and fetched on trust but does not load the
  plugin, and nothing says so; the `claude plugin install` line stays required (E23 addendum).
- The three behaviours that needed a person at a UI were exercised: the opencode Tab and `@`
  menus, and the Antigravity desktop honouring an explicit `tools` list (E19, E20 addenda).

### Known limitations

See [`docs/acceptance.md`](docs/acceptance.md). New there: opencode's roster is per machine,
like Antigravity's; `tools: []` on Antigravity is still not isolated.

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
