# Support matrix

One row per fact-checked claim the design rests on, with the version it was last confirmed at and whether the M0 sweep exercised it at runtime or it still rests on documentation and source alone.

Read with `docs/research/facts-digest.md` (the claim text and its verdict) and `docs/experiments.md` (the M0 evidence, E1–E23). Where the two disagree, **the experiment wins** — it was run against the installed binary, the digest was read from documentation and source.

## Versions this matrix describes

| tool | version | how the sweep reached it |
|---|---|---|
| Claude Code | 2.1.263 | `claude -p`, `--plugin-dir`, `plugin validate`, `plugin list` |
| Codex CLI | 0.153.4 | `codex exec`, `codex sandbox`, `codex plugin …` |
| opencode | 1.18.29 | `opencode run`, `agent list`, `run --command` |
| agy (Antigravity CLI) | 1.1.27 | `agy --print`, `--agent`, `plugin install/validate` |
| Antigravity desktop | 2.12.2 | binary inspection only — no session was driven |

**Re-verify before relying on a version-gated claim.** Four of the five tools moved within a day of the original research (`experiments.md` E2) and one gate had already flipped (E3). A claim marked *docs/source only* has never been exercised against a running tool.

## How to read the `how` column

- **runtime** — the M0 sweep exercised this claim against the installed binary and it held.
- **corrected** — the sweep contradicted or materially narrowed the digest. The design follows the experiment, not the claim text. These nine are listed again below.
- **docs/source only** — believed on documentation or source reading. Not exercised. Treat as the weakest tier.

## Corrections the sweep forced

These override the digest wherever they disagree.

| claim | the digest said | the sweep measured | evidence |
|---|---|---|---|
| `AG-06` | a list of Antigravity tool names, and that a bad name "may cause the subagent process to hang" | **seven of the names are not in the registry** and abort the agent at startup with `unknown component: tool "…" not found in registry` — loudly and before any model call, not a hang | E17 |
| `CC-07` | `claude plugin validate` catches the frontmatter fail-open | it does **not**: a colon in the value triggers a repairing sanitizer, and `memory`, unknown keys and a colon in `name` all pass | E15 |
| `CC-03` | a bare agent name resolves | true for the `--agent` flag, **false** for `Agent(...)`'s `subagent_type`, which needs `e-colleagues:<name>` | E10 |
| `CC-10` | the `agent` key makes a persona the default | true; it is **not trust-gated**, an unresolvable value fails silently, and **project scope beats user scope** | E21 |
| `AG-11` | Antigravity walks `AGENTS.md` cwd→root | **no agy agent receives it** — not a custom agent, not the default one | E19 |
| `AG-12` | a workspace agent definition ranks above plugin and global | **no workspace root delivers agents at all**, so the ranking is moot | E18 |
| `AG-02` | the CLI and desktop share one engine | the `agents:` key exists in agy 1.1.27 and **not** in desktop 2.12.2 | E16 |
| `CX-04` | `[agents]` defaults and the V1/V2 resolution | correct, and the V2 ceiling **refuses** a spawn past the limit rather than queueing it | E11 |
| `OC-07` | command keys are {description, agent, model, subtask} | the schema is **{template, description, agent, model, variant, subtask}** with `template` required | E20 |

## The Antigravity tool registry

`check.py --agy-tools` validates against this list, which was derived by installing each name as the sole entry in an agent's `tools` list and running it (E17). **Do not derive it by grepping the binary** — that yields a superset and reported all seven invalid names as present (E16 C1, superseded).

Valid at **agy 1.1.27** — 15 names:

```
view_file  run_command  write_to_file  replace_file_content  multi_replace_file_content
grep_search  find_by_name  list_dir  read_url_content  search_web
invoke_subagent  define_subagent  manage_task  manage_subagents  send_message
```

Rejected at 1.1.27, despite appearing in the binary's strings: `view_file_outline`, `view_code_item`, `command_status`, `codebase_search`, `browser_subagent`, `notify_user`, `manage_inbox`.

## Claims by host

### Claude Code

| claim | last confirmed at | digest verdict | how | M0 evidence | what the sweep showed |
|---|---|---|---|---|---|
| `CC-02` | Claude Code 2.1.263 | confirmed | runtime | E10 | manifest agents list replaces the default scan; decoy never loaded |
| `CC-03` | Claude Code 2.1.263 | confirmed | **corrected** | E10 | bare subagent_type does NOT resolve; qualified form does |
| `CC-04` | Claude Code 2.1.263 | confirmed | runtime | E10 | three validate modes; validate . is marketplace mode |
| `CC-05` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-06` | Claude Code 2.1.263 | confirmed | runtime | E23 | local-source project plugin loads on trust, no install step |
| `CC-07` | Claude Code 2.1.263 | confirmed | **corrected** | E13, E15 | tools allowlist holds for editors; validate does NOT catch the fail-open |
| `CC-08` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-09` | Claude Code 2.1.263 | confirmed | runtime | E13 | read-only reviewer still writes via Bash |
| `CC-10` | Claude Code 2.1.263 | confirmed | **corrected** | E21 | agent key works, is NOT trust-gated, unresolvable value silent |
| `CC-11` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-12` | Claude Code 2.1.263 | confirmed | runtime | E10 | plugin agent bodies reach the subagent |
| `CC-13` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-14` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-15` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-16` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |

### Codex CLI

| claim | last confirmed at | digest verdict | how | M0 evidence | what the sweep showed |
|---|---|---|---|---|---|
| `CX-01` | Codex CLI 0.153.4 | confirmed | docs/source only | — | — |
| `CX-02` | Codex CLI 0.153.4 | confirmed | runtime | E4, E5 | read-only+never blocks every write; symlinked role TOML fails at spawn |
| `CX-03` | Codex CLI 0.153.4 | refuted | runtime | E12 | project skills load untrusted; project agents do not |
| `CX-04` | Codex CLI 0.153.4 | refuted | **corrected** | E11 | V2 ceiling is 3 spawned children; a 4th is refused, not queued |
| `CX-05` | Codex CLI 0.153.4 | refuted | runtime | E5, E9 | explicit spawn ask works; unknown agent_type errors loudly |
| `CX-06` | Codex CLI 0.153.4 | confirmed | runtime | E14, E22 | developer_instructions via profile and via trusted project config |
| `CX-07` | Codex CLI 0.153.4 | confirmed | runtime | E12 | $ec-tech-lead resolves from .agents/skills untrusted |
| `CX-08` | Codex CLI 0.153.4 | confirmed | runtime | E6 | whole tree copied; .codex-plugin manifest adopted |
| `CX-09` | Codex CLI 0.153.4 | confirmed | docs/source only | — | — |
| `CX-10` | Codex CLI 0.153.4 | confirmed | runtime | E6 | marketplace add + plugin add; source forms measured |
| `CX-11` | Codex CLI 0.153.4 | confirmed | runtime | E9 | AGENTS.md reaches the primary and spawned children |
| `CX-12` | Codex CLI 0.153.4 | confirmed | docs/source only | — | — |

### opencode

| claim | last confirmed at | digest verdict | how | M0 evidence | what the sweep showed |
|---|---|---|---|---|---|
| `OC-01` | opencode 1.18.29 | confirmed | runtime | E20 | project agents load from .opencode/agents |
| `OC-02` | opencode 1.18.29 | confirmed | runtime | E20 | permission edit:deny holds on a subagent |
| `OC-03` | opencode 1.18.29 | confirmed | runtime | E20 | default_agent applies to opencode run; modes correct |
| `OC-04` | opencode 1.18.29 | confirmed | docs/source only | — | — |
| `OC-05` | opencode 1.18.29 | confirmed | runtime | E20 | permission.task allowlist evaluated mechanically |
| `OC-07` | opencode 1.18.29 | confirmed | **corrected** | E20 | run --command as subtask; command schema keys corrected |
| `OC-08` | opencode 1.18.29 | refuted | docs/source only | — | — |
| `OC-09` | opencode 1.18.29 | refuted | runtime | E20 | AGENTS.md reaches a task child |
| `OC-10` | opencode 1.18.29 | refuted | docs/source only | — | — |
| `OC-11` | opencode 1.18.29 | confirmed | docs/source only | — | — |

### Antigravity

| claim | last confirmed at | digest verdict | how | M0 evidence | what the sweep showed |
|---|---|---|---|---|---|
| `AG-02` | agy 1.1.27 / desktop 2.12.2 | confirmed | **corrected** | E16, E19 | desktop lacks agents:; body is not sliced at the first H1 |
| `AG-03` | agy 1.1.27 / desktop 2.12.2 | confirmed | runtime | E19 | agy --agent runs a mainAgent persona |
| `AG-04` | agy 1.1.27 / desktop 2.12.2 | confirmed | docs/source only | — | — |
| `AG-05` | agy 1.1.27 / desktop 2.12.2 | confirmed | runtime | E19 | a tools allowlist DOES override ambient subagent inheritance |
| `AG-06` | agy 1.1.27 / desktop 2.12.2 | confirmed | **corrected** | E17 | SEVEN of the listed tool names are not in the registry |
| `AG-07` | agy 1.1.27 / desktop 2.12.2 | confirmed | runtime | E7, E18 | validate [ok]; only a global install delivers agents |
| `AG-08` | agy 1.1.27 / desktop 2.12.2 | confirmed | runtime | E8, E18 | destination measured; re-install merges; github URL works |
| `AG-10` | agy 1.1.27 / desktop 2.12.2 | confirmed | docs/source only | — | — |
| `AG-11` | agy 1.1.27 / desktop 2.12.2 | confirmed | **corrected** | E19 | AGENTS.md does NOT reach any agy agent |
| `AG-12` | agy 1.1.27 / desktop 2.12.2 | confirmed | **corrected** | E18 | no workspace root delivers agents, so collisions are moot |

### Prior art

| claim | last confirmed at | digest verdict | how | M0 evidence | what the sweep showed |
|---|---|---|---|---|---|
| `PA-01` | n/a (public repos) | confirmed | docs/source only | — | — |
| `PA-02` | n/a (public repos) | refuted | docs/source only | — | — |

### Standards

| claim | last confirmed at | digest verdict | how | M0 evidence | what the sweep showed |
|---|---|---|---|---|---|
| `STD-01` | n/a (cross-tool) | confirmed | docs/source only | — | — |
| `STD-02` | n/a (cross-tool) | confirmed | docs/source only | — | — |
| `STD-03` | n/a (cross-tool) | confirmed | docs/source only | — | — |
## Not covered here

Five questions stay open after M0 and none is version-gated in a way this matrix can express:

- a user-scope versus project-scope `agent` key on Claude — needs a temporary edit to a user's own settings file
- the opencode Tab and `@` menus — needs the TUI
- the Antigravity **desktop's** subagent-inheritance default — needs the desktop app
- the installed directory name for `agy plugin install <github-url>` (E8) — needs the repository published
- whether a **github**-sourced self-marketplace skips the install step the way a local one does (E23) — needs the repository published
