# Support matrix

One row per fact-checked claim the design rests on, with the version it was last confirmed at and whether it was exercised against a running tool or still rests on documentation and source alone.

Every claim id is stated in full under [The claims themselves](#the-claims-themselves) below, so a citation anywhere in this repository resolves without leaving it. Read alongside [`experiments.md`](experiments.md), which holds the evidence (E1–E37). Where a claim and an experiment disagree, **the experiment wins** — it ran against the installed binary; the claim was read from documentation and source.

## Versions this matrix describes

| tool | version | how the sweep reached it |
|---|---|---|
| Claude Code | 2.1.263 | `claude -p`, `--plugin-dir`, `plugin validate`, `plugin list` — **re-verified at 2.1.325** (E36): every runtime row but `CC-06`; before that at 2.1.283 (E24) |
| Codex CLI | 0.153.4 | `codex exec`, `codex sandbox`, `codex plugin …`, `codex debug prompt-input` — **re-verified at 0.167.0** (E34): every runtime row; before that at 0.154.0 (E24) |
| opencode | 1.18.29 | `opencode run`, `agent list`, `run --command` — **re-verified at 2.2.7** (E35): every runtime row holds but `OC-07`; before that at 2.0.18 (E20 addendum), where `agent list` became `debug agents` and `run --command` a slash command in the prompt, which 2.2.7 no longer expands |
| agy (Antigravity CLI) | 1.5.3 | `agy --print`, `--agent`, `plugin install/validate` — **every Antigravity claim re-run at 1.5.3** (E32), which is the supported floor. History: first swept at 1.1.27, with the tool registry re-verified unchanged at 1.2.6 and 1.2.10 (E17 addendum, E24); those versions are no longer supported, and the registry, `AGENTS.md` delivery, workspace agents and re-install all differed there |
| Antigravity desktop | 2.12.2 | binary inspection only at 2.12.2; **driven once at 2.17.0** (E19 addendum): the `tools` allowlist holds, `AGENTS.md` does not arrive, and the binary carries the `agents:` tag 2.12.2 lacked (E24); 2.29.1 binary inspected, not driven (E32) |

**Re-verify before relying on a version-gated claim.** Four of the five tools moved within a day of the original research (`experiments.md` E2) and one gate had already flipped (E3). A claim marked *docs/source only* has never been exercised against a running tool.

## Trust levels, highest first

1. An experiment in [`experiments.md`](experiments.md), run against the installed binary.
2. A claim marked confirmed with local evidence.
3. A confirmed claim resting on documentation only — the `docs/source only` rows below.
4. Anything the design marks UNVERIFIED.

## How to read the `how` column

- **runtime** — exercised against the installed binary, and it held.
- **corrected** — the sweep contradicted or materially narrowed the digest. The design follows the experiment, not the claim text. They are listed again below; `AG-11` and `AG-12` stay there as history, since at agy 1.5.3 the experiment agrees with the claim again (E32).
- **docs/source only** — believed on documentation or source reading. Not exercised. Treat as the weakest tier.

## Corrections the sweep forced

These override the digest wherever they disagree.

| claim | the digest said | the sweep measured | evidence |
|---|---|---|---|
| `AG-06` | a list of Antigravity tool names, and that a bad name "may cause the subagent process to hang" | **seven of the names were not in the registry** up to agy 1.2.10 and aborted the agent at startup with `unknown component: tool "…" not found in registry` — loudly and before any model call, not a hang. At 1.5.3 six are rejected the same way, and six others resolve and give no tool | E17, E24, E32 |
| `CC-07` | `claude plugin validate` catches the frontmatter fail-open | it does **not**: a colon in the value triggers a repairing sanitizer, and `memory`, unknown keys and a colon in `name` all pass | E15 |
| `CC-03` | a bare agent name resolves | true for the `--agent` flag, **false** for `Agent(...)`'s `subagent_type`, which needs `e-colleagues:<name>` | E10 |
| `CC-10` | the `agent` key makes a persona the default | true; it is **not trust-gated**, an unresolvable value fails silently, and **project scope beats user scope** | E21 |
| `AG-11` | Antigravity walks `AGENTS.md` cwd→root | **no agy agent received it** at 1.1.27 and 1.2.10 — not a custom agent, not the default one. At 1.5.3 the claim holds: the default agent, a custom agent and a sub-agent receive it | E19, E24, E32 |
| `AG-12` | a workspace agent definition ranks above plugin and global | **no workspace root delivered agents at all** at 1.1.27 and 1.2.10, so the ranking was moot. At 1.5.3 four roots deliver them and the workspace definition wins | E18, E24, E32 |
| `AG-02` | the CLI and desktop share one engine | the `agents:` key exists in agy 1.1.27 and **not** in desktop 2.12.2 — and again in desktop 2.17.0, so the divergence has closed | E16, E24 |
| `AG-07` | `plugin.json` needs a `name`, and the binary errors on a missing or invalid one | at agy 1.5.3 **a missing or non-kebab `name` is a warning**, `validate` still passes, and it checks no tool name | E32 |
| `CX-04` | `[agents]` defaults and the V1/V2 resolution | correct, and the V2 ceiling **refuses** a spawn past the limit rather than queueing it | E11 |
| `CX-02` | a role file's `sandbox_mode` and `approval_policy` govern the agent spawned from it | at 0.167.0, on the V2 backend, **a spawned role ran with its parent session's sandbox and approval policy**: a `read-only` + `never` role wrote by shell and `apply_patch` under a `workspace-write` session. The role's `developer_instructions` did arrive. The same on the V1 backend, and no role-file key, config declaration or permission profile tried narrows a child (E34) | E33, E34 |
| `CC-14` | Claude Code "reads CLAUDE.md, not AGENTS.md" | at 2.1.283 an `AGENTS.md` with no `CLAUDE.md` beside it **reaches the model**; the `@AGENTS.md` import still works and is kept for older versions | E24 |
| `OC-07` | command keys are {description, agent, model, subtask} | the schema is **{template, description, agent, model, variant, subtask}** with `template` required; at 2.2.7 a slash command in the `run` prompt is no longer expanded | E20, E35 |

## The Antigravity tool registry

`check.py --agy-tools` validates every rendered Antigravity agent against this list, derived by installing each name as the sole entry in an agent's `tools` list and running it (E32, by the method of E17). **Do not derive it by grepping the binary** — that yields a superset and reported all seven names then invalid as present (E16 C1, superseded).

Valid at **agy 1.5.3**, the supported floor (E32) — 10 names that load and give the agent a tool:

```
read_file  run_command  write_file  edit_file  search_web
invoke_subagent  define_subagent  manage_task  manage_subagents  send_message
```

Load and give no tool at 1.5.3, so the gate refuses them too (E32): `grep_search`, `find_by_name`, `list_dir`, `multi_replace_file_content` and `read_url_content`, each logged `deprecated and has no effect`, and `command_status`, which logs nothing.

Rejected at 1.5.3 with `not found in registry` (E32): `view_file_outline`, `view_code_item`, `codebase_search`, `browser_subagent`, `notify_user`, `manage_inbox`.

**History: agy 1.1.27, re-verified unchanged at 1.2.6 and 1.2.10** (E17 addendum, E24), no longer supported — 15 names were valid:

```
view_file  run_command  write_to_file  replace_file_content  multi_replace_file_content
grep_search  find_by_name  list_dir  read_url_content  search_web
invoke_subagent  define_subagent  manage_task  manage_subagents  send_message
```

All 15 still resolve at 1.5.3: `view_file`, `write_to_file` and `replace_file_content` arrive as `read_file`, `write_file` and `edit_file`, and five give no tool, as above (E32). Rejected at 1.1.27 and again at 1.2.6, despite appearing in the binary's strings: the six above and `command_status`.

## Claims by host

### Claude Code

| claim | last confirmed at | verdict | how | evidence | what was measured |
|---|---|---|---|---|---|
| `CC-02` | Claude Code 2.1.325 (E36; first 2.1.263) | confirmed | runtime | E10, E24, E36 | manifest agents list replaces the default scan; decoy never loaded |
| `CC-03` | Claude Code 2.1.325 (E36; first 2.1.263) | confirmed | **corrected** | E10, E24, E36 | bare subagent_type does NOT resolve; qualified form does |
| `CC-04` | Claude Code 2.1.325 for the three validate modes (E36; first 2.1.263); installing from a marketplace at 2.1.325 in E31 only | confirmed | runtime | E10, E31, E36 | three validate modes; validate . is marketplace mode |
| `CC-05` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-06` | Claude Code 2.1.284 (E23 addendum; first 2.1.263) | confirmed | runtime | E23, E24, E23 addendum | a `directory`-source project plugin loads on trust with no install step (2.1.263, 2.1.283); a `github` source is registered and fetched on trust but does not load until `claude plugin install`, and nothing says so (2.1.284) |
| `CC-07` | Claude Code 2.1.325 (E36; first 2.1.263) | confirmed | **corrected** | E13, E15, E24, E36 | tools allowlist holds for editors; validate does NOT catch the fail-open; the fail-open measured at runtime (E36) |
| `CC-08` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-09` | Claude Code 2.1.325 (E33, E36; first 2.1.263) | confirmed | runtime | E13, E24, E33, E36 | read-only reviewer still writes via Bash; an allowlist strips MCP and re-admits it only per server name, so every specialist carries a denylist of what it was measured to inherit |
| `CC-10` | Claude Code 2.1.325 (E36; first 2.1.263); the precedence row at 2.1.263 (E21) | confirmed | **corrected** | E21, E24, E36 | agent key works, is NOT trust-gated, unresolvable value silent |
| `CC-11` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-12` | Claude Code 2.1.325 (E36; first 2.1.263) | confirmed | runtime | E10, E24, E36 | plugin agent bodies reach the subagent |
| `CC-13` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |
| `CC-14` | Claude Code 2.1.325 (E36; first 2.1.263) | confirmed | **corrected** | E24, E36 | the load order holds and the @import works, but "not AGENTS.md" no longer does: AGENTS.md is read natively |
| `CC-15` | Claude Code 2.1.325 (E36; first 2.1.263, docs/source only) | confirmed | runtime | E36 | a project `.agents/skills` skill is not loaded |
| `CC-16` | Claude Code 2.1.263 | confirmed | docs/source only | — | — |

### Codex CLI

| claim | last confirmed at | verdict | how | evidence | what was measured |
|---|---|---|---|---|---|
| `CX-01` | Codex CLI 0.167.0 (E34; first 0.153.4, docs/source only until then) | confirmed | runtime (in part) | E34 | user and project role files load; the scan is recursive; the `name` key names the role |
| `CX-02` | Codex CLI 0.167.0 (E34; first 0.153.4) | confirmed | **corrected** | E4, E5, E24, E33, E34 | read-only+never blocks every write in a session started that way; a spawned role ran with its parent's sandbox instead, on both backends, and nothing tried narrows it; symlinked role TOML fails at spawn |
| `CX-03` | Codex CLI 0.167.0 (E34; first 0.153.4) | refuted | runtime | E12, E24, E34 | project skills load untrusted; project agents do not |
| `CX-04` | Codex CLI 0.167.0 (E34; first 0.153.4) | refuted | **corrected** | E11, E24, E34 | V2 ceiling is 3 spawned children; a 4th is refused, not queued |
| `CX-05` | Codex CLI 0.167.0 (E34; first 0.153.4) | refuted | runtime | E5, E9, E24, E34 | explicit spawn ask works; unknown agent_type errors loudly |
| `CX-06` | Codex CLI 0.167.0 (E34; first 0.153.4) | confirmed | runtime | E14, E22, E24, E34 | developer_instructions via profile and via trusted project config |
| `CX-07` | Codex CLI 0.167.0 (E34; first 0.153.4) | confirmed | runtime | E12, E24, E34 | $ec-tech-lead resolves from .agents/skills untrusted; a plugin skill is injected only as `$e-colleagues:<skill>` |
| `CX-08` | Codex CLI 0.167.0 (E34; first 0.153.4) | confirmed | runtime | E6, E34 | whole tree copied; .codex-plugin manifest adopted |
| `CX-09` | Codex CLI 0.153.4 | confirmed | docs/source only | — | — |
| `CX-10` | Codex CLI 0.167.0 (E34; first 0.153.4) | confirmed | runtime | E6, E34 | marketplace add + plugin add; source forms measured |
| `CX-11` | Codex CLI 0.167.0 (E34; first 0.153.4) | confirmed | runtime | E9, E34 | AGENTS.md reaches the primary and spawned children |
| `CX-12` | Codex CLI 0.153.4 | confirmed | docs/source only | — | — |

### opencode

| claim | last confirmed at | verdict | how | evidence | what was measured |
|---|---|---|---|---|---|
| `OC-01` | opencode 2.2.7 (E35; first 1.18.29) | confirmed | runtime | E20, E20 addendum, E25 addendum, E35 | project agents load from .opencode/agents; user agents load from the config home's opencode/agents (E25 addendum) |
| `OC-02` | opencode 2.2.7 (E35; first 1.18.29) | confirmed | runtime | E20, E20 addendum, E35 | permission edit:deny holds on a subagent; `task`/`subagent` and `bash`/`shell` both accepted, so the renderer emits both; a shell rule is matched per simple command and the last match decides (E35) |
| `OC-03` | opencode 2.2.7 (E35; first 1.18.29) | confirmed | **corrected** | E20, E20 addenda, E30, E35 | default_agent applies to opencode run and the TUI starts on it, again at 2.2.7 (E30); modes correct; `agent list` gone at 2.0.18, use `debug agents`; the TUI agent cycle is Shift+Tab, not Tab; at 2.2.7 the TUI command takes no `--agent`, which `run` and `mini` keep (E30) |
| `OC-04` | opencode 2.2.7 (E35; first 1.18.29) | confirmed | runtime | E20 TUI addendum, E35 | `@` offers the specialists and the built-ins; a mention reaches the primary, which delegated at 2.0.18 and answered itself at 2.2.7 (one run each) |
| `OC-05` | opencode 2.2.7 (E35; first 1.18.29) | confirmed | runtime | E20, E20 addendum, E35 | permission.task allowlist evaluated mechanically, as `subagent` at 2.0.18; nested spawns stopped by the depth limit |
| `OC-07` | opencode 2.2.7 (E35; first 1.18.29) | confirmed | **corrected** | E20, E20 addendum, E35 | at 2.2.7 a slash command in the run prompt is not expanded and the TUI expands it; the file form loads from command/ and commands/; run --command gone since 2.0.18 |
| `OC-08` | opencode 2.2.7 (E35; first 1.18.29) | refuted | runtime | E25 addendum, E35 | skills in the user skills directory are listed by the agent and run when asked for by name |
| `OC-09` | opencode 2.2.7 (E35; first 1.18.29) | refuted | runtime | E20, E20 addendum, E35 | AGENTS.md reaches a task child |
| `OC-10` | opencode 1.18.29 | refuted | docs/source only | — | — |
| `OC-11` | opencode 2.2.7 (E35; first 1.18.29) | confirmed | runtime | E25, E35 | the documented plugin shape is rejected; the v2 agent draft has no `add`, so a plugin cannot deliver agents; commands and skills it can |

### Antigravity

| claim | last confirmed at | verdict | how | evidence | what was measured |
|---|---|---|---|---|---|
| `AG-02` | agy 1.5.3 (E32; first 1.1.27) / desktop 2.17.0 (E24; first 2.12.2) | confirmed | **corrected** | E16, E19, E24, E32 | desktop lacked agents: at 2.12.2 and carries it at 2.17.0, and its 2.29.1 binary carries it too (inspected, not driven); body is not sliced at the first H1, again at 1.5.3 |
| `AG-03` | agy 1.5.3 (E32; first 1.1.27) / desktop 2.17.0 (E19 addendum) | confirmed | runtime | E19, E19 addendum, E32 | agy --agent runs a mainAgent persona, takes the frontmatter `name` and refuses a sub-agent or a directory name with `unknown agent`; `agy agents` lists mainAgent personas only; the desktop selector lists mainAgent personas and hides sub-agents (2.17.0, not re-verified) |
| `AG-04` | agy 1.5.3 (E32; first 1.1.27, docs only) / desktop 2.12.2 | confirmed | runtime | E32 | `invoke_subagent` addresses a sub-agent by `TypeName`; an agent with `subagent: false` is refused, `not found or not allowed to be invoked`; `Workspace` modes, the clean context and `define_subagent` still rest on documentation |
| `AG-05` | agy 1.5.3 (E32; first 1.1.27) / desktop 2.17.0 (E24; first 2.12.2) | confirmed | runtime | E19, E24, E19 addendum, E32 | a tools allowlist DOES override ambient subagent inheritance, on the CLI and on the desktop; at 1.5.3 it does NOT bound MCP tools — `call_mcp_tool` and an installed plugin's MCP tools reach the agent unless `inheritMcp: false` |
| `AG-06` | agy 1.5.3 (E32; first 1.1.27) / desktop 2.17.0 (E24; first 2.12.2) | confirmed | **corrected** | E17, E24, E32 | seven of the listed tool names were not in the registry up to 1.2.10; at 1.5.3 SIX are rejected (`command_status` resolves), and five that resolve — `grep_search`, `find_by_name`, `list_dir`, `multi_replace_file_content`, `read_url_content` — are logged `deprecated and has no effect` and give the agent no tool |
| `AG-07` | agy 1.5.3 (E32; first 1.1.27) / desktop 2.17.0 (E24; first 2.12.2) | confirmed | **corrected** | E7, E18, E24, E26, E32 | validate passes with the expected counts, printing `Validation passed` and no `[ok]` at 1.5.3; a missing or invalid `name` is a warning there, not an error, and tool names are not checked; a global install was the only route for agents up to 1.2.10 and is not at 1.5.3 (see AG-12) |
| `AG-08` | agy 1.5.3 (E32; first 1.1.27) / desktop 2.17.0 (E24; first 2.12.2) | confirmed | runtime | E8, E18, E24, E27, E32 | destination measured, named after the manifest's `name`, not the source folder (E32); re-install merged at 1.1.27 (E8) and replaces at 1.5.3 (marker test, E32); an install writes an entry to `import_manifest.json` and leaves `config.json` alone; `agy plugin uninstall` removes both the directory and the entry; github URL works at 1.5.3 and installs the clone's `.git/` too; `plugin@marketplace` was parsed at 1.2.10 with no marketplace known (E8 addendum 2) — at 1.5.3 one is known, `antigravity-plugins-official`, and the form was not re-run |
| `AG-10` | agy 1.5.3 (E32; first 1.1.27, docs only) / desktop 2.12.2 | confirmed | runtime | E32 | no placeholder is substituted: `$ARGUMENTS`, `$1` and `${CLAUDE_PLUGIN_ROOT}` reached the model literally in a skill the harness expanded; a `.agents/workflows/` file was not expanded in print mode; the deprecation is stated by the bundled `migrate-workflows` skill, the retirement date still rests on documentation |
| `AG-11` | agy 1.5.3 (E32; first 1.1.27) / desktop 2.17.0 (E24; first 2.12.2) | confirmed | runtime | E19, E24, E19 addendum, E32 | at 1.5.3 `AGENTS.md` and `GEMINI.md` DO reach the default agent, a custom agent and a sub-agent, walked from the working directory to the repository root, in print mode and interactively; `CLAUDE.md` does not. They reached no agy agent at 1.1.27 and 1.2.10 (E19, E24), nor the desktop at 2.17.0 (not re-verified) |
| `AG-12` | agy 1.5.3 (E32; first 1.1.27) / desktop 2.12.2 | confirmed | runtime | E18, E24, E32 | at 1.5.3 a workspace delivers agents from `.agents/agents/`, `_agents/agents/`, `.agents/plugins/` and `_agents/plugins/`, and a workspace definition beats a globally installed plugin agent of the same name — in print mode even in an untrusted folder; a workspace skill beats a plugin skill. No workspace root delivered agents at 1.1.27 and 1.2.10 (E18, E24) |

### Prior art

| claim | last confirmed at | verdict | how | evidence | what was measured |
|---|---|---|---|---|---|
| `PA-01` | n/a (public repos) | confirmed | docs/source only | — | — |
| `PA-02` | n/a (public repos) | refuted | docs/source only | — | — |

### Standards

| claim | last confirmed at | verdict | how | evidence | what was measured |
|---|---|---|---|---|---|
| `STD-01` | n/a (cross-tool) | confirmed | docs/source only | — | — |
| `STD-02` | n/a (cross-tool) | confirmed | docs/source only | — | — |
| `STD-03` | n/a (cross-tool) | confirmed | docs/source only | — | — |
## Not covered here

Four questions stay open and none is version-gated in a way this matrix can express:

- a user-scope versus project-scope `agent` key on Claude — needs a temporary edit to a user's own settings file
- the opencode Tab and `@` menus — needs the TUI
- the Antigravity **desktop's** subagent-inheritance default — needs the desktop app
- whether a **github**-sourced self-marketplace skips the install step the way a local one does (E23) — needs the repository published

## The claims themselves

Every claim id cited anywhere in this repository resolves here, so a citation never points outside it. Each is a fact about how a host actually loads agents, skills, plugins or instruction files, established from vendor documentation and source and then independently fact-checked. **Where a claim is marked refuted, the correction is the truth, not the claim.** And where an experiment in [`experiments.md`](experiments.md) contradicts a claim, the experiment wins — it ran against the installed binary.


### Claude Code

**`CC-02`** — `.claude-plugin/plugin.json` is optional (omitted → components auto-discovered, name derived from directory); if present the only required key is `name` (kebab-case). Component-path keys: `skills` ADDS to the default `skills/` scan, while `commands`, `agents`, `workflows`, `outputStyles` REPLACE the default directory …

**`CC-03`** — Plugin components are namespaced by plugin `name`: skills `/plugin-name:skill-name` (also bare `/skill-name` if no conflict), agents `plugin-name:agent-name`, and a subfolder under a plugin's `agents/` joins the id (`agents/review/security.md` → `my-plugin:review:security`; project/user `.claude/agents/` subfolders do …

**`CC-04`** — A marketplace is `.claude-plugin/marketplace.json` at the repo root with required `name`, `owner{name}`, `plugins[]` (each requires `name` + `source`). `source` may be a relative path string (`./plugins/x`, relative to the dir containing `.claude-plugin/`; `./` = the marketplace repo itself) or an object of kind …

**`CC-05`** — Third-party install is two steps: `/plugin marketplace add owner/repo` (also git URL, `git@host:path`, `owner/repo@ref`, `url#ref`, local path, or marketplace.json URL) then `/plugin install plugin@marketplace` (scope picker user/project/local). Non-interactive: `claude plugin marketplace add owner/repo [--scope …

**`CC-06`** — Project `.claude/settings.json` supports `extraKnownMarketplaces` (name → {source, autoUpdate?}) and `enabledPlugins` (`plugin@marketplace` → bool). Both are honored only after the user accepts the workspace-trust dialog for that folder (a `-p` run or trusting a parent does not count); the marketplace is then added … **E23 addendum (2.1.284)**: measured for the `github` source — trust registers the marketplace and fetches it under `~/.claude/plugins/marketplaces/`, and the plugin does not load until `claude plugin install`; nothing is printed to say so, so the "shown" install command is not shown.

**`CC-07`** — Plugin-shipped agents support `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`; 'For security reasons, plugin subagents don't support the hooks, mcpServers, or permissionMode frontmatter fields. These fields are ignored when loading agents … **E36 (2.1.325)**: measured at runtime — a plugin agent file whose frontmatter does not parse, in the default `agents/` folder or in the manifest's `agents` list, loads under its filename with its body kept and its `tools` line dropped, and has every tool a sub-agent can have, `Agent`, `Write` and `Edit` included; only the debug log says so, and the validator's "does not load at all" is wrong. A broken value containing a colon is repaired and keeps its `tools`. `memory` gives `Write` and `Edit` to an agent with a `tools` allowlist; beside a `disallowedTools` line naming them it does not, and a call is refused. `claude plugin validate` checks no tool name in `tools` or `disallowedTools`.

**`CC-08`** — A Claude Code subagent is a Markdown file with YAML frontmatter whose body is the system prompt. Locations by priority: managed settings > `--agents '<json>'` > `.claude/agents/` (project; every `.claude/agents/` from cwd up to the repo root is scanned) > `~/.claude/agents/` > plugin `agents/`. Required `name` …

**`CC-09`** — The delegation tool is `Agent` (renamed from `Task` in v2.1.63; `Task(...)` still aliases). In `tools`, `Agent(worker, researcher)` restricts spawnable types, but 'The Agent(agent_type) allowlist syntax applies only to an agent running as the main thread with claude --agent. In a subagent definition ... any type list … **E33 (2.1.325)**: in a sub-agent's `tools`, `mcp__<server>`, `mcp__<server>__*` and a full MCP tool name re-admit that server's tools; `mcp__*` and `mcp__*__*` give nothing, so no entry covers every server. With no `tools` key and the editing tools in `disallowedTools`, every MCP tool is reached through `ToolSearch`, and a call to `Write` or `Edit` is refused by the harness. **E36 (2.1.325)**: by the host's own record of each sub-agent's request, an agent whose `disallowedTools` names `Agent, Write, Edit, NotebookEdit, WebFetch, WebSearch` has, in the foreground, `Bash, ListAgents, Read, ReportFindings, ShareOnboardingGuide, Skill, ToolSearch` and, deferred, `CronCreate, CronDelete, CronList, DesignSync, EnterWorktree, ExitWorktree, Monitor, PushNotification, RemoteTrigger, SendMessage, TaskStop` and every MCP tool; launched with `run_in_background: true` it has `Bash, Read, Skill, ToolSearch` and, deferred, `EnterWorktree, ExitWorktree, Monitor, SendMessage, TaskStop` and the MCP tools. A call to a denied tool, `NotebookEdit` included, is refused with `No such tool available`. A name in `disallowedTools` that the version does not know is ignored silently and the other entries still apply. From a sub-agent `SendMessage` queues a prompt into the main conversation, `Monitor` runs a shell command, `TaskStop` stops only the agent's own tasks, and `EnterWorktree` and `ExitWorktree` are refused.

**`CC-10`** — `claude --agent <name>` runs the whole session as that agent: 'The subagent's system prompt replaces the default Claude Code system prompt entirely ... CLAUDE.md files and project memory still load.' Plugin agents work bare (`claude --agent security-reviewer`) or scoped (`claude --agent my-plugin:security-reviewer`). …

**`CC-11`** — Subagent nesting defaults to 3 layers below the main conversation (v2.1.219+; 2.1.217–218 defaulted to 1; 2.1.172–216 fixed at 5). `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=<n>` (settable in settings.json `env`; `1` disables nesting) and `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (default 20) control it; both names are …

**`CC-12`** — A non-fork subagent starts with: its own system prompt, the delegation message, 'every level of the CLAUDE.md hierarchy the main conversation loads, including ~/.claude/CLAUDE.md, project rules, CLAUDE.local.md, and managed policy files' (built-in Explore/Plan skip this), a git status snapshot, full content of …

**`CC-13`** — SKILL.md frontmatter in Claude Code: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation` (true = user-only `/name`), `user-invocable` (false = hidden from `/` menu), `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `background`, `hooks` …

**`CC-14`** — 'Claude Code reads CLAUDE.md, not AGENTS.md.' Load order: `/etc/claude-code/CLAUDE.md` → `~/.claude/CLAUDE.md` → `./CLAUDE.md` or `./.claude/CLAUDE.md` (and every ancestor, root-first) → `./CLAUDE.local.md`; subdirectory CLAUDE.md files load on demand. `@path` imports (relative to the containing file, or … **E24 (2.1.283)**: `AGENTS.md` is also read natively — its canary reached the model with no `CLAUDE.md` present, and with both files present the model reported it once. The import stays; it is no longer the only route.

**`CC-15`** — Claude Code does not read `.agents/skills`, `~/.agents/skills`, or any other agent's skill directory. skills.md (100 KB) contains zero occurrences of `.agents`; the 2.1.261 binary's strings contain `.claude/skills` 52 times and `.agents/` zero times (the 42 bare `.agents` hits are JS property accesses like … **E36 (2.1.325)**: measured — a project `.agents/skills/<name>/SKILL.md` is not in the session's skill list, with a `.claude/skills/` skill beside it as the control. The binary's strings are no longer free of `.agents/`: four lines carry `.agents/skills`, in what reads as the importer's code.

**`CC-16`** — `claude import [codex|gemini] [--dry-run] [--yes]` is documented to bring 'instruction files, MCP servers, commands, subagents, and skills' (v2.1.213+) and to append a one-time copy of AGENTS.md to CLAUDE.md. MEASURED on this machine with five Codex TOML agents in `~/.codex/agents/` and the skill …


### Codex CLI

**`CX-01`** — Codex custom agents are standalone TOML files, one per agent, at `~/.codex/agents/*.toml` (personal) or `<repo>/.codex/agents/*.toml` (project). The loader iterates `config_layer_stack.layers_low_to_high()` and calls `collect_agent_role_files(config_folder.join("agents"))`, which recursively collects and sorts … **E34 (0.167.0)**: user and project role files both load; the project scan is recursive (`agents/sub/deeper/x.toml` is found); the `name` key, not the file name, names the role; two files with one name in a layer give one warning and one role. A role can also be declared in a config layer as `[agents.<name>]` with `description` and `config_file`.

**`CX-02`** — A Codex agent file is parsed as `RawAgentRoleFileToml` with `#[serde(deny_unknown_fields)]`: `name`, `description`, `nickname_candidates`, plus a flattened `ConfigToml`, so any ordinary config.toml key is allowed (`developer_instructions`, `model`, `model_reasoning_effort`, `sandbox_mode`, `approval_policy` … **E33 (0.167.0)**: on the V2 multi-agent backend a spawned role's thread recorded its parent session's sandbox and approval policy, not the role file's `sandbox_mode` and `approval_policy`; its `developer_instructions` did arrive. A role with `read-only` + `never` wrote by shell and `apply_patch` under a `workspace-write` session. **E34 (0.167.0)**: the same on the V1 backend (a model catalogued `v1`): the child recorded its parent's sandbox and approval policy. The role file's `model` and `model_reasoning_effort` did reach the child. No role-file key (`sandbox_mode`, `default_permissions`, a `[permissions.<name>]` table), no `[agents.<name>]` declaration, no permission profile on the parent and neither feature flag tried gave a child a narrower sandbox than its session; a session started `read-only` bounds every role in it. A trusted `PreToolUse` hook receives the child's `agent_type` and can refuse its `apply_patch` and shell calls. An unknown key drops the role with a warning in the event stream; a role file without `developer_instructions` is dropped the same way.

**`CX-03`** **— refuted** — Codex merges roles layer by layer (user → profile → project, closest-to-cwd highest → CLI); a same-named role in a higher layer wins field-by-field via `merge_missing_role_fields`, so project `.codex/agents/X.toml` overrides `~/.codex/agents/X.toml` per field. Duplicate names inside one layer log 'duplicate agent role … **E34 (0.167.0)**: a complete project role file of the same name replaces the user-level role's description and body, silently; a project file without `description` keeps the user-level description, so that field merges; a project file without `developer_instructions` is rejected (`must define developer_instructions`) and the user-level role stays whole, so the body is never inherited. The session-only trust override of E29 is enough for project role files. `.codex/skills` loads untrusted as `.agents/skills` does.

> **The correction, which is the truth:** Five of the six sub-claims hold; the last one is half wrong. Project-scoped `.codex/agents/` IS gated on trust, but project-scoped `.codex/skills/` is NOT. Untrusted project layers are "loaded but disabled" and stay in the ConfigLayerStack; `load_agent_roles` iterates `layers_low_to_high()` (which filters `!layer.is_disabled()`), so an untrusted project's …

**`CX-04`** **— refuted** — `[agents]` keys (`AgentsToml`): `enabled` (default true), `max_concurrent_threads_per_session` (alias `max_threads`; V1 default 6, V2 default 4), `max_depth` ('Maximum nesting depth for V1 agent threads. Ignored by V2.', `DEFAULT_AGENT_MAX_DEPTH = 1`), `default_subagent_model`, `default_subagent_reasoning_effort` … **E34 (0.167.0)**: the backend follows the model's `multi_agent_version` in the catalog (`codex debug models`): `--enable multi_agent_v2` forces V2 on a `v1` model, `--disable multi_agent_v2` does not move a `v2` model, and `--disable multi_agent` left the V2 spawn tool in place. On V1 a spawned child had no spawn tool at the default `max_depth`; on V2 a child spawned a grandchild (`depth` 2).

> **The correction, which is the truth:** Everything about the `[agents]` schema, defaults, alias, doc comment and its absence from the online reference is accurate and verified at tag rust-v0.153.4 (the installed version — not 0.153.3, and the install is the standalone release under ~/.codex/packages/standalone/, not the npm layout cited). What is wrong is the conclusion. `codex features list` …

**`CX-05`** **— refuted** — Codex spawn tools in the binary: `spawn_agent`, `send_input`, `resume_agent`, `wait_agent`, `close_agent` (V1) plus V2 `send_message`, `followup_task`, `interrupt_agent`, `list_agents`. `spawn_agent` takes `agent_type` (omit → inherit parent type with full-history fork; otherwise `default`), `model` … **E24 (0.154.0)**: when no role is installed at any scope the spawn tool exposes no `agent_type` parameter, so the loud `unknown agent_type` error presupposes at least one role somewhere. **E34 (0.167.0)**: V2 delivers `spawn_agent`, `wait_agent`, `send_message`, `followup_task`, `interrupt_agent`, `list_agents` in a `collaboration` namespace; `spawn_agent` takes `agent_type`, `fork_turns`, `message`, `model`, `reasoning_effort`, `task_name` and nothing about a sandbox. V1 delivers `multi_agent_v1__spawn_agent`, `send_input`, `resume_agent`, `wait_agent`, `close_agent`. E24's no-role-anywhere nuance was not re-run.

> **The correction, which is the truth:** Most of the claim holds verbatim (tool names, V1 depth = session_depth+1 refused when depth > max_depth with that exact message, DEFAULT_AGENT_MAX_DEPTH = 1, the explicit-ask runtime prompt, `unknown agent_type '<name>'`). Two parts are wrong:

**`CX-06`** — A Codex custom agent cannot be the primary thread: `codex --help` and `codex exec --help` expose no `--agent`/role flag; app-server `ThreadStartParams` has no role field; TUI `/agent` (alias `/subagents`) only switches the viewed thread and sub-agent threads are read-only ('This sub-agent is controlled by its parent. … **E34 (0.167.0)**: `--profile` takes a plain name only (`invalid --profile value … pass a plain name such as work`), so the file must be in `$CODEX_HOME`. `codex debug prompt-input`, with `-p <name>` before `debug`, shows the layered `developer_instructions` with no model call. E22 was re-run with the session-only trust override, not the dialog.

**`CX-07`** — Codex skill roots (`host_roots.rs`): user layer `~/.codex/skills` (code comment: 'Deprecated user skills location ($CODEX_HOME/skills), kept for backward compatibility.'), then `~/.agents/skills`, then bundled `~/.codex/skills/.system`; project layer `<project>/.codex/skills` plus `.agents/skills` in every directory … **E34 (0.167.0)**: a skill delivered by the plugin is listed as `e-colleagues:<skill>`, and Codex injects its body for the mention `$e-colleagues:<skill>` only; the short `$<skill>` is injected for a project skill, not for a plugin skill (the model read the file itself in two bare runs of two). A mention is expanded into a `<skill>` user message carrying the file's path and text.

**`CX-08`** — A native Codex plugin cannot bundle agents: `PluginManifestPaths` carries exactly `skills`, `mcp_servers`, `apps`, `hooks` plus metadata/`interface`; the loader discovers `skills/`, `.mcp.json`, `.app.json`, `hooks/hooks.json` and migrated command skills, and 'No code loads agent roles, subagents, commands, or prompts …

**`CX-09`** — Codex plugin root holds `.codex-plugin/plugin.json` (`name` kebab-case equal to folder, `version` strict semver, `description`, `author.name`, optional `skills` './skills/', `mcpServers`, `apps`, `interface{...}`); the bundled validator rejects `hooks` in plugin.json. The binary also recognises …

**`CX-10`** — A Codex marketplace is JSON `{name, interface{displayName}, plugins:[{name, source, policy{installation, authentication}, category}]}`; source variants: bare path, `local` (path starts `./`, inside the marketplace root), `url`, `git-subdir`, `npm`. Recognised files: `.agents/plugins/marketplace.json` …

**`CX-11`** — Codex AGENTS.md discovery: global `~/.codex/AGENTS.override.md` then `~/.codex/AGENTS.md` ('only the first non-empty file'); then from the Git root down to cwd, per directory `AGENTS.override.md` → `AGENTS.md` → `project_doc_fallback_filenames`; files are concatenated root-down so closer files override; total capped … **E34 (0.167.0)**: the child's own thread record holds the `AGENTS.md` message and no tool call, so the canary was injected, not read. Root-down order, `AGENTS.override.md` over `AGENTS.md` in one directory, the 32 KiB tail cut and `project_doc_max_bytes` were measured with `codex debug prompt-input`. The global override file and `project_doc_fallback_filenames` were not.

**`CX-12`** — Codex has no user-defined slash commands (the `/...` list is fixed). The user-level equivalent is custom prompts: Markdown in `~/.codex/prompts/` with frontmatter `description:` / `argument-hint:`, invoked `/prompts:<name>`, placeholders `$1`–`$9`, `$ARGUMENTS`, named `$KEY` (passed as `KEY=value`), `$$` literal. …


### opencode

**`OC-01`** — opencode Markdown agents live in `~/.config/opencode/agents/*.md` (global) and `.opencode/agents/*.md` (project); the loader globs `{agent,agents}/**/*.md` in every config directory (plus legacy `{mode,modes}/*.md`, forced `mode: primary`), reads with `dot: true, symlink: true`, and names the agent by path relative to … **E35 (2.2.7)**: a project agent file, or a config `agent.<name>` entry, with the name of a user agent does not replace it; the two are merged: description, mode and body from the project file where it gives them, and the permission rules of the user file followed by the project's.

**`OC-02`** — opencode agent frontmatter keys (`KNOWN_KEYS`): `name`, `model`, `variant`, `prompt`, `description` (docs: required), `temperature`, `top_p`, `mode` (`subagent|primary|all`, default `all` for custom agents), `hidden`, `color`, `steps`, `maxSteps` (deprecated), `options`, `permission` (object keyed by tool: read, edit … **E20 addendum (2.0.18)**: the runtime reports `task` as `subagent` and `bash` as `shell`, accepts either spelling, and the published schema still lists only the old ones; unknown permission keys are schema-valid, so the renderer emits both and `check.py` requires the pair. **E35 (2.2.7)**: a `shell` pattern is matched against each simple command of a line with its redirections, `*` and `?` are the only wildcards, a trailing ` *` also matches the bare command, and the last matching rule decides.

**`OC-03`** — opencode selects the primary agent with `opencode --agent <name>` / `opencode run --agent <name>` or config `default_agent` ('Must be a primary agent. Falls back to build if not set or if the specified agent is invalid'; errors if hidden). In the TUI the keybinds are `agent_cycle` (default `tab`) … **E20 addendum (2.0.18)**: `opencode agent list` no longer exists; `opencode debug agents` lists agents with their modes. **E20 TUI addendum (2.0.18)**: the TUI starts on `default_agent`; the agent cycle is **Shift+Tab**, not Tab, and cycles primaries only. **E30 (opencode 2.2.7)**: `opencode --agent <name>` is refused, `Unrecognized flag: --agent in command opencode`; `opencode run` and `opencode mini` still list the flag; `default_agent` starts the TUI on the named agent, from a project config and from a file named in `$OPENCODE_CONFIG`, which is read by the server and not by the client.

**`OC-04`** — opencode subagents are invoked (1) by the model calling the built-in `task` tool with `description`, `prompt`, `subagent_type` (= agent name), optional `task_id`, `command`, `background` (needs `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`); the tool description appends 'Available agent types and the tools they … **E20 TUI addendum (2.0.18)**: `@` offers every specialist and the built-ins `general` and `explore` regardless of the allowlist; `@reviewer …` goes to the primary, which delegates through the task tool and relays the reply. **E35 (2.2.7)**: a mention reaches the primary with the mentioned agent recorded on the message; in the one run the primary answered itself and made no `subagent` call, so that it delegates is the primary's choice and not the host's. The tool a primary delegates with is named `subagent` at 2.2.7 and takes `agent`, `description` and `prompt`; it was `task` with `subagent_type`.

**`OC-05`** — On opencode, `permission.task` on the INVOKING agent is a map of agent-name glob patterns → allow|ask|deny (e.g. `{"*":"deny","orchestrator-*":"allow"}`), evaluated in insertion order, last match wins; `deny` removes the agent from the task tool description. The built-in `plan` agent carries `{permission: task … **E20 addendum (2.0.18)**: the runtime evaluates the key under the name `subagent` (`Permission denied: subagent`), and a child spawning a child is stopped by `subagent_depth` (default 1) rather than by a session-level deny.

**`OC-07`** — opencode command files: `.opencode/commands/<name>.md` and `~/.config/opencode/commands/<name>.md` (glob `{command,commands}/**/*.md`; nested → `a/b`); frontmatter `description`, `agent`, `model`, `variant`, `subtask`; body = `template`. JSON form: top-level `command` object, schema requires `template` … **E20 addendum (2.0.18)**: `run --command` is gone; a slash command in the `run` prompt expands, with `subtask: true` honoured. The file form loaded from `.opencode/command/` and not from `.opencode/commands/`, so the `{command,commands}` glob is at most half true there. **E35 (2.2.7)**: a slash command in the `opencode run` prompt is no longer expanded: in four runs of four the model received the slash text itself. The TUI expands a command, with `subtask: true` and `agent` honoured. The file form loads from `.opencode/commands/` and from `.opencode/command/` alike. The runtime's name for a command's `subtask` key is `subagent`.

**`OC-08`** **— refuted** — opencode skill sources, in order: per config dir `{skill,skills}/**/SKILL.md` (`.opencode/skills/` from cwd up to the worktree, `~/.config/opencode/skills/`, `~/.opencode/skills`, `$OPENCODE_CONFIG_DIR/skills`); external `.claude/skills/**` and `.agents/skills/**` walking cwd → worktree plus `~/.claude/skills/**` …

> **The correction, which is the truth:** Two concrete details are wrong; the rest holds. (1) SCAN ORDER is inverted: in v1.18.25 the external `.claude`/`.agents` scan runs FIRST (home dirs `~/.claude/skills`, `~/.agents/skills` with scope "global", then the cwd→worktree upward walk with scope "project"), THEN the config directories (`~/.config/opencode`, `.opencode` cwd→worktree, `~/.opencode` …

**`OC-09`** **— refuted** — opencode project rules: walking up from cwd to the git worktree, the FIRST directory holding one of `AGENTS.md`, `CLAUDE.md` (skipped if Claude compat disabled), `CONTEXT.md` (deprecated) wins — ancestors are not stacked; within a directory `AGENTS.md` beats `CLAUDE.md`. Global: `~/.config/opencode/AGENTS.md`, else …

> **The correction, which is the truth:** Most of the claim holds, but the core precedence statement is wrong in a way that matters for a package design. Precedence is per FILENAME across the whole cwd→worktree chain, not per directory, and ancestors ARE stacked for the winning filename. `FSUtil.findUp` (packages/core/src/fs-util.ts v1.18.25) walks every directory from cwd up to and including the …

**`OC-10`** **— refuted** — opencode config (`opencode.json`/`.jsonc`, `$schema https://opencode.ai/config.json`) is `mergeDeep`-ed, later wins: remote `.well-known/opencode` → global `~/.config/opencode/opencode.json(c)` → `$OPENCODE_CONFIG` → project `opencode.json(c)` (nearest wins) → each config directory [`~/.config/opencode`, every …

> **The correction, which is the truth:** The load order, mergeDeep semantics, `{env:}`/`{file:}` substitution, directory subfolder names and the generated-files side effect are all real, but two specifics are wrong. (1) It is NOT `bun install`: the installer is the `Npm` service in `packages/core/src/npm.ts`, which drives `@npmcli/arborist` and reads/writes `package-lock.json`. Locally …

**`OC-11`** — An opencode plugin is a JS/TS module (`(input, options?) => Promise<Hooks>`, type `Plugin` from `@opencode-ai/plugin`) loaded from `.opencode/plugin(s)/*.{ts,js}`, `~/.config/opencode/plugin(s)/`, or `plugin` array entries (npm spec, `./local.ts`, `file:///...`, `[name, {options}]`); `opencode plugin <module> [-g] … **E25 (2.0.18)**: the runtime rejects that shape (`Plugin must export a default definition with an id and an effect or setup function`) and loads `export default { id, setup(ctx) }`; `ctx.agent.transform` offers `list`, `get`, `default`, `update`, `remove` and no `add`, so a plugin cannot deliver agents, while the `command` and `skill` drafts have `add`.


### Antigravity

**`AG-02`** — Antigravity `agent.md` = YAML frontmatter + Markdown body (the system prompt). Documented fields: `name` (required), `description` (required), `tools` string[] default [], `mainAgent` bool default true, `subagent` bool default true, `model` `inherit|flash|pro` default inherit, `commandExecutionPolicy` … **E24**: desktop 2.17.0 carries the `agents:` tag; the CLI/desktop divergence E16 measured at 2.12.2 is gone.

**`AG-03`** — An Antigravity custom agent runs as PRIMARY when `mainAgent` is true (default): 'If true, allows selection as the primary agent in chat interfaces.' CLI: `agy --agent <name>` (help: 'Agent for the current CLI session'; added in 1.1.1 with the `agent/agents` subcommand), value = frontmatter `name`; or the `/agents` … **E19 addendum (desktop 2.17.0)**: the desktop's agent selector lists the `mainAgent` personas and hides the sub-agents.

**`AG-04`** — Antigravity delegation: 'The parent agent calls the invoke_subagent tool', addressing by name via `TypeName` with `Workspace` of `inherit`, `branch` (isolated git worktree) or `share`. Only agents with `subagent: true` are invocable (1.1.4 fix). Subagents start with a clean context. `define_subagent` creates transient … **E32 (agy 1.5.3)**: measured — the call carries `TypeName`, and an agent with `subagent: false` is refused with `not found or not allowed to be invoked`.

**`AG-05`** — Since 1.1.25 Markdown-defined Antigravity agents 'inherit ambient skills, rules, and subagents by default, matching the configuration of default agents.' Scoping knobs: `inheritCustomizations` (1.1.14: one switch for skills, rules, plugins, subagents and MCP servers), a `rules:` list (1.1.15: named rule files always … **E19 addendum (desktop 2.17.0)**: the explicit `tools` list holds on the desktop too — the reviewer reports no `invoke_subagent`. **E32 (agy 1.5.3)**: the list is not the whole tool surface — `manage_task`, `call_mcp_tool`, `list_resources`, `read_resource` and an installed plugin's MCP tools reach an agent that never named them; `inheritMcp: false` removes the MCP tools, `inheritCustomizations: false` removes the workspace rules.

**`AG-06`** — Antigravity `tools` is an explicit allowlist ('e.g. view_file, replace_file_content, grep_search, run_command'; the blog also lists `manage_task`), with the warning 'Specifying an unmapped or misspelled tool name in the tools list may cause the subagent process to hang'. Tool names present in the binary include … **E32 (agy 1.5.3)**: six names are rejected, five resolve with no effect, and an omitted `tools` key gives a default set (`send_message`, `read_file`, `search_web`, `schedule`, `generate_image`), not no tools.

**`AG-07`** — An Antigravity plugin is `plugins/<plugin_name>/` with a ROOT `plugin.json` (required; binary errors 'missing plugin.json', 'plugin.json missing name', 'invalid plugin name: %q'; CLI docs: `name` matching `^[a-zA-Z0-9-_]+$`, optional `description`, `$schema https://antigravity.google/schemas/v1/plugin.json`; general … **E32 (agy 1.5.3)**: `validate` reports a missing manifest as `no plugin.json found at the plugin root or in .antigravity-plugin or .gemini-plugin`; a missing or non-kebab `name` is a warning, and `plugin install` names the destination after the manifest's `name`.

**`AG-08`** — Antigravity plugin roots: workspace `.agents/plugins/` or `_agents/plugins/`; global `~/.gemini/config/plugins/` (9 Google plugins live there on this machine). Enablement is recorded in `~/.gemini/config/config.json` under `plugins: {<dirname>: {enabled: true}}`, keyed by DIRECTORY name, and 'config.json wins wherever … **E8 addendum 2 (agy 1.2.10)**: `install <plugin>@<marketplace>` is parsed and `link <mp> <target>` exists, but both need a marketplace agy already knows — served from a remote catalog cache that was absent here — and nothing in the CLI or the config registers one. Not a delivery route. **E32 (agy 1.5.3)**: a marketplace is now known to the CLI (`antigravity-plugins-official`, the `Source:` of 13 installed plugins) and the help reads `plugin[@marketplace]`; the form was not re-run. An install records itself in `~/.gemini/config/import_manifest.json`, not in `config.json`.

**`AG-10`** — 'Workflows are deprecated and will be retired on November 1, 2026.' Legacy locations: workspace `.agents/workflows/<name>.md` (also `_agents/`, `.agent/`, `_agent/`), global `~/.gemini/config/workflows/*.md`, `~/.gemini/config/global_workflows/*.md`, `workflows.json`; invoked `/<name>`; 12,000-char limit. Replacement … **E32 (agy 1.5.3)**: no placeholder substitution, measured; a workspace workflow file was not expanded in print mode.

**`AG-11`** — Antigravity reads `AGENTS.md` and `GEMINI.md` as directory-scoped rules: 'The system walks up from the current working directory to the repository root and loads these files. They apply to the directory they reside in and all its subdirectories'; they 'do not support frontmatter and are always active'. Discovery … **E32 (agy 1.5.3)**: this is what the CLI does at 1.5.3, for the default agent, a custom agent and a sub-agent; `CLAUDE.md` is not read.

**`AG-12`** — Antigravity customization priority, highest first: 1. workspace project (hierarchical from cwd to repo root); 2. declared configurations (`skills.json` / `plugins.json` in the workspace); 3. global discovery `~/.gemini/config/`; 4. built-ins (mounted by name); 5. global declared configurations. 'If there are naming … **E32 (agy 1.5.3)**: rank 1 over rank 3 holds for agents and for skills.


### Prior art

**`PA-01`** — Repos that are simultaneously a Claude Code, Codex and Antigravity plugin exist: litestar-org/litestar-skills, evanca/flutter-ai-rules and nagisanzenin/omniplugin each carry a root `plugin.json` (`$schema https://antigravity.google/schemas/v1/plugin.json`), `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` and …

**`PA-02`** **— refuted** — litestar-skills keeps a canonical `agents/litestar-reviewer.md` in Antigravity tool vocabulary (`tools: [view_file, grep_search, find_by_name, run_command]`), exposed by the root Antigravity `plugin.json`; its `.claude-plugin/plugin.json` sets `"agents": ["./.claude-plugin/agents/litestar-reviewer.md"]` pointing at a …

> **The correction, which is the truth:** Most of the file-level facts are accurate, but the framing of the "canonical source" and the README quote are wrong. (1) `agents/litestar-reviewer.md` is NOT the canonical source — it is one of four GENERATED outputs. The canonical source is `tools/agent-sources/litestar-reviewer.yaml`, which uses host-neutral tool names (`read`, `grep`, `glob`, `bash`) …


### Cross-tool standards

**`STD-01`** — The Agent Skills spec (agentskills.io) defines a skill as a directory with SKILL.md: frontmatter `name` (REQUIRED; 1-64 chars; a-z, 0-9, hyphen; no leading/trailing/consecutive hyphens; 'Must match the parent directory name'), `description` (REQUIRED; 1-1024 chars), optional `license`, `compatibility` (1-500 chars) …

**`STD-02`** — No cross-tool agent/persona definition standard exists. agentskills.io, its GitHub, ACP, MCP and agents.md define none: agentskills Discussion #179 'AgentFile' (Feb 2026) is a proposal with one 'too early' reply; agentrc.ai 'Agentfile' is a single-author 'Working Draft 0.1.0-draft.6' with no tool adoption; ACP 'does …

**`STD-03`** — `.agents/skills` is read by Codex (cwd up to repo root, then `~/.agents/skills`), opencode (project walk to worktree plus `~/.agents/skills`), Antigravity 2.0 + CLI (`<workspace>/.agents/skills/<name>/SKILL.md`, also `_agents/skills`, legacy `.agent/skills`; global `~/.gemini/config/skills/`) and Gemini CLI …

