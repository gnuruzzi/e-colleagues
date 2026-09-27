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
| opencode | **1.18.29** | the 15 permission keys and `AgentConfig`'s 15 properties, re-derived from the published schema (E16 C3) |
| Google Antigravity (`agy`) | **1.1.27** | the 15-name tool registry (E17, re-verified unchanged at 1.2.6 and 1.2.10); global install is the only delivery route (E18, again at 1.2.10) |
| Antigravity desktop | 2.17.0 *(observed)* | **not a floor** — the desktop was inspected, never driven. At 2.12.2 it lacked the `agents:` key the CLI had (E16); at 2.17.0 it carries it (E24). The renderer still never emits the key, so that agents render the same on every version of either binary |
| Python | **3.11** | `tomllib` is standard library from 3.11; the shipped scripts use nothing else |

`tools/gen.py` and `tools/check.py` additionally need PyYAML. Anything that ships to a user —
`bootstrap.py`, `knowledge.py`, `status.py` — is standard library only, because it runs on
machines this project does not control.

## What the package guarantees, and what it only asks for

Stated plainly, because a guarantee that is really a request is the failure this design
exists to remove.

| rule | Codex | Claude | opencode | Antigravity |
|---|---|---|---|---|
| tech-lead is primary | prose (`developer_instructions`) | mechanical (`--agent`) | mechanical (`default_agent`) | mechanical (`mainAgent`) |
| specialists cannot spawn | V1 depth cap; **V2 prose** | mechanical (tool list) | mechanical (child `task * deny`) | mechanical (`tools` omits `invoke_subagent`, E19) |
| reviewer cannot edit **files** | mechanical | mechanical | mechanical | mechanical |
| reviewer cannot edit **via the shell** | **mechanical** (read-only sandbox, E4) | prose — Bash writes (E13) | narrowed by bash patterns | prose — `run_command` writes |
| specialists never post externally | mechanical side-effect (no network under read-only) | prose | prose | prose |
| return contract and signatures | prose | prose | prose | prose |

The one place "cannot edit" is a filesystem guarantee rather than a tool-surface one is Codex
under `read-only` + `never`. Everywhere else a determined shell command can still write, and
E13 measured exactly that on Claude: a read-only reviewer running the project's own test
suite wrote two build artefacts, doing nothing wrong.

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

- **Antigravity has no per-project roster.** No workspace directory delivers agents at 1.1.27
  (E18), so the roster is per-user and two projects on one machine share it.
- **An Antigravity re-install merges rather than replaces** (E8), so an update that drops a
  persona leaves the old agent in place and selectable. Uninstall first when the roster shrinks.
- **`AGENTS.md` never reaches an Antigravity agent** (E19). The managed block is invisible
  there, which is why each rendered body carries the contract itself.
- **A project `.claude/settings.json` `agent` key is not trust-gated** (E21) and replaces the
  whole system prompt. A cloned repository can set a session's persona before its owner
  trusts the folder. That is Claude Code's behaviour, not this package's, but anyone
  recommending the key should know it.
- **One question stays open now the repository is published**: whether a github-sourced
  self-marketplace skips the Claude install step the way a local one does (E23). The other —
  where `agy plugin install <github-url>` lands — is settled: a directory named after the
  repository (E8 addendum).
- **A user-scope install keeps no record of its profile.** `bootstrap.py --scope user --check`
  defaults to the `default` roster regardless of which profile was installed, so pass
  `--profile` to both or it will report agents missing that were never meant to be there. A
  project install has no such problem: the roster is recorded in `lock.json`.
- **Three behaviours were never exercised**: the opencode Tab and `@` menus, and the
  Antigravity desktop's subagent-inheritance default. All three need a human at a UI.
