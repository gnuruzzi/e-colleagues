# e-colleagues — design

Targets: Claude Code, OpenAI Codex CLI, opencode, Google Antigravity (the `agy` CLI and the Antigravity desktop share one config root `~/.gemini/config/`; they no longer share one engine in every detail — the `agents:` frontmatter key exists in agy 1.1.27 and not in desktop 2.12.2, `experiments.md` E16).

| tool | researched at | installed 2026-09-07 |
|---|---|---|
| Claude Code | 2.1.261 | 2.1.263 |
| Codex CLI | 0.153.4 | 0.153.4 |
| opencode | 1.18.25 | 1.18.29 |
| agy | 1.1.26 | **1.1.27** |
| Antigravity desktop | 2.11.0 | **2.12.2** |

Four of the five moved within a day of the research, and one version gate has already flipped: AG-02 records that the Antigravity `agents:` frontmatter list is 1.1.27+ and absent from the installed binary — on 1.1.27 `strings /usr/bin/agy | grep -c 'yaml:"agents'` returns 1. The sweep re-verified every version-gated claim (`experiments.md` E16): the agy tool list is valid at 1.1.27, the opencode published schema is unchanged at 1.18.29, and the desktop diverges from the CLI on `agents:` alone.

Every path, key, flag and command below carries the id of the fact-checked claim it rests on. Each id is stated in full in [`SUPPORT-MATRIX.md`](SUPPORT-MATRIX.md) — for a claim marked refuted, the correction is the truth. Anything the research could not settle is marked UNVERIFIED, and where an experiment in [`experiments.md`](experiments.md) contradicts a claim, the experiment wins.

---

## 0. Decisions of record

Each is binding. Changing one is a design change: update this table and everything downstream of it in the same commit.

| # | decision | consequence |
|---|---|---|
| D1 | **Name is `e-colleagues`** — repo directory, `plugin.json` `name`, Claude namespace, marketplace id, all identical | Antigravity keys plugin enablement by directory name [AG-07][AG-08]; Claude namespaces skills as `<plugin>:<skill>` [CC-03]; kebab-case satisfies the Claude marketplace and Codex's `[A-Za-z0-9_-]+` [CC-02][CX-09] |
| D2 | **Codex first, then port** | Codex is the tightest host: a plugin cannot carry agents [CX-08] and a custom agent can never be primary [CX-06]. Designing against it made the port downhill |
| D3 | **Roster is a catalog with a default of six** — tech-lead, developer, reviewer, security, designer, **platform** (new) | `ec-init` proposes the per-project roster from what the codebase justifies; the user approves it. The roster is a variable, so the managed block, the delegation surface and opencode's `permission.task` must stay consistent with it [OC-03][OC-07] |
| D4 | **Contract + index + multi-angle audit**, with knowledge in a layered store | `AGENTS.md` stays small; deep knowledge lives outside it; the audit indexes the project's own docs first and only authors a file where the project has no home for that lens |
| D5 | **Every knowledge file records provenance** (commit sha + paths read) | Staleness detection becomes a `git diff`, so the living-knowledge upgrade is additive rather than a redesign |
| D6 | **The tech-lead is the only external voice.** Specialists never post; they return structured findings the lead posts verbatim | Read-only specialists need no network, so Codex's `read-only` sandbox is strict *and* usable; Claude's allowlist stripping MCP [CC-09] stops mattering; no specialist needs platform credentials. Retires Q14 |
| D7 | **Portable floor is the tech-lead only.** Specialists ship as native agents exclusively | A skill cannot restrict tools portably, so a skill-adopted reviewer would run in a thread that can write — the exact fail-open the redesign exists to remove |
| D8 | **The repository is public and self-contained; the evidence ships, the raw research does not** | Superseded on publication. D8 originally kept the sanitized research in-tree; it was removed before going public — 4.7 MB of vendored third-party documentation and the previous package's prompts — so what ships is the *evidence*: `experiments.md` (23 experiments run against the installed tools) and `SUPPORT-MATRIX.md`, which now states all 52 claims in full so every citation resolves inside the repository. No claim id points outward |

Per-directory `AGENTS.md` knowledge files (the one mechanically-injected option, [CX-11][OC-09][AG-11][CC-14]) are permitted as a project override but are never the architecture: they only carry directory-local knowledge, and what the team needs is cross-cutting.

---

## 1. Summary

- One git repository is simultaneously a Claude Code plugin and its own marketplace, a Codex plugin and its own marketplace, and an Antigravity plugin. The three manifests live at paths proven to coexist in public repos [PA-01]; §6 explains why Codex tolerates the Antigravity manifest at the root.
- A persona is authored once as host-neutral YAML plus a Markdown prompt. A generator renders each host's dialect and commits it behind a CI drift gate. No cross-tool persona format exists, so this is the only way to avoid tool-vocabulary drift [STD-02][PA-02].
- Skills are the one artifact all four tools ingest, so every command is a skill. Codex, opencode and Antigravity read `.agents/skills`; Claude Code does not and gets skills through the plugin [STD-03][CC-15].
- **Each persona has two jobs**: a delegation role (who does the work) and an audit lens (which angle it learns the project from). Six personas, six lenses.
- **`ec-init` owns the contract; `ec-onboard` owns the knowledge.** The contract comes from an interview, because only a human knows the board, the labels and who may merge. The knowledge comes from an audit, because it is derivable from the repository.
- The tech-lead is primary by mechanism on Claude, opencode and Antigravity, and by `developer_instructions` on Codex, where a custom agent can never be primary [CX-06].
- "Must not edit" is mechanical for editor tools on all four hosts, and for the shell only on Codex when the role sets both `sandbox_mode = "read-only"` and `approval_policy = "never"` [CX-02]. Elsewhere the shell stays a prose-governed write path, narrowed on opencode by `bash` pattern rules.
- The team is flat by default, but honestly so: opencode enforces it alone (children get `task * deny`) [OC-05]; Claude through generated tool lists [CC-09]; Codex only on the V1 backend, and V1 versus V2 is chosen per model [CX-04][CX-05]; Antigravity through an explicit `tools` list, which **does** override ambient subagent inheritance (E19) [AG-05][AG-06].
- The lead never assumes knowledge arrives ambiently. **Every delegation brief names the knowledge files the child must read** — which makes the store work identically on all four hosts with nothing left to verify.

---

## 2. The team

### 2.1 Roster and lenses

| persona | delegation role | audit lens | writes knowledge |
|---|---|---|---|
| **tech-lead** | primary; plans, delegates, verifies; owns AGENTS.md and the index; the only voice to the user and the only external poster | `architecture` — module boundaries, data flow, cross-cutting decisions | yes |
| **developer** | implements, writes tests | `build-and-test` — what the build and test commands actually do, not what the README claims | yes |
| **reviewer** | read-only adversarial review | `standards-and-coverage` — coverage reality, standards as practised versus documented | yes |
| **security** | read-only audit | `security-posture` — dependency and CVE exposure, secrets handling, attack surface | yes |
| **designer** | UI/UX, implementation-ready specs | `design-system` — tokens, components, accessibility conventions | yes |
| **platform** | CI/CD, deploy, infrastructure | `ci-cd-and-infra` — pipelines, environments, observability | yes |

`platform` is new in revision 3. It closes the one lens that is present in virtually every real repository and was owned by nobody in the five-persona team.

`designer` is dropped from projects with no user interface. That is the roster mechanism at work, not a special case.

### 2.2 The catalog and profiles

`team.yaml` holds the catalog (all six, plus anything a domain pack adds), named profiles, the signature table and the package version:

```yaml
version: 0.1.0
name_prefix: ""            # "ec-" for user-scope installs on machines that already have a `reviewer`
catalog: [tech-lead, developer, reviewer, security, designer, platform]
profiles:
  default: [tech-lead, developer, reviewer, security, designer, platform]
  minimal: [tech-lead, developer, reviewer]
  library: [tech-lead, developer, reviewer, security, platform]   # no UI
signatures:
  tech-lead: "👨‍💻 Tech-Lead: "
  developer: "🛠️ Developer: "
  reviewer:  "🕵️ Reviewer: "
  security:  "🛡️ Security: "
  designer:  "🎨 Designer: "
  platform:  "⚙️ Platform: "
```

`ec-init` proposes a roster from evidence in the repository — a UI framework in the manifests argues for `designer`, a CI configuration for `platform` — and the user approves it. The chosen roster is recorded in `.e-colleagues/lock.json` and rendered into the managed block, the delegation surface of the lead's body, and opencode's `permission.task` allowlist. `--prune` rewrites all three in one transaction, because a dangling opencode agent reference is a hard config error for every opencode user in the repository [OC-03][OC-07]. On Antigravity `--prune` must also **delete** the dropped persona's file: `agy plugin install` merges into the existing directory rather than replacing it, so a removed agent survives an upgrade and stays selectable (`experiments.md` E8).

---

## 3. Source of truth and the generator

```yaml
# personas/reviewer.yaml
name: reviewer                 # kebab-case, no ':' [CC-03]; never default|worker|explorer (Codex built-ins)
display: Reviewer
signature: "🕵️ Reviewer: "
role: specialist               # primary | specialist
description: >-                # the ONE routing sentence every host uses to decide when to delegate here
  Use for adversarial review of an in-review change: edge cases, races, leaks, coverage.
  Do not use to implement fixes.
capabilities:
  edit: false
  shell: true                  # may run the project's test/lint commands
  web: false
  delegate: []                 # persona names this one may spawn; [] = leaf
external_post: false           # true only for tech-lead (D6)
lens:
  name: standards-and-coverage
  paths_hint: [test/, "**/*Test.*", .editorconfig, "**/lint*", "**/*.pre-commit-config.yaml"]
  writes_knowledge: true
model: inherit
prompt: prompts/reviewer.md
```

A tool's vocabulary never appears in `personas/`. Claude's `Read, Edit` copied into opencode fails the schema or vanishes into `options` [OC-02], and an unknown name in an Antigravity `tools` list kills the agent at startup [AG-06]. The mapping lives in `hosts/<tool>.yaml`:

| capability | Claude [CC-07][CC-09] | opencode `permission` [OC-02][OC-05] | Antigravity `tools` [AG-06] | Codex [CX-02] |
|---|---|---|---|---|
| read | `Read` | `read: allow` | `view_file` | n/a (sandbox governs) |
| search | `Grep, Glob` | `grep, glob, list` | `grep_search, find_by_name, list_dir` | n/a |
| shell | `Bash` | `bash` (pattern rules for read-only personas) | `run_command` | n/a |
| web | `WebFetch, WebSearch` | `webfetch, websearch` | `read_url_content, search_web` | n/a |
| edit: true | no `tools` key (inherit) | `edit: allow` | `write_to_file, replace_file_content, multi_replace_file_content` | `sandbox_mode = "workspace-write"` |
| edit: false | `tools: Read, Grep, Glob, Bash` allowlist | `edit: deny` | the list above minus the three write tools | `sandbox_mode = "read-only"` **and** `approval_policy = "never"` |
| delegate: [] | `disallowedTools: Agent` (edit: true) or `Agent` absent from the allowlist (edit: false) | child gets `task * deny` automatically | `tools` without `invoke_subagent`, `define_subagent` — **mechanical**: a specialist so rendered reports the tool unavailable and cannot reach a sibling (Q8 settled, E19) | prose; V1 depth cap only |
| delegate: [...] | no `tools` key; built-ins denied via project `permissions.deny` (§8) | `task: {"*": deny, "<name>": allow, …}` | `invoke_subagent` in `tools` | prose only [CX-05] |
| external_post: false | nothing to grant — no MCP, no platform CLI in the brief | — | — | `read-only` already blocks network |

**The Antigravity names above are the measured registry, not AG-06's list.** Seven names AG-06 gives — `view_file_outline`, `view_code_item`, `command_status`, `codebase_search`, `browser_subagent`, `notify_user`, `manage_inbox` — are **not in the registry** at agy 1.1.27 and abort the agent at executor construction with `unknown component: tool "<name>" not found in registry` (`experiments.md` E17). The full valid set is `view_file`, `run_command`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`, `grep_search`, `find_by_name`, `list_dir`, `read_url_content`, `search_web`, `invoke_subagent`, `define_subagent`, `manage_task`, `manage_subagents`, `send_message`. Membership must be re-derived by running one agent per name at each supported agy version; grepping the binary's strings yields a superset and is not a validity test.

`sandbox_mode` is always written on Codex, because an omitted key inherits the session sandbox [CX-02]. `approval_policy = "never"` is mandatory for every read-only role: under the default `on-request` the model may obtain an approved escalation that runs outside the sandbox [CX-02].

`tools/gen.py` renders, per persona and profile:

- **Codex** `dist/codex/agents/<name>.toml` for specialists: `name`, `description`, `sandbox_mode`, `approval_policy`, `developer_instructions` — five keys, no more. The file flattens the whole config schema, so any ordinary config key parses, but a key that is neither `name`/`description`/`nickname_candidates` nor a valid config key drops the entire agent with only a startup warning [CX-02]. For the tech-lead it renders `developer_instructions` into `dist/codex/config.snippet.toml` (the managed region for a project config) and `dist/codex/e-colleagues.config.toml` (the user profile) instead [CX-06].
- **Claude** `dist/claude/agents/<name>.md`: `name`, `description`, `model`, and either a `tools` allowlist (read-only personas) or `disallowedTools` (writers). The tech-lead carries **no** `tools` key, because an explicit allowlist removes every tool it does not name — all MCP tools, `Skill`, `AskUserQuestion`, `TodoWrite`, plan mode — and MCP can only be re-admitted per server name, which the package cannot know [CC-09]. Never `permissionMode`, `hooks` or `mcpServers` (silently ignored in plugin agents) and never `memory` on a read-only persona, which re-enables Write and Edit [CC-07].
- **opencode** `dist/opencode/agents/<name>.md`: `description`, `mode`, `permission`, `model`; no `name` key, since frontmatter `name` overrides the filename-derived one [OC-02]; body becomes `prompt`.
- **Antigravity** `agents/<name>/agent.md`: `name`, `description`, `mainAgent`, `subagent`, `model`, `commandExecutionPolicy: sandbox`, explicit `tools`; body uses H2 headings only, because bodies are described as H1-delimited and the slicing is UNVERIFIED [AG-02].
- **`skills/ec-tech-lead/SKILL.md`**: the tech-lead body as a portable skill, frontmatter `name`, `description`, `metadata` only [STD-01].

Every body is shared fragments + persona prompt + team table + a host-specific "Your runtime" appendix, and opens with a `generated from personas/<name>.yaml, do not edit` line. Generated files are committed, because Claude, Codex and Antigravity all copy the plugin directory on install and a consumer install must be a plain fetch with no build step [AG-08]. `tools/check.py --drift` regenerates into a temp directory and fails CI on any diff [PA-02].

---

## 4. The persona bodies

Every body follows one skeleton, in this order, with every section present so the renderer can rely on it and two personas can be diffed.

**1. Position in the tree.** "You were spawned by the Tech-Lead (Tech-Lead: you are started by the user). You report to whoever spawned you, by ending with the RETURN block. You do not initiate contact with the user (Tech-Lead exempt); if the user speaks to you directly in your thread, answer briefly and still end with the RETURN block. You never contact a sibling or ask another colleague to do something; if the Developer needs the Designer's spec, say so under follow-ups and let your spawner delegate. On the Codex V2 backend you may see the whole parent conversation; act only on the delegation brief."

Every runtime is a tree: Claude returns only the subagent's final text to the spawner [CC-11]; Codex children are threads controlled by the parent, read-only to the user on V2 and typeable on V1 [CX-06]; opencode children get `task * deny` [OC-05]; Antigravity children start with a clean context [AG-04].

**2. Operating rules**, numbered and testable.

- **R1** Read the contract (`AGENTS.md`) if it is not already in context, and read every knowledge file the brief names.
- **R2** Scope: do exactly the delegated task. Stop at the acceptance criteria or at the first blocker. Never widen scope, never start a competing branch.
- **R3** Evidence: "passes", "done" and "fixed" must carry the command and its exit code or output excerpt. No evidence, no claim.
- **R4** Side effects, per persona. Reviewer and Security: you may read anything and run the test, lint, build and scanner commands named in `AGENTS.md`; you may not create, modify or delete any file by any means, including `sed -i`, shell redirection, formatters with write flags, `git commit` and `git stash`. If a tool lets you, the rule still stands.
- **R5** **You never post to an external platform.** Return findings; the Tech-Lead posts them. (D6 — this inverts the rule in the pre-revision-3 prompts.)
- **R6** Restricted actions — push, merge, tag, close, bulk-triage — only if `AGENTS.md` grants them to your role.

**3. The RETURN contract**, verbatim at the end of every specialist's output, with findings structured so the lead can relay them without loss:

```
### RETURN
status: done | partial | blocked | needs-decision
task: <reference as delegated>
changed: <files, branch, MR/issue refs, or none>
evidence: <commands run, exit codes, output excerpts>
findings:
  - severity: blocking | nit
    path: <file, or "-" for a whole-change finding>
    line: <number, or "-">
    body: <the comment, written to be posted verbatim>
risks: <unresolved>
follow-ups: <suggested delegations for the Tech-Lead>
questions: <decisions only the user can take>
knowledge: <lens file this run would add or change, or none>
```

No host enforces this mechanically; it is prompt-level, and `check.py`'s persona lint asserts only that the block is present verbatim in every specialist body.

**4. The lens section.** What this persona learns about a project, its `paths_hint`, and the authoring rule: *index the project's own documentation first; author a knowledge file only for a lens the project has no home for; never restate what the project already documents.*

**5. Tech-lead rules** (T-series, in addition to R1–R6).

- **T1** Propose freely; obtain the user's explicit approval before any structural or strategic change, before writing `AGENTS.md`, and before any restricted action.
- **T2** Every delegation uses the delegation brief: persona, task, acceptance criteria, work-item or change-request reference, constraints, **the knowledge files to read**, context files, "read AGENTS.md first", "end with the RETURN block". The brief deliberately contains the words "spawn a sub-agent", because Codex spawns only on an explicit ask [CX-05], and it names no spawn parameters, because V1 and V2 signatures differ [CX-04][CX-05].
- **T3** Delegate only to the named colleagues, never to a built-in type (Explore, Plan, general-purpose; default, worker, explorer; build, plan, general; research, browser, self). If the host refuses the spawn, say so and do the work yourself. **Never adopt a read-only persona's identity in a thread that can write.**
- **T4** Report a change as done only after a Reviewer RETURN with no blocking findings, plus a Security RETURN for security-relevant changes.
- **T5** You are the only voice to the user. Relay RETURN blocks as a signed summary; never paste one raw.
- **T6** You are the only external poster. Post each finding **verbatim** under the originating persona's signature (`🕵️ Reviewer: …`); your own words carry your own signature. Post only where `AGENTS.md` says, using only the tools it names. If it names none, stop and ask.

**6. Self-sufficiency on Claude.** `claude --agent` replaces the entire built-in system prompt [CC-10], so the tech-lead body carries a short tool-conduct section that the other hosts treat as harmless reinforcement.

**7. The host appendix**, generated: how to address the team on this host — Claude "the `Agent` tool with `subagent_type` one of {{names}}" — **qualified as `e-colleagues:<name>`, because bare names do not resolve there** (E10; the earlier note claiming the opposite was wrong) [CC-09][CC-03]; Codex "spawn a sub-agent with `agent_type` exactly one of …; the runtime refuses unknown types" [CX-05]; opencode "`task` with `subagent_type` …" [OC-04][OC-05]; Antigravity "`invoke_subagent` with `TypeName` …" [AG-04]. Specialists are told they have no spawn tool on this host.

Descriptions are routing sentences ("Use for …; do not use for …") because every host uses `description` to decide delegation [CC-08][CX-02][OC-04][AG-02]. The signature table is generated from `team.yaml`, so signatures cannot diverge between a body, the managed block and the index.

---

## 5. The knowledge architecture

### 5.1 Three regions in AGENTS.md, three owners

The whole block sits directly after the H1, because Codex truncates the **tail** once `project_doc_max_bytes` (default 32768) is spent [CX-11] and the spawn sentence is load-bearing [CX-05].

```markdown
# AGENTS.md — <project>

<!-- e-colleagues:begin v=0.1.0 profile=default -->        package-owned; rewritten on update
## E-Colleagues
| Colleague | Signature | Spawn name |
| Tech-Lead | `👨‍💻 Tech-Lead:` | (primary) |
| Developer | `🛠️ Developer:` | developer |
| …
The Tech-Lead delegates by spawning sub-agents of exactly these types: developer, reviewer,
security, designer, platform. Specialists never spawn.
Specialists never post externally: findings return to the Tech-Lead, who posts them.
If no Tech-Lead persona is active in this session, invoke the `ec-tech-lead` skill first.
<!-- e-colleagues:index -->                                audit-owned; rewritten by an audit
| lens | where it lives | derived from |
| architecture | docs/adr/ (project's own) | — |
| ci-cd-and-infra | .e-colleagues/knowledge/ci-cd-and-infra.md | a3f91e2 · 2026-09-07 |
<!-- e-colleagues:project-bindings -->                     the team's; never touched by an update
### Platforms and tools
### Workflow and permissions
<!-- e-colleagues:end -->
```

The spawn sentence names personas, not host syntax. **Claude needs the qualified form** `e-colleagues:<name>` — bare `subagent_type` names do not resolve (`experiments.md` E10) — so the qualification is applied by the Claude renderer in `hosts/claude.yaml` and appears in the Claude tech-lead's own body, not in this host-neutral block. Codex takes the bare names as written (E5).

Budgets: the package-owned region stays under 2 KB; the index grows one row per lens; `bootstrap.py --check` **fails** (not warns) when total `AGENTS.md` exceeds 30 KiB, because the bump to 65536 lives in the trust-gated project config [CX-11][CX-03] and an untrusted teammate never gets it. Antigravity's 12,000-character limit is printed as a caution only: it is documented for `.agents/rules/*.md` and its application to `AGENTS.md` is UNVERIFIED [AG-11].

`AGENTS.md` is read natively by Codex [CX-11], opencode [OC-09] and Antigravity [AG-11]; Claude gets it through a two-line `CLAUDE.md` containing `@AGENTS.md` [CC-14]. Never run `/import codex` in a bootstrapped repository: it appends a copy of AGENTS.md into CLAUDE.md [CC-14][CC-16].

### 5.2 The store

```
.e-colleagues/
├─ knowledge/<lens>.md        one file per lens that needed authoring
└─ lock.json                  package version, roster, sha256 per written file, completed lenses
```

One directory, one line of root-level footprint. `ec-init` offers to place the store wherever the project already keeps documentation instead; the default never colonizes `docs/`.

Provenance frontmatter is what makes the rest cheap:

```yaml
---
lens: ci-cd-and-infra
persona: platform
derived_from:
  commit: a3f91e2
  paths: [.gitlab-ci.yml, gradle/, Makefile]
  at: 2026-09-07
package_version: 0.1.0
confidence: high
---
```

So **staleness detection is a `git diff`, not a feature**: `git diff --name-only a3f91e2..HEAD -- <recorded paths>`. A non-empty result marks that lens stale. `ec-status` ships this in v1; automatic refresh comes later and needs no new metadata. Inside a file, every non-obvious claim cites the path it came from — the same discipline as this project's own claim ids.

### 5.3 Two skills, two jobs

**`ec-init` owns the contract.** The contract is interview-derived, because only a human knows the board, the labels, the branching rule and who may merge or tag. It writes the managed block, the project-bindings scaffold, the per-tool drop-ins and the lock.

**`ec-onboard` owns the knowledge.** The knowledge is repository-derived, so it is audited, not asked.

1. Inventory, read-only: stack, manifests, CI configuration, test layout, directory shape.
2. **Index what already exists first** — README, `docs/`, ADRs, CONTRIBUTING, an existing `AGENTS.md` — and map each lens to its existing home.
3. Present the gap list *and* the proposed roster together. The user approves both.
4. Dispatch one specialist per gap lens, **in waves sized to the host's concurrency ceiling**. On the Codex V2 backend `max_concurrent_threads_per_session` counts the primary, so the default 4 permits three spawned agents [CX-04]: six lenses is two waves. Measured (Q16, `experiments.md` E11): three concurrent children exactly, and a fourth **fails** with `collab spawn failed: agent thread limit reached` rather than queueing — so the skill must batch explicitly and treat that error as a wave boundary, not a lens failure. It should read `[agents] max_concurrent_threads_per_session` where set rather than hardcoding three.
5. The lead consolidates: writes only approved files, records provenance, updates the index and the lock.
6. Reports what was found, what was authored, what was left to the project's own docs, and what stayed uncertain.

`lock.json` records completed lenses, so an interrupted pass resumes rather than restarting.

### 5.4 The retrieval rule

Ambient injection is trusted for the **contract only**. Claude subagents receive the whole CLAUDE.md hierarchy including the `@AGENTS.md` import [CC-12]; the Antigravity CLI inherits rules by default since 1.1.25 while the desktop default is UNVERIFIED [AG-05]; Codex children **do** re-run AGENTS.md discovery, independently of history forking (Q9 settled, E9); opencode task children **do** receive it (Q7 settled, E20); and on Antigravity **no agent receives it at all** — neither a custom agent nor the default one had the workspace `AGENTS.md` in context (Q8, E19), so Antigravity children start clean [AG-04] and so do Antigravity primaries.

Therefore **knowledge is never assumed to arrive ambiently**: the delegation brief names the files (T2). This is host-independent, works today, and leaves nothing to verify. It is now measured on all four hosts, and on Antigravity it is not a fallback but **the only mechanism** — since `AGENTS.md` never reaches an agy agent, the managed block is invisible there and the Antigravity persona bodies must carry the contract themselves (E19). R1 keeps "read the contract if it is not in context" as the belt-and-braces fallback.

---

## 6. Repository layout

```
e-colleagues/                          # dir name is load-bearing [AG-07][AG-08]
├── plugin.json                        # Antigravity manifest; root; regular file; name == directory name
├── .claude-plugin/
│   ├── plugin.json                    # Claude manifest: "agents" = explicit FILE list under ./dist/claude/agents/
│   └── marketplace.json               # self-marketplace: name, owner, description, version, plugins[0]{name, source:"./", version}
├── .codex-plugin/plugin.json          # Codex manifest: skills only; no agents key exists [CX-08][CX-09]
├── .agents/plugins/marketplace.json   # Codex marketplace, {source:"local", path:"./"}; read before .claude-plugin's [CX-10]
├── personas/                          # SOURCE OF TRUTH
│   ├── <name>.yaml                    # six personas
│   ├── prompts/<name>.md
│   └── _shared/{tree,rules,return,brief,lens}.md
├── hosts/{codex,claude,opencode,antigravity}.yaml
├── team.yaml
├── skills/
│   ├── ec-init/                       # contract: SKILL.md, references/, scripts/bootstrap.py
│   ├── ec-onboard/                    # knowledge: the multi-angle audit
│   ├── ec-onboard/                     # knowledge: SKILL.md, scripts/knowledge.py
│   ├── ec-status/                      # staleness: SKILL.md, scripts/status.py
│   ├── ec-review/  ec-audit/
│   └── ec-tech-lead/                  # GENERATED portable floor (D7)
├── agents/<name>/agent.md             # GENERATED Antigravity dialect
├── dist/                              # GENERATED, committed
│   ├── team.json                       # roster data for the stdlib-only bootstrap
│   ├── codex/agents/*.toml, config.snippet.toml, e-colleagues.config.toml
│   ├── claude/agents/*.md
│   └── opencode/{agents,commands}/*.md, opencode.json, .gitignore
├── tools/{gen.py,check.py}    install.py
├── tests/test_bootstrap.py            # stdlib unittest, like the script it tests
├── docs/{design.md,experiments.md,acceptance.md,SUPPORT-MATRIX.md}
└── VERSION  README.md  CHANGELOG.md  LICENSE  .gitattributes  .gitignore
```

**Why root `agents/` is Antigravity's while Claude's live under `dist/claude/`**: the Claude manifest's `agents` key takes explicit file paths and REPLACES the default `agents/` scan, so Claude never reads the Antigravity files [CC-02]. Antigravity discovers `agents/` by convention with no manifest key [AG-07][PA-02]. Neither `claude plugin validate` nor a `--plugin-dir` load ever sees the foreign root `agents/` (Q1 settled, `experiments.md` E10): a decoy agent placed in Claude's default scan location was absent from the loaded roster. The fallback — an `antigravity/` sub-plugin — is worse than it looks, because Antigravity keys enablement by directory name, so the installed directory would be named `antigravity` rather than `e-colleagues` [AG-08].

**Why Codex tolerates the root `plugin.json`**: Codex checks a root `plugin.json` first and adopts it only when its `$schema` starts with `https://agent-plugins.org/schemas/`; any other schema is treated as unrelated and Codex falls back to `.codex-plugin/plugin.json` (codex-rs `find_plugin_manifest_path`; read from source, not in the digest). Both halves are now measured, not read from source (`experiments.md` E6). Two invariants `check.py` asserts: the root `plugin.json` is a regular file, never a symlink, and it never carries an agent-plugins.org schema. The symlink failure mode is milder than predicted but still wrong — the install succeeds, no manifest version resolves, and the plugin lands in an unversioned `.../<plugin>/local` directory rather than `.../<plugin>/<version>`.

**Why the Codex marketplace file wins**: Codex takes the first existing of `.agents/plugins/marketplace.json`, `.agents/plugins/api_marketplace.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json` (marketplace.rs), so the Codex-native file is preferred when both exist [CX-10].

**Dev-time versus shipped code.** `tools/gen.py` and `tools/check.py` run in this repository and in CI, and may use PyYAML — CI installs it in one line. Anything that ships to a user, above all `scripts/bootstrap.py`, stays Python 3 standard library only, because it runs on machines this project does not control. The generator therefore renders any data the bootstrap needs into JSON rather than expecting it to parse YAML.

**Why the bootstrap script lives inside the skill**: Claude, Codex and Antigravity all copy the whole plugin directory on install, so the script travels with the skill [AG-08]. The skill body refers to it host-neutrally as "`scripts/bootstrap.py` beside this SKILL.md", never through `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`, which only Claude expands [CC-13]. Python 3, standard library only.

**Everything in that tree ships.** All four dialects are rendered and committed, and the drift gate keeps them in step with `personas/`. Codex was built first because it is the tightest host (D2), which is why its slice is described in most detail below.

---

## 7. Per-host delivery matrix

| | Codex | Claude Code | opencode | Antigravity |
|---|---|---|---|---|
| agents delivered by | project `.codex/agents/*.toml` (trust-gated) or user `~/.codex/agents/` **real files**; a plugin cannot carry agents [CX-01][CX-03][CX-08] | plugin `agents` list [CC-02]; optional project `.claude/agents/` copies, which beat the plugin [CC-08] | project `.opencode/agents/*.md` or user `~/.config/opencode/agents/`; no bundle format [OC-01][OC-11] | **global `agy plugin install <dir>` only** — no workspace root delivers agents at 1.1.27 (E18), so the roster is per-user, not per-project [AG-07][AG-08] |
| tech-lead primary | `developer_instructions` in a trusted `.codex/config.toml` or `codex --profile e-colleagues`; floor `$ec-tech-lead` [CX-06][CX-07] | `claude --agent tech-lead`; opt-in project `.claude/settings.json` `"agent"` [CC-10][CC-03] | `opencode.json` `default_agent: tech-lead` + `mode: primary` [OC-03] | `mainAgent: true`; `agy --agent tech-lead`, `/agents` panel, desktop dropdown [AG-03] |
| delegation restricted | prose; unknown `agent_type` errors loudly, e.g. `unknown agent_type 'reviewer'` [CX-05] | denylist of built-ins via project `permissions.deny` [CC-09]; prose for the rest. **`subagent_type` must be the qualified `e-colleagues:<name>`** — bare names do not resolve (`experiments.md` E10) | `permission.task` allowlist; children get `task * deny` [OC-05] | prose; specialists' `tools` omit `invoke_subagent` (effect UNVERIFIED, Q8) [AG-05][AG-06] |
| read-only reviewer/security | `sandbox_mode = "read-only"` **and** `approval_policy = "never"` [CX-02] | `tools: Read, Grep, Glob, Bash`, no `memory` [CC-07] | `permission: {edit: deny}` + `bash` pattern rules [OC-02] | `tools` without the three write tools [AG-06] |
| skills | plugin skills, or project `.agents/skills` — one of them → `$ec-init` [CX-07][CX-09] | plugin `skills/` → `/e-colleagues:ec-init` [CC-03] | `.agents/skills` or `~/.config/opencode/skills` — one of them → `/ec-init` [OC-07][OC-08] | plugin `skills/` or `.agents/skills`, workspace wins → `/ec-init` [AG-10][AG-12] |
| instructions | `AGENTS.md` root-down, 32 KiB cap, tail truncated [CX-11] | `CLAUDE.md` = `@AGENTS.md` [CC-14]; subagents receive it [CC-12] | `AGENTS.md` stacked cwd→root; CLAUDE.md then ignored [OC-09] | `AGENTS.md` walked cwd→root; CLAUDE.md never read [AG-11] |
| install | `codex plugin marketplace add <owner>/e-colleagues` + `codex plugin add e-colleagues@e-colleagues`, then `bootstrap.py --scope user` [CX-10] | `claude plugin marketplace add <owner>/e-colleagues` + `claude plugin install e-colleagues@e-colleagues` [CC-05]; **or** nothing at all — a repo whose own `.claude/settings.json` declares the marketplace and enables the plugin loads it on trust with no install step, scoped to that repo and absent from `claude plugin list` (Q13, E23; measured for a `directory` source, not yet for `github`) | none; `ec-init` writes the project files [OC-10] | `git clone` + `agy plugin install ./e-colleagues`, or `agy plugin install https://github.com/<owner>/e-colleagues`; destination is `~/.gemini/config/plugins/e-colleagues/` (Q12 settled, E8) [AG-08] |

`agy plugin install https://github.com/<owner>/e-colleagues` **is** offered: it is verified to work for `github.com` HTTPS URLs, which agy normalizes to `<url>.git` and hands to `git clone --depth 1` (`experiments.md` E8). Still not offered, because measured absent: `owner/repo` shorthand, non-github hosts, `file://`, the SSH form, and `plugin@marketplace` on Antigravity [AG-08]; and `claude import codex`, which found zero importable items on a machine with five Codex agents and a skill present [CC-16].

---

## 8. Enforcement matrix and fail-open risks

| rule | Codex | Claude | opencode | Antigravity |
|---|---|---|---|---|
| tech-lead is primary | prose in a developer message | mechanical (`--agent`) | mechanical (`default_agent`) | mechanical (`mainAgent`, `--agent`) |
| delegate only to the team | prose (unknown type errors loudly) | mechanical denylist of built-ins; team-only is prose | mechanical allowlist | prose |
| specialists cannot spawn | V1: depth cap; **V2: prose** [CX-04] | mechanical (generated tool lists) | mechanical (child `task * deny`) | mechanical — an explicit `tools` list omitting `invoke_subagent` overrides ambient inheritance (E19) |
| reviewer/security cannot edit | mechanical **including the shell**, with `read-only` + `never` | editor tools mechanical; Bash writes | editor tools mechanical; bash narrowed by patterns | editor tools mechanical; `run_command` writes |
| specialists never post externally | mechanical side-effect of `read-only` | prose (nothing granted in the brief) | prose | prose |
| return contract, signatures | prose | prose | prose | prose |

Fail-open cases and their guards:

- **A Claude plugin agent with a YAML error loads under its filename with every field dropped**, so a read-only reviewer inherits Write, Edit and Bash [CC-07]. `claude plugin validate` is **not** a sufficient guard: at 2.1.263 a colon in the value — which every routing sentence has — makes a malformed frontmatter pass, and `memory`, unknown keys and the three ignored keys pass too (`experiments.md` E15). `check.py` parses the rendered frontmatter itself (§13 item 2).
- **opencode agents fail open; opencode commands fail closed.** An unknown frontmatter key in an agent is silently moved into `options`, so a misspelled `permision:` yields a reviewer with full default permissions; only a wrong type aborts the load [OC-01][OC-02]. An invalid key in a command file aborts the entire config, and a typo in `default_agent` is a hard error [OC-07][OC-03]. `check.py` rejects any agent key outside opencode's known set and any `options` content, because the runtime will not.
- **The Codex sandbox is bypassable under `approval_policy = "on-request"`** [CX-02]. Every read-only role sets `never`.
- **A project `.claude/settings.json` `agent` key is NOT trust-gated, and an unresolvable value fails silently** (Q3, E21). It applied in a folder recorded as `hasTrustDialogAccepted = False`, and since that key replaces the whole system prompt [CC-10], a cloned repository can control a session's persona before its owner trusts the folder — an asymmetry with `extraKnownMarketplaces`, which *is* trust-gated [CC-06]. A misspelt agent name produces no error and no warning, just a silently default session. The README must state the first; `ec-status` must catch the second.
- **The Codex read-only sandbox blocks every write, so it runs only test suites that write nothing.** Measured (Q19, `experiments.md` E4): a real test target executes and reports correctly under `read-only` + `never`, so R3 evidence survives — but the workspace, `/tmp`, `$TMPDIR` and `$HOME` are all read-only, and no `sandbox_mode` setting expresses "read-only workspace plus a writable scratch dir" (`sandbox_workspace_write.*` only *adds* roots, and only when the workspace is already writable). So the fallback — a per-project `hosts.codex.sandbox_mode: workspace-write` override for the reviewer with a `check.py` warning — is the **common** case for any project that compiles, writes coverage, or uses a temp file, not an edge case. Where it is taken, read-only stops being a guarantee and the enforcement matrix above must be read as prose for that project. The beta `[permissions.<name>]` profiles are an unprobed lead for expressing the middle ground.
- **Bash is a write path on Claude, opencode and Antigravity.** Measured on Claude (`experiments.md` E13): the rendered read-only reviewer, doing nothing but its job — running the project's test suite, which its own capability spec permits — wrote two build artifacts into the workspace. On Claude read-only is a tool-surface guarantee, not a filesystem one. R4 names the permitted shell uses. On opencode the renderer sets pattern rules rather than a blanket `ask`. The original reason — that an `ask` from a subtask might hang `opencode run` — is **wrong**: in headless `run` mode opencode stamps `question: * deny` on parent and subtask sessions alike, so such a prompt is denied, not left hanging (Q7, E20). Pattern rules remain right for a better reason: a blanket denial silently removes the shell at the moment the reviewer needs it, which is worse than a narrow allowlist: `bash: {"*": "allow", "git commit*": "deny", "git stash*": "deny", "sed -i*": "deny", "* > *": "deny"}` [OC-02].
- **An Antigravity tool name outside the registry aborts the agent at startup** — not a hang, as AG-06 warned, but `Error: Agent execution terminated due to error.` with the offending name only in `--log-file` (E17). Seven of AG-06's names are invalid at 1.1.27. `check.py --agy-tools` rejects any name outside the list **measured by running one agent per name** at the supported version; grepping the binary is a superset and must not be used.
- **Codex spawns only when AGENTS.md or a skill asks explicitly** [CX-05], so the managed block carries the literal spawn sentence and names no spawn parameters. In an untrusted Codex project the agents are absent and the sentence produces a loud `unknown agent_type`; the block therefore also says to invoke `ec-tech-lead` first [CX-03][CX-06].
- **A malformed Codex agent TOML is a startup warning and a silently missing persona** [CX-02]. `check.py --codex` parses each file with `tomllib` and enforces the key whitelist statically.
- **Codex truncates AGENTS.md at the tail** [CX-11]; the block is first and `--check` fails above 30 KiB.

Prose-only ceilings, stated plainly: signatures everywhere; the primary persona on Codex; delegation targets on Codex and Antigravity, and team-only delegation on Claude beyond the built-in denylist; specialists-cannot-spawn on the Codex V2 backend; shell-mediated writes on Claude, opencode and Antigravity.

---

## 9. The Codex delivery slice

| what | mechanism | scope | trust needed |
|---|---|---|---|
| the six skills | `codex plugin marketplace add <owner>/e-colleagues` + `codex plugin add e-colleagues@e-colleagues` | user | no |
| five specialists | `bootstrap.py --scope user` → `~/.codex/agents/*.toml`, real files | user | no |
| specialists, project override | `bootstrap.py --scope project` → `.codex/agents/*.toml` | project | **yes** [CX-03] |
| tech-lead | `~/.codex/e-colleagues.config.toml` → `codex --profile e-colleagues` | user | no |
| tech-lead, project | managed region in `.codex/config.toml`: `developer_instructions`, `project_doc_max_bytes = 65536` | project | **yes** |
| tech-lead, floor | `$ec-tech-lead` skill | any | no |
| the contract | `AGENTS.md` managed block | project | no |

Notes that bind the implementation:

- **Real files, never symlinks.** Codex opens a role's config with `O_NOFOLLOW` at spawn, so a symlinked `~/.codex/agents/*.toml` is discovered but fails when spawned — **measured** (Q4, `experiments.md` E5): identical file content, symlink → `agent type is currently not available`, real file → spawns [CX-02]. `--scope user` writes copies, and `check.py` refuses to emit a symlink into an agents directory. Consequence for §14: a symlink-installed persona cannot spawn at all, so replacing that layout is a fix rather than a tidy-up.
- **`~/.codex/config.toml` is never written by this package.** Codex rewrites that file itself, and on this machine it is deliberately untracked state. The profile is a separate file; `codex --profile` reads `~/.codex/<name>.config.toml` [CX-03].
- **Skills live in exactly one scope per host.** A user with the plugin *and* project `.agents/skills` copies sees `ec-init` twice, because same-named skills are not merged [CX-07]. The plugin is the documented route; project copies are opt-in (`--vendor-skills`). Project skills are **not** trust-gated (the CX-03 correction), so `$ec-tech-lead` works in an untrusted clone even when the agents do not load — **measured** in one run (Q17, `experiments.md` E12): the skill loaded and its body was followed, while the project agent failed with `unknown agent_type '<name>'`.
- **Two install stories.** Route A is per-user: plugin for skills, `bootstrap.py --scope user` for personas and the profile. Route B is per-repo: the project carries `.codex/agents/`, the `.codex/config.toml` managed region and vendored skills, so a teammate clones, trusts once and has the team with nothing installed.
- **Locating the script after a plugin install** is settled (Q15, `experiments.md` E6): the whole tree is copied to `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`, so the script is at `.../skills/ec-init/scripts/bootstrap.py`. The **version is a path segment**, so nothing may hardcode the path; the skill resolves the script relative to its own `SKILL.md`, as §6 already requires.
- **The `--profile` route works** (`experiments.md` E14): `--profile <name>` layers `$CODEX_HOME/<name>.config.toml` over the base config and its `developer_instructions` reaches the model, and `-c developer_instructions=""` clears it for one session (Q10). Caveat: an **unknown profile name is silently ignored**, not an error, so a typo yields a session with no tech-lead and no complaint — `ec-status` should check the profile file exists.

---

## 10. Project bootstrap flow

Invoke from inside the tool: `$ec-init` (Codex) [CX-07], `/e-colleagues:ec-init` (Claude) [CC-03], `/ec-init` (opencode, Antigravity) [OC-07][AG-10].

1. **Detect**, read-only. `bootstrap.py --check` reports which tool binaries are on PATH (used only for printed start commands and the user-scope path), whether `AGENTS.md`, `CLAUDE.md`, the managed regions and `.e-colleagues/lock.json` exist, lock version versus package version, and drift of every managed file. The model audits the codebase as it does today.
2. **Bootstrap path** (no `AGENTS.md`): propose the roster (§2.2) and interview one topic at a time — the project-management platform *and its exact tools*, the code host *and its tools*, branching, review and merge flow, who may push, merge, tag. Draft `AGENTS.md`: title, then the managed block, then the project's own sections. Write only after explicit approval. Then `bootstrap.py --write`, which targets **all** supported tools by default: the drop-ins are small and inert on hosts that do not read them, and writing only for the bootstrapper's tools leaves every teammate on another tool half-configured.
3. **Audit path** (`AGENTS.md` exists): additive only. Propose inserting the managed block as the first section if missing, refreshing the package-owned region in place if its version marker is older, and surface stack drift as suggestions. Never restructure project prose.
4. **Offer `ec-onboard`** once the contract exists.
5. **What `--write` produces**, idempotent, never overwriting a file it does not own:
   - `.codex/agents/*.toml` for the roster's specialists, and a managed region at the top of `.codex/config.toml` with `developer_instructions` and `project_doc_max_bytes = 65536` [CX-01][CX-06][CX-11].
   - `CLAUDE.md` containing `@AGENTS.md`, or that line inside a managed block in an existing `CLAUDE.md`; imports resolve relative to the containing file [CC-14].
   - `.claude/settings.json` merged: `extraKnownMarketplaces["e-colleagues"] = {"source": {"source": "github", "repo": "<owner>/e-colleagues"}}` (`git` with `url` for other hosts) [CC-06]; `enabledPlugins["e-colleagues@e-colleagues"]: true`; `permissions.deny` for built-in agent types [CC-09]; optional `"agent"` — the **bare** `tech-lead` whenever `.claude/agents/` copies are vendored, since a scoped name resolves only to the plugin, and `e-colleagues:tech-lead` only when they are not [CC-03].
   - `.opencode/agents/*.md`, `.opencode/commands/{ec-review,ec-audit}.md`, `.opencode/.gitignore`, and `opencode.json` merged with `$schema` and `default_agent` [OC-01][OC-07][OC-10][OC-03].
   - `.agents/skills/ec-*/` copies, opt-in via `--vendor-skills` [CX-07][OC-08][AG-12]. Never `.claude/skills/`, where opencode would see every skill twice [OC-08].
   - Optional `.agents/plugins/e-colleagues/` workspace copy of the Antigravity plugin [AG-08].
   - `.e-colleagues/lock.json`.
6. **Print** per tool: the start command; the trust prompts teammates will see (Claude workspace trust for `extraKnownMarketplaces` [CC-06]; Codex project trust for `.codex/agents` and `.codex/config.toml`, while `.agents/skills` loads untrusted [CX-03]); the `claude plugin install` line teammates may need, since a project-enabled plugin from an external source does not load until they run it, while a **locally**-sourced one loads on trust with no install step (Q13, E23) and the github case is still open until the repo is published [CC-06]; `agy --agent tech-lead` [AG-03]; and the `AGENTS.md` byte count against the 32 KiB Codex cap [CX-11].

`ec-status` and the first line of the tech-lead body detect "running without the persona" and print the install line.

---

## 11. Extension model

- **Add a persona to the package**: `personas/<name>.yaml` plus `prompts/<name>.md`, add it to the catalog and a profile, run `tools/gen.py`. `check.py` enforces kebab-case, no `:` [CC-03], not a Codex built-in name, unique across profiles, and a lens name unique in the catalog.
- **Profiles**: named subsets of the catalog. `bootstrap.py --profile` filters the drop-ins, the managed block, the lead's delegation surface and opencode's `permission.task` [OC-05].
- **A specialist that delegates** is a profile setting. The generator then emits, for that profile only, opencode `subagent_depth: 2` plus a `permission.task` entry on the middle agent — both are required [OC-05]; Codex `[agents] max_depth = 2` with the note that V2 ignores it [CX-04]; on Claude the middle agent drops `disallowedTools: Agent`, since a type list inside a subagent is ignored [CC-09]; `invoke_subagent` in the Antigravity list [AG-06].
- **Project overrides** use each host's precedence: `.claude/agents/<name>.md` beats the plugin [CC-08]; a trusted `.codex/agents/<name>.toml` replaces the user-layer role wholesale [CX-03]; the opencode drop-in already *is* the effective file, and an edited managed file flips to project-owned in the lock; a workspace `.agents/…` tree **delivers no agents at all** at agy 1.1.27 — neither `.agents/plugins/`, `_agents/plugins/` nor `.agents/agents/` surfaced one, so the name-collision question is moot and the global install is the only route (E18) [AG-12][AG-03]. Project-only personas live in `.e-colleagues/personas/<name>.yaml` and are rendered by the bundled script.
- **Domain packs**: a directory or git URL with `pack.yaml`, `personas/`, `prompts/`, optional `skills/` and an `AGENTS.fragment.md`; `bootstrap.py --pack <path|url>` renders them and appends the fragment inside its own managed block. A pack may add lenses.
- **A fifth host later** is one more `hosts/<tool>.yaml` and one renderer.

---

## 12. Updates and drift

**In the package repository.** Generated files are committed but guarded: `check.py --drift` regenerates into a temp directory and fails on any diff [PA-02]. One `VERSION` is stamped into the root `plugin.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (top level **and** entry), `.codex-plugin/plugin.json`, `team.yaml` and every `SKILL.md` `metadata.version`; `--versions` asserts lockstep [STD-01][CC-04][CX-09][AG-07].

**In a consumer's tools.** Codex `codex plugin marketplace upgrade` [CX-10]; Claude refreshes the marketplace on `claude plugin install …@e-colleagues` and `extraKnownMarketplaces.*.autoUpdate` exists [CC-05][CC-06]; Antigravity `git pull` then re-install — a second install **merges** into the existing directory and leaves deleted files behind (Q12 settled, `experiments.md` E8), so uninstall-first is not a fallback but the required sequence whenever the roster shrinks [AG-08]; user-scope Codex and opencode files are re-copied by `bootstrap.py --scope user`.

**In a consumer project.** `.e-colleagues/lock.json` records the package version and a sha256 per written file. `--check` classifies each file as current, stale or project-owned; `--update` rewrites only stale package-owned files and the package-owned region of the managed block; `--prune` removes only files the tool wrote that are absent from the new roster and, in the same run, rewrites `default_agent`, `permission.task` allowlists and command `agent:` fields, because a dangling opencode reference is a hard config error for every opencode user in the repository [OC-03][OC-07]. `--check` fails if any such reference dangles.

**Two lifecycles, deliberately separate.** A package update never touches `.e-colleagues/knowledge/`. Knowledge staleness is git-based (§5.2), driven by the recorded commit and paths. Bumping e-colleagues must never invalidate what the team learned about a project.

---

## 13. Validation and CI

1. `python3 tools/check.py --drift --versions`, plus manifest sanity: the root `plugin.json` is a regular file, carries the Antigravity schema, and never an agent-plugins.org schema (§6).
2. **Claude, three runs** — worth running, but **not** the guard for [CC-07]. `claude plugin validate --strict ./dist/claude/agents` (directory mode; it needs an ancestor `.claude-plugin/` or it reports a mode error that looks like a failure); `claude plugin validate --strict .claude-plugin/plugin.json`; `claude plugin validate --strict .claude-plugin/marketplace.json`. `validate .` here runs in marketplace mode, confirmed [CC-04]. `--strict` requires `description` and `version` on the marketplace manifest and `version` on the plugin manifest, which `gen.py` stamps [CC-04].

   **Measured at 2.1.263 (`experiments.md` E15): validate misses most agent frontmatter faults.** A value containing a colon — which the canonical routing sentence always has — triggers a repairing sanitizer, so an unterminated quote *passes*. Also passing: a colon in `name`, `permissionMode`/`hooks`/`mcpServers`, an unknown key, and `memory: true` on a `tools`-restricted persona. It reliably catches only a parse error with no colon in the value, and a missing `description`. Skills are covered better than agents: a broken `SKILL.md` is caught even from manifest mode.

   Therefore **`check.py` owns the [CC-07] guard**: it parses every rendered Claude agent's frontmatter with a strict YAML parser and enforces the key whitelist — no `permissionMode`, `hooks`, `mcpServers`, no `memory` on a read-only persona, no `:` in `name`, no unknown keys. Because `gen.py` renders these files, a fault means a generator bug, which is what the drift gate is for; the gate simply has to be ours.
3. `agy plugin validate .` must print `[ok]` with the expected component counts; no `mcp_config.json` is shipped, so it is not PATH-dependent [AG-07]. `check.py --agy-tools` asserts every tool name is in the list re-derived at the installed agy version [AG-06].
4. **Codex has no validate subcommand**: `check.py --codex` parses each TOML with `tomllib`, asserts the five-key whitelist and non-blank `name`, `description`, `developer_instructions` [CX-02], and `sandbox_mode = "read-only"` with `approval_policy = "never"` for every `edit: false` persona.
5. `check.py --opencode` validates `opencode.json` against a vendored copy of `https://opencode.ai/config.json`; rejects any agent frontmatter key outside opencode's known set and any `options` content, because agents fail open [OC-01][OC-02]; requires lowercase permission keys, `mode: primary` on the tech-lead, `mode: subagent` plus a description on specialists [OC-03][OC-04], `permission.task` on any delegating persona [OC-05], command keys within **{template, description, agent, model, variant, subtask}** with `template` **required** and `additionalProperties: false` (the vendored schema; the earlier list omitted `template` and `variant`), and `agent` resolving to a rendered agent [OC-07], and `default_agent` resolving to a non-hidden primary [OC-03].
6. `check.py --skills`: frontmatter within {name, description, metadata}; `name` equals the directory and matches `^[a-z0-9]+(-[a-z0-9]+)*$`, at most 64 characters; description at most 1024; no `compatibility`, which Codex's bundled validator omits [STD-01]; no `$ARGUMENTS`, `$N`, `!cmd`, `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}` in any body, because Codex and Antigravity load the skill and perform no substitution, so the literal token reaches the model [CX-12][AG-10]; body under 7 KB.
7. `check.py --personas` (new): every body carries all skeleton sections of §4 in order; the RETURN block appears verbatim; `description` is a routing sentence; `external_post: false` on every persona but the tech-lead; every catalog lens name is unique.
8. `check.py --knowledge` (new): provenance frontmatter validates against the §5.2 schema; index rows correspond one-to-one with files on disk; a fixture repository where a recorded path is touched really does report stale; an interrupted audit resumes from the lock.
9. Budgets: package-owned managed region at most 2 KB; template plus block at most 16 KiB; `bootstrap.py --check` fails above 30 KiB total [CX-11]; 12,000 characters printed as an Antigravity caution [AG-11].
10. Bootstrap tests (pytest, stdlib only): `--write` into a temp directory seeded with an existing `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, `opencode.json` and `.codex/config.toml`; assert nothing outside owned keys and markers changed, the second run is a no-op, `--check` is clean, a hand edit flips a file to project-owned, `--update` rewrites only stale files, and `--prune` leaves no dangling opencode reference.
11. Minimum versions live in `docs/acceptance.md`, one row per claim id the package rests on (`docs/SUPPORT-MATRIX.md`).
12. Manual release checklist: Codex `$ec-init` resolves and a spawned reviewer cannot write even via an approved command [CX-05][CX-02]; then `claude --plugin-dir . --agent tech-lead` cannot spawn Explore or Plan but can spawn the roster as `e-colleagues:<name>` (bare names do not resolve, E10) [CC-09][CC-10]; opencode Tab shows tech-lead as default and `@reviewer` cannot edit [OC-03][OC-05]; `agy --agent tech-lead` can `invoke_subagent` the roster and a specialist cannot invoke a sibling [AG-03][AG-06].

---

## 14. Migrating from an earlier setup

The package this replaced was Codex-only: five agent TOMLs, all `sandbox_mode =
"workspace-write"` — including reviewer and security, so "does not edit source" was prose
alone — plus a skill in the deprecated `~/.codex/skills` root [CX-07]. It was installed by
symlink, which is why Q4 mattered: a symlinked role file is discovered and then fails at
spawn (`experiments.md` E5), so those personas could not be delegated to at all.

Anyone migrating from a similar arrangement needs three things, in this order:

1. **Install the new personas first**, so the team is never unavailable:
   `bootstrap.py --scope user --write`. It writes real files, and replaces a symlink rather
   than writing through it.
2. **Verify one actually spawns** before removing anything. A persona that loads is not a
   persona that spawns.
3. **Then remove the old files**, including any dangling symlink left in `~/.codex/agents/`
   and any copy in a deprecated skill root.

A project already carrying its own team section keeps it: the managed block is inserted below
the title and no existing prose is restructured.

---

## 15. Verifying a host

Every host fact this design rests on was probed against the installed tool before code
depended on it, and every outcome is recorded in [`experiments.md`](experiments.md) with the
command, the version and the raw output. That record is the authority. This section is the
method, because it will be needed again for a new host or a new version.

- **Build a throwaway fixture that really is a plugin** for the host under test, in a scratch
  directory, and delete it afterwards. Several questions — does the manifest's `agents` key
  replace the default scan, does a workspace plugin root deliver agents — cannot be answered
  any other way.
- **Separate what can be automated from what needs a human.** Some probes need a TTY or a
  trust dialog, and pretending otherwise produces a confident wrong answer.
- **Re-verify anything version-gated.** Four of the five tools released a new version within a
  day of the research being written, and one gate had already flipped by the time it was
  checked.
- **Mutating probes run against the fixture, never a real project.** Snapshot host state
  before, diff after, reverse every change and record the reversal. Never hand-write
  `~/.codex/config.toml`: Codex rewrites that file itself.
- **A probe that produces no output has produced no finding.** Check the exit code, include a
  positive control, and never read silence as evidence. This one caught several errors here,
  including in checks written to catch errors.
- **A gate that has never failed is not yet a gate.** Break it deliberately before relying on
  it.

It is worth the ceremony. Nine design decisions changed as a result of that first sweep, the
largest being that seven Antigravity tool names the vendor documentation lists are absent from
the tool registry and abort an agent at startup — so a renderer built from the documentation
would have produced agents that could not start at all.

Three behaviours remain unexercised because they need a human at a user interface. They are
listed under "Known limitations" in [`acceptance.md`](acceptance.md), marked untested rather
than assumed.

---

## 16. Extending this

The shape that made four hosts tractable, for whoever adds a fifth — or a persona, or a lens.

**Adding a host.** Write `hosts/<name>.yaml` with that tool's vocabulary and nothing else, add
a renderer to `gen.py`, and add a gate to `check.py`. No persona file changes. The gate is the
work: every host so far fails open somewhere, and the failure is never where the documentation
says it is. Probe it first — §15 is the method.

**Adding a persona.** A `personas/<name>.yaml` and a prompt body. The renderers, the managed
block, the index and `permission.task` all follow from `team.yaml`, so nothing else is
hand-edited. Give it a lens no other persona has, and a description that says when *not* to
use it, because every host routes on that sentence.

**What is deliberately not solved.** Automatic refresh of stale knowledge — `ec-status`
reports staleness and the metadata to refresh it exists, but a refresh writes files and needs
approval. External posting by anyone but the tech-lead, which D6 forecloses. And per-project
rosters on Antigravity, which the host does not currently allow.
