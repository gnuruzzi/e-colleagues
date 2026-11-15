# Acceptance

What must be true for this package to work, and how each claim was established. Read with
[`SUPPORT-MATRIX.md`](SUPPORT-MATRIX.md), which maps every claim id to the version it was
last confirmed at, and [`experiments.md`](experiments.md), which holds the evidence.

Where a document and an experiment disagree, **the experiment wins**: it ran against the
installed binary.

## Minimum versions

Each is the version the behaviour this package depends on was *measured* at, not the version
the feature was introduced in. Below it, nothing is promised.

| host | minimum | why this floor |
|---|---|---|
| OpenAI Codex CLI | **0.153.4** | `read-only` + `approval_policy = "never"` blocks every write (E4); role files parse under `deny_unknown_fields` with a five-key whitelist [CX-02]. Re-verified at 0.154.0 (E24) |
| Claude Code | **2.1.263** | plugin `agents` takes a file list and replaces the default scan (E10); `subagent_type` needs the qualified name (E10). Re-verified at 2.1.283 (E24) |
| opencode | **1.18.29** | the 15 permission keys and `AgentConfig`'s 15 properties, re-derived from the published schema (E16 C3). Re-verified at 2.0.18 (E20 addendum) |
| Google Antigravity (`agy`) | **1.5.3** | every Antigravity claim was re-run there (E32): the ten tool names that load and give a tool, which are the only ones the rendered agents list; `AGENTS.md` reaching the default agent, a custom agent and a sub-agent; and a re-install that replaces the installed directory exactly. Versions 1.1.27 to 1.2.10 are no longer supported |
| Antigravity desktop | 2.17.0 *(observed)* | **not a floor** — inspected at 2.12.2, driven once at 2.17.0 (E19 addendum): the `tools` allowlist holds there too and `AGENTS.md` does not arrive. At 2.12.2 it lacked the `agents:` key the CLI had (E16); at 2.17.0 it carries it (E24). Not driven since: at 2.29.1 only its binary was read (E32). The renderer still never emits the key, so that agents render the same on every version of either binary |
| Python | **3.11** | `tomllib` is standard library from 3.11; the shipped scripts use nothing else |

`tools/gen.py` and `tools/check.py` additionally need PyYAML. Anything that ships to a user —
`bootstrap.py`, `knowledge.py`, `status.py`, `fleet.py` — is standard library only, because it
runs on machines this project does not control.

## What the package guarantees, and what it only asks for

Stated plainly, because a guarantee that is really a request is the failure this design
exists to remove.

| rule | Codex | Claude | opencode | Antigravity |
|---|---|---|---|---|
| tech-lead is primary | prose (`developer_instructions`) | mechanical (`--agent`) | mechanical (`default_agent`) | mechanical (`mainAgent`) |
| specialists cannot spawn | V1 depth cap; **V2 prose** | mechanical (tool list) | mechanical (child `task * deny`) | mechanical (`tools` omits `invoke_subagent`, E32) |
| reviewer cannot edit **files** | mechanical only in a `read-only` session (E33) | mechanical, denied by name (E33) | mechanical | mechanical |
| reviewer cannot edit **via the shell** | **mechanical** in a `read-only` session (E4); prose under `workspace-write` (E33) | prose — Bash writes (E13) | narrowed by bash patterns | prose — `run_command` writes |
| a specialist posts only where the contract grants it | prose | prose | prose | prose |
| return contract and signatures | prose | prose | prose | prose |

The one place "cannot edit" is a filesystem guarantee rather than a tool-surface one is a Codex
session started `read-only`. The role file's `read-only` + `never` did not reach a spawned
reviewer at 0.167.0: it ran with the session's sandbox and wrote where the session could (E33).
Everywhere else a determined shell command can still write, and
E13 measured exactly that on Claude: a read-only reviewer running the project's own test
suite wrote two build artefacts, doing nothing wrong.

Every sub-agent reaches the session's MCP tools (E32, E33), and no host tells a write through
MCP from a read. What a specialist may do with a platform is the project's contract and
nothing else.

## The cost of that guarantee

Codex's `read-only` blocks **every** write — workspace, `/tmp`, `$TMPDIR` and `$HOME` (E4).
Tests that write anything at all fail under it, and no `sandbox_mode` expresses "read-only
workspace plus a writable scratch directory". A project whose suite compiles, writes coverage
or uses a temp file needs the per-project `hosts.codex.sandbox_mode: workspace-write`
override, and read-only then stops being a guarantee for that project. This is the common
case, not an edge case.

## Acceptance checklist

Run before a release. Everything except the last section is automated.

```bash
python3 tools/check.py            # nine gates: personas, four host dialects, skills,
                                  # bodies, knowledge, vendor validators, drift
python3 tools/gen.py --check      # the committed tree matches the source
python3 -m unittest discover -s tests
```

Then, per host, by hand — because no static check can prove a runtime behaviour:

- **Codex** — `$ec-init` resolves in a session; a spawned reviewer cannot write even through
  an approved command; a symlinked role file fails with `agent type is currently not
  available`, so the installer must write real files.
- **Claude** — `claude --plugin-dir . --agent tech-lead` spawns `e-colleagues:<name>` and not
  a built-in; the bare name is absent from the agent list.
- **opencode** — `default_agent` makes the tech-lead primary; the reviewer's `edit: deny`
  refuses a write.
- **Antigravity** — `agy --agent tech-lead` can `invoke_subagent` the roster; a specialist
  reports `invoke_subagent` unavailable.

## Known limitations

- **This package gives Antigravity no per-project roster.** It installs globally only, by
  choice, so two projects on one machine share the roster. The host itself delivers workspace
  agents, from `.agents/agents/`, `_agents/agents/`, `.agents/plugins/` and `_agents/plugins/`
  (E32).
- **An Antigravity persona has no search tool**, because agy has none to list (E32). It
  searches through `run_command`, which every persona has.
- **The designer and the tech-lead have web access and a shell together.** A page either one
  reads could try to steer it into running a command; nothing but the persona's own rules and
  the host's approvals stands between. The other specialists have a shell and no web access.
- **opencode's roster is per-machine too.** `bootstrap.py --scope user` writes the agents to
  `~/.config/opencode/agents/` and the five skills to `~/.config/opencode/skills/`; nothing
  writes them into a project, and there is no bundle or plugin route (E25). The global config is never written, so the tech-lead is chosen per
  session with `--agent`, with Tab in the TUI, or by a `default_agent` the user sets.
- **An Antigravity re-install replaces the installed directory exactly** (E32). A persona
  dropped from the package is gone after the next install; no uninstall is needed.
- **`AGENTS.md` reaches every Antigravity agent tried**: the default one, a custom one and a
  sub-agent (E32). Each rendered body still carries the contract itself, because the desktop
  app did not receive `AGENTS.md` when last driven, at 2.17.0 (E19 addendum), and has not been
  driven since.
- **A project `.claude/settings.json` `agent` key is not trust-gated** (E21) and replaces the
  whole system prompt. A cloned repository can set a session's persona before its owner
  trusts the folder. That is Claude Code's behaviour, not this package's, but anyone
  recommending the key should know it.
- **An Antigravity workspace agent replaces the installed persona of the same name** (E32).
  A repository's `.agents/agents/<name>/agent.md` is what `agy --agent <name>` runs there
  instead of the installed plugin's agent, in print mode even in a folder nobody has trusted. Measured with a probe name, not with `tech-lead`. That is Antigravity's
  behaviour, not this package's, which never writes such a file. `fleet.py start` names any
  agent file in the new worktree that carries the tech-lead's name, and starts all the same; it
  matches the name by pattern, so it is a warning and not a guard.
- **Both questions left open at publication are settled.** A github-sourced self-marketplace
  does *not* skip the Claude install step: trusting the folder registers and fetches the
  marketplace, the plugin loads only after `claude plugin install`, and nothing is printed to
  say so (E23 addendum). `agy plugin install <github-url>` lands in a directory named
  `e-colleagues`, and a local install takes that name from the manifest's `name`, not from the
  source folder (E32).
- **A user-scope install keeps no record of its profile.** `bootstrap.py --scope user --check`
  defaults to the `default` roster regardless of which profile was installed, so pass
  `--profile` to both or it will report agents missing that were never meant to be there. A
  project install has no such problem: the roster is recorded in `lock.json`.
- **The three UI behaviours are now exercised** (E20 TUI addendum, E19 addendum). In the
  opencode TUI the agent cycle is Shift+Tab, not Tab, and it cycles primaries only; `@` offers
  every specialist and also the built-ins the allowlist denies, and a mention routes through
  the tech-lead. The Antigravity desktop honours an explicit `tools` list the way the CLI does.
- **`ec-fleet` needs workmux and is measured on all four hosts** (E26 to E31). workmux needs its status hooks set up for each host it starts (`workmux setup`);
  they report the overview's states. Run by `fleet.py`, which gives it no input, it did not
  stop to ask about another agent's hooks (E27); that the missing input is why is an inference.
  The Codex plugin route is UNVERIFIED.
- **`fleet.py start` reports success once the launcher returns.** If the host then exits, the
  session has no row in the overview: on Claude Code without this package's plugin,
  `claude --agent tech-lead` ends with `--agent 'tech-lead' not found` (E31).
- **On opencode the fleet needs workmux's current plugin and starts a private server per
  session** (E30). An earlier one-file workmux plugin does not load at opencode 2.2.7, and then
  no opencode session has a row; `workmux setup` replaces it. The start command names a config
  file beside the script and uses `--standalone`, because opencode's TUI takes no `--agent`;
  what a server per session costs is not measured. opencode shows no trust prompt: it applies
  a repository's own config and runs its plugins unasked.
- **A `--scope user` update keeps what Codex appended to its profile** only while the package's
  part of that file is unchanged. When it has changed, the old file is kept as `.bak` and
  Codex's own entries are not carried into the new one (E29, E30).
- **A session at its host's trust prompt can be missing from the overview.** On Codex and Claude
  Code workmux does not list it until the prompt is answered (E29, E31). Codex asks only in a
  repository it has never trusted, and the default start trusts the worktree for that session,
  so the prompt does not show (E29). Claude Code asks once per repository, and no way to
  pre-answer it for one session was found (E31).
- **For an Antigravity session workmux reports only `working` and `done`** (E26). A session at
  one of agy's approval prompts reads `working`, and the overview does not look inside a
  `working` session, so it cannot show that approval. Codex and Claude Code sessions read
  `waiting` there (E29, E31).
- **`fleet.py` trusts a new Antigravity worktree for its own session**, so agy's trust dialog
  does not show and nothing is saved (E28). It reads the path from workmux's `--dry-run`
  output, which is not a promised interface. When it cannot learn the path, or with
  `trust = ""` in the config, the dialog shows, the start prompt runs behind it and, with agy
  set to ask before every command, the session waits there and reads `working` (E27).
- **Away from the desk rests on each host's own remote feature.** The package builds none, and
  none is measured reaching a session in a window; E26 records one report for agy 1.5.3.
