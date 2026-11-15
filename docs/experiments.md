# Experiments

What was actually run against the installed tools, and what came back: the exact command, the version, the raw output, the verdict and the design consequence. **This is the authority.** Where an entry here contradicts a claim in [`SUPPORT-MATRIX.md`](SUPPORT-MATRIX.md), the entry wins — it ran against the binary; the claim was read from documentation and source. An unknown with no entry here is still open, and no code may depend on it.

Tranches: **A** automated, **B** interactive — needing a TTY or a trust dialog, **C** re-verification of version-gated claims, because four of the five tools moved within a day of the research.

## Status

| # | tranche | unknown | status |
|---|---|---|---|
| Q1 | A | Claude ignores the Antigravity-format root `agents/` when the manifest lists files explicitly | **settled** (E10) |
| Q2 | A | bare names in `Agent(...)`'s `subagent_type` resolve to plugin agents under `--agent` | **settled** (E10) |
| Q3 | B | project `.claude/settings.json` `agent` key: trust-gated, precedence, unresolvable value | **settled** (E21) |
| Q4 | A | Codex `O_NOFOLLOW`: symlinked role TOMLs fail at spawn | **settled** (E5) |
| Q5 | A | Codex root-as-plugin marketplace entry `path: "./"` | **settled** (E6) |
| Q6 | A | `agy plugin validate` / `install` on a tree carrying all three manifests | **settled** (E7) |
| Q7 | B | opencode runtime: Tab and `@` menus, `default_agent`, subtask `ask`, AGENTS.md in task children | **settled** (E20, its 2.0.18 addendum, and the TUI addendum: Shift+Tab cycles the primaries, `@` offers the specialists and routes through the tech-lead) |
| Q8 | B | Antigravity: `tools` allowlist versus ambient subagent inheritance, `tools: []`, H1 slicing, name collisions | **settled** (E17–E19, and the E19 addendum: the desktop at 2.17.0 behaves as the CLI); `tools: []` alone not isolated |
| Q9 | A | does a spawned Codex child re-run AGENTS.md discovery | **settled** (E9) |
| Q10 | A+B | `-c developer_instructions=""` clears the project value for one session | **settled** (E14 profile layer, E22 project layer) |
| Q11 | A | `agy plugin install <github-url>` syntax | **settled** (E8) |
| Q12 | A | `agy plugin install <dir>` destination, and second-install behaviour | **settled** (E8) |
| Q13 | B | a project-enabled plugin sourced `./`: auto-installed on trust, or external | **settled** (E23 and its addendum): a `directory` source loads on trust; a `github` source is registered and fetched on trust but loads only after `claude plugin install`, and nothing says so |
| Q14 | — | Codex read-only sandbox blocks network, so read-only specialists cannot post | **retired by design** (E1) |
| Q15 | A | Codex plugin cache layout, for locating the bundled bootstrap script | **settled** (E6) |
| Q16 | A | V2 concurrency ceiling for the onboarding audit waves | **settled** (E11) |
| Q17 | A | does `$ec-tech-lead` resolve from project skills in an untrusted clone | **settled** (E12) |
| Q18 | C | agy 1.1.27 `agents:` frontmatter key | **settled** (E3) |
| Q19 | A | does the Codex read-only sandbox permit running the project's tests | **settled** (E4) |
| — | C | installed versions versus research targets | **settled** (E2) |
| — | C | agy tool list, Antigravity desktop 2.12.2, opencode 1.18.29 schema, Claude 2.1.263 | **settled** (E16) |
| — | C | the 2026-09-27 snapshot: Claude 2.1.283, Codex 0.154.0, agy 1.2.10, desktop 2.17.0 | **settled** (E24); opencode 2.0.18 in the E20 addendum |
| — | A | can a plugin, a `references` entry or a skill source deliver agents to an opencode project | **settled** (E25): no — agents come only from the two directories and the config key; a plugin can add commands and skills |
| — | B | a fleet of Antigravity tech-leads through workmux: dispatch from a session, prompt delivery, commit, status values, the captured screen | **settled** (E26): dispatch from a session, prompt delivery and commit hold, with stops that need the person; the states item holds only in part, because workmux reports only `working` and `done` for agy |
| — | B | the fleet skill end to end on Antigravity: a dispatched tech-lead loads `ec-fleet` from its start prompt, and the overview reads its stop | **settled** (E27): both hold; a session at the first-run trust dialog read `working`, not `done`, because its first command waited for approval behind the dialog |
| — | B | can `fleet.py` start an Antigravity tech-lead in a new worktree without agy's trust dialog | **settled** (E28): yes — it reads the path from `workmux add <name> --dry-run` and passes it in a session-only `trustedWorkspaces` setting; nothing is saved |
| — | B | the fleet skill on Codex: start, first-run prompts, states, the captured screen, end to end | **settled** (E29): all hold with the default start command; workmux reports `working`, `waiting` and `done`; a session at Codex's trust prompt is missing from the overview, and a session-only `-c 'projects={…}'` override removes that prompt; the plugin route was not measured |
| — | B | the fleet skill on opencode: start, first-run prompts, states, the captured screen, end to end | **settled** (E30, opencode 2.2.7): the TUI has no `--agent`, so the old default start failed while `fleet.py` reported success; a config file named in `$OPENCODE_CONFIG` with `--standalone` starts the tech-lead; no first-run prompt; `working`, `waiting` and `done`; the block is read once text beside it is ignored; a session with no agent configured ran as opencode's own default agent and did not adopt the tech-lead |
| — | B | the fleet skill on Claude Code: start, first-run prompts, states, the captured screen, end to end | **settled** (E31): all hold once the plugin is installed; without it the host exits and `fleet.py start` still reports success; trust is kept per repository, with no session-only way to pre-answer it; a session at the trust dialog is missing from the overview |
| — | C | the 2026-11-15 Antigravity sweep: agy 1.5.3 | **settled** (E32): AG-06, AG-07, AG-11 and AG-12 changed; the desktop not driven |

---

## The fixture

Several questions need a tree that really *is* a plugin for the host under test. This was that fixture — a throwaway in a scratch directory, deleted afterwards. Its shape is recorded so it can be rebuilt for a new host or version without re-deriving the manifests.

```
e-colleagues/                              # directory name is load-bearing [AG-07][AG-08]
├── plugin.json                            # Antigravity; ROOT; regular file; $schema antigravity.google (never agent-plugins.org)
├── .claude-plugin/plugin.json             # Claude; "agents" = explicit FILE list under ./dist/claude/agents/
├── .claude-plugin/marketplace.json        # Claude self-marketplace; plugins[0].source = "./"; needs description + version for --strict
├── .codex-plugin/plugin.json              # Codex; skills only; no agents key exists [CX-08]
├── .agents/plugins/marketplace.json       # Codex marketplace; plugins[0].source = {"source":"local","path":"./"}  (E6)
├── agents/{reviewer,tech-lead}/agent.md    # Antigravity dialect; explicit `tools` allowlist of verified names
├── agents/decoy-antigravity.md            # decoy in Claude's DEFAULT scan location, to make Q1 falsifiable (E10)
├── dist/claude/agents/{reviewer,tech-lead}.md
├── dist/codex/agents/reviewer.toml        # five keys only; read-only + approval_policy = "never"
├── dist/opencode/agents/reviewer.md
└── skills/ec-tech-lead/SKILL.md           # portable floor; no $ARGUMENTS, no ${CLAUDE_*}
```

Two companion trees, also throwaway:

- `m0/proj` — a real little project (`src/calc.py`, stdlib `unittest` tests, `make test`, an `AGENTS.md` with the managed block and the canary `BLUEBIRD-7731`) used by E4, E9, E11, E13. Its test run writes `__pycache__`, which is what makes it a useful sandbox probe.
- `m0/untrusted` — a repository deliberately absent from `~/.codex/config.toml`'s `[projects.*]`, carrying both `.agents/skills/ec-tech-lead/SKILL.md` (canary `MAGPIE-4402`) and `.codex/agents/m0-projonly.toml`, used by E12.

**Safety rules, followed throughout**: every mutating probe ran against these trees, never a real project; `~/.codex/config.toml` was never written by hand (Codex wrote and removed its own `[marketplaces.e-colleagues]` table); `~/.gemini/config/config.json` and both plugin trees were snapshotted before and diffed after. At the end of tranche A all four diffs were **identical** — Codex config, Codex plugins tree, Antigravity config, Antigravity plugins tree — and `~/.codex/agents/` held only the pre-existing agent files it started with. One residue needed manual removal: `codex plugin remove` leaves an empty `~/.codex/plugins/cache/<marketplace>/` directory behind.

---

## E1 — Q14 retired by design

**Not tested.**

Design decision D6 makes the tech-lead the only external voice: specialists return structured findings and never touch the network. Whether the Codex `read-only` sandbox blocks outbound network therefore has no bearing on the package. Recorded so a later reader does not re-open it looking for evidence.

Consequence: no probe needed. If D6 is ever reversed, Q14 reopens.

---

## E2 — installed versions versus research targets (tranche C)

**Date** 2026-09-07.

```console
$ for c in claude codex opencode agy; do printf '%s: ' "$c"; "$c" --version; done
claude: 2.1.263 (Claude Code)
codex: codex-cli 0.153.4
opencode: 1.18.29
agy: 1.1.27

$ pacman -Q antigravity antigravity-cli
antigravity 2.12.2-1
antigravity-cli 1.1.27_5211191891591168-1
```

| tool | researched at | installed | moved? |
|---|---|---|---|
| Claude Code | 2.1.261 | 2.1.263 | yes |
| Codex CLI | 0.153.4 | 0.153.4 | no |
| opencode | 1.18.25 | 1.18.29 | yes |
| agy | 1.1.26 | 1.1.27 | yes |
| Antigravity desktop | 2.11.0 | 2.12.2 | yes |

**Verdict**: four of five tools moved within a day of the research. **Consequence**: tranche C is not optional. Every claim carrying a version gate is re-verified before code depends on it; `docs/SUPPORT-MATRIX.md` records the version each claim was last confirmed at.

---

## E3 — Q18: the agy `agents:` frontmatter key is now present (tranche C)

**Date** 2026-09-07. **agy 1.1.27** (`/usr/bin/agy`).

AG-02 records: "1.1.27 adds an `agents:` list … the installed agy is 1.1.26 and neither local binary has a `yaml:"agents,` tag (grep count 0), so a package emitting `agents:` must gate on CLI >= 1.1.27".

```console
$ command -v strings agy
/usr/sbin/strings
/usr/sbin/agy

$ agy --version
1.1.27

$ strings -n 6 /usr/bin/agy | /usr/bin/grep -c 'yaml:"agents'
1

$ strings -n 6 /usr/bin/agy | /usr/bin/grep -c 'yaml:"mainAgent'      # sanity check: a tag known to exist
1
```

**Verdict**: confirmed present. AG-02's version gate has flipped on this machine. The `mainAgent` count is included so an empty result cannot be mistaken for a working grep — a zero on both lines would have meant a broken command, not a finding.

**Consequences**: (1) the design may not assume the key is absent; (2) AG-05's flat-team story needs re-reading, since an `agents:` list may be a cleaner lever than relying on a `tools` allowlist to override ambient subagent inheritance — folded into Q8; (3) `check.py --agy-tools` depends on the verified tool-name list, which must be re-derived at 1.1.27 rather than inherited from the 1.1.26 research.

**Still unknown**: what the key does at runtime, and its behaviour on 1.1.26 (irrelevant here, since the minimum shifts to 1.1.27 if the package emits it). The Antigravity desktop 2.12.2 `language_server` has not been re-checked.

---

## E4 — Q19: the Codex read-only sandbox runs tests but permits no write anywhere (tranche A)

**Date** 2026-09-07. **codex-cli 0.153.4.** Probed with `codex sandbox`, which runs a command under the sandbox with no model turn.

Fixture: a throwaway project at `<scratch>/m0/proj` with `src/calc.py`, two stdlib `unittest` tests and `make test` → `python3 -m unittest discover -s tests -q`. The suite passes unsandboxed and writes `__pycache__/*.pyc` as a side effect, so it is a realistic "test run that writes build artifacts".

```console
$ make test                                   # unsandboxed control
Ran 2 tests in 0.000s
OK
$ find . -name '*.pyc' | wc -l
2

$ find . -name __pycache__ -type d -exec rm -rf {} +
$ codex sandbox -c sandbox_mode=read-only -c approval_policy=never -- make test
python3 -m unittest discover -s tests -q
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
exit=0
$ find . -name '*.pyc' | wc -l
0
```

The suite **passed** and wrote **nothing**: CPython silently skips writing `__pycache__` when the directory is not writable.

The boundary, same sandbox (`read-only` + `never`), one command each:

| probe | result |
|---|---|
| `echo x > ./canary.txt` (workspace) | `rc=1  sh: ./canary.txt: Read-only file system` |
| `echo x > /tmp/m0-canary.txt` | `rc=1  /tmp/m0-canary.txt: Read-only file system` |
| `echo x > "$TMPDIR/…"` | `rc=1  Read-only file system` |
| `echo x > "$HOME/m0-canary.txt"` | `rc=1  Read-only file system` |
| `mkdir -p ./build` | `rc=1  cannot create directory ‘./build’: Read-only file system` |
| `head -1 src/calc.py` | `rc=0` — reads fine |
| `git status --porcelain` | `rc=0` |
| `git commit --allow-empty` | `rc=128  fatal: Unable to create '…/.git/index.lock'` |
| `curl -m 8 https://example.com` | `rc=6  Could not resolve host: example.com` |

Control at `sandbox_mode = "workspace-write"` + `never`: the same `make test` wrote its 2 `.pyc` files, and `/tmp` was writable.

**Verdict**: read-only permits a test suite to **execute**, and R3 evidence is therefore possible — but only for a suite that writes nothing at all. The sandbox is total: workspace, `/tmp`, `$TMPDIR` and `$HOME` are all read-only, so it is not merely the workspace that is protected.

**Consequences**:
1. The design's central guarantee survives — `read-only` + `never` is strict *and* a reviewer can still run tests and cite output.
2. But §8's fallback ("a per-project `hosts.codex.sandbox_mode: workspace-write` override for the reviewer with a `check.py` warning") will be the **common** case, not the rare one: any suite that compiles to a build directory, writes a coverage or report file, or uses a scratch temp file will fail — a Gradle or Maven build certainly will. The design must say this plainly rather than treating the override as an edge case.
3. There is no in-between setting. `sandbox_workspace_write.writable_roots` only *adds* roots and applies only when `sandbox_mode = "workspace-write"`, which always makes the workspace itself writable. `exclude_slash_tmp` and `exclude_tmpdir_env_var` only subtract. So "read-only workspace plus a writable scratch dir" is not expressible through `sandbox_mode`.
4. Lead, not yet settled: the beta `[permissions.<name>]` profiles (config reference: built-ins `:read-only`, `:workspace`, `:danger-full-access`; "Don't combine with `sandbox_mode` or `[sandbox_workspace_write]`") may express it. `-c permissions.default=":read-only"` is **not** the invocation — it fails `invalid type: string ":read-only", expected struct PermissionProfileToml in `permissions``. Worth a probe before the reviewer's Codex dialect is settled.

**Bonus, recorded not sought**: the network probe shows the read-only sandbox blocks outbound DNS. That is the evidence retired Q14 (E1) would have gathered. D6 stands on its own; this only means a reversal of D6 would find read-only unusable for posting.

---

## E5 — Q4: a symlinked Codex role TOML is discovered but fails at spawn (tranche A)

**Date** 2026-09-07. **codex-cli 0.153.4**, model `gpt-6-astra`.

CX-02 predicts it from source: `core/src/agent/role.rs` reads the role's `config_file` with `read_sensitive_file_to_string`, which opens `O_NOFOLLOW` and fails on a symlink at the final path component, surfacing as `AGENT_TYPE_UNAVAILABLE_ERROR`. This gates any migration from a symlink-installed layout.

Both runs used the **same file content** at `~/.codex/agents/m0-reviewer.toml`, differing only in symlink versus regular file, and the same prompt. No pre-existing agent file was touched; only `m0-reviewer.toml` was added and then removed.

```console
$ ln -sfn <scratch>/m0/agents-src/m0-reviewer.toml ~/.codex/agents/m0-reviewer.toml
$ codex exec -C <proj> -s read-only --skip-git-repo-check \
    "Delegate to a sub-agent: spawn one sub-agent of agent_type 'm0-reviewer' with the message
     'report'. This is an explicit request for sub-agent delegation. Then report VERBATIM either
     the sub-agent's reply or the exact error text you received. Do not do the work yourself."

2026-09-07T21:26:11.141123Z ERROR codex_core::tools::router: error=agent type is currently not available
codex
agent type is currently not available
```

```console
$ rm ~/.codex/agents/m0-reviewer.toml
$ cp <scratch>/m0/agents-src/m0-reviewer.toml ~/.codex/agents/m0-reviewer.toml   # real file
$ codex exec …same prompt…

codex
🕵️ Reviewer: SPAWN-OK
```

**Verdict**: confirmed exactly as inferred. The error text is `agent type is currently not available`, matching `AGENT_TYPE_UNAVAILABLE_ERROR`. A symlinked role TOML is a silently missing persona at spawn time, not a load error.

**Consequences**:
1. §9's "Real files, never symlinks" is now measured, not inferred. `bootstrap.py --scope user` must write copies, and `check.py` should refuse to emit a symlink into an agents directory.
2. A symlink-installed layout is **broken, not merely fragile** — such personas cannot spawn at all. Replacing it with real files is a fix, not a tidy-up.
3. Two facts fell out of the control run: a spawned child does receive its role's `developer_instructions` (it returned the signature the TOML told it to use), and `codex exec` will spawn when the prompt explicitly asks for sub-agent delegation by name, consistent with CX-05.

---

## E6 — Q5 and Q15: Codex root-as-plugin marketplace, and the plugin cache layout (tranche A)

**Date** 2026-09-07. **codex-cli 0.153.4.** Fixture: the throwaway tree carrying all three manifests.

### Q5 — which `source` forms resolve a root-as-plugin entry

`codex plugin marketplace add <dir>` registered the fixture and **Codex wrote the record into `~/.codex/config.toml` itself** — a `[marketplaces.e-colleagues]` table with `source_type = "local"`. This is the working rule in action: the package never writes that file; Codex does.

With the marketplace registered, `.agents/plugins/marketplace.json` was rewritten in place once per candidate `source` form and `codex plugin list` re-run:

| `source` value | resolves? |
|---|---|
| `"./"` | yes |
| `"."` | yes |
| `{"source": "local", "path": "./"}` | yes — the form design §6 specifies |
| `{"type": "local", "path": "./"}` | no |
| `{"local": {"path": "."}}` | no — fails with `plugin ... was not found in marketplace ...` |

```console
$ codex plugin add e-colleagues@e-colleagues
Added plugin `e-colleagues` from marketplace `e-colleagues`.
Installed plugin root: ~/.codex/plugins/cache/e-colleagues/e-colleagues/0.0.0
```

### Q15 — cache layout

The layout is `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`, and the **entire source tree is copied verbatim** — `skills/`, but also `dist/` (including `dist/codex/agents/reviewer.toml`), the root `plugin.json`, `.claude-plugin/`, `.codex-plugin/` and `.agents/`.

**Consequences**:
1. §6's marketplace entry is correct as written; `gen.py` may emit either it or the bare `"./"`.
2. §9's open question — "locating the script after a plugin install" — is answered: the bootstrap script travels with the plugin and is reachable at `~/.codex/plugins/cache/<mkt>/<plugin>/<version>/skills/ec-init/scripts/bootstrap.py`. But **the version is a path segment**, so nothing may hardcode it; the skill must resolve the script relative to its own `SKILL.md`, which is what §6 already requires for a different reason.
3. `codex plugin remove` needs the qualified form: bare `codex plugin remove e-colleagues` fails with `plugin requires --marketplace unless passed as <plugin>@<marketplace>`.

### Bonus — both root-`plugin.json` invariants from §6, now measured

§6 asserts two invariants `check.py` must enforce. Both were tested by giving the root manifest version `9.9.9` and `.codex-plugin/plugin.json` version `0.0.0`, so the installed cache path names the manifest Codex adopted:

| root `plugin.json` | installed root | adopted manifest |
|---|---|---|
| `$schema: https://antigravity.google/schemas/v1/plugin.json` | `…/e-colleagues/0.0.0` | `.codex-plugin/plugin.json` ✅ |
| no `$schema` at all | `…/e-colleagues/0.0.0` | `.codex-plugin/plugin.json` |
| `$schema: https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` | `…/e-colleagues/9.9.9` | **the root manifest** — the forbidden case |
| Antigravity schema, but the file is a **symlink** | `…/e-colleagues/local` | **neither** — no version resolved |

**Verdict**: §6 is right that an agent-plugins.org schema on the root manifest hijacks Codex's manifest resolution, and right that a symlinked root manifest breaks it. One correction to §6's wording: a symlinked root `plugin.json` does not make Codex "see no plugin at all" — the install still succeeds, but no manifest version resolves and the plugin lands in an unversioned `local` directory. The consequence for `check.py` is unchanged; the predicted failure mode is not.

---

## E7 — Q6: `agy plugin validate` and `install` accept the three-manifest tree (tranche A)

**Date** 2026-09-07. **agy 1.1.27.**

```console
$ agy plugin validate <fixture>
  [ok]    <fixture>
          ✔ skills      : 1 processed
          ✔ agents      : 2 processed
          - commands    : skipped (not found)
          - mcpServers  : skipped (not found)
          - hooks       : skipped (not found)
exit=0
```

**Verdict**: Antigravity validates the tree with the expected component counts and says nothing about the foreign `.claude-plugin/`, `.codex-plugin/` or `.agents/plugins/` directories, or about `dist/`. The three manifests coexist. §13 item 3's gate (`must print [ok] with the expected component counts`) is implementable exactly as written.

Note the counts come from the Antigravity-format `agents/<name>/agent.md` tree, not from `dist/claude/agents/`, which agy ignores — the mirror image of the Claude arrangement in §6.

---

## E8 — Q12 and Q11: Antigravity install destination, re-install semantics, and URL syntax (tranche A)

**Date** 2026-09-07. **agy 1.1.27.** `~/.gemini/config/config.json` and the plugins tree were snapshotted before and diffed after; both were restored to byte-identical state at the end (see Reversal).

### Q12 — destination and second install

```console
$ agy plugin install <fixture>
  [ok]    e-colleagues
          ✔ skills      : 1 processed
          ✔ agents      : 2 processed
```

- **Destination**: `~/.gemini/config/plugins/e-colleagues/` — the global root AG-08 names, confirmed at 1.1.27. `~/.gemini/antigravity-cli/plugins/` does not exist, as AG-08 predicted.
- **The whole tree is copied verbatim**, including `dist/`, `.claude-plugin/`, `.codex-plugin/` and `.agents/`. So the bootstrap script travels with the plugin here too.
- **`config.json` is not touched.** After the install it was byte-identical to the snapshot and contained no `e-colleagues` key. AG-08's "enablement is recorded in config.json keyed by directory name" is about `agy plugin enable/disable`; a plain install writes no entry, so a freshly installed plugin is enabled by absence rather than by record.
- **`agy plugin list`** reported the plugin under `imports`, and reported `No imported plugins.` again as soon as the directory was deleted — no separate registry file exists (`grep -rl importedAt ~/.gemini/config/` found none), so the listing is derived from the directory.
- **A second install MERGES; it does not replace.** A marker file added to the source, installed, then deleted from the source and re-installed, **survived** in the destination:

```console
$ echo modified-marker > <fixture>/skills/ec-tech-lead/MARKER.txt
$ agy plugin install <fixture>            # marker now in the destination
$ rm <fixture>/skills/ec-tech-lead/MARKER.txt
$ agy plugin install <fixture>
$ ls ~/.gemini/config/plugins/e-colleagues/skills/ec-tech-lead/
MARKER.txt  SKILL.md
```

**Consequence**: on Antigravity an upgrade leaves deleted files behind. A roster change that drops a persona — exactly what `--prune` exists for (§2.2) — would leave the removed `agents/<name>/agent.md` in place and the persona still selectable. The update story must uninstall-then-install, or delete known-stale paths explicitly. This is new: the design listed second-install behaviour as unknown and assumed nothing.

### Q11 — install target syntax

| target | result |
|---|---|
| `gnuruzzi/e-colleagues` | `Error: install target must be a directory: gnuruzzi/e-colleagues` |
| `https://github.com/gnuruzzi/e-colleagues` | **accepted** → `Cloning plugin from https://github.com/gnuruzzi/e-colleagues.git...`, running `git clone --depth 1 <url>.git /tmp/plugin-install-<n>` |
| `http://127.0.0.1:8731/e-colleagues.git` (local HTTP git server) | `Error: failed to parse GitHub URL: currently only supports github.com: 127.0.0.1:8731` |
| `file:///…/e-colleagues.git` | `Error: install target must be a directory` |
| `git@github.com:gnuruzzi/e-colleagues.git` | `Error: unknown marketplace: github.com:gnuruzzi/e-colleagues.git` — the `@` makes it parse as `plugin@marketplace` |
| `e-colleagues@antigravity`, `e-colleagues@google` | `Error: unknown marketplace: <name>` |

The `https://github.com/...` run was observed with `pstree`, which showed `agy → git clone --depth 1 … → git-remote-http → askpass`: it hung only because the repository was not yet published at the time and git had no TTY for credentials. The clone path itself is real and reached.

**Verdict**: `agy plugin install <github-url>` **is** supported, for `github.com` HTTPS URLs only. `owner/repo` shorthand, other git hosts, `file://`, SSH form and `plugin@marketplace` are all rejected, the last confirming AG-08.

**Consequence**: §7's "Not offered, because unverified or measured absent: `agy plugin install <github-url>`" can be **reversed** — the README may document `agy plugin install https://github.com/<owner>/e-colleagues` alongside the clone-then-install-directory route. One residual unknown: the installed directory name for a URL install was not observed (the repository is unpublished), and AG-07/AG-08 key enablement by directory name, so this must be confirmed once the repository is public.

### Addendum 2026-09-20 — the URL install, measured against the published repository (#3)

**agy 1.2.6** — the CLI had moved from the 1.1.27 everything above was measured at; see the
version-drift note in `SUPPORT-MATRIX.md`.

```console
$ agy plugin install https://github.com/gnuruzzi/e-colleagues
Cloning plugin from https://github.com/gnuruzzi/e-colleagues.git...
  [ok]    e-colleagues
          ✔ skills      : 4 processed
          ✔ agents      : 6 processed

$ ls ~/.gemini/config/plugins/ | grep e-colleagues
e-colleagues
$ agy agents
flutter_a11y_agent
tech-lead
```

**Verdict**: the URL install lands at `~/.gemini/config/plugins/e-colleagues/` — the directory
takes the repository's name, so D1's requirement that the installed directory be
`e-colleagues` holds for the URL route as well as the local one. `config.json` was untouched,
as for a directory install. The residual question E8 left open is closed. Reversed afterwards;
the plugins tree and `config.json` were verified identical to the pre-experiment snapshot.

### Reversal

```console
$ rm -rf ~/.gemini/config/plugins/e-colleagues
$ diff <snapshot>/gemini-config.json ~/.gemini/config/config.json    # IDENTICAL
$ diff <snapshot>/gemini-plugins-tree.txt <after>                    # IDENTICAL
$ agy plugin list
No imported plugins.
```

---

### Addendum 2026-09-27 — `plugin@marketplace` is parsed at agy 1.2.10 and resolves against nothing a user can register (#14)

**agy 1.2.10.** `agy plugin --help` now reads `install <target>       Install a plugin (supports plugin@marketplace)` and lists a new `link <mp> <target>     Generate link to a marketplace`. E8 recorded `plugin@marketplace` as measured absent at 1.1.27, so both were probed, against a scratch copy of this repository, with the Antigravity config tree listed before and diffed after every command.

| command | result |
|---|---|
| `agy plugin install e-colleagues@e-colleagues` — a marketplace name Claude Code has registered on this machine (E23) | rc 1, `Error: unknown marketplace: e-colleagues` |
| `agy plugin install definitely-not-a-plugin@claude-plugins-official` — Claude's default marketplace | rc 1, `Error: unknown marketplace: claude-plugins-official` |
| `agy plugin install definitely-not-a-plugin@not-a-marketplace` — control | rc 1, `Error: unknown marketplace: not-a-marketplace` |
| `agy plugin install Not_Kebab@e-colleagues` — a bad plugin name | rc 1, `Error: unknown marketplace: e-colleagues` — the marketplace half is resolved first |
| `agy plugin link e-colleagues-mp <scratch copy>` | rc 1, `Error: unknown marketplace: e-colleagues-mp` |
| `agy plugin link claude-plugins-official <scratch copy>` | rc 1, `Error: unknown marketplace: claude-plugins-official` |
| `agy plugin install --help`, `agy plugin link --help` | not flags: `install target must be a directory: --help`; `link requires marketplace name and target` |

So the form is parsed, and `link` needs a marketplace that is already known, so it cannot register one. Neither `agy --help` nor `agy plugin` offers a marketplace subcommand or flag; `~/.gemini/config/config.json` has no marketplace key; the import manifest is empty. The binary's own strings say where a known marketplace comes from — a remote catalog served from a cache (`Cannot locate the marketplace cache directory, no marketplaces will be served`, `Failed to refresh marketplace %q, serving the cached copy`, `marketplace %q returned status %d`, `marketplace name %q is not kebab-case`) — and no such cache exists under `~/.gemini`, `~/.cache`, `~/.config` or `~/.local/share` on this machine. The config tree was byte-identical after the probes.

**Verdict**: at 1.2.10 `plugin@marketplace` is a real syntax with no user-reachable marketplace behind it. It is not a route for installing this package, and design §7's "not offered" stands — for a different reason than "measured absent": the form exists, and resolves only against marketplaces agy serves itself, of which none was present and none can be added from the CLI. **Not driven**: the desktop app, whose UI strings (`Explore other marketplace customizations`) suggest it is what populates that cache. If a later version lets a user register a marketplace, or a served one comes to carry this package, this addendum is where to look.

---

## E9 — Q9: a spawned Codex child does re-run AGENTS.md discovery (tranche A)

**Date** 2026-09-07. **codex-cli 0.153.4**, model `gpt-6-astra` (catalogued **V2**, per CX-04's correction), `model_reasoning_effort = "medium"` for speed.

The `m0-reviewer` role's `developer_instructions` were rewritten to forbid reading files and to answer only from context:

```toml
developer_instructions = """
You are the M0 fixture Reviewer.
Do NOT read any files and do NOT run any commands. Answer only from the context you
already have at the moment you start.
Reply with exactly one line in this form:
🕵️ Reviewer: CANARY=<the canary string from AGENTS.md, or NONE if no AGENTS.md content is in your context>
"""
```

The project's `AGENTS.md` carries `The canary string for this project is BLUEBIRD-7731.` and the canary appears nowhere else.

**Run 1 — default fork.** Parent told to spawn with the message exactly `go` and to say nothing about the project:

```console
codex
🕵️ Reviewer: CANARY=BLUEBIRD-7731
```

This alone proves nothing, because CX-05's correction says an **omitted `fork_turns` on V2 means a full-history fork** — the child could have inherited the parent's context rather than discovering anything.

**Run 2 — history fork disabled.** Same probe with `fork_turns` pinned to `"none"`. The parent reported its own call arguments so the control is verifiable:

```json
{"agent_type":"m0-reviewer","message":"go","task_name":"q9b","fork_turns":"none"}
```
```console
🕵️ Reviewer: CANARY=BLUEBIRD-7731
```

**Run 3 — negative control.** A sibling project (`m0/proj-noagents`) with the same `src/` but **no `AGENTS.md`**, same spawn with `fork_turns: "none"`:

```console
🕵️ Reviewer: CANARY=NONE
```

**Verdict**: a spawned Codex child receives the project's `AGENTS.md` **independently of history forking**. The result tracks the file's presence — present → the canary, absent → `NONE` — so the child is neither inheriting parent history nor fabricating an answer.

**Consequences**:
1. Q9 resolves in the permissive direction, so §5.4's list of "UNVERIFIED whether the child sees AGENTS.md" loses its Codex entry.
2. It changes **nothing** in the architecture, and that is the point: D4/§5.4 already decided that knowledge is never assumed to arrive ambiently and that **every delegation brief names the files the child must read**. Q9 turns that from a necessity into belt-and-braces on Codex. The rule stays, because opencode (Q7) and the Antigravity desktop are still open and the rule costs nothing.
3. Practical consequence for the managed block: the contract *does* reach a Codex specialist, so the block's spawn sentence and return contract are in the child's context without the parent repeating them.

**Caveat**: the child was *instructed* not to read files and self-reported compliance; the probe cannot prove it ran no command. The three-run contrast makes reading-instead-of-injection an unlikely explanation but not an excluded one. If that distinction ever matters, re-probe with a canary that is not readable from the child's cwd.

---

## E10 — Q1 and Q2: Claude ignores the Antigravity root `agents/`, but bare `subagent_type` names do not resolve (tranche A)

**Date** 2026-09-07. **Claude Code 2.1.263.** Fixture loaded with `claude --plugin-dir <fixture> --agent tech-lead -p …`.

To make Q1 falsifiable the fixture's root `agents/` was given a **decoy** that Claude would load if it ever scanned that directory: `agents/decoy-antigravity.md`, a well-formed Claude agent named `decoy-antigravity`, sitting in Claude's *default* scan location while `.claude-plugin/plugin.json` listed only `./dist/claude/agents/{tech-lead,reviewer}.md`.

### Q1 — the manifest `agents` list replaces the default scan

The lead was asked to enumerate its available `subagent_type` values. The list contained:

```
… e-colleagues:reviewer, e-colleagues:tech-lead, Explore, feature-dev:code-architect, … general-purpose, Plan, …
```

`decoy-antigravity` was **absent**, and a direct follow-up returned `DECOY-VISIBLE: no`.

**Verdict**: confirmed. `agents` in the plugin manifest REPLACES the default `agents/` scan [CC-02], so the root `agents/` tree may hold the Antigravity dialect without Claude ever reading it. §6's polyglot layout works at runtime, not just in `validate`.

### Q2 — bare names do NOT resolve as `subagent_type`

The design assumed a bare name would resolve. It does not:

```
SPAWN-FAILED: Agent type 'reviewer' not found. Available agents: claude, …,
e-colleagues:reviewer, e-colleagues:tech-lead, Explore, …
```

The qualified name works:

```
SPAWNED: 🕵️ Reviewer: — No write tool was available; the file was not created.
```

Note the asymmetry, which CC-03's nuance 2 covers for one case only: **`--agent tech-lead` (bare) resolved fine** — the session ran as the tech-lead and used its signature — while `subagent_type: "reviewer"` did not. Bare-name lookup applies to the `--agent` CLI flag, not to the Agent tool's `subagent_type`, at least when the agent comes from a plugin.

**Consequences**:
1. **The managed block's spawn sentence is wrong for Claude.** §5.1 has the lead delegate "sub-agents of exactly these types: developer, reviewer, security, designer, platform" — bare names, which are correct on Codex (proven in E5) and wrong here. Either the block carries both forms, or the Claude tech-lead body carries the `e-colleagues:`-qualified roster while the host-neutral block stays generic. The second is the better fit for §3's rule that no tool vocabulary appears in `personas/` — the qualification is a host fact, so it belongs to the Claude renderer in `hosts/claude.yaml`.
2. It also settles the naming half of D1: because the qualified form is `<plugin>:<agent>`, the plugin name is load-bearing in every Claude delegation string, not only in skill invocation.
3. §13 item 12's manual checklist must spawn `e-colleagues:<name>`, not `<name>`.

### Bonus — the read-only reviewer held, and §8's Bash fail-open is real

The spawned `e-colleagues:reviewer` reported its own toolset as `Read` and `Bash` only, with no `Write`, `Edit` or `NotebookEdit` — the `tools:` allowlist applied as [CC-07] predicts. Asked to create `/tmp/m0-claude-canary.txt` it could not, and the file was verified absent afterwards.

But the reason it could not is **not** the persona contract. The block came from the session's working-directory sandbox:

```
Output redirection to '/tmp/m0-claude-canary.txt' was blocked. For security, Claude Code
may only write to files in the allowed working directories for this session: '…'
```

The subagent itself flagged the gap: a Bash-enabled read-only reviewer could still write *inside* the working directory. That is exactly the fail-open §8 lists ("Bash is a write path on Claude, opencode and Antigravity") and it means the `/tmp` refusal must not be mistaken for evidence that the contract holds.

---

## E11 — Q16: the V2 concurrency ceiling is three spawned children, and it refuses rather than queues (tranche A)

**Date** 2026-09-07. **codex-cli 0.153.4**, model `gpt-6-astra` (V2 backend), **no `[agents]` block in `~/.codex/config.toml`**, so `max_concurrent_threads_per_session` is at its V2 default of 4.

A dedicated `m0-timer` role was installed at user scope whose whole job is to bracket a fixed sleep with timestamps, so concurrency is measured rather than asserted:

```toml
developer_instructions = """
Run this single shell command and nothing else:
  sh -c 'date +%s.%N; sleep 25; date +%s.%N'
Then reply with exactly one line:
TIMER <the message you were given> START=<first timestamp> END=<second timestamp>
"""
```

The primary was asked to spawn **five** of them at once and report any spawn error verbatim:

```console
2026-09-07T21:36:10.735448Z ERROR codex_core::tools::router: error=collab spawn failed: agent thread limit reached
2026-09-07T21:36:15.599049Z ERROR codex_core::tools::router: error=collab spawn failed: agent thread limit reached

TIMER A START=1788816961.626005409 END=1788816986.629773617
TIMER B START=1788816964.867883007 END=1788816989.871200937
TIMER C START=1788816970.907885743 END=1788816995.911487912
SPAWN-ERROR: collab spawn failed: agent thread limit reached
SPAWN-ERROR: collab spawn failed: agent thread limit reached
```

Each child slept 25.0 s, and the three intervals overlap for **15.7 s**, so all three ran genuinely concurrently rather than in sequence.

**Verdict**: CX-04 is confirmed exactly. `max_concurrent_threads_per_session` **counts the primary**, so the default of 4 permits **three** concurrent spawned children. Three succeeded, two failed.

**Consequences**:
1. §5.4 step 4's arithmetic stands: six lenses is **two waves** of three at the default.
2. **New, and it changes `ec-onboard`**: over-spawning **refuses**, it does not queue. The error is `collab spawn failed: agent thread limit reached`, raised at spawn time. So the lead cannot fire all six lenses and let the runtime schedule them — the skill must batch explicitly, and must treat that error as a wave boundary rather than a lens failure. The design said "in waves sized to the host's concurrency ceiling"; this is why that wording is load-bearing.
3. The ceiling is a config value a user may have changed, so `ec-onboard` should not hardcode 3. Reading `[agents] max_concurrent_threads_per_session` where present, defaulting to 4-minus-primary, and treating the refusal as backpressure is the robust shape.

---

## E12 — Q17: in an untrusted Codex clone the project skill loads and the project agent does not (tranche A)

**Date** 2026-09-07. **codex-cli 0.153.4.**

A fresh repository at `<scratch>/m0/untrusted`, **absent from `~/.codex/config.toml`'s `[projects.*]` table**, carrying both halves of the contrast:

- `.agents/skills/ec-tech-lead/SKILL.md` — the portable floor, whose body ends "say the exact words: TECH-LEAD CONTRACT ADOPTED, and then report the project-skill canary MAGPIE-4402"
- `.codex/agents/m0-projonly.toml` — a project-scope agent

One `codex exec` run asked for both:

```console
codex
👨‍💻 Tech-Lead: TECH-LEAD CONTRACT ADOPTED
MAGPIE-4402

2026-09-07T21:38:30.124735Z ERROR codex_core::tools::router: error=unknown agent_type 'm0-projonly'
codex
👨‍💻 Tech-Lead: PROJECT-AGENT-ERROR: unknown agent_type 'm0-projonly'
```

`grep -c "<path>" ~/.codex/config.toml` returned `0` after the run, confirming the folder was never trusted along the way.

**Verdict**: both halves confirmed in one run. Project skills are **not** trust-gated — the CX-03 correction is right, `$ec-tech-lead` resolves, its body is followed, and the canary proves the skill file itself was read rather than the name merely recognised. Project agents **are** trust-gated and fail loudly with `unknown agent_type '<name>'`.

**Consequences**:
1. D7's portable floor works where it is most needed: the teammate who clones and does not trust still gets the Tech-Lead contract.
2. §8's prediction is exact: "In an untrusted Codex project the agents are absent and the sentence produces a loud `unknown agent_type`". The managed block's instruction to invoke `ec-tech-lead` first is the correct mitigation, and the error is loud enough to be self-explaining.
3. `ec-init`'s route B (per-repo vendoring) degrades predictably: skills work untrusted, personas need the trust dialog.

---

## E13 — §8's Bash write path on Claude, measured rather than argued

**Date** 2026-09-07. **Claude Code 2.1.263.** Not a numbered unknown — §8 asserts it, and the fixture made it cheap to check.

The rendered read-only reviewer (`tools: Read, Grep, Glob, Bash`, no `memory`) was spawned as `e-colleagues:reviewer` and **asked to do something entirely within its role**: run the project's test suite. The persona spec permits exactly this (`shell: true  # may run the project's test/lint commands`). No instruction to violate the contract was given.

```console
pyc files before: 0
   … reviewer runs `make test`, reports 2/2 passing …
pyc files after: 2
tests/__pycache__/test_calc.cpython-314.pyc
src/__pycache__/calc.cpython-314.pyc
```

**Verdict**: a read-only Claude reviewer wrote two files into the workspace while doing its job correctly. Bash is a write path, mechanically, with no misbehaviour involved.

Why the test is framed this way: an earlier probe *asked* the reviewer to create a file, and it declined on role discipline — its own report noted that "absence is evidence for the negative claim, not proof of it", and that with `Bash` unrestricted a write "would almost certainly have succeeded". Asking a well-behaved agent to misbehave measures the prompt, not the capability. Running the tests measures the capability.

**Consequences**:
1. §8's "editor tools mechanical; Bash writes" is confirmed for Claude, and so is the honesty of the enforcement matrix: on Claude, read-only is a *tool-surface* guarantee, not a filesystem one. Only Codex's `read-only` + `never` is mechanical for the shell too (E4).
2. It sharpens the contrast E4 sets up: Codex buys a real filesystem guarantee at the price of a reviewer that cannot run a writing test suite; Claude buys a reviewer that can run anything at the price of the guarantee. That trade belongs in §8 explicitly.
3. A refusal from `/tmp` must never be cited as evidence the contract holds — that block came from the session working-directory sandbox, not from the persona (E10).

---

## E14 — Q10: `-c developer_instructions=""` clears the layered value for one session (tranche A)

**Date** 2026-09-07. **codex-cli 0.153.4.**

`~/.codex/m0probe.config.toml` was created as a profile layer (top-level keys, not nested — as `config-advanced.md` requires):

```toml
developer_instructions = """
You are the M0 probe Tech-Lead.
Begin every reply with the exact token: DEVINSTR-ACTIVE-KESTREL-9120
"""
```

Four runs of the same prompt, `Say only the word ping.`:

| invocation | last message |
|---|---|
| `codex exec` (no profile) | `ping` |
| `codex exec --profile m0probe` | `DEVINSTR-ACTIVE-KESTREL-9120 ping` |
| `codex exec --profile m0probe -c developer_instructions=""` | `ping` |
| `codex exec --profile m0probe -c developer_instructions="…OVERRIDE-TOKEN-SISKIN-3311"` | `OVERRIDE-TOKEN-SISKIN-3311 ping` |

**Verdict**: `-c developer_instructions=""` **clears** the layered value for that session, and a non-empty `-c` **replaces** rather than merges. The escape hatch §9 assumed exists.

**Consequence for §9, and a correction of scope**: the two profile runs also confirm the user-scope tech-lead delivery route end to end — `--profile <name>` really does layer `$CODEX_HOME/<name>.config.toml` over the base config (binary help: "Layer $CODEX_HOME/<name>.config.toml on top of the base user config"), and `developer_instructions` from that file reaches the model. §9's "tech-lead: `~/.codex/e-colleagues.config.toml` → `codex --profile e-colleagues`" works.

**New fail-open worth a guard**: an unknown profile name is **silently ignored**, not an error. `codex exec --profile definitely-not-a-profile "Say only ping."` ran normally and answered `ping`, exit 0. So a typo in the documented install command yields a session with no tech-lead and no complaint. The README's invocation and any wrapper should be exact, and `ec-status` is the natural place to check that the profile file exists.

**Caveat on scope**: this was measured against the **profile** layer. Q10 as written asks about the **trusted-project** `.codex/config.toml` value, which cannot be exercised without the trust dialog. The precedence chain makes the same outcome very likely (both are config layers below `-c`), but the project layer specifically moves to tranche B alongside Q3 and Q13.

---

## E15 — `claude plugin validate` does not catch every agent frontmatter error, and a colon in the value hides the rest

**Date** 2026-09-07. **Claude Code 2.1.263.** Not a numbered unknown — this contradicts design §13 item 2, which rests the whole [CC-07] fail-open guard on one validate invocation.

§13 item 2 says `claude plugin validate --strict ./dist/claude/agents` (directory mode) "is the one that catches an agent YAML parse error — the fail-open case of [CC-07]". It catches *some*, and the exception is the shape this package ships.

### What directory mode does catch

An unterminated quote whose value contains **no colon**, inside a tree with an ancestor `.claude-plugin/`:

```console
$ claude plugin validate --strict <plugin>/dist/claude/agents
  ❯ frontmatter: YAML frontmatter failed to parse: YAML Parse error: Unexpected character.
    At runtime this agent does not load at all — with no frontmatter name it is treated as
    a co-located reference document and skipped.
✘ Validation failed
```

Also caught: a missing `description` (a warning, an error under `--strict`).

### What it does not catch

Same tree, same kind of break, but the value contains a colon — and the design's canonical routing sentence does (`description: Use for adversarial review of an in-review change: edge cases, races, leaks, coverage.`):

| agent frontmatter | `--strict` result |
|---|---|
| `description: " unterminated quote here` | **caught** |
| `description: "Adversarial review: unterminated quote.` | **passed** ✔ |
| `description: Use for adversarial review: edge cases, races, leaks.` (unquoted colon — normally a YAML error) | **passed** ✔ |
| `name: rev:iewer` (a colon in `name`, rejected since 2.1.218 per CC-03) | **passed** ✔ |
| `permissionMode: bypassPermissions`, `hooks: {}`, `mcpServers: {}` (the three keys CC-07 says are ignored in plugin agents) | **passed** ✔ |
| `permision: nonsense` (misspelled key) | **passed** ✔ |
| `memory: true` on a `tools`-restricted reviewer (the CC-07 trap that re-enables Write and Edit) | **passed** ✔ |

The first two rows were confirmed genuinely malformed with `yaml.safe_load`, which raised `ScannerError while scanning a quoted scalar` — so the pass is validate's leniency, not a well-formed input. A colon in the value evidently triggers a repairing sanitizer, the same shape opencode has ([OC-02] "unquoted colons in YAML values are auto-sanitised").

Two mechanics worth recording because they cost time to find:

- Directory mode needs an **ancestor `.claude-plugin/`**. Pointed at a bare directory it reports `No manifest found in directory. Expected .claude-plugin/marketplace.json or .claude-plugin/plugin.json` and exits 1, which looks like a validation failure but is a mode error.
- `--json` reports `"contents": []` both for a clean directory and for one where nothing was recognised, so an empty `contents` cannot be read as "validated and fine".
- Validating the **plugin manifest** (`.claude-plugin/plugin.json`) does open skills and reports a broken `SKILL.md`, but does not report broken agents. Skills are better covered than agents.

**Consequences**:
1. **§13 item 2 must be rewritten.** Validate is worth running, but it is not the guard for [CC-07]. `check.py` must parse every rendered Claude agent's frontmatter itself with a strict YAML parser and assert the key whitelist — which §13 item 2 already says for `permissionMode`/`hooks`/`mcpServers` ("`check.py` forbids those keys itself") and must now also say for parse errors, `memory` on a read-only persona, colons in `name`, and unknown keys.
2. This is a **rendered-output** check, so the risk is small in practice: `gen.py` emits the frontmatter, so a malformed one means a generator bug, not a hand-edit. That is exactly what a drift gate is for — but it means the gate has to be ours, not the vendor's.
3. The finding is version-specific (2.1.263) and belongs in `docs/SUPPORT-MATRIX.md` as a claim that must be re-checked, since the sanitizer could be added to or removed from the validator at any release.

---

## E16 — tranche C re-verification at the installed versions

**Date** 2026-09-07. Re-verification of everything version-gated, plus the agy tool list.

### C1 — the agy tool-name list, re-derived at 1.1.27 (feeds `check.py --agy-tools`)

E3 flagged that the AG-06 tool list "must be re-derived at 1.1.27 rather than inherited from the 1.1.26 research". Every name AG-06 lists is present in `/usr/bin/agy` at 1.1.27:

```console
$ strings -n 4 /usr/bin/agy > /tmp/agy.strings     # 1,853,997 lines
$ grep -cw <name> /tmp/agy.strings
```

| tool | hits | tool | hits |
|---|---|---|---|
| `view_file` | 126 | `codebase_search` | 3 |
| `view_file_outline` | 2 | `read_url_content` | 13 |
| `view_code_item` | 4 | `search_web` | 10 |
| `run_command` | 35 | `browser_subagent` | 6 |
| `command_status` | 5 | `invoke_subagent` | 65 |
| `write_to_file` | 24 | `define_subagent` | 6 |
| `replace_file_content` | 10 | `notify_user` | 4 |
| `multi_replace_file_content` | 6 | `manage_task` | 25 |
| `grep_search` | 15 | `manage_inbox` | 1 |
| `find_by_name` | 5 | `manage_subagents` | 8 |
| `list_dir` | 4 | `send_message` | 55 |
| **`definitely_not_a_tool`** | **0** | *(negative control)* | |

Word-boundary matching (`-w`) is required, not whole-line (`-x`): under `-x` several real names score 0 because they only ever appear embedded in longer strings, which would have produced a list that wrongly rejects `view_file` — the most basic tool there is. The negative control is included so an all-zero column could not be mistaken for a finding.

**Verdict**: AG-06's list is valid at 1.1.27 and is the list `check.py --agy-tools` should carry.

### C2 — Antigravity desktop 2.12.2: the CLI and the desktop have diverged

Re-checking the `language_server` yaml tags and the inheritance default at desktop 2.12.2 (`/opt/Antigravity/resources/bin/language_server`, from `pacman -Q antigravity` → `2.12.2-1`).

Every AG-02 frontmatter tag is present in the desktop binary — `name`, `description`, `tools`, `mainAgent`, `subagent`, `model`, `commandExecutionPolicy`, `mcpServers`, `skills`, `plugins`, `hidden`, `inheritMcp`, `inheritCustomizations`, `rules`, `disabled`, `enabledTools`, `disabledTools` — with `yaml:"notARealKey` scoring 0 as a control. **Except one:**

```console
$ for b in /usr/bin/agy /opt/Antigravity/resources/bin/language_server; do
    echo "-- $b"
    printf '   yaml:"agents      : %s\n' "$(strings -n 6 "$b" | grep -c 'yaml:"agents')"
    printf '   yaml:"mainAgent   : %s   (control)\n' "$(strings -n 6 "$b" | grep -c 'yaml:"mainAgent')"
    printf '   yaml:"tools       : %s   (control)\n' "$(strings -n 6 "$b" | grep -c 'yaml:"tools')"
  done
-- /usr/bin/agy
   yaml:"agents      : 1
   yaml:"mainAgent   : 1   (control)
   yaml:"tools       : 2   (control)
-- /opt/Antigravity/resources/bin/language_server
   yaml:"agents      : 0
   yaml:"mainAgent   : 1   (control)
   yaml:"tools       : 2   (control)
```

The CLI's tag is `yaml:"agents,omitempty"`. The two controls match exactly across both binaries, so the greps demonstrably work on each.

**Verdict**: **the `agents:` key exists in agy CLI 1.1.27 and does not exist in Antigravity desktop 2.12.2.**

**Consequence — a correction to the design's opening premise.** `docs/design.md` line 3 says "the `agy` CLI and the Antigravity desktop share one engine and one config root `~/.gemini/config/`". The shared config root still holds; **one engine no longer does**, at least for this key. A package that emits `agents:` would be understood by the CLI and would be an unknown key on the desktop. Since E3 already folded the `agents:`-as-a-flat-team-lever idea into Q8, this narrows it: whatever Q8 concludes, `agents:` cannot be the mechanism unless the design accepts CLI-only enforcement. The `tools`-allowlist route stays the portable one.

The **inheritance default** half of this item is not settled here — `inheritCustomizations` is present as a tag in both binaries, but its default value is a runtime behaviour, which is Q8 and needs a session. It stays in tranche B.

### C3 — opencode 1.18.29: the published schema is unchanged

```console
$ curl -sS https://opencode.ai/config.json -o new.json
$ wc -c new.json vendored-copy.json
39039 new.json
39039 vendored-copy.json
```

Byte-identical, 19 `$defs` in both. `AgentConfig` carries the same 15 properties as at 1.18.25 — `color, description, disable, hidden, maxSteps, mode, model, options, permission, prompt, steps, temperature, tools, top_p, variant` — with nothing added or removed, and `mode` still `["subagent","primary","all"]`.

`PermissionConfig` confirms OC-02's 15 permission keys verbatim — `read, edit, glob, grep, list, bash, task, external_directory, todowrite, question, webfetch, websearch, lsp, doom_loop, skill` — and carries an `additionalProperties: {$ref: PermissionRuleConfig}`, which is why OC-02's nuance that "permission keys are not limited to the 15 named" holds.

**Verdict**: no refresh needed; the vendored copy is current. OC-01/OC-02's `KNOWN_KEYS` derivation stands, and `check.py --opencode` can validate against the file already in the tree.

### C4 — Claude 2.1.263 spot-check

The plugin-agent frontmatter list and the three validate modes were exercised as part of Q1/Q2 and recorded in **E10** and **E15**. The three validate modes all pass on a clean fixture; `validate .` runs in marketplace mode as §13 predicts; and E15 records where `--strict` does *not* catch what §13 item 2 assumed it would.

---

## E17 — the Antigravity tool registry, measured at runtime: seven names in AG-06 are invalid

**Date** 2026-09-08. **agy 1.1.27**, model GPT-OSS 120B (Medium). Tranche B, and the single most consequential result of the sweep.

E16 C1 re-derived AG-06's tool list by grepping `strings /usr/bin/agy` and reported every name present. **That method was wrong, and this entry supersedes it.** Presence of a string in the binary does not mean the name resolves in the tool registry.

It surfaced by accident: a fixture tech-lead carrying AG-06's names failed with only `Error: Agent execution terminated due to error.` The `--log-file` gave the real cause:

```
E0908 21:37:05.797896 errorreport.go:224] failed to construct executor: failed to resolve components:
  unknown component: tool "command_status" not found in registry
```

Each of the 22 candidate names was then installed as the sole entry in a probe agent's `tools` list and run with a one-character prompt, with `definitely_not_a_tool` as a negative control:

| tool | verdict | tool | verdict |
|---|---|---|---|
| `view_file` | valid | `codebase_search` | **INVALID** |
| `view_file_outline` | **INVALID** | `read_url_content` | valid |
| `view_code_item` | **INVALID** | `search_web` | valid |
| `run_command` | valid | `browser_subagent` | **INVALID** |
| `command_status` | **INVALID** | `invoke_subagent` | valid |
| `write_to_file` | valid | `define_subagent` | valid |
| `replace_file_content` | valid | `notify_user` | **INVALID** |
| `multi_replace_file_content` | valid | `manage_task` | valid |
| `grep_search` | valid | `manage_inbox` | **INVALID** |
| `find_by_name` | valid | `manage_subagents` | valid |
| `list_dir` | valid | `send_message` | valid |
| | | `definitely_not_a_tool` | **INVALID** (control) |

**The registry at 1.1.27 is these 15**: `view_file`, `run_command`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`, `grep_search`, `find_by_name`, `list_dir`, `read_url_content`, `search_web`, `invoke_subagent`, `define_subagent`, `manage_task`, `manage_subagents`, `send_message`.

**Consequences**:

1. **Design §3's Antigravity column is wrong in four of its five rows** and would have shipped agents that cannot start:

   | capability | §3 says | corrected |
   |---|---|---|
   | read | `view_file, view_file_outline, view_code_item` | `view_file` only |
   | search | `grep_search, find_by_name, list_dir, codebase_search` | drop `codebase_search` |
   | shell | `run_command, command_status` | `run_command` only |
   | web | `read_url_content, search_web` | unchanged — both valid |
   | edit | the three write tools | unchanged — all three valid |

   Every rendered Antigravity agent carrying the §3 read list would fail at startup, so this would have broken the Antigravity port outright rather than degrading quietly.

2. **AG-06's failure-mode warning is wrong at 1.1.27, in the safe direction.** It says an "unmapped or misspelled tool name in the tools list may cause the subagent process to hang". It does not hang: it fails fast and loudly at executor construction, before any model call. That makes it cheap to test — which is what made this sweep affordable — but the surfaced message is generic, and the actionable name appears only in `--log-file`.

3. **`check.py --agy-tools` must validate against a list derived this way**, not from `strings`. The list is version-specific and belongs in `docs/SUPPORT-MATRIX.md` with its derivation method recorded, because a name can enter or leave the registry at any release.

4. E16 C1's table stands only as "names present in the binary", which is a superset of the registry and **not** a validity test. The corrected list above supersedes it for every purpose.

---

### Addendum 2026-09-20 — re-run at agy 1.2.6 (#6)

The CLI had moved from 1.1.27 to **1.2.6** (desktop 2.12.2 → 2.15.0) since E17. The same
probe was re-run: one agent per name, installed globally, one-character prompt, with
`definitely_not_a_tool` as the negative control.

**The registry is unchanged.** The same 15 names resolve; the same 7 are rejected; the control
is rejected. Every valid name was confirmed by an observed `pong`, not by inference.

| valid (15) | rejected (7) |
|---|---|
| `view_file` `run_command` `write_to_file` `replace_file_content` `multi_replace_file_content` `grep_search` `find_by_name` `list_dir` `read_url_content` `search_web` `invoke_subagent` `define_subagent` `manage_task` `manage_subagents` `send_message` | `view_file_outline` `view_code_item` `command_status` `codebase_search` `browser_subagent` `notify_user` `manage_inbox` |

Two things changed around the registry, neither of which alters the list:

1. **The error now reaches stdout, as structured JSON.** At 1.1.27 stdout said only
   `Agent execution terminated due to error.` and the offending name appeared in `--log-file`
   alone (E17 consequence 2). At 1.2.6 the print-mode output is
   `AGY_ERROR: {"short_error":"… unknown component: tool \"<name>\" not found in registry",
   "status":"UNKNOWN","error_code":2,"code_kind":"grpc","retryable":false,…}` — the name is in
   the message a user actually sees.

2. **A model-capacity error had to be told apart from a registry error.** The default model
   (`gpt-oss-120b-medium`) returned `UNAVAILABLE (code 503): No capacity available` on several
   runs. E17's classifier — any failure is INVALID — would have produced false negatives. The
   ordering E17 established still holds and was re-verified first with the control: a registry
   miss fails at executor construction, *before* any model call, so a 503 means the name
   resolved. The sweep classified on the registry phrase, treated a 503 as "resolved, retry",
   and the six names that first hit a 503 were re-run until each returned `pong`.

**Consequence**: `hosts/antigravity.yaml` and `check.py --agy-tools` need no change. The floor
stays 1.1.27, and the list is now confirmed at two versions. The desktop (2.15.0) was still
not driven; only the CLI was.

**Other hosts, noted for a consistent snapshot, not re-verified**: Claude Code 2.1.278
(was 2.1.263), Codex CLI 0.154.0 (was 0.153.4), opencode **2.0.8** (was 1.18.29 — a major
bump). For opencode the published schema at `opencode.ai/config.json` was re-fetched and is
byte-identical (39,039 bytes): the same 15 `AgentConfig` keys, the same 15 permission keys, the
same command shape with `template` required. So the opencode gate's key lists are unaffected
by the 2.x bump; its runtime behaviour (E20) was not re-run.

---

## E18 — Q8 part 1: Antigravity workspace plugin roots deliver no agents at 1.1.27

**Date** 2026-09-08. **agy 1.1.27.**

Design §7 offers two Antigravity delivery routes: `agy plugin install <dir>`, "or workspace `.agents/plugins/e-colleagues/` [AG-07][AG-08]". The second was tested with the same fixture plugin (4 agents, 1 skill, `agy plugin validate` → `[ok]`) placed at each candidate workspace root, running `agy agents` from inside the workspace:

| location | `agy agents` output |
|---|---|
| `<repo>/.agents/plugins/e-colleagues/` | `flutter_a11y_agent` (a pre-existing global plugin) — **fixture absent** |
| `<repo>/_agents/plugins/e-colleagues/` | `flutter_a11y_agent` — **fixture absent** |
| `<repo>/.agents/agents/tech-lead/` | `flutter_a11y_agent` — **fixture absent** |
| global `agy plugin install <dir>` | `flutter_a11y_agent tech-lead` — **fixture present** |

**Verdict**: at 1.1.27 only the global install delivers agents. No workspace root does.

Note the global row lists `tech-lead` alone out of the fixture's four agents; the other three carry `mainAgent: false`, so `agy agents` lists selectable primaries, not the whole roster. They remain invocable as subagents (E19).

**Consequences**:
1. **§7's workspace route must be withdrawn** for agents. Whether workspace `.agents/skills` still works for skills is untested here and is a separate claim [AG-12].
2. This costs Antigravity the per-project roster. On Codex a project can carry `.codex/agents/` and on opencode `.opencode/agents/`, so D3's "roster is a variable" is per-project there; on Antigravity the roster is per-user and global, and two projects on one machine share it. The design should say so rather than implying parity.

---

## E19 — Q8 part 2: a `tools` allowlist does override ambient subagent inheritance; the body is not sliced; AGENTS.md never arrives

**Date** 2026-09-08. **agy 1.1.27**, model GPT-OSS 120B (Medium), fixture installed globally (E18 having shown workspace roots deliver nothing). All tool names are from the measured registry (E17).

### The central question — can a specialist reach a sibling?

The fixture's `reviewer` carries `tools: [view_file, grep_search, list_dir, run_command]` — **deliberately omitting `invoke_subagent`** — and a sibling `leaky` exists to be reached. The lead was asked to invoke the reviewer and pass on a task instructing it to invoke `leaky`:

```
Q8-LEAD-ACTIVE
…
4) Reviewer's reply verbatim:

Q8-REVIEWER-ACTIVE
My token is Q8-REVIEWER-ACTIVE. I attempted to invoke a sibling subagent named 'leaky'
using invoke_subagent, but that tool is not available in my environment. Therefore no
subagent was invoked.
```

**Verdict**: an explicit `tools` list omitting `invoke_subagent` **does** override ambient subagent inheritance. The specialist reports the tool absent and cannot reach a sibling.

**Consequence**: the last UNVERIFIED cell in §8's enforcement matrix closes, and it closes *mechanically* rather than as prose. "Specialists cannot spawn" is now enforced on three hosts (Claude via tool lists, opencode via child `task * deny`, Antigravity via the `tools` allowlist) and remains prose only on the Codex V2 backend. AG-05's ambient-inheritance worry is real but an explicit allowlist beats it.

### H1 body slicing — does not happen

AG-12 raised whether an agent body is sliced at its first H1. The fixture tech-lead's body has two H1s with a canary (`BADGER-4417`) in the **second** section. Asked whether its own instructions contain that token: **"Yes."** The whole body reaches the agent.

### AGENTS.md does not reach an agy agent

With deliberately distinct canaries — `WALRUS-3092` in the workspace `AGENTS.md`, `BADGER-4417` in the agent body — and the instruction not to read any files:

| run | body canary | AGENTS.md canary |
|---|---|---|
| `agy --agent tech-lead --print` | **Yes** | **NONE** |
| `agy --print` (default agent, control) | — | **NONE** |

**Verdict**: at 1.1.27 in print mode, workspace `AGENTS.md` content is **not ambiently injected** into either a custom agent or the default agent.

**Caveat, stated because the first attempt got this wrong**: an earlier run used `OSPREY-1201` in the body and `OSPREY-7788` in `AGENTS.md`, and the model conflated them and reported the body token as the project canary. That run is discarded; only the distinct-canary runs above are evidence. And this probe measures *ambient injection only* — the agent was told not to read files, so it does not show that agy could never load `AGENTS.md`, only that it is not in context by default. Conditions not reproduced here (an indexed project, `rules/AGENTS.md` placement per AG-07, interactive mode) might change it.

**Consequence**: §5.4's retrieval rule is vindicated a third time. On Antigravity the contract does **not** arrive ambiently, so the delegation brief naming the files is not belt-and-braces here — it is the only mechanism. It also means the managed block in `AGENTS.md` is invisible to agy agents, so the Antigravity tech-lead body must carry the contract itself rather than relying on the block.

### Still open in Q8

The **Antigravity desktop's** inheritance default (`inheritCustomizations`) was untested until the addendum below — it needs the desktop app, not the CLI. `tools: []` semantics were not isolated either, because the empty-list agent was superseded by the registry work; the practical answer is covered by AG-06's "an omitted `tools` list means no tools", which remains unverified for the empty-list case.

### Addendum 2026-10-03 — the desktop, driven (#5)

**Antigravity desktop 2.17.0** (About dialog), with the E19 probe plugin installed globally from the CLI (`q8-lead` with `invoke_subagent`; `q8-reviewer` without it; `q8-leaky` to be reached), a workspace folder carrying an `AGENTS.md` with `Canary: WALRUS-3092`, and a person at the app.

| step | observed |
|---|---|
| the agent selector | `Main Agent`, `q8-lead`, `firestore-rules-author`, `flutter_a11y_agent`. The two sub-agents are absent, as `mainAgent: false` predicts [AG-03]. `firestore-rules-author` is a Google plugin's agent the CLI's `agy agents` did not list at the time, because the desktop refreshed that plugin on launch |
| the E19 prompt to `q8-lead` | `REVIEWER-SAID: Q8-REVIEWER-ACTIVE. The invocation could not happen because I do not have the invoke_subagent tool.` |
| body canary and `AGENTS.md` canary | `BODY: YES` / `PROJECT: NONE` |

**Verdict**: the desktop behaves as the CLI did in E19 on every point. An explicit `tools` list omitting `invoke_subagent` holds there too, so the enforcement-matrix cell "specialists cannot spawn" is mechanical on the desktop as well; the whole body arrives; the workspace `AGENTS.md` does not. Q8 closes, with `tools: []` still not isolated.

**Host state**: the probe plugin was uninstalled and none of its files remain. The desktop, run for the first time in this period, wrote two migration flags into `config.json` and refreshed Google's bundled plugins on launch; that is the desktop's own doing, recorded so the next snapshot diff is read correctly.

---

## E20 — Q7: opencode runtime, everything but the TUI menus

**Date** 2026-09-08. **opencode 1.18.29**, model `opencode/gemini-3.5-flash-lite` (chosen as a cheap model; the provider's default `glm-5.3` first returned `Insufficient balance`).

Fixture `m0b/q7-repo`: `opencode.json` with `default_agent: tech-lead`, a `permission.task` allowlist and a `command` block; `.opencode/agents/{tech-lead,reviewer}.md`; an `AGENTS.md` whose canary `HERON-5540` appears in no other file (verified with `grep -rl`).

| # | question | verdict |
|---|---|---|
| 1 | project agents load, with the right modes | **yes** — `opencode agent list` shows `tech-lead (primary)`, `reviewer (subagent)` alongside the built-ins |
| 2 | `default_agent` from project config | **yes** — a bare `opencode run` prints `> tech-lead · gemini-3.5-flash-lite` and the reply carries the persona token |
| 3 | `permission.task` allowlist enforced | **yes, mechanically** — the log records `message=evaluated permission=task pattern=reviewer action.action=allow` |
| 4 | `permission: {edit: deny}` on a subagent | **holds** — asked to use the write tool, the reviewer replied it "was refused because the reviewer agent lacks editing tools", and the file was verified absent |
| 5 | AGENTS.md reaches a task child | **yes** — the child, told not to read files, returned `HERON-5540` |
| 6 | `run --command <name>` as a subtask | **works** — `opencode run --command ec-review` ran the reviewer as a subtask and returned its token |
| 7 | can a subtask `ask` the user in `opencode run`? | **it cannot, and it does not hang** — see below |
| 8 | Tab and `@` menus | **not tested** — needs the TUI (still open) |

### The `ask`-from-a-subtask question, answered from the session log

§8 hedges opencode's `bash` rules "because an `ask` from a subtask may be unanswerable in `opencode run` (UNVERIFIED, Q7)". The debug log shows opencode pre-empting this. Every session created under `opencode run` carries a deny list, and the **subtask** session gets one more entry than its parent:

```
parent  permission=[{"permission":"question","pattern":"*","action":"deny"},
                    {"permission":"plan_enter",...,"deny"},{"permission":"plan_exit",...,"deny"}]
subtask permission=[… the same three …, {"permission":"todowrite","pattern":"*","action":"deny"}]
```

So in headless `run` mode the `question` tool is **denied outright**, for parent and subtask alike, rather than asked and left hanging.

**Consequence**: the reason for preferring `bash` pattern rules over a blanket `ask` survives, but the stated justification changes — a blanket `ask` would not hang a headless run, it would be denied. Pattern rules remain the right choice because a denial is a silent capability loss at the moment the reviewer needs the shell, which is worse than a narrow allowlist. §8's parenthetical should be restated accordingly.

### A correction to §13 item 5

§13 item 5 requires "command keys within {description, agent, model, subtask}". The vendored schema's `Config.command.additionalProperties` gives **{template, description, agent, model, variant, subtask}** with `additionalProperties: false` and **`template` required**. A generated command without `template` would fail validation, and `variant` is missing from the design's list.

### Two non-findings, recorded so they are not mistaken for findings later

Two runs were killed at their timeouts (600 s and 240 s) and looked like hangs. Both were **slowness on the lite model**, not permission blocks: the same delegation completed in about a minute with a shorter prompt, and `--command` completed on a 150 s retry. No opencode hang was observed at any point, and none should be inferred from the earlier logs.

---

### Addendum 2026-09-27 — re-run at opencode 2.0.18 (#11)

**opencode 2.0.18**, model `opencode/gemini-3.5-flash-lite` as before. Fixture: the rendered `dist/opencode/agents/*.md` under `.opencode/agents/`, the rendered `opencode.json` plus a `command` block, an `AGENTS.md` with the canary `HERON-5540`, in a fresh git repository. Every run was `opencode run --standalone --print-logs --log-level debug`, stdin closed. Tool calls now go through a code-mode `execute` tool — the log shows `tools.task({subagent_type: …})` and `tools.shell({command: …})` — which is also how the runtime's own names for the permissions show through (#12).

| # | question | at 2.0.18 |
|---|---|---|
| 1 | project agents load, with the right modes | **reproduced, by a different command.** `opencode agent list` is gone (`Unexpected positional argument: "list"`); `opencode debug agents` lists the six with `tech-lead` primary and the rest subagents, and `opencode debug config` lists the project `opencode.json` and `.opencode/` as sources |
| 2 | `default_agent` from project config | **reproduced.** A bare `opencode run` printed `> tech-lead · gemini-3.5-flash-lite` and the reply carried the signature |
| 3 | `permission.task` allowlist enforced | **reproduced, renamed.** `reviewer` → `ALLOWED: 🕵️ Reviewer: REVIEWER-OK`; the built-in `general` → `DENIED: Permission denied: subagent`. The permission is evaluated under the name `subagent`; the key in the file is still `task`, and so is the tool the model calls |
| 4 | `permission: {edit: deny}` on a subagent | **holds.** The rendered reviewer, asked through the tech-lead, refused on role discipline and the tech-lead re-routed the job to the developer, which is allowed to write — a probe of the persona, not the mechanism. Measured instead on a fixture agent with `edit: deny` run directly with `--agent`: it made two `execute` calls to `fs.writeFileSync`, reported `ENOENT`, and no file appeared in the tree or anywhere else on disk. `execute` results are not logged, so whether `fs` threw or wrote into a sandbox is not known; nothing reached the working tree |
| 5 | `AGENTS.md` reaches a task child | **reproduced.** `CHILD: PROJECT: HERON-5540` from a child told to read nothing |
| 6 | `run --command <name>` as a subtask | **the flag is gone; a slash command in the prompt does the job.** `opencode run "/ec-review"` with the command in `opencode.json` ran the reviewer as a subtask, which returned the template's `COMMAND-SUBTASK-OK from reviewer`. The file form loads from **`.opencode/command/`** (singular): `.opencode/command/ec-review-file.md` expanded, `.opencode/commands/ec-review-file.md` did not, and the lead treated `/ec-review-file` as literal text |
| 7 | can a subtask `ask` in `opencode run`? | **still cannot, by a different mechanism.** At 1.18.29 every headless session carried `question * deny`. At 2.0.18 the question is asked and immediately dismissed — `✗ Asked 1 question failed`, `Error: The user dismissed this question` — and the run **exits 1 with no reply**. The reason for pattern rules over a blanket `ask` survives: a blanket `ask` would now end the run |
| — | a child spawning a child (E20 recorded `task * deny` on the subtask session) | **still blocked, by a different mechanism.** The reviewer, told to delegate to the developer, returned `NESTED: DENIED Subagent depth limit reached (1). Increase "experimental.subagent_depth" to allow nested subagents.` The static allowlist it inherits from `opencode.json` would have permitted it; the depth limit is what stops it. `debug agents` shows no session-level deny |
| 8 | Tab and `@` menus | **not tested** — the TUI, #5 |

**Verdict**: every row E20 established holds at 2.0.18. What moved is the surface around them: two commands the matrix cites are gone, the file-form command directory is singular, and the two "cannot" results now rest on a dismissed question and a depth limit rather than on session permissions. The schema at `opencode.ai/config.json` is unchanged (39,039 bytes; E24), so the gate's key lists still match the file format, while the runtime already speaks the new names — the renderer decision is #12.

**Host state**: nothing under `~/.config/opencode` changed; opencode wrote its own logs and snapshots under `~/.local/share/opencode`, as it does for every run. The background service it starts was stopped afterwards.

### Addendum 2026-10-03 — the TUI menus, row 8 (#5)

**opencode 2.0.18**, a project carrying the rendered `.opencode/agents/*.md` and `opencode.json` with `default_agent: tech-lead`, a person at the TUI.

| step | observed |
|---|---|
| on start | the session shows `tech-lead`; the status line reads `Tech-Lead · GLM-5.3 Default / OpenCode · max` |
| Tab | does nothing. **Shift+Tab** cycles the primaries: `tech-lead`, `build`, `plan`. The footer says so: `shift+tab agents  ctrl+p commands`. Specialists are not in the cycle, as `mode: subagent` predicts |
| `@` in the prompt | a list of skills, then agents `@general`, `@explore`, `@designer`, `@developer`, `@platform`, `@reviewer`, `@security`, then files. All five specialists are offered. So are the built-ins `general` and `explore`, which the tech-lead's allowlist denies — the menu does not filter by permission |
| `@reviewer reply with exactly AT-MENTION-OK` | the **tech-lead** answered: it read for a contract, spawned the Reviewer as a sub-agent, and relayed `🕵️ Reviewer: AT-MENTION-OK`. A mention is a routing hint to the primary, which delegates through the task tool, not a direct line to the specialist |

**Verdict**: row 8 closes and Q7 is fully settled. One correction: OC-03 says the agent cycle is `agent_cycle` on Tab; at 2.0.18 it is Shift+Tab.

---

## E21 — Q3: the project `agent` key works, is **not** trust-gated, and fails silently

**Date** 2026-09-08. **Claude Code 2.1.263.** Fixture `m0b/q3-repo`: `.claude/settings.json` = `{"agent": "tech-lead"}` plus a project `.claude/agents/tech-lead.md` whose body begins every reply with `Q3-PROJECT-AGENT-ACTIVE`.

### Does the key take effect?

Interactive session, trust prompt accepted, one `hi`:

```
❯ hi
● Q3-PROJECT-AGENT-ACTIVE
  Hi Hamid — what would you like to work on?
```

**Yes.** The persona replaced the default system prompt, as CC-10 describes for `--agent`.

### Is it trust-gated?

An identical, never-trusted twin (`m0b/q3-untrusted`, fresh git repo, absent from `~/.claude.json`) was run headlessly. A `-p` run does not accept trust — confirmed after the fact: the entry it created records `hasTrustDialogAccepted = False`.

| folder | `hasTrustDialogAccepted` | output |
|---|---|---|
| `q3-repo` (trusted) | `True` | `Q3-PROJECT-AGENT-ACTIVE` / `ping` |
| `q3-untrusted` | `False` | `Q3-PROJECT-AGENT-ACTIVE` / `ping` |

**No — the `agent` key is not trust-gated**, and neither is the project `.claude/agents/*.md` it resolves to.

This is a **meaningful asymmetry with [CC-06]**, where `extraKnownMarketplaces` is explicitly honoured only after the trust dialog. The consequence is worth stating plainly: a cloned repository can replace the entire system prompt of a Claude Code session — CC-10: "The subagent's system prompt replaces the default Claude Code system prompt entirely" — before its owner has trusted the folder. That is a property of Claude Code, not of this package, but the package's own README should not encourage a project `agent` key without saying so.

### An unresolvable value

`{"agent": "no-such-agent-exists"}` in the same trusted folder:

```console
$ claude -p "Say only the word ping." --output-format text
ping
exit=0
```

**Silently ignored.** No error, no visible warning in `-p`, no token — the session simply runs as the default agent. CC-10 nuance 6 predicts "continues with defaults plus a warning" for an agent that *vanishes*; in `-p` no warning surfaced.

**Consequence**: a typo in the key is invisible, which is the same failure shape as the Codex `--profile` typo (E14). Both belong in `ec-status`: it should assert that the configured agent name actually resolves.

### Precedence: a project `agent` key beats a user-level one

**Added 2026-09-08**, with explicit permission to write a user-level
`~/.claude/settings.json` temporarily. A probe agent `user-level` was placed in
`~/.claude/agents/` (a plain directory; only its contents are symlinks) and `{"agent":
"user-level"}` added to the user settings.

| folder | project `agent` | user `agent` | result |
|---|---|---|---|
| a scratch dir with no project settings | — | `user-level` | `Q3-USER-AGENT-ACTIVE` |
| `m0b/q3-repo` | `tech-lead` | `user-level` | **`Q3-PROJECT-AGENT-ACTIVE`** |

The first row is the control: without it, a project win could equally have meant the user key
never applied at all.

**Verdict**: **project scope beats user scope.** CC-10's nuance 1 flags the precedence of a
*plugin's* `agent` key as undocumented; for project-versus-user the answer is now measured.

**Consequence**: §7's opt-in project `.claude/settings.json` `"agent"` works even for the users
most likely to have set their own default agent, which was the worry. It does **not** settle
plugin-versus-user, and the standing don't-do list already forbids shipping a plugin
`settings.json` with an `agent` key, so that gap stays closed by decision rather than by test.

**Restoration**: `~/.claude/settings.json` was restored from a byte-exact backup and verified
by `sha256sum` and `diff`, and the probe agent was deleted. No unrelated change was touched.

---

## E22 — Q10b: the trusted-project `developer_instructions` layer, closing Q10

**Date** 2026-09-08. **codex-cli 0.153.4.** Completes E14, which could only reach the profile layer.

Fixture `m0b/q10-repo` carries `.codex/config.toml`:

```toml
developer_instructions = """
You are the M0 tranche B project Tech-Lead.
Begin every reply with the exact token: Q10-PROJECT-DEVINSTR-ACTIVE
"""
```

The folder was trusted through the Codex TUI trust dialog by hand — Codex recorded it itself, as the working rule requires:

```toml
[projects."…/m0b/q10-repo"]
trust_level = "trusted"
```

| invocation | last message |
|---|---|
| `codex exec -C <proj> …  "Say only the word ping."` | `Q10-PROJECT-DEVINSTR-ACTIVE ping` |
| the same plus `-c developer_instructions=""` | `ping` |

**Verdict**: a trusted project `.codex/config.toml` `developer_instructions` reaches the model, and `-c developer_instructions=""` clears it for one session — the same behaviour E14 measured for the profile layer. **Q10 is closed on both layers.**

**Consequence**: §9's route B (per-repo: the project carries `.codex/agents/`, the `.codex/config.toml` managed region and vendored skills, so a teammate clones, trusts once and has the team) is confirmed for its tech-lead half. Combined with E12 — project *skills* load untrusted while project *agents* need trust — the degradation story for an untrusted clone is now fully mapped:

| in an untrusted Codex clone | result |
|---|---|
| `$ec-tech-lead` skill | loads and is followed (E12) |
| `.codex/agents/*.toml` specialists | absent; loud `unknown agent_type '<name>'` (E12) |
| `.codex/config.toml` `developer_instructions` | not applied until trust (E22, by construction) |

---

## E23 — Q13: a project-enabled plugin from a local marketplace loads on trust, with no install step

**Date** 2026-09-08. **Claude Code 2.1.263.**

Fixture `m0b/q13-clone`: a fresh `git clone` of a repository that is simultaneously a plugin (`.claude-plugin/plugin.json`, one agent, one skill) and its own marketplace (`.claude-plugin/marketplace.json`, `plugins[0].source = "./"`), plus a project `.claude/settings.json` declaring the marketplace and enabling the plugin.

### First attempt: the `source` shape, and how Claude reports a bad one

`"source": "<absolute path>"` — a bare string — is **rejected**. On startup Claude showed a blocking panel:

```
  Settings Warning
  …/m0b/q13-clone/.claude/settings.json
  └ extraKnownMarketplaces.e-colleagues: Invalid marketplace entry was ignored: source: Invalid input
  The values listed above were skipped; the rest of the file is in effect.
  ❯ 1. Continue    2. Fix with Claude    3. Exit and fix manually
```

`extraKnownMarketplaces[<name>].source` must be an **object**. The settings reference gives `github`, `git`, `url`, `npm`, `archive`, `git-subdir`, and — the one that makes a local test possible — `file` (`path` to a `marketplace.json`) and **`directory`** (`path` to a directory containing `.claude-plugin/marketplace.json`).

Two things worth keeping: an invalid marketplace entry is **skipped, not fatal**, and the rest of the file still applies; and Claude surfaces it loudly rather than silently — unlike the `agent` key (E21), which fails in total silence.

### Second attempt: `{"source": "directory", "path": "<repo>"}`

No warning, and with the folder trusted:

| check | result |
|---|---|
| marketplace registered on the machine | **yes** — `known_marketplaces.json` now lists `e-colleagues` beside `claude-plugins-official` |
| appears in `claude plugin list` | **no** — "Installed plugins:" lists nothing for it |
| present in `installed_plugins.json` | **no** |
| `subagent_type` offered **inside** the repo | **yes** — `e-colleagues:tech-lead` |
| `subagent_type` offered **outside** the repo (control, run from `/tmp`) | **no** — zero matches |
| the agent actually runs | **yes** — `SPAWNED: Q13-PLUGIN-AGENT-ACTIVE` |
| the plugin's skill is available | **yes**, as `e-colleagues:ec-tech-lead` |

**Verdict**: a plugin enabled by a repository's own `.claude/settings.json`, from a marketplace that same file declares, **loads and works on trust with no separate install step** — and it is scoped to that repository rather than installed onto the machine. `claude plugin list` is not a reliable way to check whether it is active; the agent and skill listings are.

**Consequences**:
1. CC-06's nuance 3 — "Docs are silent on marketplace-relative-path plugin sources … Do not over-generalize to 'no plugin ever loads from project settings alone'" — was right to hedge. For a local source, no install step is required.
2. §7's Claude install row can note that a teammate who clones a bootstrapped repository gets the team on trust alone, without running `claude plugin install`.
3. `check.py` must validate any `extraKnownMarketplaces` entry it writes against the object form, because a wrong shape is silently skipped after one dismissible warning — and the plugin then simply never appears.

**Limitation, stated because it bounds the conclusion**: this was measured with a **`directory`** source using an absolute path — which a shipped repository cannot hardcode. The design's real distribution is a `github` source, and CC-06's v2.1.195 restriction is written specifically about "an external source (GitHub, npm)". So this result does **not** show that a github-sourced self-marketplace skips the install step; that remains open until the repository is published and can be tested as `{"source": "github", "repo": "<owner>/e-colleagues"}`. It folds into the same follow-up as E8's residual directory-name question.

### Addendum 2026-09-28 — the `github` source: registered and fetched on trust, but the plugin does not load (#4)

**Claude Code 2.1.284.** The repository is public, so the shape a repository would actually ship could be measured: a fresh clone carrying `.claude/settings.json` with `extraKnownMarketplaces["e-colleagues"] = {"source": {"source": "github", "repo": "<owner>/e-colleagues"}}` and `enabledPlugins["e-colleagues@e-colleagues"] = true`. Claude's plugin state was cleaned first — the `directory`-source registration E23's re-run had left under the same name was removed with `claude plugin marketplace remove` — so the machine held no `e-colleagues` marketplace and no installed plugin, which is what a cloning teammate has.

The folder was trusted through the dialog. The first screen showed **nothing**: no settings warning, no install instruction, no visible fetch — straight to the prompt.

| check | result |
|---|---|
| marketplace registered on the machine | **yes** — `known_marketplaces.json` gained `e-colleagues` with the `github` source and an `installLocation` under `~/.claude/plugins/marketplaces/`, and that directory is a checkout of the repository at its current head |
| appears in `claude plugin list` | **no** |
| present in `installed_plugins.json` | **no** |
| `subagent_type` offered inside the clone, with the marketplace already on disk | **no** — `NO-E-COLLEAGUES-AGENTS` |
| the plugin's skills inside the clone | **no** — `NO-E-COLLEAGUES-SKILLS` |
| a live spawn of `e-colleagues:reviewer` inside the clone | **fails** — `Agent type 'e-colleagues:reviewer' not found`, followed by the built-in list |
| outside the clone (control) | `NO-E-COLLEAGUES-AGENTS`, as before |

**Verdict**: for a **`github`** source, trust registers and fetches the marketplace but does **not** load the plugin. `claude plugin install e-colleagues@e-colleagues` is still required, exactly as CC-06's v2.1.195 restriction says for an external source. E23's result stands for a `directory` source only. What CC-06 did not say: at 2.1.284 **nothing tells the user**. The digest says the install command is "shown"; here the absence was silent in the interactive first screen and in `-p`, and `claude plugin list` shows nothing for it.

**Consequences**:
1. The README's Claude install keeps both commands. A teammate who clones a repository that declares the marketplace, and trusts it, gets the marketplace registered and nothing else; the install line is not optional, and the tech-lead body's "running without the persona" check is what tells them.
2. Design §7's Claude install cell and §10 step 6 say so, and the question closes in `acceptance.md`.

---

## E24 — re-verification sweep at the 2026-09-27 snapshot (#13)

**Date** 2026-09-27. Installed: **Claude Code 2.1.283**, **Codex CLI 0.154.0** (model `gpt-6-astra`), **agy 1.2.10** (default model), **Antigravity desktop 2.17.0**. opencode is at 2.0.18 and is not part of this sweep (#11). Every experiment below was re-run with the command its original entry records, against a fresh throwaway fixture in a scratch directory, with host state snapshotted before and diffed after. Where a row says *reproduced*, the original entry stands and this table is the evidence at the new version. Where it says otherwise, the row states what moved.

### Codex CLI 0.154.0

| experiment | claim | result |
|---|---|---|
| E4 | `read-only` + `never` runs a test suite and blocks every write | **reproduced.** `make test` passed and wrote no `.pyc`. Workspace, `/tmp`, `$TMPDIR`, `$HOME`, `mkdir ./build` and `git commit` all failed `Read-only file system` (rc 1; rc 128 for git); reads and `git status` rc 0; `curl` rc 6 `Could not resolve host`. The `workspace-write` control wrote two `.pyc` files and a file in `/tmp` |
| E5 | a symlinked role TOML fails at spawn | **reproduced.** Symlink: `agent type is currently not available`. The same content as a real file: `🕵️ Reviewer: SPAWN-OK` |
| E11 | the V2 ceiling refuses a fourth spawn rather than queueing | **reproduced.** Five requested; A, B and C ran (each 25.0 s, the three intervals overlapping for 18.9 s); two `collab spawn failed: agent thread limit reached` |
| E12 | untrusted clone: the project skill loads, the project agent does not | **reproduced, with a nuance.** `$ec-tech-lead` was adopted and returned `MAGPIE-4402`; the spawn produced `unknown agent_type 'm0-projonly'` and no trust entry was written. The nuance: that error appears only when at least one role exists at user scope. With no role installed anywhere, the spawn tool exposes **no `agent_type` parameter** at all, and the primary reports that it cannot request the type rather than receiving an error. The original run had user-scope roles installed, which is why it never saw this |
| E14 | profile layer; `-c developer_instructions` clears or replaces | **reproduced**, all five rows, including the silently ignored unknown profile name |
| E22 | trusted project `developer_instructions` | **reproduced.** Plain `ping` before trust; `Q10-PROJECT-DEVINSTR-ACTIVE ping` after the trust dialog; `-c developer_instructions=""` clears it. Codex wrote the `[projects."…"]` entry itself |

One mechanic that cost a full round of timeouts: `codex exec` reads more of its prompt from stdin when stdin is not a TTY and blocks on an open pipe with `Reading additional input from stdin...`. Every scripted invocation needs `< /dev/null`.

### Claude Code 2.1.283

| experiment | claim | result |
|---|---|---|
| E10 | the manifest `agents` list replaces the scan; a bare `subagent_type` does not resolve | **reproduced.** The decoy in root `agents/` was absent (`DECOY-VISIBLE: no`); bare `reviewer` → `Agent type 'reviewer' not found`; `e-colleagues:reviewer` spawned and reported its tools as `Read` and `Bash` |
| E13 | Bash is a write path for the read-only reviewer | **capability reproduced; behaviour changed.** From inside the reviewer's own Bash, `os.access('.', W_OK)` was `True` and `sys.dont_write_bytecode` was `False`, and the tech-lead's identical Bash wrote the two `.pyc` files. But the rendered reviewer, on its own initiative and citing R4, ran `make test` under `PYTHONDONTWRITEBYTECODE=1` and wrote nothing. The persona now suppresses the side effect; the tool surface does not, and §8's cell stays *prose* |
| E15 | `plugin validate --strict` misses most frontmatter faults | **reproduced.** The same two caught (colon-free unterminated quote, now worded `Unexpected EOF`; missing description) and the same six pass, `memory: true` on a `tools`-restricted agent included |
| E21 | the project `agent` key works, is not trust-gated, and is silent on a bad value | **reproduced.** Token untrusted in four of five runs; token trusted; `no-such-agent-exists` → plain `ping`, exit 0. Two differences: the very first `-p` run in the fresh untrusted directory returned no token and was not reproduced in four further runs, cause not found; and a `-p` run no longer records the folder in `~/.claude.json` at all (at 2.1.263 it recorded `hasTrustDialogAccepted: false`). The precedence row was not re-run: it needs a user-level settings write |
| E23 | a local-source self-marketplace loads on trust with no install step | **reproduced.** `known_marketplaces.json` lists it; `installed_plugins.json` and `claude plugin list` do not; inside the clone the `e-colleagues:` agents and all four skills are offered and `e-colleagues:reviewer` spawned (`SPAWN-OK-Q13`); outside the clone none are. The github-source variant is still #4 |

**New: `AGENTS.md` reaches Claude with no `CLAUDE.md` at all.** In a directory holding only `AGENTS.md` (canary `BLUEBIRD-7731`), the default agent, told not to read files, answered `PROJECT: BLUEBIRD-7731`; the control directory with no `AGENTS.md` answered `PROJECT: NONE`. With both a `CLAUDE.md` containing `@AGENTS.md` and the `AGENTS.md` present, the model reported the token once — a self-report, so weak evidence against duplication, but no evidence for it. **Consequence**: the two-line import [CC-14] is no longer the only route on 2.1.283; it is kept because it costs nothing and older versions need it. The vendor changelog was not checked; this is measured only.

### agy 1.2.10 and Antigravity desktop 2.17.0

| experiment | claim | result |
|---|---|---|
| E17 | the 15-name registry | **reproduced.** Same 15 valid, each with an observed `pong` — four (`run_command`, `grep_search`, `read_url_content`, `manage_task`) resolved on the first pass but answered the one-character prompt with a clarification request, and gave `pong` on a second pass with a stricter fixture body; same 7 rejected with `not found in registry`; control rejected. No 503 this time |
| E18 | no workspace root delivers agents | **reproduced** for the original three roots and two more (`.gemini/agents/<name>/`, `.agents/<plugin>/`); only `agy plugin install` does |
| E19 | a `tools` list omitting `invoke_subagent` holds; the body is not sliced; `AGENTS.md` reaches no agent | **reproduced.** The reviewer: "I do not have an `invoke_subagent` tool available in my toolset"; `BODY: YES` for the second-H1 canary; `PROJECT: NONE` for both the custom agent and the default one |
| E16 C2 | the desktop lacks the `agents:` key the CLI has | **flipped.** Desktop 2.17.0's `language_server` carries `yaml:"agents` (1 hit; controls `mainAgent` 1, `notARealKey` 0), the same as the CLI. The divergence AG-02 records is gone. The renderer's `never_emit: [agents]` now rests on portability across versions rather than on a measured divergence |

**Host state**: `~/.gemini/config/config.json` and the plugins tree were byte-identical after each install and uninstall; `~/.codex/config.toml` is identical apart from the trust entry Codex wrote for the E22 fixture, and `~/.codex/agents/` was removed again because it did not exist before; `~/.claude.json` gained the two trusted fixture folders; `~/.claude/settings.json` was not touched.

**Not re-run**: E6 to E9 (Codex marketplace, cache layout, `AGENTS.md` reaching a child), E20 (opencode, #11), and E21's precedence row.

---

## E25 — opencode 2.0.18 has no plugin route for agents: plugins add commands and skills, `references` delivers nothing (#24)

**Date** 2026-09-28. **opencode 2.0.18.** Asked while deciding #24: could the team reach an opencode project the way it reaches the other three hosts — installed once, from this repository — instead of as files written into every project? Three candidates: the `references` config key, new in 2.x and described only as "named git or local directory references"; the `plugin` key and its `.opencode/plugins/` directory; and the `skills` sources. No model call was needed. Everything was read back with `opencode debug agents` and with marker files the plugin wrote about itself.

### `references` is not a config source

A consumer project whose `opencode.json` carried `references: {"ec": {"path": "<provider>"}}`, the provider being a directory shaped like a plugin repository — `.opencode/agents/*.md` copied from `dist/opencode/`, plus an `opencode.json`. `opencode debug config` listed the consumer's own files as sources and never the provider; `debug agents` listed the built-ins only. The documentation page has a "References" heading with no content under it. The `repository`/`branch` form was not run: it is the same mechanism with a remote source, and the local one delivered nothing.

### Plugins: the documented shape is rejected, and the real API has no `add` for agents

The documented shape — `export const Plugin = async ({project, client, $, directory, worktree}) => hooks` — fails at load with `Plugin must export a default definition with an id and an effect or setup function` (server log, `failed to load plugin`; both `.opencode/plugin/` and `.opencode/plugins/` are scanned). The shape that loads at 2.0.18 is `export default { id, setup(ctx) }`, and `setup` receives a context whose namespaces are `agent`, `command`, `skill`, `permission`, `reference`, `plugin`, `tool`, `mcp`, `catalog`, `integration`, `worktree`, `location` and `app` — a `v2` API the installed `@opencode-ai/plugin` 1.18.15 package already types under `dist/v2/`. Each namespace offers `transform(draft => …)`. What each draft can do, measured by dumping its methods from inside the hook and then trying them:

| draft | methods at 2.0.18 | can a plugin deliver this? |
|---|---|---|
| `agent` | `list`, `get`, `default`, `update`, `remove` | **no** — there is no `add`. A plugin can modify, hide or default agents that already exist, and at transform time the draft held only the seven built-ins, so even `update("reviewer", …)` did not reach a project agent |
| `command` | `add` | yes |
| `skill` | `list`, `get`, `add`, `update`, `remove` | yes |

`debug agents` afterwards listed the fixture's fourteen agents unchanged: no `plugin-agent`, the reviewer's description untouched. The package's types agree — its `AgentDraft` has the same five methods and no `add` — while the runtime's command draft has an `add` the package's `CommandDraft` type lacks, so the binary is ahead of the package, not behind it.

### Consequences

1. **opencode cannot be a plugin host for the team at 2.0.18.** Agents load from exactly `~/.config/opencode/agents/`, `.opencode/agents/` and the config's `agent` key. The documentation says so, and the plugin API confirms it by omission. The delivery choice for #24 is project files or user-scope files, not a plugin.
2. Commands and skills *could* ship from a plugin. Nothing here needs that yet; it is recorded so the next reader does not re-derive it.
3. OC-11's "no bundle format" moves from documentation to measured, with the reason.

**Method note, so the next probe does not lose an hour to it**: `opencode debug agents` returns `[]` for a few seconds after the background service starts or restarts, and returned `[]` throughout for directories the service had not settled on. Every reading above was taken after polling until the list was non-empty. A reading of `[]` is not a finding.

**Host state**: the probe plugins lived in a fixture's `.opencode/plugins/` and were removed; nothing under `~/.config/opencode` changed; the background service was stopped afterwards.

### Addendum 2026-09-29 — the user-scope route, measured

The route that remains was run end to end. `bootstrap.py --scope user --write --profile library`, with `HOME` and `XDG_CONFIG_HOME` pointed at a throwaway home, wrote the five roster agents to `<config-home>/opencode/agents/*.md` as real files and touched no real directory. Then, from an empty project with only `XDG_CONFIG_HOME` redirected:

| command | result |
|---|---|
| `opencode run --standalone --agent tech-lead "Say only the word ping."` with the agents installed | `> tech-lead · gemini-3.5-flash-lite` and `👨‍💻 Tech-Lead: ping` |
| the same with the real config home, where nothing is installed | `Error: Agent not found: "tech-lead"`, exit 1 |

**Verdict**: opencode 2.0.18 loads agents from the user directory the installer writes to, and the tech-lead's body reaches the model from there. OC-01's user-directory half moves from documentation to measured. The global config was not written and was not needed for `--agent`; a `default_agent` for the TUI stays the user's own edit [OC-03].

**Skills too (2026-10-03).** opencode has no plugin to carry the four skills, so the same install now copies them to `<config-home>/opencode/skills/<name>/`. From the same throwaway home, the tech-lead asked to list its `ec-` skills answered `ec-init`, `ec-onboard`, `ec-status`, `ec-tech-lead`; the control against the real config home answered `NO-EC-SKILLS`; and asked to "use the ec-status skill on this project" it ran the status script and relayed its output verbatim (`no .e-colleagues/lock.json — this project is not bootstrapped. Run ec-init.`, correct for an empty project). OC-08's user skills directory moves from documentation to measured, and opencode onboards with the same skill names as the other hosts.

---

## E26 — what a fleet of Antigravity tech-leads rests on: workmux dispatch, prompt delivery, commit, states, the captured screen

**Date** 2026-11-14. **agy 1.5.3**, model Gemini 4 Argon (High), the configured default; **workmux 0.1.281**; **tmux 3.8**. Tranche B: every step after the first needs a terminal.

A planned fleet skill will start one tech-lead per issue, each in its own workmux worktree and terminal window. It rests on six host facts:

1. **The basics at the installed version:** `--agent`, the tool registry, and the install route.
2. **A session can run workmux through its shell tool,** reaching the terminal multiplexer and creating a worktree outside its own directory.
3. **A tech-lead that workmux starts in a worktree gets its start prompt and can commit.** Whether it loads a skill from that prompt is measured later.
4. **The states workmux reports** for a session that is working, one that has stopped, and one at a host approval prompt.
5. **A captured screen of a stopped session holds its last RETURN block in full.**
6. **The host's remote feature reaches a session in a window.**

This entry measures items 1 to 4. Item 5 is recorded because step 6 measured it. Item 6 is not measured.

Everything ran in a throwaway repository, `<tmp>/repo` (`git init`, one commit, a repository-local identity, no signing), from a tmux session created for the probe, `e26-probe`, so no other session or window was touched. workmux puts worktrees in `<tmp>/repo__worktrees/`. These were real sessions on the owner's account. Three reached the model: the print-mode check in step 2, the dispatching tech-lead (two messages), and the worktree tech-lead (four prompts, its start prompt included). The two trust checks in step 4 sent no prompt.

Every interactive session also printed `⚠ Sign-in update needed … some requests may fail`. No request failed.

### 1. Versions, and the Antigravity hooks

```console
$ agy --version
1.5.3
$ workmux --version
workmux 0.1.281
$ tmux -V
tmux 3.8
$ cat ~/.gemini/config/hooks.json
{
  "workmux-status": {
    "PreInvocation": [
      {
        "command": "workmux register-agent >/dev/null 2>&1 || true; printf '{}\\n'",
        "type": "command"
      },
      {
        "command": "workmux set-window-status working >/dev/null 2>&1 || true; printf '{}\\n'",
        "type": "command"
      }
    ],
    "Stop": [
      {
        "command": "workmux set-window-status done >/dev/null 2>&1 || true; printf '{}\\n'",
        "type": "command"
      }
    ]
  }
}
```

That file is where `workmux docs` says `workmux setup` installs the Antigravity hooks (`PreInvocation` marks the pane working, `Stop` marks it done), and it holds exactly those hooks. Nothing in it can report a waiting state, which matches the documentation's "Antigravity CLI (`agy`): No 💬 waiting state". The hooks were already installed; `workmux setup` was not run.

### 2. The basics at 1.5.3

```console
$ agy agent
firestore-rules-author
tech-lead
$ agy plugin list
Installed plugins:
…
- e-colleagues (enabled, 0.1.1)
    Source:     antigravity
    Components: 4 skills, 6 agents
…
$ cmp ~/.gemini/config/plugins/e-colleagues/agents/tech-lead/agent.md agents/tech-lead/agent.md; echo "cmp rc=$?"
cmp rc=0
$ agy --agent tech-lead --print "Say only the word ping."      # in <tmp>/repo; rc 0, stderr empty
👨‍💻 Tech-Lead: ping
```

The global `agy plugin install` route still delivers the agents, the installed tech-lead is byte-identical to the rendered one, and its body reaches the model. The tech-lead carries an explicit list of eleven tool names, and a name missing from the registry aborts an agent before any model call (E17). By that rule, those eleven still resolve at 1.5.3. This is inferred from the one run above, not swept: the full 22-name sweep of E17 was not re-run.

The validator moved. Run from the repository root:

```console
$ agy plugin validate .; echo "rc=$?"
Validating e-colleagues (plugin.json)

  ⚠ AGENTS.md: never loaded: plugins load rules only from rules/. Move it to rules/AGENTS.md
  · plugin.json: no logo: the plugin shows a generic icon. Add "logo": "assets/logo.svg" (a .png, .svg, .jpg, .jpeg or .webp file inside the plugin)

  skills 4 · agents 6 · rules 0 · hooks 0 · mcpServers 0 · sidecars 0

✔ Validation passed with 1 warning
rc=0
```

It passes, but it no longer prints the `[ok]` that `tools/check.py` looks for, so that gate fails at 1.5.3 on an unchanged tree. Its advice to move `AGENTS.md` into `rules/` is what the standing don't-do list forbids [AG-05].

### 3. A session runs `workmux add`

The dispatching tech-lead was started in the probe session's pane, in `<tmp>/repo`, as `agy --agent tech-lead -i "<instruction>"`, the instruction being:

```
Run this exact command yourself in the shell, then report its output: workmux add probe-a --background --agent "agy --agent tech-lead" --prompt "Reply with the single word ready, then stop."
```

It stopped three times before the worktree existed:

1. agy's trust dialog for `<tmp>/repo`, a folder it had not seen. Accepted.
2. agy's approval for the command. Option 1 was chosen:

   ```
   Requesting permission for:
      workmux add probe-a --background --agent "agy --agent tech-lead" --prompt "Reply with the single word ready,
   then stop."

   Run this command?
   > 1. Yes, run command
     2. Yes, and always allow in this conversation for commands that start with 'workmux'
     3. Yes, and always allow for commands that start with 'workmux' (Persist to settings.json)
     4. No, cancel
   ```

   The probe machine's agy settings carry `"ask": ["command(*)", …]`. agy's behaviour without that setting was not checked.
3. workmux's own question. agy runs commands in a pseudo-terminal (`ps` showed the `workmux add` process on its own pts), so workmux saw a terminal and offered to update the hooks of a *different* agent it detected on the machine. The command's output, from agy's task log, path redacted:

   ```
   ┌ Status Tracking
   │
   │  Detected Copilot CLI (found Copilot config directory; status tracking update available)

     ● Update ~/.copilot/hooks/workmux-status.json
     ├─ +13 -0 [━━━━━━━━━━━━] at line 22
   …
     Install or update status tracking hooks? [Y/n] n

   ✓ Successfully created worktree and tmux window for 'probe-a'
     Base: main
     Worktree: <tmp>/repo__worktrees/probe-a
   ```

   The tech-lead did not guess. It ended its turn with `👨‍💻 Tech-Lead: I launched the command (…), and it is currently waiting on an interactive prompt:`, quoted the question, and asked `Should I send Y or n to proceed?`. `n` was typed into its input, and the log above shows the command received it and finished. `Y` would have rewritten a file in the owner's home.

```console
$ git worktree list
<tmp>/repo                    969dfb8 [main]
<tmp>/repo__worktrees/probe-a 969dfb8 [probe-a]
$ tmux list-windows -t e26-probe -F '#{session_name}:#{window_index} #{window_name} #{pane_id} #{pane_width}x#{pane_height}'
e26-probe:0  repo %22 120x40
e26-probe:1  probe-a %23 238x63
$ tr '\0' '|' < /proc/<agy in %23>/cmdline
agy|--agent|tech-lead|-i|Reply with the single word ready, then stop.|
```

(The window names carry a glyph that the probe machine's shell prompt adds; it is removed above.) The worktree is outside the agy workspace, a sibling of the repository, and was created without complaint. The window opened in the tmux session of the pane that ran `workmux add`. `--agent` took a whole command with arguments. workmux appended agy's own `-i <prompt>` to it, so it recognised the command as agy, and the session later registered as `"agent_kind": "agy"`. It also wrote the prompt to `.workmux/PROMPT-probe-a.md` in the worktree and added `.workmux/` to `.git/info/exclude`.

### 4. The prompt arrives, and the worktree session commits

The new window did not show the prompt. It showed agy's trust dialog for the new path:

```
Accessing workspace:

<tmp>/repo__worktrees/probe-a

Do you trust the contents of this project?

Antigravity CLI requires permission to read, edit, and execute files here.

> Yes, I trust this folder
  No, exit
```

After the dialog was accepted, the screen showed the prompt and its answer at once:

```
> Reply with the single word ready, then stop.
…
▸ Thought for 19s, 1.0k tokens

  ready
```

The hook calls for that pane, from workmux's log (UTC):

```
20:17:08  window created, pane %23
20:17:11  "workmux", "register-agent"
20:17:11  "workmux", "set-window-status", "working"
20:17:31  "workmux", "set-window-status", "done"
          (trust dialog still on screen; accepted at about 20:19:07; no hook call follows)
20:19:57  "workmux", "register-agent"          <- the next prompt, sent with workmux send
```

The turn took 20 seconds by the hooks and "19s" by the screen, and no hook fired after the dialog was accepted. That points to the start prompt having run *behind* the trust dialog, before the folder was trusted. This is an inference from timestamps. The prompt needed no tool, so what a start prompt that does need a tool does behind the dialog is not measured. The reply came without the signature. It followed "the single word" literally. Every later reply carried the signature.

Trust is kept per exact path. The trusted `<tmp>/repo` did not cover its sibling worktree, and in a test with no prompt, `agy --agent tech-lead` in a new subfolder `<tmp>/repo/sub` raised the dialog too. That test was answered "No, exit", and the agy settings file's hash did not change. A session-only setting does avoid the dialog. `agy --agent tech-lead --settings <tmp>/trust-settings.json` with `{"trustedWorkspaces": ["<tmp>/fresh"]}`, started in a new folder `<tmp>/fresh`, opened straight at the input box with no dialog, and the settings file's hash was identical before and after.

Then the commit:

```console
$ workmux send probe-a "Create a file named probe.txt containing the word probe, then commit it with git with the message: add probe.txt"
```

The file was written without a prompt. The command `git add probe.txt && git commit -m "add probe.txt"` asked for approval once and was approved once. The reply:

```
  👨‍💻 Tech-Lead: Created probe.txt with probe and committed it.

    $ git add probe.txt && git commit -m "add probe.txt"
    [probe-a 57567b8] add probe.txt
     1 file changed, 1 insertion(+)
     create mode 100644 probe.txt
    (exit code 0)
```

```console
$ git log --oneline -1          # in <tmp>/repo__worktrees/probe-a
57567b8 add probe.txt
```

### 5. States

`workmux status --json probe-a` was polled through each moment. One reading, trimmed:

```json
{
  "worktree": "probe-a",
  "branch": "probe-a",
  "project": "repo",
  "status": "done",
  "elapsed_secs": 30,
  "title": "…",
  "pane_id": "%23",
  "workdir": "<tmp>/repo__worktrees/probe-a",
  "agent_kind": "agy",
  "session": "e26-probe",
  …
}
```

| moment, in the probe-a session | `status` | `elapsed_secs` read |
|---|---|---|
| the commit turn, model at work (polled every 3 s) | `working` | 3, 6, 9, 12, 2, 5, 8, 0, 3, 6 (reset at each model step) |
| at the approval for `git add … && git commit …` | `working` | 18, 28, 38 |
| that turn finished after the approval | `done` | 1 |
| at the approval for `date` (asked: "Run the shell command date and show its output.") | `working` | 7, 42 |
| after choosing `4. No, cancel` there: the screen showed `⎿  User declined the tool call` and `⎿  Interrupted · What should Antigravity CLI do instead?`, input box idle | `working` | 75, 80, … 112, then 163 |
| at the first-run trust dialog, after the start turn had finished behind it | `done` | 24, 30, 100, 120 |

The dispatching tech-lead read `working` (76 s) at its own approval for `workmux add`. While the `date` approval waited, `workmux list` showed `probe-a  5m   working  ✓    ●         ../repo__worktrees/probe-a`. **`waiting` never appeared.** A declined tool call fires no `Stop`, so the declined session read `working` until its next turn ended.

The screen does show the approval. `workmux capture probe-a --lines 200` at the `date` approval, tail:

```
> Run the shell command date and show its output.

● Ran (date) (ctrl+o to expand)

Command
────────────────────────────────────────────────────────────…

Requesting permission for:
   date

Run this command?
> 1. Yes, run command
  2. Yes, and always allow in this conversation for commands that start with 'date'
  3. Yes, and always allow for commands that start with 'date' (Persist to settings.json)
  4. No, cancel

  ↑/↓ Navigate · tab Amend · ctrl+g edit/expand command
esc to cancel … tech-lead (Gemini 4 Argon · high)  /agents
```

### 6. The captured screen around a RETURN block

```console
$ workmux send probe-a "Say in one line that the date command was declined, then end your reply with this block in a code fence, one field per line: ### RETURN, status: needs-decision, task: probe-a, changed: none, evidence: date was declined, findings: none, risks: none, follow-ups: none, questions: <one question of at least 400 characters asking whether to retry the date command or skip it, with the reasons for each>, knowledge: none"
$ workmux capture probe-a --lines 200      # after status turned done; pane 238 columns × 63 rows
```

The session had no copy of `personas/_shared/return.md`, so the prompt listed the block's fields inline, with `findings: none`. Lines 39–63 of the 63 captured. The two long rules are trimmed with `…`, the padding in the status line is trimmed with `…`, and trailing spaces are stripped: the TUI pads the signature line, and the first two lines of the `questions:` value end in five and one trailing spaces. Nothing else is changed:

```
────────────────────────────────────────────────────────────
> Say in one line that the date command was declined, then end your reply with this block in a code fence, one field per line: ### RETURN, status: needs-decision, task: probe-a, changed: none, evidence: date was declined, findings: none,
  risks: none, follow-ups: none, questions: <one question of at least 400 characters asking whether to retry the date command or skip it, with the reasons for each>, knowledge: none

▸ Thought for 11s, 541 tokens

  👨‍💻 Tech-Lead: Execution of the date shell command was declined by the user permission check.

    ### RETURN
    status: needs-decision
    task: probe-a
    changed: none
    evidence: date was declined
    findings: none
    risks: none
    follow-ups: none
    questions: Would you like me to retry running the shell command "date" (which requires your explicit permission approval in the prompt so that we can capture and verify the actual live system clock output from the shell environment
    as originally requested), or should we skip executing the "date" command altogether (which avoids re-triggering the permission prompt and respects your previous denial while allowing us to conclude the probe-a task immediately
    without shell timestamp output)?
    knowledge: none

────────────────────────────────────────────────────────────…
>
────────────────────────────────────────────────────────────…
? for shortcuts … tech-lead (Gemini 4 Argon · high)  /agents
```

What a reader of this capture has to handle:

- **No fence and no frame.** The code fence is not drawn. There are no ```` ``` ```` markers and no box characters. Every line of the block, `### RETURN` included, is indented four spaces. The signature line is indented two.
- **Wrapping is the TUI's own.** A long value breaks at a word boundary at the pane width: the first two lines of the `questions:` value are 235 characters in a 238-column pane. The continuation lines carry the *same* four-space indent as the field lines, with no hanging indent, so only the missing `<field>:` at the start tells a continuation from a field. `tmux capture-pane -J` does not join them, because the TUI writes each line itself.
- **The capture is the visible screen only.** agy draws on the alternate screen here: `#{alternate_on}` 1 and `#{history_size}` 0, read on the dispatching session's pane. The probe machine's agy settings carry `"altScreenMode": "always"`, and whether that is agy's default was not checked. `--lines 200` returned 63 lines on the 63-row pane, and 53 at the approval prompt. It never returned more than the pane's height. A reply whose tail is taller than the pane would lose the top of its block.
- **Not exercised:** the nested `findings:` list, with its `  - severity:` sub-lines, so how its extra indent renders is not measured.

### Reported, not measured

The owner reports that at agy 1.5.3, a session started with `agy --agent tech-lead --remote-control` in a terminal-multiplexer window was visible on their phone, and that an Antigravity session was able to run workmux. The first report bears on item 6, the host's remote feature reaching a session in a window. Step 3 measures the second report; the first is still the owner's report.

### Consequences

1. **Item 1, the basics at the installed version, holds at agy 1.5.3.** `--agent tech-lead` resolves, the body arrives, and the global plugin install still delivers the agents. That the tech-lead's eleven tool names resolve is inferred, not swept: see the paragraph after step 2's commands. The full registry sweep was not re-run. `tools/check.py`'s `agy plugin validate` gate needs its success test updated for 1.5.3's output. That is not done here.
2. **Item 2, a session runs workmux through its shell tool, holds, with two stops that need the person.** An agy session ran `workmux add` through its shell tool, reached tmux, and created a worktree outside its own folder. Before that it waited on agy's approval for the command, because the probe machine's settings ask before every command, and on workmux's offer to update the hooks of another agent. That offer reads an answer from the terminal agy gives its commands. So the fleet skill's prerequisite is `workmux setup` run for *every* agent workmux detects, not only Antigravity. A dispatching session should expect one approval per `workmux add` unless the person allows `workmux` commands.
3. **Item 3, a worktree tech-lead getting its start prompt and committing, holds, with one stop per new worktree.** The start command is `workmux add <name> --background --agent "agy --agent tech-lead" --prompt "<text>"`, which workmux runs as `agy --agent tech-lead -i "<text>"`. Each new worktree path raises agy's trust dialog. Trust is per exact path, so trusting the main checkout or a parent folder does not help, and the session waits in its window until someone accepts. In a test, a session-only `--settings '{"trustedWorkspaces": ["<folder>"]}'` skipped the dialog and saved nothing, so it could go in the start command. Trusting a folder is a decision for the person. Whether a start command may make it on their behalf is left to the owner; this entry does not decide it. The worktree session committed after one approval. Loading the skill from the start prompt is not measured, because the skill does not exist yet.
4. **Item 4, the states workmux reports, holds only in part: for agy it reports only `working` and `done`.** A session at an approval prompt reads `working`. A session whose tool call was declined reads `working` until its next turn ends. A session at the first-run trust dialog read `done` once its start turn had finished. So status alone cannot tell "waiting on the person" from "working", and an overview built on status shows less for this host. That limits the overview; it does not stop Antigravity tech-leads from being dispatched. The screen can tell: at an approval prompt the capture contains `Requesting permission for:` and `Run this command?`.
5. **Item 5, a captured screen holding the last RETURN block in full, is outside this entry's scope.** It is recorded because step 6 measured it. It holds as long as the reply's tail fits the visible screen: the block was in the capture in full. A reader must find `### RETURN` after leading spaces, join continuation lines that do not start with a field name, and strip trailing spaces.

**Host state.** `workmux remove -f probe-a` removed the worktree and the branch (`✓ Removed worktree 'probe-a' and branch 'probe-a'`). Afterwards `workmux status --json` listed `"agents": []`, `git worktree list` listed only `<tmp>/repo`, and the probe's tmux session was killed. Answering `n` had created `~/.local/state/workmux/setup.json` (`{"declined": ["copilot"], "declined_skills": []}`), `workmux send` had created `~/.local/state/workmux/sent/`, and workmux kept a state file for each of the two probe panes. All four were removed to restore the earlier state. `~/.copilot/hooks/workmux-status.json`, `~/.gemini/config/config.json` and `~/.gemini/settings.json` have the same hashes as before, and by modification time `~/.gemini/config/hooks.json` and the workmux config were not touched after the probe began. One change was left: agy itself wrote `<tmp>/repo` and `<tmp>/repo__worktrees/probe-a` into `trustedWorkspaces` in `~/.gemini/antigravity-cli/settings.json` when the two dialogs were accepted. Without those two entries, the file's current content re-serialises to exactly its size before the probe (2,583 bytes). The two entries now point at paths that no longer exist. This probe does not edit the owner's agy settings.

---

## E27 — the fleet skill end to end on Antigravity: a dispatched tech-lead loads `ec-fleet` from its start prompt, and the overview reads its stop

**Date** 2026-11-14. **agy 1.5.3**, model Gemini 4 Argon (High), the configured default; **workmux 0.1.281**; **tmux 3.8**; this package as of commit `c2d6b91`. Tranche B.

E26 left two of the fleet's host facts unmeasured, because the skill did not exist yet: the second half of its item 3, that a tech-lead workmux starts in a worktree loads the skill from its start prompt, and its item 5 end to end, that the overview reads a real stop. This entry measures both with the real skill installed, the package's default start command and no config file (`~/.config/e-colleagues/fleet.toml` absent, `XDG_CONFIG_HOME` and `EC_FLEET_CONFIG` unset).

Everything ran in a throwaway repository, `<tmp>/repo` (`git init`, one commit, a repository-local identity, no signing). Its contract came from the deterministic half of `ec-init`, `python3 skills/ec-init/scripts/bootstrap.py <tmp>/repo --write` (`wrote 3 files, 3 changed`: `AGENTS.md`, `CLAUDE.md`, `.e-colleagues/lock.json`), committed. No interview was run, so the project bindings are empty: no tracker, no tools, no `### Parallel work` lines. The probe used its own tmux session, `e27-probe`, and touched no other session or window. Two real sessions on the owner's account reached the model: the dispatching tech-lead (three messages) and the dispatched one (its start prompt only). Every interactive session again printed `⚠ Sign-in update needed … some requests may fail`; no request failed.

Tool-call timings below come from agy's own transcript of each session (`~/.gemini/antigravity-cli/brain/<conversation>/.system_generated/logs/transcript.jsonl`), hook timings from workmux's log, both in UTC.

### 1. The install

Before:

```console
$ agy --version
1.5.3
$ agy plugin list
Installed plugins:
…
- e-colleagues (enabled, 0.1.1)
    Source:     antigravity
    Components: 4 skills, 6 agents
…
$ ls ~/.gemini/config/plugins/e-colleagues/skills
ec-init
ec-onboard
ec-status
ec-tech-lead
```

The install source was a clean export of the tracked files, so nothing untracked reached the plugin directory, in a directory named `e-colleagues` because agy keys a plugin by its directory name (E8):

```console
$ git archive fleet-skill | tar -x -C <tmp>/export/e-colleagues
$ cd <tmp>/export && agy plugin install ./e-colleagues; echo "rc=$?"
  [ok]    e-colleagues
          ✔ skills      : 5 installed (ec-fleet, ec-init, ec-onboard, ec-status, ec-tech-lead)
          ✔ agents      : 6 installed (designer, developer, platform, reviewer, security, tech-lead)
          Installed to ~/.gemini/config/plugins/e-colleagues (replaced existing installation)
rc=0
$ agy plugin list
…
- e-colleagues (enabled, 0.1.1)
    Source:     antigravity
    Components: 5 skills, 6 agents
…
```

The installed `skills/ec-fleet/SKILL.md`, `skills/ec-fleet/scripts/fleet.py` and `agents/tech-lead/agent.md` are byte-identical to the repository's (`cmp` rc 0 for each).

**At 1.5.3 the install replaced the old one; it did not merge.** "replaced existing installation" is literal. Before, the destination held 116 files, 29 of them absent from the source: the earlier install's `.git/` directory and two `__pycache__/*.pyc` files. Afterwards it held exactly the export's 87 files, path for path, and the 29 were gone. E8 measured the opposite at agy 1.1.27, where a file deleted from the source survived a re-install, so on this one run at 1.5.3 the finding contradicts E8. The places that stated E8's merge finding now give both versions: `docs/acceptance.md`, the README's Antigravity block, `docs/design.md` §2.2 (`--prune` on Antigravity) and §12 (updates in a consumer's tools), `hosts/antigravity.yaml`, and claim AG-08 in `docs/SUPPORT-MATRIX.md`.

### 2. The dispatching session starts issue 12

The dispatching tech-lead was started in the probe session's first pane, in `<tmp>/repo`, with a session-only trust setting so that its own folder raised no dialog (E26):

```console
$ agy --agent tech-lead --settings <tmp>/trust-settings.json -i 'use the ec-fleet skill; start 12'
```

`<tmp>/trust-settings.json` holds `{"trustedWorkspaces": ["<tmp>/repo"]}`. The session opened with no dialog and still asked before every command, so the session-only setting did not drop the saved `"ask"` setting.

Its first tool call read `~/.gemini/config/plugins/e-colleagues/skills/ec-fleet/SKILL.md`. Its second was the start, which asked for approval:

```
Requesting permission for:
   python3 ~/.gemini/config/plugins/e-colleagues/skills/ec-fleet/scripts/fleet.py start 12 --host antigravity

Run this command?
> 1. Yes, run command
…
```

Option 1 was chosen. The transcript records `Command exited with code 0.` and the output `started issue-12`, and the reply was:

```
  👨‍💻 Tech-Lead: Started worktree issue-12 for issue 12.

  • Command: python3 ~/.gemini/config/plugins/e-colleagues/skills/ec-fleet/scripts/fleet.py start 12 --host antigravity (exit code 0)
  • Output: started issue-12
```

It read no `AGENTS.md` before starting. With this contract that changes nothing: there is no naming line, so the default name applies either way. Whether a dispatching session reads the contract and honours a naming line is not measured.

workmux's log for that call, trimmed, and what it started:

```
22:02:21.060  workmux add issue-12 --background --agent "agy --agent tech-lead" --prompt "Use the ec-fleet skill. Your assignment: issue 12."   cwd=<tmp>/repo
22:02:21.096  create:start branch="issue-12" base=Some("main")
22:02:21.139  window created, pane %26
22:02:21.231  create:completed path=<tmp>/repo__worktrees/issue-12
```

```console
$ tmux list-windows -t e27-probe -F '#{session_name}:#{window_index} #{window_name} #{pane_id} #{pane_width}x#{pane_height} #{pane_current_command}'
e27-probe:0  repo %25 200x50 agy
e27-probe:1  issue-12 %26 238x63 agy
$ tr '\0' '|' < /proc/<agy in %26>/cmdline
agy|--agent|tech-lead|-i|Use the ec-fleet skill. Your assignment: issue 12.|
```

A window appeared, in the probe's session. The dispatched session got no trust setting: the default start command, as the skill ships it.

**workmux asked nothing.** In E26, `workmux add` run from agy's pseudo-terminal stopped to offer an update to another agent CLI's status hooks, and its log shows 90 seconds between the command's start and `create:start`. Here, run by `fleet.py`, which gives the launcher no stdin, the same two events are 36 ms apart. No question reached anyone, no `~/.local/state/workmux/setup.json` (where an answer is recorded, E26) was written, and that other agent's hooks file has the same hash as before, unchanged since before E26. `workmux setup` was not run. That workmux skips the question because its stdin is not a terminal is an inference from this one run.

### 3. At the trust dialog

The new window showed agy's trust dialog for the new path, trailing spaces stripped:

```
Accessing workspace:

<tmp>/repo__worktrees/issue-12

Do you trust the contents of this project?

Antigravity CLI requires permission to read, edit, and execute files here.

> Yes, I trust this folder
  No, exit

  ↑/↓ Navigate · enter Confirm
```

With the dialog on screen, the dispatching session was sent `overview`. It ran `python3 ~/.gemini/config/plugins/e-colleagues/skills/ec-fleet/scripts/fleet.py overview` after one approval, exit code 0. The output, from the transcript, matches the screen:

```
NAME      STATE    HOST  RETURN  QUESTIONS
repo      working  agy           (this session)
issue-12  working  agy
```

Its reply showed the table and added: "issue-12 is currently working (note that some hosts also report a session waiting at one of the host's own approval or first-run prompts as working)."

**The session at the dialog read `working`, not `done`, so its row says nothing more.** It sat at the dialog for 5 min 27 s. `workmux status --json` read `working` throughout (`elapsed_secs` 34, 56, 320, 332), and no hook call came between its `working` at 22:02:23 and the dialog's acceptance at 22:07:50. The transcript shows why. The start turn ran *behind* the dialog:

| step | what | created | completed |
|---|---|---|---|
| 0 | the start prompt, `Use the ec-fleet skill. Your assignment: issue 12.` | 22:02:23 | |
| 1 | the model's first response, with two tool calls: `read_file ~/.gemini/config/plugins/e-colleagues/skills/ec-fleet/SKILL.md` and `run_command "pwd && ls -la"` | 22:02:23 | |
| 2 | the read | 22:02:30 | 22:02:31 |
| 3 | the command | 22:02:31 | 22:08:08 |

The command's approval waited, unseen, behind the dialog, and a session at an approval reads `working` (E26). E26's start prompt needed no tool, so its turn ended behind the dialog and read `done`. The table also settles E26's inference from timestamps: the start prompt runs before the folder is trusted. The model ran, and a file read completed, while the dialog was on screen.

The dialog was then accepted in that window, acting as the person.

### 4. The dispatched tech-lead loads the skill and stops

The approval for `pwd && ls -la` appeared as soon as the dialog closed. It asked three times in all, each time for a read-only command, and each was answered with option 1: `pwd && ls -la`, `ls -la .e-colleagues`, `git status && git remote -v && git log -n 5`. Between them it read `AGENTS.md`, `README.md` and the installed `scripts/fleet.py`. The `Stop` hook marked it `done` at 22:09:33.

`workmux capture issue-12 --lines 200`, the overview's own read, returned 38 lines (the pane was 238 × 63; `#{alternate_on}` 1, `#{history_size}` 0). Lines 7–38 follow. The long rules and the status-line padding are trimmed with `…`, trailing spaces are stripped (the `status:` line ends in one), and nothing else is changed:

```
────────────────────────────────────────────────────────────…
> Use the ec-fleet skill. Your assignment: issue 12.

⚠ Sign-in update needed
  ⎿  Your sign-in is missing permissions that are now required, so some requests may fail. Run /logout to sign in again.

○ Thought for 52.3s (Initial hypothesis: This appears to be a fleet probe, as the README.md file suggests. Further investigation reveals AGENTS.md lacks details about platforms, tools, workflow and permissions. Therefore, access to i...)
● Explored 1 file (SKILL.md)
● Ran (pwd && ls -la)
● Explored 2 files (AGENTS.md, README.md)
● Ran 2 commands (ls -la .e-colleagues · git status && git remote -v && git log -n 5)
● Explored 1 file (fleet.py) (ctrl+o to expand)

▸ Thought for 10s, 529 tokens

  👨‍💻 Tech-Lead: I read AGENTS.md, and ### Platforms and tools has no issue tracker or tool bindings configured (and git remote -v has no remote URL). Please share the brief for issue 12 or specify which tracker/tool to read it from.

    ### RETURN
    status: blocked
    task: issue 12
    changed: none
    evidence: read AGENTS.md (Platforms and tools is empty); git remote -v (exit 0, empty origin)
    findings: none
    risks: none
    follow-ups: none
    questions: What is the specification for issue 12, or which tracker and tool should I use to read it?
    knowledge: none

────────────────────────────────────────────────────────────…
>
────────────────────────────────────────────────────────────…
? for shortcuts … tech-lead (Gemini 4 Argon · high)  /agents
```

What shows that it loaded the skill from its start prompt:

- **The prompt arrived.** It is the transcript's first user input and the first line of the conversation on screen.
- **The skill was its first act.** The first tool call, in the model's first response to that prompt, read the installed `skills/ec-fleet/SKILL.md`. The thought summary for that response, as first shown: "Initial assessment: Task requires utilizing the `ec-fleet` skill. The first step involves reading the skill's instructions."
- **It followed the skill's rules for an issue assignment.** It read `AGENTS.md`, as the skill's "The contract" says to. It looked for the tracker the contract names, found none, and asked and waited (rule 3) instead of guessing at an issue it could not read.
- **It ended with the skill's RETURN block** at the very end, its keys complete and in order, `task: issue 12`, and its question under `questions` (rule 4). Nothing in the tech-lead's own body asks it to end a reply with a RETURN block: the block is what its specialists return to it, and T5 tells it to relay those as a signed summary, never raw. The block comes from the skill.

The block rendered as E26 step 6 describes: no fence drawn, every line indented four spaces, the signature two. No value wrapped, and `findings: none` again, so the nested list is still not exercised.

### 5. The overview reads the stop

The dispatching session was sent `overview` again and ran the same command after one approval, exit code 0. The output, from the transcript, matches the screen:

```
NAME      STATE    HOST  RETURN   QUESTIONS
repo      working  agy            (this session)
issue-12  done     agy   blocked  What is the specification for issue 12, or which tracker and tool should I use to read it?
```

Its reply showed the table, then: `issue-12 has stopped (RETURN: blocked) and is waiting for your input in its own session: "What is the specification for issue 12, or which tracker and tool should I use to read it?"`. The installed script's `last_return`, run on the saved capture, returns `{'status': 'blocked', 'questions': 'What is the specification for issue 12, or which tracker and tool should I use to read it?'}`.

`repo` is the dispatching session's own row, named after the main checkout's directory and marked `(this session)`; it reads `working` because the overview runs inside its turn. `workmux status --json` is scoped to the repository it runs in (`"scope": {"repository": "<that repository>", "all": false}`): from `<tmp>/repo` it listed only the probe's two sessions, although another agent session was registered on the same tmux server. So the overview lists the sessions of the dispatching session's repository only.

### Verdicts

1. **"A tech-lead started by workmux in a worktree gets its start prompt and loads the skill from it": holds** at agy 1.5.3 with workmux 0.1.281. `fleet.py start` delivered the prompt through workmux's `-i`. The tech-lead's first tool call read the installed `SKILL.md`, and its first stop followed the skill's rules for an issue assignment. The start turn begins behind the trust dialog, before the person trusts the folder.
2. **"A captured screen of a stopped session contains its last RETURN block in full, and the overview reads it": holds.** The capture held the whole block, and the overview showed `done`, `blocked` and the question verbatim.
3. **Against E26, and against what design §17 and the acceptance notes said: a tech-lead started by `fleet.py` read `working` at the first-run trust dialog, not `done`.** Its start turn stops at the approval for its first command, hidden behind the dialog. The overview therefore showed `working` with RETURN and QUESTIONS empty, not `no RETURN block on screen`. This was measured with agy set to ask before every command (E26). Without that setting the first command might run behind the dialog and the turn end as `done`; that is not measured.

### Not measured

- A contract with `### Parallel work` lines: naming, posting, pushing, and whether a dispatching session reads `AGENTS.md` and honours a naming line.
- Any stop after the first: an answered question, `ready to push`, a commit or a push from the worktree.
- A block taller than the pane, a wrapped value, the nested `findings:` list.
- Several issues at once, and the plan assignment.
- The trust dialog on a machine whose agy settings do not ask before every command.
- Why workmux asked nothing: see the inference in step 2.
- Codex, opencode and Claude Code, and remote use on any host.

**Host state.** The plugin install replaced `~/.gemini/config/plugins/e-colleagues/` with this package's tracked files at `c2d6b91` (five skills, six agents), as the owner approved, and that install was left in place. agy wrote `<tmp>/repo__worktrees/issue-12` into `trustedWorkspaces` in `~/.gemini/antigravity-cli/settings.json` when its dialog was accepted. That entry is the file's only change (2,866 bytes before, 3,018 after), and it now points at a path that no longer exists. The dispatching session's session-only setting saved nothing. agy also kept its usual per-session records under `~/.gemini/antigravity-cli/` (conversations, transcripts, logs, prompt history), and workmux appended to its log. workmux kept a state file for each of the two probe panes under `~/.local/state/workmux/agents/`; both were removed, and the list of workmux state files matches the one taken before. No `setup.json` or `sent/` was created. `~/.gemini/config/config.json`, `~/.gemini/settings.json`, `~/.gemini/config/hooks.json` and `~/.copilot/hooks/workmux-status.json` have the same hashes as before, and the workmux config was not modified. `workmux remove -f issue-12` printed `✓ Removed worktree 'issue-12' and branch 'issue-12'`. Afterwards `workmux status --json` in `<tmp>/repo` listed `"agents": []`, `git worktree list` listed only `<tmp>/repo`, the probe's tmux session was killed, and no agy process remained.

---

## E28 — a fleet tech-lead opens in a new worktree with no trust dialog: a session-only trust setting carrying the path workmux reports before it creates anything

**Date** 2026-11-15. **agy 1.5.3**, model Gemini 4 Argon (High), the configured default; **workmux 0.1.281**; **tmux 3.8**. Tranche B.

E26 found that every new worktree raises agy's trust dialog, that trust is kept per exact path, and that `--settings` with `trustedWorkspaces` avoids the dialog for one session in a folder whose path is known. E27 found what the dialog costs: the started session sits behind it and reads `working`. The open question was whether `fleet.py start` can hand a new worktree's session that setting, when workmux and not the script chooses the worktree's path.

Everything ran in a throwaway repository, `<tmp>/repo` (`git init`, one commit, a repository-local identity, no signing), from a tmux session created for the probe, `e28-probe`. Every start was run by `fleet.py` in that session's first pane, with a config file that shortens the start prompt to `Reply with the single word ready, then stop.` so that each run costs one short turn. The hash of `~/.gemini/antigravity-cli/settings.json` was taken before the first step and after each one.

### 1. agy has no trust flag, and the setting needs the absolute path

`agy --help` at 1.5.3 lists no flag for trust. The one route is the setting:

```
  --settings    Settings for this session only, never saved: a JSON object of settings.json keys, inline or as a file path
```

A search of the binary's strings for trust settings found only `json:"trustedWorkspaces,omitempty"`. That is a search, not proof that no other key exists.

A relative path is not accepted. In a new worktree:

```console
$ agy --agent tech-lead --settings '{"trustedWorkspaces":["."]}'
Accessing workspace:
<tmp>/repo__worktrees/issue-12
Do you trust the contents of this project?
```

### 2. workmux passes the start command's arguments literally

The first attempt let the shell in the new pane supply the path. The host's start command was `agy --agent tech-lead --settings "{\"trustedWorkspaces\":[\"$PWD\"]}"`. workmux typed this into the pane:

```console
$ agy --agent tech-lead --settings '{"trustedWorkspaces":["$PWD"]}' -i "$(cat .workmux/PROMPT-issue-12.md)"
```

and the process list showed the argument as `{"trustedWorkspaces":["$PWD"]}`. workmux re-quotes each argument, so nothing in the start command is expanded in the pane, and the dialog showed. The path has to be known before the start.

### 3. workmux reports the path before it creates anything

```console
$ workmux add issue-13 --dry-run
Worktree: <tmp>/repo__worktrees/issue-13
Branch:   issue-13
Base:     main
Target:   issue-13 (window)

Files to copy or symlink:
  (none)

Post-create hooks:
  (none)
```

rc 0, and `git worktree list` was the same before and after. For a name whose worktree already exists it prints the same first line, with `Base:     existing branch`. There is no machine-readable form: `workmux add issue-13 --headless --json --dry-run` gave rc 1, `Error: Layout, fork, wait, and dry-run options cannot be used with --headless`. `workmux path <name>` prints the path only once the worktree exists, and `workmux open` takes no `--agent`, so the worktree cannot be made first and the agent started second.

### 4. With the path in the setting, the session opens with no dialog

`fleet.py start 15`, with the package's default Antigravity host and no other change. workmux's log, in order:

```
args=["workmux", "add", "issue-15", "--dry-run"]
args=["workmux", "add", "issue-15", "--background", "--agent", "agy --agent tech-lead --settings '{\"trustedWorkspaces\":[\"<tmp>/repo__worktrees/issue-15\"]}'", "--prompt", "Reply with the single word ready, then stop."]
```

The script printed `started issue-15`, rc 0, and nothing on stderr. The new window, with agy's banner and an account notice removed:

```
> Reply with the single word ready, then stop.
▸ Thought for 13s, 676 tokens
  👨‍💻 Tech-Lead: ready
```

No dialog. `workmux status --json` gave `"status": "done"`, `"agent_kind": "agy"`. Asked next to run `git branch --show-current`, the session stopped at agy's approval for that command, as this machine's settings ask before every command; approved once, it ran:

```
● Ran (git branch --show-current) (ctrl+o to expand)
  👨‍💻 Tech-Lead: git branch --show-current (exit code 0):
    issue-15
```

So a session trusted this way works in its worktree. The settings file's hash was identical before and after, and it held no path of this probe: nothing was saved. A run before the script was changed, with the same start command written into the config by hand for `issue-14`, gave the same result.

### 5. Control: without the setting, the dialog shows

`fleet.py start 16` with `trust = ""` under `[hosts.antigravity]`. workmux's log shows one call and no dry run:

```
args=["workmux", "add", "issue-16", "--background", "--agent", "agy --agent tech-lead", "--prompt", "Reply with the single word ready, then stop."]
```

and the new window showed:

```
Accessing workspace:
<tmp>/repo__worktrees/issue-16
Do you trust the contents of this project?
Antigravity CLI requires permission to read, edit, and execute files here.
> Yes, I trust this folder
  No, exit
```

It read `done`, as E26 saw for a start prompt that needs no tool. It was answered "No, exit".

### 6. A path with a space, and `--base`

A second repository, `<tmp>/my repo`, with a branch `other` one commit ahead of `main`. `fleet.py start 20`, then `fleet.py start 21 --base other`. workmux's log:

```
args=["workmux", "add", "issue-20", "--dry-run"]
args=["workmux", "add", "issue-20", "--background", "--agent", "agy --agent tech-lead --settings '{\"trustedWorkspaces\":[\"<tmp>/my repo__worktrees/issue-20\"]}'", "--prompt", "Reply with the single word ready, then stop."]
args=["workmux", "add", "issue-21", "--dry-run"]
args=["workmux", "add", "issue-21", "--background", "--agent", "agy --agent tech-lead --settings '{\"trustedWorkspaces\":[\"<tmp>/my repo__worktrees/issue-21\"]}'", "--prompt", "Reply with the single word ready, then stop.", "--base", "other"]
```

Both sessions opened with no dialog and answered `ready`, so a path holding a space passes through the setting. And `--base` reaches workmux as its own `--base`:

```console
$ git worktree list
<tmp>/my repo                     0db7aa5 [main]
<tmp>/my repo__worktrees/issue-20 0db7aa5 [issue-20]
<tmp>/my repo__worktrees/issue-21 19c2ce2 [issue-21]
$ git log --oneline --all
0db7aa5 init
19c2ce2 other
```

`issue-21` starts at `other`'s commit, `issue-20` at `main`'s. The settings file's hash was unchanged.

### Verdict

**At agy 1.5.3 with workmux 0.1.281, `fleet.py start` opens an Antigravity tech-lead in a new worktree with no trust dialog and saves nothing.** It asks workmux for the path with `workmux add <name> --dry-run`, reads the `Worktree:` line, and appends `--settings '{"trustedWorkspaces":["<path>"]}'` to the start command. The trust is for that session and that path only. When the script cannot learn the path it says so on stderr and starts without the setting, so the dialog shows as before.

**Not measured:**

- A worktree path holding a quote or a backslash. The script refuses one, and the start then goes ahead without the setting; that refusal is tested, not measured against agy.
- Any workmux other than 0.1.281. The `Worktree:` line is its human-readable output, not an interface it promises.
- What agy loads from a folder trusted this way, such as that folder's own hooks, against one trusted through the dialog.
- Codex, opencode and Claude Code, whose own first-run prompts were not looked at.

**Host state.** Six worktrees were made and removed (`✓ Removed worktree 'issue-12' and branch 'issue-12'`, and the same for 14, 15, 16, 20 and 21). Afterwards `workmux status --json` in `<tmp>/repo` listed `"agents": []`, `git worktree list` listed only `<tmp>/repo`, both probe tmux sessions were killed and no agy process remained. `~/.gemini/antigravity-cli/settings.json` had the same hash at every step. workmux kept a state file for each of five probe panes under `~/.local/state/workmux/agents/`; all five were removed. agy kept its usual per-session records, and workmux appended to its log.

---

## E29 — the fleet skill on Codex: the default start works end to end and workmux reports `working`, `waiting` and `done`; a session at Codex's trust prompt is missing from the overview, and a session-only `-c 'projects={…}'` override removes that prompt

**Date** 2026-11-15. **codex-cli 0.167.0**, model gpt-6.1-sol at reasoning effort high, both set in the profile file on the probe machine; **workmux 0.1.281**; **tmux 3.8**; this package as of commit `754fce5`. Tranche B.

E26 to E28 measured `ec-fleet` on Antigravity only, and design §17 lists Codex as UNVERIFIED. This entry answers the same questions for Codex:

1. **Start.** Does `fleet.py start` with the package's default command open the window, start the tech-lead and deliver the prompt, and does workmux report the session?
2. **First-run prompts.** Does a new worktree stop at one, what does workmux report meanwhile, and can it be pre-answered for one session, saving nothing?
3. **States.** Which of `working`, `done` and `waiting` does workmux report, and what does a session at an approval read?
4. **The captured screen.** Does the overview read a RETURN block from Codex's screen?
5. **End to end.** Does a started tech-lead load `ec-fleet` from its start prompt, read `AGENTS.md` and stop with a RETURN block that the overview shows?
6. **Dispatch from inside a Codex session.** Can a Codex tech-lead run `fleet.py start` itself, and what does it need?

Everything ran in three throwaway repositories, `<tmp>/repo` and, for one control each, `<tmp>/repo.two` and `<tmp>/my repo` (each `git init`, one commit, a repository-local identity, no signing, then `python3 <pkg>/skills/ec-init/scripts/bootstrap.py <repo> --write`, `wrote 3 files, 3 changed`, committed; no interview, so the project bindings are empty). `<pkg>` is a clean export of this package's tracked files at `754fce5`; every `fleet.py` run used that copy or a byte-identical one. The probe used its own tmux session, `e29-probe`, and ran `fleet.py` from that session's shell pane. Other probes ran on the same tmux server in their own sessions at the same time; `workmux status --json` is scoped to the repository it runs in (E27), so they never appeared in this probe's readings. No config file existed (`~/.config/e-colleagues/` absent, `XDG_CONFIG_HOME` and `EC_FLEET_CONFIG` unset); where a step used one, it says so.

These were real sessions on the owner's account. Ten reached the model, seven in steps 2 to 7 and three in step 8. The seven: four with the start prompt shortened to `Reply with the single word ready, then stop.`, one of which then took three more prompts (steps 4 and 5); the end-to-end tech-lead (its start prompt only); the dispatching tech-lead (two messages); and the session it started (the short prompt). The three in step 8 took the short prompt and one more each. The hand checks of the trust prompt in steps 3 and 8 sent no prompt.

Tool-call timings come from Codex's own record of each session (`~/.codex/sessions/2026/11/15/rollout-*.jsonl`), hook timings from workmux's log, both in UTC.

### 1. Versions, the Codex hooks, and what was installed

```console
$ codex --version
codex-cli 0.167.0
$ workmux --version
workmux 0.1.281
$ tmux -V
tmux 3.8
```

`~/.codex/hooks.json` holds one command per event, and nothing else:

| event | command |
|---|---|
| `SessionStart` (matcher `startup\|resume\|clear`) | `workmux register-agent` |
| `UserPromptSubmit`, `PostToolUse`, `SubagentStart`, `SubagentStop` | `workmux set-window-status working` |
| `PermissionRequest` | `workmux set-window-status waiting` |
| `Stop` | `workmux set-window-status done` |

`workmux docs` lists Codex as `✅ Supported` in its status table with no limiting note, and does not say where its Codex hooks go. The hooks were already installed; `workmux setup` was not run. Codex keeps a trusted hash for each of the seven hooks under `[hooks.state]`, and those were already present, in `~/.codex/config.toml` and in the profile file alike.

What this package had installed for Codex, as found:

```console
$ ls ~/.codex/agents
designer.toml  developer.toml  platform.toml  reviewer.toml  security.toml
$ python3 <pkg>/skills/ec-init/scripts/bootstrap.py --scope user --check; echo "rc=$?"
  e-colleagues.config.toml is out of date
  opencode/skills/ec-fleet is missing or out of date
  opencode/skills/ec-init is missing or out of date
3 file(s) need --write
rc=1
$ codex plugin list
…
PLUGIN                     STATUS         VERSION  SOURCE
e-colleagues@e-colleagues  not installed           <the repository checkout>
…
```

The two opencode lines are another host's and outside this entry. The five role files are byte-identical to the export's (`cmp` rc 0 for each). The profile file `~/.codex/e-colleagues.config.toml` exists: its first 111 lines are the export's whole profile (`diff` rc 0), and 33 further lines follow that this package does not render: `model = "gpt-6.1-sol"`, `model_reasoning_effort = "high"`, `[tui]`, `[tui.model_availability_nux]` and `[hooks.state]` with the seven hashes. That is why `--check` calls it out of date. Who wrote the two model lines was not established.

**The plugin was not installed, so Codex had no `ec-fleet` skill on this machine.** The documented install, `codex plugin add e-colleagues@e-colleagues`, was attempted with the export as its source and was refused, before it ran, by the permission system of the session that ran this probe. Nothing was installed. From step 6 on the skill was therefore supplied the other way design §7 names for Codex, as a project skill: `<pkg>/skills/ec-fleet` copied to `<tmp>/repo/.agents/skills/ec-fleet/` (`cmp` rc 0 for `SKILL.md` and `scripts/fleet.py`) and committed on `main`, so every new worktree carries it. The plugin route is not measured.

### 2. Start: the window, the command, the prompt

```console
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py start 12 --host codex; echo "rc=$?"     # in <tmp>/repo, 08:13:59
started issue-12
rc=0
$ git worktree list
<tmp>/repo                     05d8110 [main]
<tmp>/repo__worktrees/issue-12 05d8110 [issue-12]
$ tmux list-windows -t e29-probe -F '#{session_name}:#{window_index} #{window_name} #{pane_id} #{pane_width}x#{pane_height} #{pane_current_command}'
e29-probe:0  repo %38 200x50 bash
e29-probe:1  issue-12 %39 238x63 codex
```

(The window names carry a glyph that the probe machine's shell prompt adds; it is removed here.) Nothing on stderr. workmux's log for the call, and what it typed into the new pane, read with `tmux capture-pane -p -a` from the normal screen behind Codex's alternate screen:

```
08:13:59.343  workmux add issue-12 --background --agent "codex --profile e-colleagues" --prompt "Use the ec-fleet skill. Your assignment: issue 12."   cwd=<tmp>/repo
08:13:59.393  create:creating worktree branch="issue-12" path=<tmp>/repo__worktrees/issue-12 base=Some("main")
08:13:59.425  window created, pane %39
08:13:59.505  create:completed
```

```console
$ codex --no-daemon --profile e-colleagues -- "$(cat .workmux/PROMPT-issue-12.md)"
$ tr '\0' '|' < /proc/<codex in %39>/cmdline
codex|--no-daemon|--profile|e-colleagues|--|Use the ec-fleet skill. Your assignment: issue 12.|
```

**workmux adds `--no-daemon` and `--` itself.** The start command took arguments, and workmux recognised it as Codex: it put the prompt after `--` as Codex's positional prompt, and wrote it to `.workmux/PROMPT-issue-12.md`, with `.workmux/` added to `.git/info/exclude`, as on Antigravity (E26). `workmux add` asked nothing, as in E27.

This first start went no further: it stopped at Codex's trust prompt (step 3), was never answered, and was removed. The same command at 08:24:32, in the repository once trusted, is the end-to-end run of step 6. There the prompt was submitted on its own and the session registered. `workmux status --json` for a session that has run its turn, here the first one that did (step 3), trimmed:

```json
{
  "worktree": "issue-13",
  "branch": "issue-13",
  "project": "repo",
  "status": "done",
  "elapsed_secs": 24,
  "title": "Reply ready | issue-13",
  "pane_id": "%45",
  "workdir": "<tmp>/repo__worktrees/issue-13",
  "agent_kind": "codex",
  "session": "e29-probe",
  …
}
```

**The session is the tech-lead.** `--profile e-colleagues` layers the profile file, and the session record's developer messages include one of 20,429 characters beginning `# Tech-Lead`, before the user message that holds the start prompt. Every reply but three carried the signature `👨‍💻 Tech-Lead:`; the three were replies to "the single word ready", as in E26, and two more such replies were signed. The status line read `GPT-6.1-Sol high`, the profile file's model, where `~/.codex/config.toml` names another.

A side observation: started by hand with `--profile` and without `--no-daemon`, Codex shows a startup warning, `Running without the shared background server: --profile requires embedded mode.` workmux's own start never showed it.

### 3. First-run prompts

#### The trust prompt, and what workmux reports at it

The new window of step 2 showed this and nothing else, trailing spaces stripped:

```
  Folder access
  <tmp>/repo__worktrees/issue-12

  Note: You’re in a subdirectory of a Git project. Trusting will apply to the repository root:
  <tmp>/repo

  Trust this folder? Codex can read, edit, and run files here, subject to your permission settings. Folder settings can run code automatically, even without a model request. Continue only if you trust these files. Your trust decision
  will be saved.

› 1. Trust and continue
  2. Back to Agent Command Center

  enter continue · esc back
```

```console
$ workmux status --json          # in <tmp>/repo, the session at the prompt
{
  …
  "agents": [],
  "target_errors": []
}
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py overview; echo "rc=$?"
no sessions
rc=0
```

**A Codex session at the trust prompt is not in `workmux status --json` at all, so the overview has no row for it.** The `SessionStart` hook is what registers the pane, and it had not run: workmux's log holds the `window created` line for pane `%39` and no call from that pane. The same held for two more sessions left at the prompt (`%46`, `%62`: one `window created` line each, no call), against 5 log lines from a pane whose prompt was accepted. Later, with three sessions at the prompt and one finished, the overview printed one row:

```
NAME      STATE  HOST   RETURN  QUESTIONS
issue-13  done   codex          no RETURN block on screen
```

and in `<tmp>/repo.two`, `workmux list`, run with no terminal on stdin, showed the waiting one with no agent:

```
BRANCH    AGE  AGENT  MUX  UNMERGED  PATH
main      -    -      -    -         (here)
issue-21  <1m  done   ✓    -         ../repo.two__worktrees/issue-21
issue-22  <1m  -      ✓    -         ../repo.two__worktrees/issue-22
```

The start prompt does not run behind this prompt, unlike on Antigravity (E27): no turn starts until it is answered.

#### Trust is saved per repository root, and it covers every worktree

`fleet.py start 15` with a config file that sets only `[hosts.codex] prompt = "Reply with the single word ready, then stop."` showed the same prompt. `1. Trust and continue` was chosen there at 08:20:04, acting as the person. The hooks then ran (`register-agent` 08:20:06.800, `working` 08:20:06.844, `done` 08:20:08.569), and the screen showed the prompt and its answer:

```
› Reply with the single word ready, then stop.

• ready

  Worked for 3s • 9:20 AM
```

Codex saved the decision in the **profile file**, not in `~/.codex/config.toml`, whose hash did not change. `~/.codex/e-colleagues.config.toml` grew from 7,071 to 7,242 bytes by exactly:

```toml
[projects."<tmp>/repo"]
trust_level = "trusted"
```

The key is the repository root, as the prompt said, not the worktree. The next start, `fleet.py start 16` with the same config and so the package's default start command, opened with no prompt:

```console
$ codex --no-daemon --profile e-colleagues -- "$(cat .workmux/PROMPT-issue-16.md)"
```

```
08:20:40 [('issue-16', 'working', 1)]
08:20:42 [('issue-16', 'done', 0)]
```

So on Codex a new worktree raises the trust prompt only when the repository itself has never been trusted. Whether a decision saved in the profile file also holds for a session started without the profile was not measured.

#### A session-only pre-answer

`codex --help` at 0.167.0 lists no flag for trust. It lists `--dangerously-bypass-approvals-and-sandbox`, which was not tried, because it also removes the sandbox. `-c <key=value>` overrides a configuration value for one invocation. Each form below was tried by hand in the untrusted worktree `<tmp>/repo__worktrees/issue-12`, added to `codex --no-daemon --profile e-colleagues`, with no prompt, so no model call. All but the first two also carried `-c check_for_update_on_startup=false` (see the next heading). `<root>` is `<tmp>/repo`.

| added arguments | trust prompt |
|---|---|
| none (control) | shown |
| `-c 'projects."<worktree>".trust_level="trusted"'` | shown |
| `-c 'projects."<root>".trust_level="trusted"'` | shown |
| `-c 'projects={"<worktree>"={trust_level="trusted"}}'` | **not shown** |
| `-c 'projects={"<root>"={trust_level="trusted"}}'` | **not shown** |
| `-c 'projects={"."={trust_level="trusted"}}'` | shown |
| `-s workspace-write -a on-request` | shown |

The override works as an inline table, with the absolute path of the worktree or of the root as its key. The dotted form with a quoted key does not work, and neither does a relative path. Why the dotted form fails was not looked into. The two sessions that showed no prompt opened straight at the input box. `~/.codex/config.toml`, the profile file and `~/.codex/version.json` had the same hashes after every one of these runs.

Then through `fleet.py`, in `<tmp>/repo.two`, a repository Codex had never seen, with a dot in its path. The config file:

```toml
[hosts.codex]
prompt = "Reply with the single word ready, then stop."
trust = "-c 'projects={\"{worktree}\"={trust_level=\"trusted\"}}'"
```

`fleet.py --config <that file> start 21 --host codex` printed `started issue-21`, rc 0, nothing on stderr. workmux's log, in order, and what it typed:

```
args=["workmux", "add", "issue-21", "--dry-run"]
args=["workmux", "add", "issue-21", "--background", "--agent", "codex --profile e-colleagues -c 'projects={\"<tmp>/repo.two__worktrees/issue-21\"={trust_level=\"trusted\"}}'", "--prompt", "Reply with the single word ready, then stop."]
```

```console
$ codex --no-daemon --profile e-colleagues -c 'projects={"<tmp>/repo.two__worktrees/issue-21"={trust_level="trusted"}}' -- "$(cat .workmux/PROMPT-issue-21.md)"
```

The new window, with Codex's update banner removed:

```
  >_ OpenAI Codex (v0.167.0)
     <tmp>/repo.two__worktrees/issue-21

› Reply with the single word ready, then stop.

• 👨‍💻 Tech-Lead: ready

  Worked for 4s • 9:29 AM
```

No prompt. `workmux status --json` gave `('issue-21', 'done', 6, 'codex', '%61')`. The control, `fleet.py start 22` with a config that sets only the short prompt, typed `codex --no-daemon --profile e-colleagues -- "$(cat .workmux/PROMPT-issue-22.md)"` and showed the trust prompt for `<tmp>/repo.two__worktrees/issue-22`, and no agent was registered. It was not answered. After both, `~/.codex/config.toml` and the profile file had the hashes they had before: nothing was saved, and the profile file held no path under `<tmp>/repo.two`.

An earlier pair in `<tmp>/repo`, before it was trusted, gave the same result: `start 13` with the same `trust` string preceded by `-c check_for_update_on_startup=false` opened with no prompt and answered `ready` (`working` 08:17:55.5, `done` 08:17:57.7), and `start 14` and `start 15` without the override showed the prompt.

#### The update notice

At 08:15:07, during the probe, Codex's own update check rewrote `~/.codex/version.json`: `{"latest_version":"0.169.0","last_checked_at":"2026-11-15T08:15:07…Z","dismissed_version":null}`. From then on, a session started by hand **with no prompt** stopped first at a second first-run prompt, before the trust prompt:

```
  Update available · 0.167.0 → 0.169.0
  Release notes: https://github.com/openai/codex/releases/latest

› 1. Update now (runs `sh -c 's=$(curl -fsSL https://chatgpt.com/codex/install.sh) && CODEX_NON_INTERACTIVE=1 eval "$s"'`)
  2. Skip
  3. Skip until next version

  enter continue · esc skip
```

It was seen twice and skipped with `esc` both times; `version.json` did not change. With `-c check_for_update_on_startup=false` it did not show, in five hand runs.

**No start made by `fleet.py` showed it.** Six starts after 08:15:07 carried a start prompt and not that setting. None stopped at this prompt: one went straight to the trust prompt and stayed there, and the five that ran a turn showed a banner instead, above the conversation, and went on:

```
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✨ Update available! 0.167.0 -> 0.169.0                                                                          │
│ Run sh -c 's=$(curl -fsSL https://chatgpt.com/codex/install.sh) && CODEX_NON_INTERACTIVE=1 eval "$s"' to update. │
…
```

That a start prompt is what turns the blocking prompt into a banner is an inference from those runs. It matters because `enter` at the blocking prompt updates Codex.

### 4. States

The session `issue-16` (pane `%51`) was sent prompts by typing into its own pane, and `workmux status --json` was polled.

| moment, in the `issue-16` session | `status` | `elapsed_secs` read |
|---|---|---|
| the start turn, model at work | `working` | 1 |
| that turn finished | `done` | 0, 2, 4, 6, then 43 |
| asked to run `touch ~/e29-probe-approval.txt` with escalated permissions; at Codex's approval for it | `waiting` | 2, 5, 8, 11, 14, 17 |
| after `esc` there: the screen showed `✗ You canceled the request to run touch ~/e29-probe-approval.txt` and `■ Conversation interrupted`, input box idle | `waiting` | 30, 33, 36, 39, 42, 45, then 56 |
| asked the same for `touch /dev/shm/e29-probe-approval.txt`; model at work, then at the approval | `working`, then `waiting` | 3, 6; then 3, 6, 15 |
| `y` there, command run, turn finished | `working`, then `done` | 2; then 2, 4, 6 |

The hook calls from that pane, from workmux's log:

```
08:20:39.832  register-agent
08:20:39.877  set-window-status working
08:20:42.070  set-window-status done
08:21:25.434  set-window-status working      <- prompt submitted
08:21:29.779  set-window-status waiting      <- approval shown
                                             <- esc at 08:21:59: no hook call
08:22:27.039  set-window-status working      <- next prompt submitted
08:22:33.717  set-window-status waiting
08:22:48.102  set-window-status working      <- approved; the command had run
08:22:50.397  set-window-status done
```

**All three states appear, and a session at an approval reads `waiting`.** Two limits. A declined approval fires no hook, so the session read `waiting` until its next prompt was submitted, 28 seconds after the decline, though it was idle at its input box. And nothing marks the approval itself: `working` returns only when the approved command has finished, so a session running a long command it was approved for reads `waiting` meanwhile. Step 7 shows that case in the overview's own row.

The overview with the session at the first approval, and the screen there (`workmux capture issue-16 --lines 200`, tail):

```
NAME      STATE    HOST   RETURN  QUESTIONS
issue-16  waiting  codex          no RETURN block on screen
```

```
• Running touch ~/e29-probe-approval.txt

  Would you like to run the following command?

  Environment: local

  Reason: Do you approve running touch ~/e29-probe-approval.txt to create the file outside the sandbox?

  $ touch ~/e29-probe-approval.txt

› 1. Yes, proceed (y)
  2. Yes, and don't ask again for commands that start with `touch ~/e29-probe-approval.txt` (p)
  3. No, and tell Codex what to do differently (esc)

  Press enter to confirm or esc to cancel
```

Codex asked here because the command wrote outside its sandbox. The session ran under `approval_policy` `on-request` and the `workspace-write` sandbox, by its own record; commands inside the sandbox ran without a question throughout the probe.

### 5. The captured screen around a RETURN block

The same session was sent E26's prompt, with the task and the declined command changed:

```
Say in one line that the first touch command was declined, then end your reply with this block in a code fence, one field per line: ### RETURN, status: needs-decision, task: issue 16, changed: none, evidence: touch was declined, findings: none, risks: none, follow-ups: none, questions: <one question of at least 400 characters asking whether to retry the declined touch command or skip it, with the reasons for each>, knowledge: none
```

`workmux capture issue-16 --lines 200` returned 63 lines on the 238 × 63 pane (`#{alternate_on}` 1, `#{history_size}` 0). Lines 42–63, trailing spaces stripped, nothing else changed:

```
• 👨‍💻 Tech-Lead: The first touch command was declined.

  ### RETURN
  status: needs-decision
  task: issue 16
  changed: none
  evidence: touch was declined
  findings: none
  risks: none
  follow-ups: none
  questions: Would you like me to retry the declined command, touch ~/e29-probe-approval.txt, with a fresh request for escalated permissions so that we can verify creation at the originally requested home-directory path, or skip it
  because the replacement command targeting /dev/shm/e29-probe-approval.txt already exited successfully, while recognizing that skipping avoids another approval prompt and an additional file but leaves the original home-directory
  operation unverified?
  knowledge: none

  Worked for 11s • 9:23 AM


› Ask Codex to do anything

  GPT-6.1-Sol high · <tmp>/repo__worktrees/issue-16 · Reply ready
  ← for agents · ? for shortcuts
```

```console
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py overview; echo "rc=$?"
NAME      STATE  HOST   RETURN          QUESTIONS
issue-16  done   codex  needs-decision  Would you like me to retry the declined command, touch ~/e29-probe-approval.txt, with a fresh reque…
rc=0
```

`overview --json` gave the whole question, its three screen lines joined with single spaces. The script's `last_return`, run on the saved capture, returns the same, and `None` for the capture taken at the approval.

How Codex's screen differs from Antigravity's (E26 step 6), for a reader of the capture:

- **No fence and no frame, as there.** Every line of the block is indented two spaces, not four. A wrapped value continues with the same two-space indent.
- **The block is not the last thing on screen.** Codex adds a line of its own after every reply, `Worked for 11s • 9:23 AM`, then the input box and a status line. The script reads them into the `knowledge` value, which it does not use.
- **The capture is the visible screen only, as there.** Codex drew on the alternate screen and `--lines 200` returned the pane's 63 rows. `codex --help` lists `--no-alt-screen`; it was not tried.

### 6. End to end

With the skill committed as a project skill (step 1) and `<tmp>/repo` trusted (step 3), the package's default start, no config file:

```console
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py start 12 --host codex; echo "rc=$?"     # 08:24:32
started issue-12
rc=0
$ codex --no-daemon --profile e-colleagues -- "$(cat .workmux/PROMPT-issue-12.md)"         # typed by workmux
```

No prompt of any kind showed, and no approval was asked: its three commands ran inside the sandbox. The session's own record:

| time | what |
|---|---|
| 08:24:34.8 | session starts in `<tmp>/repo__worktrees/issue-12` |
| 08:24:36.1 | developer message beginning `# Tech-Lead`; the instructions from `AGENTS.md` |
| 08:24:36.2 | user: `Use the ec-fleet skill. Your assignment: issue 12.` |
| 08:24:39.2 | assistant: `👨‍💻 Tech-Lead: I’m using the ec-fleet skill to load issue 12’s assignment and workflow, …` |
| 08:24:39.8 | first command: `cat .agents/skills/ec-fleet/SKILL.md`, exit 0 |
| 08:24:44.8 | together: `cat AGENTS.md`, and `pwd; git status --short; git remote -v; rg --files -g '*.md' …` |
| 08:24:51.9 | `cat README.md CLAUDE.md; rg --files --hidden …; git log -5 --oneline; git config --get remote.origin.url`, exit 1 from the last of them |
| 08:25:06.6 | final message; the `Stop` hook marks the pane `done` |

`workmux status --json` read `working` from 08:24:36 to 08:25:05 and `done` from 08:25:09. `workmux capture issue-12 --lines 200` returned 63 lines; lines 14–50, trailing spaces stripped:

```
› Use the ec-fleet skill. Your assignment: issue 12.


• 👨‍💻 Tech-Lead: I’m using the ec-fleet skill to load issue 12’s assignment and workflow, then I’ll inspect the repository contract and scope the work.

• Explored
  └ Read SKILL.md (ec-fleet skill), AGENTS.md
    + Show details

• Ran pwd; git status --short; git remote -v; rg --files -g '*.md' -g '!AGENTS.md' -g '!node_modules' -g '!vendor'
  └ origin
    CLAUDE.md
    README.md
    + 1 line (^t to expand)

• Exited (status 1) cat README.md CLAUDE.md; rg --files --hidden -g '!.git' -g '!node_modules' -g '!.agents/skills/**' -g '!.claude/skills/**'; git log -5 --oneline; git config --get remote.origin.url
  └ a4e5159 chore: carry the ec-fleet skill as a project skill
    05d8110 chore: bootstrap the contract
    4c135ad chore: initial commit
    + 8 lines (^t to expand)

• 👨‍💻 Tech-Lead: Please provide issue 12’s text, or its URL and the tool I should use to read it. AGENTS.md has empty tracker/tool bindings, and origin has no URL.

  The ec-fleet skill (.agents/skills/ec-fleet/SKILL.md) requires: “The issue is your brief. Read it yourself, with the tools the contract names.” I need that brief before implementing.

  ### RETURN
  status: blocked
  task: issue 12
  changed: none
  evidence: cat AGENTS.md exit 0; git config --get remote.origin.url exit 1
  findings: []
  risks: Issue scope unavailable
  follow-ups: none
  questions: Provide issue 12's text, or URL and reading tool
  knowledge: none

  Worked for 31s • 9:25 AM
```

It loaded the skill as its first act, read the contract, found no tracker, and asked and waited instead of guessing, with the skill's RETURN block at the end of its message, keys complete and in order. `findings: []` is its own wording for none. The overview, with step 5's session still open:

```console
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py overview; echo "rc=$?"
NAME      STATE  HOST   RETURN          QUESTIONS
issue-12  done   codex  blocked         Provide issue 12's text, or URL and reading tool
issue-16  done   codex  needs-decision  Would you like me to retry the declined command, touch ~/e29-probe-approval.txt, with a fresh reque…
rc=0
```

### 7. A Codex session runs `fleet.py start`

The dispatching tech-lead was started by hand in the probe's shell pane, in `<tmp>/repo`:

```console
$ EC_FLEET_CONFIG=<tmp>/fleet-short.toml codex --profile e-colleagues 'use the ec-fleet skill; start 17'
```

The variable points at the config that only shortens the start prompt, so that the session it starts costs one short turn; it changes nothing else. The session ran under `approval_policy` `on-request` and the `workspace-write` sandbox with no network, by its own record: the whole file system readable; `<tmp>/repo`, `/tmp` and `$TMPDIR` writable; `.git`, `.agents`, `.codex` and `.aws` under `<tmp>/repo` read-only. Its commands, from that record:

| time | command | result |
|---|---|---|
| 08:26:02.8 | `cat .agents/skills/ec-fleet/SKILL.md` | exit 0 |
| 08:26:06.7 | `python3 .agents/skills/ec-fleet/scripts/fleet.py start 17` | exit 2, `fleet: no host chosen: pass --host (antigravity, claude, codex, opencode) or set default_host in the config` |
| 08:26:09.9 | `python3 .agents/skills/ec-fleet/scripts/fleet.py start 17 --host codex`, in the sandbox | exit 101, below |
| 08:26:13.4 | the same command, asking to run outside the sandbox | approval shown; approved at 08:26:36; exit 0, `started issue-17` |

The sandboxed run failed inside workmux, before it did anything:

```
thread 'main' (3) panicked at ~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/tracing-appender-0.2.5/src/rolling.rs:156:14:
initializing rolling file appender failed: InitError { context: "failed to create log file", source: Os { code: 30, kind: ReadOnlyFilesystem, message: "Read-only file system" } }
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

**workmux cannot start inside Codex's sandbox, because it cannot open its log under `~/.local/state/workmux/`.** The tech-lead then asked, and Codex showed:

```
• Running python3 .agents/skills/ec-fleet/scripts/fleet.py start 17 --host codex

  Would you like to run the following command?

  Environment: local

  Reason: May I run the fleet launcher outside the sandbox so workmux can write its log and start issue 17?

  $ python3 .agents/skills/ec-fleet/scripts/fleet.py start 17 --host codex

› 1. Yes, proceed (y)
  2. Yes, and don't ask again for commands that start with `python3 .agents/skills/ec-fleet/scripts/fleet.py start 17 --host codex` (p)
  3. No, and tell Codex what to do differently (esc)
```

Option 1 was chosen, acting as the person. workmux's log shows the start within the same second, from the dispatching pane, and the new session ran its turn:

```
08:26:36.177  workmux add issue-17 --background --agent "codex --profile e-colleagues" --prompt "Reply with the single word ready, then stop."   cwd=<tmp>/repo  tmux_pane=%38
```

```
  👨‍💻 Tech-Lead: Started issue 17 with Codex in worktree issue-17. Fleet launcher exited 0: started issue-17.
```

It passed no `--host` at first, as the skill says, and added its own after `no host chosen`. It retried the failed command with the same flags, only outside the sandbox. `$TMUX_PANE` reached the command, so the window opened in the probe's session.

Sent `overview`, it asked at once to run `python3 .agents/skills/ec-fleet/scripts/fleet.py overview` outside the sandbox (`Reason: May I run the fleet overview outside the sandbox so workmux can initialize its log and read session status?`), was approved once, and showed:

```
  NAME      STATE    HOST   RETURN          QUESTIONS
  repo      waiting  codex                  (this session)
  issue-12  done     codex  blocked         Provide issue 12's text, or URL and reading tool
  issue-16  done     codex  needs-decision  Would you like me to retry the declined command, touch ~/e29-probe-approval.txt, with a fresh reque…
  issue-17  done     codex                  no RETURN block on screen

  Issue 17 may be at a host prompt or have stopped without a complete RETURN block visible. done indicates the session stopped, not that the issue is complete.
```

Its own row is found and marked `(this session)`. It reads `waiting`, not `working`, because the overview ran as an approved command (step 4).

The probe's repository is under `/tmp`, which this sandbox leaves writable. The failure above does not depend on that, since workmux's log is under the home directory. What else a sandboxed start would be refused in a repository elsewhere was not reached, and does not matter once the command runs outside the sandbox.

### 8. The `trust` string in a trusted repository, and in a path holding a space

Two cases the string had not met, measured before it could become a default. Both ran through `fleet.py` with this config, and each control with the same file but `trust = ""`:

```toml
[hosts.codex]
prompt = "Reply with the single word ready, then stop."
trust = "-c 'projects={\"{worktree}\"={trust_level=\"trusted\"}}'"
```

To see whether a session loads the project's own Codex config, which Codex reads only in a trusted project, each repository first got a committed `.codex/config.toml` holding one line, `model_reasoning_effort = "low"`. The profile file sets `high`, and Codex's status line shows the effort in use, so `low` there means the project's file was loaded.

#### An already-trusted repository

`<tmp>/repo`, whose root Codex had saved as trusted in step 3. `start 41` is the control, `start 42` carries the string. Both printed `started issue-4N`, rc 0, nothing on stderr. What workmux typed, and the process arguments:

```console
$ codex --no-daemon --profile e-colleagues -- "$(cat .workmux/PROMPT-issue-41.md)"
codex|--no-daemon|--profile|e-colleagues|--|Reply with the single word ready, then stop.|
$ codex --no-daemon --profile e-colleagues -c 'projects={"<tmp>/repo__worktrees/issue-42"={trust_level="trusted"}}' -- "$(cat .workmux/PROMPT-issue-42.md)"
codex|--no-daemon|--profile|e-colleagues|-c|projects={"<tmp>/repo__worktrees/issue-42"={trust_level="trusted"}}|--|Reply with the single word ready, then stop.|
```

Neither showed a prompt. Both answered `ready` and read `done` (`[('issue-41', 'done', 3), ('issue-42', 'done', 5)]`), and both status lines read `GPT-6.1-Sol low`. Each was then asked `Run the shell command git branch --show-current and show its output in one line.`; neither asked for approval, and the screens differ only in the name:

```
• Ran git branch --show-current
  └ issue-42

• 👨‍💻 Tech-Lead: issue-42
```

The two sessions' own records agree on everything trust could change:

| | `issue-41`, no string | `issue-42`, with the string |
|---|---|---|
| `approval_policy` | `on-request` | `on-request` |
| sandbox | `workspace-write` | `workspace-write` |
| effort | `low` | `low` |
| writable | the worktree, `/tmp`, `$TMPDIR` | the worktree, `/tmp`, `$TMPDIR` |
| read-only inside the worktree | `.git`, `.agents`, `.codex`, `.aws` | `.git`, `.agents`, `.codex`, `.aws` |
| developer messages, characters | 21,524, 20,429, 2,400, 271 | 21,524, 20,429, 2,400, 271 |
| hook calls | `register-agent`, `working`, `done`; then `working`, `working`, `done` | the same |

**The override is merged into the saved `projects` table; it does not replace it.** Five hand runs in the trusted worktree `<tmp>/repo__worktrees/issue-41`, the arguments of each added to `codex --no-daemon --profile e-colleagues -c check_for_update_on_startup=false`, with no prompt and so no model call:

| added arguments | trust prompt | status line |
|---|---|---|
| none (control) | not shown | `GPT-6.1-Sol low` |
| `-c 'projects={"/nonexistent-e29"={trust_level="trusted"}}'` | not shown | `GPT-6.1-Sol low` |
| `-c 'projects={"<worktree>"={trust_level="untrusted"}}'` | **shown** | |
| `-c 'projects={"<root>"={trust_level="untrusted"}}'` | **shown** | |
| `-c 'projects={"<root>"={trust_level="untrusted"},"<worktree>"={trust_level="trusted"}}'` | not shown | `GPT-6.1-Sol low` |

An override that names only some other path leaves the root's saved trust in force, so the session's `projects` table still held the saved entry. The two `untrusted` rows show the override is read at all in this repository, and the last row that an entry for the worktree itself outranks one for the root. That last row sets both in one override; a root *saved* as `untrusted` was not measured.

#### A worktree path holding a space

`<tmp>/my repo`, a new repository Codex had never seen. `workmux add issue-31 --dry-run` printed `Worktree: <tmp>/my repo__worktrees/issue-31`. `fleet.py --config <the file> start 31 --host codex` printed `started issue-31`, rc 0, nothing on stderr. workmux's log, what it typed, and the process arguments:

```
args=["workmux", "add", "issue-31", "--dry-run"]
args=["workmux", "add", "issue-31", "--background", "--agent", "codex --profile e-colleagues -c 'projects={\"<tmp>/my repo__worktrees/issue-31\"={trust_level=\"trusted\"}}'", "--prompt", "Reply with the single word ready, then stop."]
```

```console
$ codex --no-daemon --profile e-colleagues -c 'projects={"<tmp>/my repo__worktrees/issue-31"={trust_level="trusted"}}' -- "$(cat .workmux/PROMPT-issue-31.md)"
codex|--no-daemon|--profile|e-colleagues|-c|projects={"<tmp>/my repo__worktrees/issue-31"={trust_level="trusted"}}|--|Reply with the single word ready, then stop.|
```

The override reached Codex as one argument, space included. The new window, with the update banner removed:

```
  >_ OpenAI Codex (v0.167.0)
     <tmp>/my repo__worktrees/issue-31

› Reply with the single word ready, then stop.

• 👨‍💻 Tech-Lead: ready

  Worked for 5s • 9:38 AM

› Ask Codex to do anything

  GPT-6.1-Sol low · <tmp>/my repo__worktrees/issue-31 · Confirm readiness
```

No prompt, `('issue-31', 'done', 4, 'codex', '%73')`, and asked for `git branch --show-current` it ran it with no approval and answered `👨‍💻 Tech-Lead: issue-31`. The status line reads `low`: **a worktree trusted only by the override loads the project's `.codex/config.toml`**, as one trusted through the prompt does. The control, `start 32` with `trust = ""`, typed `codex --no-daemon --profile e-colleagues -- "$(cat .workmux/PROMPT-issue-32.md)"` and showed the trust prompt for `<tmp>/my repo__worktrees/issue-32`, naming the root `<tmp>/my repo`; no agent was registered, and it was not answered.

`~/.codex/config.toml`, the profile file, `~/.codex/version.json` and `~/.codex/hooks.json` had the same hashes before this step and after it, and the profile file still holds one `projects` entry, the one from step 3.

### Verdicts

1. **Start: holds** at codex-cli 0.167.0 with workmux 0.1.281. `fleet.py start <ref> --host codex` with the package's default command and no config file opens the window, and workmux types `codex --no-daemon --profile e-colleagues -- "$(cat .workmux/PROMPT-<name>.md)"`. In a trusted repository the prompt is submitted on its own, the session is the tech-lead, and `workmux status --json` reports it with `"agent_kind": "codex"`. The profile file was present on the probe machine; a machine without it was not measured.
2. **First-run prompts: one, the trust prompt, and only in a repository Codex has never trusted.** Trust is saved per repository root and covers every worktree, so `fleet.py`'s default start raised no prompt once the root was trusted. In an untrusted repository the session waits at the prompt with its start prompt unsent, and it is **absent** from `workmux status --json` and from the overview. The skill says such a session shows as `working`, or as stopped with `no RETURN block on screen`; on Codex it does not show at all. A `trust` string removes the prompt for one session and saves nothing: `-c 'projects={"{worktree}"={trust_level="trusted"}}'`, measured through `fleet.py` with a control, also for a path holding a dot and one holding a space. In a repository already trusted the string changes nothing that was looked at: the override is merged into the saved `projects` table, and the session matched its control in prompts, approvals, sandbox, the project config it loaded and its hook calls (step 8). Accepted by hand under `--profile`, the decision is saved in the profile file, not in `~/.codex/config.toml`. `fleet.py` was not changed.
3. **States: `working`, `waiting` and `done` are all reported.** A session at one of Codex's approvals reads `waiting`. It still reads `waiting` after the approval is declined, until its next prompt, and while a command it was approved for is running.
4. **The captured screen: holds.** The overview read `needs-decision` and a question wrapped over three screen lines, and `blocked` and its question from the end-to-end stop. No parser fault was found. Codex adds a `Worked for …` line after the block; the script tolerates it.
5. **End to end: holds, with the skill delivered as a project skill.** A tech-lead started with the default prompt read `.agents/skills/ec-fleet/SKILL.md` as its first command, read `AGENTS.md`, and stopped with a complete RETURN block that the overview showed. The plugin route was not measured.
6. **Dispatch from inside a Codex session: holds, with one approval per call that reaches workmux.** In the sandbox workmux aborts on its log file, so `fleet.py start` and `fleet.py overview` each run only outside it, and Codex asks first. Nothing else blocked. `fleet.py start` with no host needed no approval, as it fails before reaching workmux.

### Not measured

- The plugin route for the skill on Codex: the install was refused by the probe session's permission system. So also how a Codex session reaches `scripts/fleet.py` under `~/.codex/plugins/cache/`, and the approvals that needs.
- The default start on the machine as found, with no `ec-fleet` skill available to Codex.
- A machine with no `~/.codex/e-colleagues.config.toml`; design §9 records that an unknown profile name is silently ignored (E14).
- The `trust` string in a repository whose root is *saved* as `untrusted`. In one override, an entry for the worktree outranked an `untrusted` one for the root (step 8).
- Project role files (`.codex/agents/*.toml`) in a worktree trusted by the override. The project `.codex/config.toml` loads there (step 8); role files were not tried.
- Whether trust saved in the profile file applies to a session without `--profile`, and whether trust saved in `~/.codex/config.toml` applies under it.
- A machine where Codex has not yet recorded the hooks' hashes: whether a hook review is then a further first-run prompt.
- Option 2 at an approval, "don't ask again": where it is saved, and whether it would cover the next `fleet.py start`, whose command line differs by the reference.
- The states while a specialist runs (`SubagentStart` and `SubagentStop` are hooked; no specialist was spawned).
- A block taller than the pane, the nested `findings:` list, any stop after the first, a commit or a push from the worktree, `--base`, the plan assignment, a contract with `### Parallel work` lines, several real issues at once.
- `--no-alt-screen`, the shared background server (workmux passes `--no-daemon`), and remote use.
- Why the update notice blocks only a session started with no prompt: see the inference in step 3.
- Any Codex other than 0.167.0. 0.169.0 was offered during the probe and not installed.

**Host state.** Nothing of this package was installed, removed or updated for Codex: `codex plugin list` still shows it as not installed, `~/.codex/plugins/cache/` has no directory for it, and the five role files have the hashes they had. The probe wrote no Codex file. `~/.codex/config.toml`, `~/.codex/hooks.json`, `~/.codex/.codex-global-state.json` and the file behind `~/.codex/AGENTS.md` have the same hashes as before. Codex itself changed two files, both before step 8, and both changes were left; step 8 changed neither, by hash. It wrote `[projects."<tmp>/repo"]` with `trust_level = "trusted"` into `~/.codex/e-colleagues.config.toml` when its prompt was accepted, that file's only change (7,071 bytes before, 7,242 after; without its last three lines the file has its earlier hash); the entry points at a throwaway repository, and this probe does not edit the owner's Codex files. And its update check rewrote `~/.codex/version.json` at 08:15:07; only the earlier hash was kept, not the earlier content. Codex also kept its usual per-session records under `~/.codex/` (ten session files, prompt history, its state databases and logs), and workmux appended to its log.

Nine worktrees were made and removed in `<tmp>/repo`, two in `<tmp>/repo.two` and two in `<tmp>/my repo`, each with `✓ Removed worktree '<name>' and branch '<name>'`. Afterwards `workmux status --json` listed `"agents": []` in all three, `git worktree list` listed only the main checkout in all three, the probe's tmux session was killed, and `pgrep -x codex` found no process. workmux kept a state file for seven of the probe's panes under `~/.local/state/workmux/agents/`; all seven were removed, and no file there names a path of this probe. The approved command created `/dev/shm/e29-probe-approval.txt`, which was removed; the declined one created nothing.

Two slips, both in the probe's own panes. `workmux list`, run once from the shell pane, stopped at workmux's offer to update another agent CLI's status hooks (E26); it was ended with ctrl-c, unanswered. No `~/.local/state/workmux/setup.json` or `sent/` exists, and that agent's hooks file was last modified a month before the probe. And one command line meant for the shell was typed into Codex's own session list, which is where ctrl-c at the update prompt leads, not to the shell. Checked right after, no session file had been created since the previous probe session, and Codex's session index and state database had not been written since then either.

---

## E30 — the fleet skill on opencode 2.2.7: the default start command no longer exists and the installed workmux plugin no longer loads; with `default_agent` set and workmux's current plugin, a tech-lead loads `ec-fleet`, workmux reports `working`, `waiting` and `done`, and the overview reads its RETURN block unless the block sits beside opencode's sidebar

**Date** 2026-11-15. **opencode 2.2.7**; **workmux 0.1.281**; **tmux 3.8**; this package as of commit `754fce5`. The model was a local one served by llama.cpp behind an OpenAI-compatible endpoint, the probe machine's last-used model in the opencode TUI, except for one turn (step 4). Tranche B.

E26 to E28 measured `ec-fleet` on Antigravity only, and design §17 lists opencode as UNVERIFIED. The repository's opencode claims were last confirmed at 2.0.18. This entry answers the same questions for opencode at 2.2.7:

1. **Start.** Does `fleet.py start` with the package's default command open the window, start the tech-lead and deliver the prompt, and does workmux report the session?
2. **First-run prompts.** Does a new worktree stop at one, and can it be pre-answered for one session?
3. **States.** Which of `working`, `done` and `waiting` does workmux report, and what does a session at an approval read?
4. **The captured screen.** Does the overview read a RETURN block from opencode's screen?
5. **End to end.** Does a started tech-lead load `ec-fleet` from its start prompt, read `AGENTS.md` and stop with a RETURN block that the overview shows?
6. **Dispatch from inside a session.** Can an opencode tech-lead itself run `fleet.py start`, and what does it need?

Everything ran in a throwaway repository, `<tmp>/repo` (`git init`, one commit, a repository-local identity, no signing, then `python3 skills/ec-init/scripts/bootstrap.py <tmp>/repo --write`, `wrote 3 files, 3 changed`, committed), from a tmux session created for the probe, `e30-probe`. `fleet.py` was run from a shell pane of that session, from a clean export of the package at `754fce5`. No `~/.config/e-colleagues/fleet.toml` existed, and `XDG_CONFIG_HOME` and `EC_FLEET_CONFIG` were unset; a run "with a config file" below passed `--config <tmp>/cfg/<name>.toml` and says what the file held. Where a question did not need the real prompt, the config set `prompt = "Reply with the single word ready, then stop."`.

The fixture changed during the probe, and each change was a commit in `<tmp>/repo`, so every new worktree carried it:

- first, after the one turn that reached a hosted model (step 4, the probe's second start), an `opencode.json` that restricts opencode to the machine's local provider (`enabled_providers`, `model`, `small_model`), so that no further prompt left the machine;
- then workmux's current opencode plugin under `.opencode/plugins/workmux-status/` (step 3);
- then `"default_agent": "tech-lead"` in that `opencode.json` (step 4), taken out again for the two `OPENCODE_CONFIG_CONTENT` starts in step 4 and for all of steps 10 and 11.

Twelve sessions reached a model, each for one to five prompts. In the captures below the local model's label is replaced by `<local model>`, its provider's by `<local provider>`, the name of an MCP server in the sidebar by `<mcp server>`, and trailing spaces are stripped. Times are UTC, from workmux's log and from opencode's own session export (`opencode session export <id>`).

### 1. Versions, the install, and what was there

```console
$ opencode --version
opencode v2.2.7
$ workmux --version
workmux 0.1.281
$ tmux -V
tmux 3.8
$ opencode service status
stopped
```

The package was already installed for opencode, from an earlier version. `~/.config/opencode/agents/` held its six agents, `~/.config/opencode/skills/` held `ec-init`, `ec-onboard`, `ec-status` and `ec-tech-lead` and no `ec-fleet`, beside six skills that are not this package's, and `~/.config/opencode/plugins/` held one file, `workmux-status.ts`. The six installed agents were byte-identical to the export's (`cmp` rc 0 for each).

The documented update, `bootstrap.py --scope user --write` (design §7, §9), is one command for two hosts: it also rewrites `~/.codex/agents/*.toml` and `~/.codex/e-colleagues.config.toml`. Its `--check` said so:

```console
$ python3 skills/ec-init/scripts/bootstrap.py --scope user --check; echo "rc=$?"
  e-colleagues.config.toml is out of date
  opencode/skills/ec-fleet is missing or out of date
  opencode/skills/ec-init is missing or out of date
3 file(s) need --write
rc=1
```

The first line is not a stale package file. `diff` of the export's profile against the installed one showed the installed file as the export's 111 lines plus 33 more that Codex had appended itself: a model choice, `[tui]` counters and seven `[hooks.state…] trusted_hash` entries. `--write` replaces that file whole, so it would have dropped them. This probe's host is opencode, so it did not run that. It ran the same script with `--dist` pointing at a staging directory `<tmp>/stage/dist/codex/agents` that holds no Codex files, beside links to the export's `dist/opencode/agents` and `skills`, which makes the script skip its Codex half:

```console
$ python3 skills/ec-init/scripts/bootstrap.py --scope user --write --dist <tmp>/stage/dist/codex/agents; echo "rc=$?"
installed 0 personas into ~/.codex/agents as real files:
delivered as developer_instructions instead, not a role file: tech-lead, developer, reviewer, security, designer, platform [CX-06]
installed 6 agents into ~/.config/opencode/agents: tech-lead, developer, reviewer, security, designer, platform
installed 5 skills into ~/.config/opencode/skills: ec-fleet, ec-init, ec-onboard, ec-status, ec-tech-lead
start with `opencode run --agent tech-lead`; in the TUI cycle to it with Shift+Tab, or set `default_agent` in your global opencode config, which this script never writes [OC-03]
rc=0
```

By `sha256sum` before and after, three files changed under `~/.config/opencode/`: `skills/ec-fleet/SKILL.md` and `skills/ec-fleet/scripts/fleet.py` are new, and `skills/ec-init/SKILL.md` differs. The six agents and the other three skills were rewritten with the same bytes. The six foreign skills, the plugin file, and the global config have the same hashes as before. `diff -r` of the export's `skills/` against the installed directory reported only the six foreign skills. The script's first two output lines are wrong for this run; they describe the empty staging directory.

`opencode debug agents`, run in `<tmp>/repo`, listed `tech-lead` with `"mode": "primary"`, a first permission rule of `*` / `*` / `allow`, and `read` of `*.env` set to `ask`. So this tech-lead runs shell commands with no approval, and reading a `.env` file is one thing that raises opencode's permission prompt. That command also started opencode's background service (`opencode serve --service`), which every later session shared. It was stopped at the end.

### 2. Start: the default command fails, and `fleet.py` reports success

```console
$ python3 skills/ec-fleet/scripts/fleet.py start 12 --host opencode; echo "rc=$?"
started issue-12
rc=0
```

workmux's log for that call, and what it typed into the new pane:

```
08:14:33  workmux add issue-12 --background --agent "opencode --agent tech-lead" --prompt "Use the ec-fleet skill. Your assignment: issue 12."   cwd=<tmp>/repo
08:14:33  create:creating worktree branch="issue-12" path=<tmp>/repo__worktrees/issue-12 base=Some("main")
08:14:34  create:completed
```

```console
$ opencode --agent tech-lead --prompt "$(cat .workmux/PROMPT-issue-12.md)"
DESCRIPTION
  OpenCode command line interface

USAGE
  opencode <subcommand> [flags] [<directory>]
…
FLAGS
  --standalone            Run with a private server instead of the background service
  --server string         Connect to a server URL instead of the background service
  --auto                  Auto-approve permissions that are not explicitly denied
  --continue, -c          Continue the last session
  --session, -s string    Session ID to continue, or to create if it does not exist
  --prompt string         Prompt to use
…
ERROR
  Unrecognized flag: --agent in command opencode

$ echo "last rc=$?"
last rc=1
```

**At 2.2.7 the top-level `opencode` command has no `--agent` flag.** `opencode run --help` and `opencode mini --help` both still list `--agent string    Agent to use`; the TUI does not. The window opened, in the probe's session, the worktree and the prompt file were made, and workmux recognised the command as opencode and appended `--prompt "$(cat …)"`. Then opencode printed its usage and exited, and the pane fell back to a shell.

Nothing reports the failure. `fleet.py` printed `started issue-12` with rc 0, because workmux had done its part. No session registered:

```console
$ workmux status --json          # in <tmp>/repo
…
  "agents": [],
…
$ python3 skills/ec-fleet/scripts/fleet.py overview; echo "rc=$?"
no sessions
rc=0
```

### 3. The status plugin installed on this machine does not load at 2.2.7

`~/.config/opencode/plugins/workmux-status.ts` is workmux's opencode plugin in an earlier form: one file that exports a named `Plugin` function and calls `workmux register-agent` and `workmux set-window-status` from opencode's server. opencode 2.2.7 refuses it, at every start of a session, in `~/.local/share/opencode/log/opencode.log`:

```
level=WARN message="failed to load plugin" target=~/.config/opencode/plugins/workmux-status.ts cause="Cause([Fail(PluginModule.LoadError: Plugin must export a default definition with an id and an effect or setup function. (cause: SchemaError(Missing key\n  at [\"default\"])))])" role=server
```

The effect, measured with a config file holding `start = "opencode"` and the short prompt: the TUI opened, answered `ready`, and `workmux status --json` listed `"agents": []` at every poll, from 6 seconds after the start to after the turn's end 90 seconds later. workmux's log shows no `register-agent` and no `set-window-status` from that pane. **On this machine as found, workmux reports nothing for an opencode session, so the overview has no row for it.**

workmux 0.1.281 carries a newer plugin. To read it without changing the owner's files, `workmux setup --hooks` was run with `HOME` set to an empty scratch directory holding only `.config/opencode/` (it needs a terminal, so it ran in a pane of the probe's session):

```
  • OpenCode (found OpenCode config directory): not configured
  Install or update status tracking hooks? [Y/n] Y
  ✓ Installed OpenCode plugin to <scratch home>/.config/opencode/plugins/wo…
```

It wrote `plugins/workmux-status/index.ts`, `status.ts` and `tui.ts`, and a manifest `.workmux-status.json`. `index.ts` is a server plugin that does nothing, with the comment `Pane-local status tracking belongs to the TUI, not OpenCode's shared server.` `tui.ts` is a TUI plugin: it runs `workmux register-agent` when the TUI starts and `workmux set-window-status working|waiting|done` from the TUI process, `waiting` on `permission.asked` and `form.created`. Run again in a second scratch home holding a copy of this machine's one-file plugin, the same command said `OpenCode (found OpenCode config directory): update available` and offered to replace it. It was answered `n`. `workmux setup` was not run against the real home, and `~/.config/opencode/plugins/workmux-status.ts` has the same hash as before.

For the rest of this entry, those three files were committed to the fixture as `.opencode/plugins/workmux-status/`. opencode loaded them from there with no prompt (`msg="loading plugin" id=<tmp>/repo__worktrees/issue-15/.opencode/plugins/workmux-status`), and the same start as above then registered:

```
08:21:35  workmux add issue-15 --background --agent "opencode" --prompt "Reply with the single word ready, then stop."
08:21:38  "workmux", "register-agent"                  pane %53
08:21:38  "workmux", "set-window-status", "working"
08:22:41  "workmux", "set-window-status", "done"
```

```json
{
  "worktree": "issue-15",
  "branch": "issue-15",
  "project": "repo",
  "status": "done",
  "elapsed_secs": 4,
  "title": "OpenCode",
  "pane_id": "%53",
  "workdir": "<tmp>/repo__worktrees/issue-15",
  "agent_kind": "opencode",
  "session": "e30-probe",
  …
}
```

So every status reading below is workmux's current plugin, loaded from the project. That the same plugin behaves the same when `workmux setup` installs it under `~/.config/opencode/` is an inference.

### 4. What does start a tech-lead

**`opencode mini --agent tech-lead` starts the tech-lead and is invisible to workmux.** With `start = "opencode mini --agent tech-lead"` and the short prompt, workmux typed `opencode mini --agent tech-lead --prompt "$(cat .workmux/PROMPT-issue-13.md)"`, and the pane showed:

```
▪ oc mini v2.2.7 · <tmp>/repo__worktrees/issue-13
› Reply with the single word ready, then stop.
👨‍💻 Tech-Lead: ready
Tech-Lead · Iceman Free · 2.6s
┃
tech-lead · Iceman Free · 12.1K (5%) · OpenCode · ctrl+p menu
```

The persona arrived. The model did not come from the TUI's last-used model: `mini` picked a hosted model of the `OpenCode` provider. That is the one turn that left the machine, and it is why the fixture then got its `opencode.json`. Repeated later with that file and with workmux's current plugin in the fixture, `mini` answered on the local model as `Tech-Lead`, and `workmux status --json` listed `"agents": []` at every poll through the 74-second turn: the TUI plugin does not run in `mini`.

**Plain `opencode` starts whatever agent the config names.** With `start = "opencode"` workmux typed `opencode --prompt "$(cat .workmux/PROMPT-issue-14.md)"`. Without `default_agent` the footer read `Build · <local model>`, opencode's own default agent, and it answered `ready`. With `"default_agent": "tech-lead"` in the fixture's `opencode.json` the same start gave:

```
  ┃  Reply with the single word ready, then stop.

     + Thought · 2.0s

     ready

     Tech-Lead · <local model> · 1m 8s · 0.3 tok/s
  ┃
  ┃  Tech-Lead · <local model> <local provider> · medium
```

and `workmux status --json` read `working` through the turn and `done` after it, `"agent_kind": "opencode"`. That is the combination the rest of this entry uses: `start = "opencode"`, `default_agent` in a config opencode reads, and workmux's current plugin. [OC-03]'s `default_agent` still holds at 2.2.7 for the TUI; its `opencode --agent <name>` does not.

**Carrying `default_agent` in the start command did not work.** opencode reads a config from the environment variable `OPENCODE_CONFIG_CONTENT`, and `--standalone` gives a session its own server, which would read that session's environment. Two forms were tried with `default_agent` taken out of the fixture again:

```
start = "env 'OPENCODE_CONFIG_CONTENT={\"default_agent\":\"tech-lead\"}' opencode --standalone"
  typed:  env OPENCODE_CONFIG_CONTENT={"default_agent":"tech-lead"} opencode --standalone --prompt "$(cat .workmux/PROMPT-issue-18.md)"
  log:    level=WARN message="configuration normalization diagnostic" source=OPENCODE_CONFIG_CONTENT … action="rejected malformed JSON or JSONC document"
  footer: Build · <local model>

start = "env 'OPENCODE_CONFIG_CONTENT={\"default_agent\": \"tech-lead\"}' opencode --standalone"
  typed:  env OPENCODE_CONFIG_CONTENT={"default_agent": "tech-lead"} opencode --standalone -- "$(cat .workmux/PROMPT-issue-19.md)"
  pane:   env: ‘tech-lead}’: No such file or directory
```

workmux dropped the single quotes around the assignment both times, so the shell ate the double quotes. In the first form it still recognised opencode behind `env`, injected `--prompt`, and the standalone session registered with workmux (`working`, then `done`) as `Build`. Inline JSON cannot be carried this way. A path to a file can: step 10.

### 5. First-run prompts: none

No new worktree stopped at a prompt. Nine worktrees were opened in the TUI, steps 10 and 11 included, and two in `mini`, each a path opencode had never seen, and each went straight to its start prompt. opencode also read the fixture's `opencode.json` (the `default_agent` above) and loaded and ran the fixture's `.opencode/plugins/` code without asking. So there is nothing to pre-answer, no `trust` string for this host was looked for, and no control was run. The other side of that: at 2.2.7 a repository's own config chooses the agent and its plugin code runs in the TUI, before anyone is asked anything. Only the fixture's files were used to see this.

### 6. States

One session, `issue-17`, the tech-lead in the TUI. Prompts were typed into its pane. `workmux status --json` was polled every 4 or 5 seconds; the hook times are from workmux's log.

| moment | `status` | hook call |
|---|---|---|
| the start turn, model at work | `working` | 08:24:30 `working` |
| that turn ended | `done` | 08:25:39 `done` |
| asked to read `.env`; model at work | `working` | 08:25:57 `working` |
| at opencode's permission prompt for `Read .env` | **`waiting`** (elapsed 1, 6, 29) | 08:26:05 `waiting` |
| `Reject` chosen there: the reply footer says `interrupted` | `done` | 08:26:57 `done` |
| asked again; at the same prompt | `waiting` (elapsed 1, 13) | 08:30:51 `waiting` |
| `Allow once` chosen | `working`, then `done` 2 s later | 08:31:04 `working`, 08:31:06 `done` |
| a tech-lead at a form of opencode's question tool (steps 8 and 9) | `waiting` | 08:43:52, 08:50:01 `waiting` |
| that form dismissed with esc: footer `interrupted` | `done` | 08:44:30 `done` |

**All three states appear.** `workmux capture issue-17 --lines 200` at the permission prompt, tail:

```
  ┃  Read the file .env in this directory with your read tool and tell me how many lines it has.
  ┃
     + Thought · 7.1s
     ⠼ Read .env
  ┃
  ┃  △ Permission required
  ┃    → Read .env
  ┃
  ┃  Path: .env
  ┃
  ┃
  ┃   Allow once   Always allow   Reject                              ctrl+f fullscreen  ⇆ select  enter confirm
```

and the overview there:

```
NAME      STATE    HOST      RETURN  QUESTIONS
issue-17  waiting  opencode          no RETURN block on screen
```

Unlike Antigravity (E26), a rejected permission and a dismissed question both end the turn, so the session reads `done`, not `working`. The tech-lead's permissions allow everything but reading `.env` files, so its shell commands never raised a prompt: in this entry `waiting` came only from the `.env` read and from the question tool.

### 7. The captured screen around a RETURN block

The same session was asked for the block the way E26 step 6 asked: one line, then the block in a code fence, `findings: none`, and a question of at least 400 characters. The local model left `knowledge:` out the first time (its raw text ends `…assuming it is safe.` and the closing fence, by the session export). The overview said `no RETURN block on screen`, which is what the skill promises for an incomplete block. Asked to add the last line, it sent the block whole. `workmux capture issue-17 --lines 200` returned 62 lines on the 238 × 63 pane (`#{alternate_on}` 1, `#{history_size}` 0). Lines 40 to 55:

```
     Reading .env was rejected (the tool call was declined), so I have no line count to report.

     ### RETURN
     status: needs-decision
     task: issue-17
     changed: none
     evidence: the read of .env was rejected
     findings: none
     risks: none
     follow-ups: none
     questions: Do you want me to retry reading `.env` so I can report its line count, or should I skip it entirely? Retrying is the right move if `.env` is expected to be readable by me and its
     line count is genuinely needed for this task; skip it if the file is sensitive/should never be opened, if the count was only a provisional check now superseded, or if access was denied for
     permission or policy reasons that retrying would not change. Note that `.env` often holds secrets, so I want your explicit go-ahead before opening it again rather than assuming it is safe.
     knowledge: none

     Tech-Lead · <local model> · 12.7s · 18.6 tok/s
```

```
NAME      STATE  HOST      RETURN          QUESTIONS
issue-17  done   opencode  needs-decision  Do you want me to retry reading `.env` so I can report its line count, or should I skip it entirely…
```

What a reader of an opencode capture has to handle:

- **No fence and no frame**, as on Antigravity. Every line of the block is indented five spaces, and so is the sentence above it. The user's own prompt is drawn inside a `┃` bar; the reply is not.
- **Wrapping is the TUI's own**, at a word boundary, and a continuation line has the same indent as a field line.
- **The capture is the visible screen only.** The TUI draws on the alternate screen: 62 lines from a 63-row pane, 93 from a 94-row pane, 23 from a 24-row one.
- **The nested `findings:` list** (from step 8): `- severity:` is indented seven spaces and `path:`, `line:`, `body:` nine, but a wrapped `body:` falls back to five, the block's own indent. `fleet.py` read that block correctly.
- **The sidebar shares the block's rows.** In a pane this wide the TUI draws a sidebar at the right edge: the session's title, `Context`, a token count, a percentage, `MCP` and one line per MCP server, on screen rows 3 to 10. The probe machine's opencode settings carry `"sidebar": "auto"`; whether that is opencode's default was not checked. A capture is whole screen rows, so a block line on one of those rows ends in sidebar text.

That last point breaks the parser. On the 63-row pane the block sat on rows 42 to 53 and the sidebar on rows 3 to 10, so they never met. The window was then resized to 238 × 25, which puts the same block on rows 4 to 15. Rows 4 to 10 of that capture, with the blank columns between the two parts cut and marked `~`:

```
     ### RETURN                               ~
     status: needs-decision                   ~     Context
     task: issue-17                           ~     14,020 tokens
     changed: none                            ~     21% used
     evidence: the read of .env was rejected  ~
     findings: none                           ~     MCP
     risks: none                              ~     • <mcp server>              Connected
```

```console
$ python3 skills/ec-fleet/scripts/fleet.py overview
NAME      STATE  HOST      RETURN  QUESTIONS
issue-17  done   opencode          no RETURN block on screen
```

The block is on screen, whole, from `### RETURN` through `knowledge:`. `last_return` reads the status as `needs-decision`, a run of spaces, `Context`, which is not one of the four, and returns nothing. One row higher (238 × 24) the status line fell on a sidebar row that is blank, and the same block read correctly, with `task`, `changed` and `evidence` carrying sidebar text that `fleet.py` does not use. A `questions:` line on a sidebar row would be shown with the sidebar's text on its end; that was not produced. The failing capture is saved as a fixture, 24 lines, with the path in its footer, the model's label and the MCP server's name replaced by text of the same length so that no column moves; `last_return` returns `None` on the saved copy too. In a long session the sidebar also lists other things, such as modified files, and reaches further down; how far was not measured.

### 8. End to end

With the skill installed as in step 1, `default_agent` and the plugin in the fixture, and a config file holding only `start = "opencode"`, so the prompt was the package's own:

```
08:31:17  workmux add issue-12 --background --agent "opencode" --prompt "Use the ec-fleet skill. Your assignment: issue 12."
08:31:20  "workmux", "register-agent"                  pane %65
08:31:20  "workmux", "set-window-status", "working"
08:43:52  "workmux", "set-window-status", "waiting"
```

The session's tool calls, from its export, shortened:

| time | tool | input |
|---|---|---|
| 08:31:20 | `skill` | `{"id": "ec-fleet"}` |
| 08:32:29 | `shell` ×2 | `cd "<the worktree's path, mistyped>" && pwd && git status …` (both failed: no such directory) |
| 08:33:17 | `shell` | `pwd && echo "---" && ls -la` |
| 08:34:58 | `shell` ×2 | `echo "=== AGENTS.md ==="; cat AGENTS.md; … cat CLAUDE.md; … cat README.md; … cat opencode.json`, and a listing |
| 08:35:53 to 08:37:44 | `shell` ×7 | the prompt file, the lock, `git log`, `git remote -v`, `git ls-files`, the head of the installed `fleet.py` |
| 08:39:13 | `shell` | `cd ~/.config/opencode/skills/ec-fleet && … python3 scripts/fleet.py overview` |
| 08:39:13 | `shell` | `workmux status …; workmux status --json …` |
| 08:43:52 | `question` | a form with three options and a free-text field |

- **The prompt arrived**, as the first line of the conversation on screen and the export's first message.
- **The skill was its first act**, through opencode's `skill` tool, by the name in the prompt.
- **It read `AGENTS.md`**, with `cat`, three and a half minutes in. It ran every shell command with no approval.
- **It did not stop with a RETURN block.** It found no tracker and no brief, said so, and asked through opencode's question tool: `→ Asked 1 question`, then a form headed `Questions` with `↑↓ select  enter submit  esc dismiss`. A form is not the end of a turn, so the session read `waiting`, and the overview showed:

  ```
  NAME      STATE    HOST      RETURN  QUESTIONS
  issue-12  waiting  opencode          no RETURN block on screen
  ```

  The question itself was on that session's screen. The skill's rule 4 asks for the block "every time you stop"; whether a question form counts as a stop is not something the skill says, and this model read it as not one.
- **An issue tech-lead ran the overview.** The skill tells an issue tech-lead to ignore **Dispatching**. This one ran `fleet.py overview` anyway, and it ran it from the skill's directory, which is not inside the repository. `workmux status --json` is scoped to the repository it runs in (E27); run from outside any repository it was not scoped at all, and the table listed a session of another repository on the same tmux server beside the fixture's own, which was marked `(this session)`. That other session read `working`, so its screen was not captured. Had it been stopped, `fleet.py` would have captured it.

The form was dismissed with esc, which ended the turn (`interrupted`, `done`). The session was then told, in its own pane, that the question was dismissed, that the project names no tracker, and to stop the way the skill tells an issue tech-lead to stop. Its second stop, lines 69 to 86 of the 93 captured on the 382 × 94 pane, the three longest lines cut with `…`:

```
     ### RETURN
     status: blocked
     task: issue 12 (ec-fleet assignment)
     changed: none
     evidence: git log --oneline --all -20 (5 chore commits, author Fleet Probe); git diff main..issue-12 --stat (empty); git remote -v (origin, no URL); …
     findings:
       - severity: blocking
         path: -
         line: -
         body: "issue 12 has no substantive brief: the worktree is a probe fixture (README: 'A throwaway repository for a host probe'; …), the PROMPT is fleet.py's literal prompt constant, and the project names no tracker (git remote `origin` has no URL). There is nothing to implement here. The
     fleet mechanics the probe targets do work: … Carrying on into an empty brief was not possible, and the user disabled further questions, so this
     is handed back."
     risks: none outstanding
     follow-ups: none — this run only verified the opencode host + workmux-status integration, which is working. …
     questions: ready to push
     knowledge: none

     Tech-Lead · <local model> · 15m 38s · 11.6 tok/s
```

```console
$ python3 skills/ec-fleet/scripts/fleet.py overview
NAME      STATE  HOST      RETURN   QUESTIONS
issue-12  done   opencode  blocked  ready to push
```

The overview read it: `done`, `blocked`, and the `questions` value as written. `ready to push` under `blocked` is the model's, not the parser's.

### 9. A tech-lead session runs `fleet.py start`

The dispatching tech-lead was started in the probe's shell pane, in `<tmp>/repo`, with no fleet config of any kind:

```console
$ opencode --prompt 'use the ec-fleet skill; start 13'
```

It opened with no prompt of opencode's own, as `Tech-Lead`, and registered with workmux as `repo`. Its tool calls and their results, from the export:

```
08:47:24  skill   {"id": "ec-fleet"}
08:48:32  shell   cd ~/.config/opencode/skills/ec-fleet && python3 scripts/fleet.py start 13
                  fleet: no host chosen: pass --host (antigravity, claude, codex, opencode) or set default_host in the config          exit 2
08:49:28  question  "Which host should the worktree for issue 13 start on?"  (opencode (Recommended) / claude / codex / antigravity)
08:50:19  shell   cd ~/.config/opencode/skills/ec-fleet && python3 scripts/fleet.py start 13 --host opencode
                  Error: Current directory is not a git repository.                                                                 exit 1
08:50:37  shell   python3 ~/.config/opencode/skills/ec-fleet/scripts/fleet.py start 13 --host opencode   workdir=<the repository's path, mistyped>
                  Working directory does not exist: …
```

Three things stopped it before a worktree existed, none of them an approval:

1. **It changed into the skill's directory to run the script.** The skill says "Run the script beside this file" and shows `python3 scripts/fleet.py start <reference>`. This session and the one in step 8 both turned that into `cd <skill directory> && python3 scripts/fleet.py …`. From there `workmux add` is outside the repository and fails. Had the skill's directory been inside some other git repository, workmux would have made the worktree there; that was checked beforehand and it is not.
2. **It asked which host**, through the question tool, where the skill says to run the script again with its own host. The session read `waiting`. `opencode (Recommended)` was chosen, acting as the person.
3. **It mistyped the repository's path** when it tried to go back, and then looked for the repository under the parent directories. That is this model and this long path, not the host.

It was interrupted and told to run the script by its full path with no `cd`:

```
08:53:45  shell   python3 ~/.config/opencode/skills/ec-fleet/scripts/fleet.py start 13 --host opencode
                  started issue-13                                                                                                  exit 0
08:53:50  shell   python3 ~/.config/opencode/skills/ec-fleet/scripts/fleet.py overview
                  NAME      STATE    HOST      RETURN   QUESTIONS
                  repo      working  opencode           (this session)
                  issue-12  done     opencode  blocked  ready to push                                                               exit 0
```

```
08:53:50.571  workmux add issue-13 --background --agent "opencode --agent tech-lead" --prompt "Use the ec-fleet skill. Your assignment: issue 13."   cwd=<tmp>/repo tmux_pane=%40
08:53:50.608  create:start branch="issue-13" base=Some("main")
08:53:50.655  window created, pane %76
08:53:50.751  create:completed path=<tmp>/repo__worktrees/issue-13
```

- **No approval was asked**, by opencode or by workmux. opencode ran the command at once, under the tech-lead's `*: allow`. workmux asked nothing: 37 ms from the command's start to `create:start`. Earlier in the probe a bare `workmux list` typed in a terminal pane had stopped at workmux's offer to update another agent CLI's hooks (E26); it was aborted with ctrl+c, and nothing was written.
- **The shell tool runs in the session's own pane environment.** workmux logged `tmux_pane=%40`, the dispatching TUI's pane, although the shared `opencode serve --service` process carried the `TMUX_PANE` of the window that had first started it, a pane closed long before. So the new window opened in the dispatching session's tmux session, and the overview marked the right row `(this session)`.
- **The dispatched window died as in step 2.** It was started with the package's default command, printed `Unrecognized flag: --agent in command opencode`, and held a shell. The dispatching tech-lead read `started issue-13`, ran the overview twice, saw no `issue-13` row, and went looking for the reason. It was interrupted there.

### 10. The agent through a config file named in the environment

OC-10 says opencode merges a config file from the path in `$OPENCODE_CONFIG` after the global config and before the project's. A path needs no quotes, so it can pass through workmux where inline JSON could not (step 4). The file was `<tmp>/agentcfg/agent.json`, holding only `{"default_agent": "tech-lead"}`. The fixture's `opencode.json` had no `default_agent`; it kept the local provider, and the fixture kept workmux's plugin.

First with no prompt, in `<tmp>/repo`, with the background service stopped:

```console
$ env OPENCODE_CONFIG=<tmp>/agentcfg/agent.json opencode --standalone debug config      # rc 0; type, path and default_agent of each source, in the order printed
document   ~/.config/opencode/opencode.json     default_agent: -
directory  ~/.config/opencode
document   <tmp>/agentcfg/agent.json            default_agent: tech-lead
document   <tmp>/repo/opencode.json             default_agent: -
directory  <tmp>/repo/.opencode
$ env OPENCODE_CONFIG=<tmp>/agentcfg/agent.json opencode --standalone models            # rc 0: six models, all of the local provider
```

**`$OPENCODE_CONFIG` is read at 2.2.7**, in the place OC-10 gives it, and the project's provider restriction still applied. The same two commands were the check, before each start below, that the session would be on the local provider.

**With `--standalone`: holds.** A config file with `start = "env OPENCODE_CONFIG=<tmp>/agentcfg/agent.json opencode --standalone"` and the short prompt:

```
09:09:04.168  workmux add issue-20 --background --agent "env OPENCODE_CONFIG=<tmp>/agentcfg/agent.json opencode --standalone" --prompt "Reply with the single word ready, then stop."
09:09:07.025  "workmux", "register-agent"                  pane %80
09:09:07.484  "workmux", "set-window-status", "working"
09:10:08.907  "workmux", "set-window-status", "done"
```

workmux typed `env OPENCODE_CONFIG=<tmp>/agentcfg/agent.json opencode --standalone --prompt "$(cat .workmux/PROMPT-issue-20.md)"`. The probe's own read of that line was cut after `--prom`; the process list gives the rest, `opencode|--standalone|--prompt|Reply with the single word ready, then stop.|`, with a child `opencode serve --stdio --port 0`, both carrying `OPENCODE_CONFIG=<tmp>/agentcfg/agent.json` and the new pane's `TMUX_PANE`. The screen:

```
     ready

     Tech-Lead · <local model> · 1m 0s · 0.3 tok/s
  ┃
  ┃  Tech-Lead · <local model> <local provider> · medium
```

The footer read `Tech-Lead` from the first capture, 8 seconds after the start. `workmux status --json` read `working` and then `done`, `"agent_kind": "opencode"`. `opencode service status` read `stopped` before and after: the session used no shared service.

**Without `--standalone`: it depends on who started the background service.** The variable is read by the server process, and the shared service is one process that keeps the environment of whichever client started it.

| the background service | `opencode debug config`, no variable on the client | `env OPENCODE_CONFIG=… opencode debug config` | `fleet.py start` with `start = "env OPENCODE_CONFIG=<tmp>/agentcfg/agent.json opencode"` |
|---|---|---|---|
| stopped, then started by a client that carried the variable (`env OPENCODE_CONFIG=… opencode models`) | lists `<tmp>/agentcfg/agent.json`, `default_agent: tech-lead` | lists it | `issue-21`: footer `Tech-Lead`, prompt arrived, registered as `opencode`, `working` then `done` |
| stopped, then started by a client without it (`opencode debug config`) | does not list it | **does not list it** | `issue-22`: footer **`Build`**, prompt arrived, registered as `opencode`, `working` then `done` |

In both rows workmux typed the same thing, `env OPENCODE_CONFIG=<tmp>/agentcfg/agent.json opencode --prompt "$(cat .workmux/PROMPT-issue-22.md)"` (the name apart), and the TUI process carried the variable:

```
opencode|serve|--service|                                                 TMUX_PANE=%79
opencode|--prompt|Reply with the single word ready, then stop.|           TMUX_PANE=%82 OPENCODE_CONFIG=<tmp>/agentcfg/agent.json
```

So on a service that is already running, the variable on the start command does nothing, silently. And a service started with it gives the file to every later session on that machine, also ones started without the variable (first row, second column), until the service stops. opencode's log names the variable nowhere. A server that read the file logged a file watcher on the file's directory (`message="watcher started" path=<tmp>/agentcfg`); the server that ignored the client's variable logged nothing about it.

**A path with a space: fails.** The same file at `<tmp>/agent cfg/agent.json`, with the assignment in single quotes:

```
start = "env 'OPENCODE_CONFIG=<tmp>/agent cfg/agent.json' opencode --standalone"
  typed:  env OPENCODE_CONFIG=<tmp>/agent cfg/agent.json opencode --standalone -- "$(cat .workmux/PROMPT-issue-23.md)"
  pane:   env: ‘cfg/agent.json’: No such file or directory
```

workmux dropped the quotes again, as in step 4, and here it also did not recognise opencode: it appended `-- "<prompt>"`, not `--prompt`. No session started, `fleet.py` printed `started issue-23` with rc 0, and `workmux status --json` listed `"agents": []`.

### 11. The fallback: no agent configured, and the real prompt

With `start = "opencode"`, no `default_agent` in any config, no `$OPENCODE_CONFIG`, and the package's own prompt. The fixture's `AGENTS.md` carries the managed block, with its line "If no Tech-Lead persona is active in this session, invoke the `ec-tech-lead` skill first."

```
09:14:00.865  "workmux", "register-agent"                  pane %84, issue-24
09:14:01.334  "workmux", "set-window-status", "working"
09:28:14.270  "workmux", "set-window-status", "done"       <- interrupted by the probe
```

The footer read `Build`. What it did, in order, from the session export:

| time | what |
|---|---|
| 09:14:01 | text: "I'll start by loading the ec-fleet skill to understand the workflow for this assignment." Tool `skill`, `{"id": "ec-fleet"}` |
| 09:15:03 | text: "I've been assigned issue 24 as an issue tech-lead. Let me start by reading the AGENTS.md (in context) …". `shell`: `pwd`, branch, status, log. `shell`: `cd ~ && git log …; ls -d ~/repos/*` |
| 09:15:38 | `shell`: `cd ~/.config/opencode/skills/ec-fleet && python3 scripts/fleet.py overview`. `shell`: `cd` to a guessed path under the home directory, mistyped, which failed |
| 09:16:05 to 09:26:21 | seventeen more `shell` calls and three `read` calls, two of them failed: the worktree, its git metadata, the prompt file, the lock, the installed `fleet.py`, and repeated attempts to `cd` to its own path, mistyped |
| 09:28:14 | interrupted with esc, 14 minutes in, with no stop of its own |

- **It did not load `ec-tech-lead`.** One `skill` call in the whole session, `ec-fleet`. The managed block's line was in its context, by its own words, and it did not act on it.
- **It never signed.** None of its 16 text parts carries the tech-lead's signature, and all 21 assistant messages are recorded with `"agent": "build"`.
- **It took the assignment anyway**, calling itself "an issue tech-lead", with `Build`'s permissions: everything allowed, and no delegation limit. It wrote nothing: 21 `shell`, 3 `read`, 1 `skill`, no edit, and `git status` in the worktree was clean afterwards.
- **It left the worktree.** Its second command listed the directories under `~/repos`, and it ran the overview from the skill's directory, which again listed a session of another repository (step 8).
- **It did not stop by itself** in 14 minutes. Told, in its pane, that the project names no tracker and to stop the way the skill tells an issue tech-lead to stop, it ended 4 min 42 s later with a complete block. Lines 74 to 86 of the 93 captured, the evidence line cut with `…`:

```
     ### RETURN
     status: blocked
     task: issue 24
     changed: none
     evidence: fleet.py overview (…); git worktree list (…); git log --all --oneline (6 chore commits, no issue content); cat .e-colleagues/lock.json (roster/lenses, no tracker); …
     git remote -v (origin empty); AGENTS.md bindings read (no tracker/platforms named)
     findings: []
     risks: none — nothing was changed or shipped
     follow-ups: none
     questions: There is no issue 24 brief available in this fixture — no tracker is named in AGENTS.md and the repo has no remote, so the brief cannot be read. Point me at it (URL, local path, or paste it), or tell me to redefine the assignment.
     knowledge: none

     Build · <local model> · 4m 42s · 12.2 tok/s
```

```console
$ python3 skills/ec-fleet/scripts/fleet.py overview
NAME      STATE  HOST      RETURN   QUESTIONS
issue-24  done   opencode  blocked  There is no issue 24 brief available in this fixture — no tracker is named in AGENTS.md and the rep…
```

So with no agent configured the overview looks the same as for a tech-lead, `opencode` in the HOST column and a readable block, and nothing in it says the session is not one. One run, one local model.

### Verdicts

1. **Start: fails with the package's default, and nothing says so.** `opencode --agent tech-lead` is not a command at 2.2.7: the top-level command has no `--agent`. workmux opens the window and types `opencode --agent tech-lead --prompt "$(cat .workmux/PROMPT-<name>.md)"`; the pane then holds a shell with opencode's usage error, `fleet.py start` prints `started <name>` with rc 0, and `workmux status --json` reports no session. With `start = "opencode"` and `default_agent: tech-lead` in a config opencode reads, workmux types `opencode --prompt "$(cat .workmux/PROMPT-<name>.md)"`, the TUI opens as the tech-lead and the prompt arrives. `opencode mini --agent tech-lead` also starts the tech-lead but is never reported. Without `default_agent` in a config, `start = "env OPENCODE_CONFIG=<path>/agent.json opencode --standalone"`, the file holding `{"default_agent": "tech-lead"}`, starts the tech-lead too, tracked, whatever the machine's config says; without `--standalone` the same command works only when it is the one that starts the background service, and a path with a space breaks it (step 10). The session is reported, with `"agent_kind": "opencode"`, only by workmux 0.1.281's current plugin: the one-file plugin installed on this machine fails to load at 2.2.7, so as found workmux reports no opencode session at all and the overview has no row. The current plugin was loaded from the fixture.
2. **First-run prompts: none.** A new worktree goes straight to its prompt, and opencode applies the repository's config and runs its plugins unasked. There is nothing to pre-answer, so no `trust` string is needed and none was tested.
3. **States: `working`, `waiting` and `done`, all three.** A session at opencode's permission prompt, or at a question-tool form, reads `waiting`. A rejected permission or a dismissed form ends the turn and reads `done`.
4. **The captured screen: the overview reads the block, with one parser bug.** A complete block was read on a 63-row and a 94-row pane, with a wrapped value and with the nested `findings:` list. When the `status:` line shares a screen row with sidebar text, the overview says `no RETURN block on screen` with the whole block in view. That capture is saved as a fixture.
5. **End to end: holds in part.** The tech-lead loaded `ec-fleet` from the start prompt as its first act and read `AGENTS.md`. Its first stop was a question-tool form, not a RETURN block, and the overview showed `waiting` and `no RETURN block on screen`. Told to stop as the skill says, it ended with a complete block and the overview showed `done`, `blocked` and its `questions` value. With no agent configured, `start = "opencode"` and the same prompt, opencode's `Build` agent took the assignment: it loaded `ec-fleet`, did not load `ec-tech-lead`, never signed, did not stop in 14 minutes, and gave a block the overview read once it was told to stop (step 11). The managed block's line did not hold in that run.
6. **Dispatch from inside a session: holds, with no approval and with one trap.** An opencode tech-lead ran `fleet.py start` and `fleet.py overview` through its shell tool with no approval, workmux asked nothing, and the window opened in its own tmux session. Left alone, it first ran the script from the skill's directory, where the start fails with `Current directory is not a git repository` and from where the overview is no longer scoped to the project. The window it started died on the default start command, as in verdict 1.

### Not measured

- Any of this with workmux's plugin installed by `workmux setup` under `~/.config/opencode/`. It was loaded from the fixture's `.opencode/plugins/` only.
- `default_agent` in the global config. It was set in the fixture's `opencode.json` only.
- What `--standalone` costs and changes: each session then runs its own server, and whether such a session shares the session list, the service's remote features or anything else with the background service was not looked at.
- The `$OPENCODE_CONFIG` form in a home directory whose path holds a space, beyond the one failing start in step 10, and any way to quote such a path through workmux.
- The fallback of step 11 more than once, or with another model.
- Which model the TUI uses in a new worktree with no project config. From step 4 on the fixture named the local one.
- Any model but the one local model. The mistyped paths, the question forms and the overview run by an issue tech-lead are that model's.
- A `questions:` line beside sidebar text, the sidebar in a long session, and a pane too narrow for the sidebar.
- A block taller than the pane.
- A contract with `### Parallel work` lines, a commit or a push from a worktree, several issues at once, and the plan assignment.
- `--auto`, opencode's flag that approves every permission not denied, and a tech-lead whose permissions ask before shell commands.
- opencode's remote features (`opencode pair`, `--server`).
- opencode between 2.0.18 and 2.2.7: the version at which `--agent` left the top-level command, and the one at which the one-file plugin stopped loading, are UNVERIFIED.

**Host state.** The opencode install was updated from the export at `754fce5` and left updated: under `~/.config/opencode/`, `skills/ec-fleet/` is new (two files) and `skills/ec-init/SKILL.md` changed; the six agents and the other three `ec-` skills were rewritten with identical bytes. The six skills that are not this package's, `plugins/workmux-status.ts`, `cli.json`, the global `opencode.json` and the global `AGENTS.md` have the same hashes as before. Nothing was written under `~/.codex/` by this probe. Its agents directory is untouched. `~/.codex/e-colleagues.config.toml` has a different hash than before; who wrote it is not established here. opencode's background service was started by the probe and stopped at the end (`opencode service status`: `stopped`, as before; no opencode process left); stopping it removed a stale `~/.local/state/opencode/service.json` left by an earlier opencode version. opencode kept its usual records: twelve sessions in its database, its log, and twelve prompts appended to `~/.local/state/opencode/prompt-history.jsonl`, the TUI's input history. `model.json`, `kv.json` and `auth.json` have the same hashes as before. Fifteen worktrees were made and removed, `issue-12` to `issue-24` with 12 and 13 made twice (`✓ Removed worktree 'issue-12' and branch 'issue-12'`, and the same for each). Afterwards `workmux status --json` in `<tmp>/repo` listed `"agents": []`, `git worktree list` listed only `<tmp>/repo`, and the probe's tmux session was killed. workmux kept a state file for four probe panes under `~/.local/state/workmux/agents/`; all four were removed. No `setup.json` and no `sent/` was created, the other agent CLI's hooks file has the same hash as before, and the workmux config was not modified. workmux appended to its log. The two scratch homes used in step 3 and the two `agent.json` files of step 10 are under `<tmp>`. Steps 10 and 11 were a second sitting, with its own probe session of the same name and its own hashes: between its start and its end the only file that differs is `prompt-history.jsonl`, and the service, started and stopped twice, was left stopped.

---

## E31 — the fleet skill on Claude Code: it runs end to end once the plugin is installed, trust is kept per repository and not per worktree, and workmux reports `waiting` at an approval

**Date** 2026-11-15. **Claude Code 2.1.325**, model Opus 5.5 with xhigh effort, the owner's configured default; **workmux 0.1.281**; **tmux 3.8**; this package as a clean export of commit `754fce5`, called `<pkg>` below. Tranche B.

E26 to E28 measured the fleet skill on Antigravity only, and design §17 lists Claude Code as UNVERIFIED. This entry answers the same questions for Claude Code: the start, the first-run prompt, the states, the captured screen, the skill end to end, and a dispatch from inside a session.

Everything ran in a throwaway repository, `<tmp>/repo` (`git init`, one commit, a repository-local identity, no signing), with its contract from `python3 <pkg>/skills/ec-init/scripts/bootstrap.py <tmp>/repo --write` (`wrote 3 files, 3 changed`), committed. No interview was run, so the project bindings are empty. A second repository, `<tmp>/repo2` (`git init`, one commit), served as the control for trust. The probe used its own tmux session, `e31-probe`, and touched no other. `fleet.py` was run from a shell pane of that session, from the export, with `~/.config/e-colleagues/fleet.toml` absent and `XDG_CONFIG_HOME` and `EC_FLEET_CONFIG` unset unless a step names a config file. workmux puts worktrees in `<tmp>/repo__worktrees/`.

These were real sessions on the owner's account. Nine reached the model: seven worktree tech-leads with a one-line start prompt (three of them with one to five further prompts), one with the skill's real start prompt, and one dispatching tech-lead (two messages). Hook timings come from workmux's log, tool calls from Claude Code's own transcript of each session (`~/.claude/projects/<folder>/<session>.jsonl`), both in UTC. In every capture below the line of the owner's status bar that carries an account and a machine name is cut, the banner's plan label is cut, and trailing spaces are stripped.

### 1. Versions, the hooks, and the machine as found

```console
$ claude --version
2.1.325 (Claude Code)
$ workmux --version
workmux 0.1.281
$ tmux -V
tmux 3.8
```

The hooks in `~/.claude/settings.json`, re-wrapped, nothing else changed. They were already there; `workmux setup` was not run, and the file was read, not edited:

```json
"hooks": {
  "Notification":     [{"matcher": "permission_prompt|elicitation_dialog",
                        "hooks": [{"type": "command", "command": "workmux set-window-status waiting"}]}],
  "PostToolUse":      [{"hooks": [{"type": "command", "command": "workmux set-window-status working"}]}],
  "SessionStart":     [{"matcher": "startup|resume|clear|fork",
                        "hooks": [{"type": "command", "command": "workmux register-agent"}]}],
  "Stop":             [{"hooks": [{"type": "command", "command": "workmux set-window-status done"}]}],
  "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "workmux set-window-status working"}]}]
}
```

Unlike the Antigravity hooks (E26), these can report a waiting state. The same file sets `"model": "opus"`, `"tui": "fullscreen"` and `"permissions": {"allow": ["Read", "Glob", "Grep", "WebFetch", "WebSearch"]}`, and no `defaultMode`.

This package was not installed for Claude Code: `claude plugin list` ran and listed the owner's plugins, none of them `e-colleagues` (a `grep` of its output for the name matched nothing, exit code 1), and `~/.claude/agents/` held no `tech-lead`. workmux runs with the owner's global config: one pane per window holding the agent, and `base_branch: auto`.

### 2. The default start command with the plugin not installed

```console
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py start 12 --host claude; echo "rc=$?"
started issue-12
rc=0
```

workmux's log, trimmed:

```
08:13:10.509  workmux add issue-12 --background --agent "claude --agent tech-lead" --prompt "Use the ec-fleet skill. Your assignment: issue 12."   cwd=<tmp>/repo
08:13:10.548  create:start branch="issue-12" base=Some("main")
08:13:10.591  window created, pane %37
08:13:10.684  create:completed path=<tmp>/repo__worktrees/issue-12
```

The window opened and the worktree was made. What workmux typed into the pane, and what came back (the list of the machine's own agents is cut):

```console
$ claude --agent tech-lead -- "$(cat .workmux/PROMPT-issue-12.md)"
--agent 'tech-lead' not found. Available agents: claude, claude-code-guide, …, statusline-setup, web-fetch
```

Claude Code exited at once and the pane was back at its shell (`#{pane_current_command}` `bash`). The same command typed by hand in the first pane gave the same message and `rc=1`. No model was reached and no trust dialog was shown: the name is checked first.

```console
$ workmux status --json          # in <tmp>/repo
  …
  "agents": [],
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py overview; echo "rc=$?"
no sessions
rc=0
```

**`fleet.py start` printed `started issue-12` with exit code 0 for a host that had already exited, and the overview has no row for it.** The script reports what workmux did, and workmux made the window. The failure is on that window's screen and nowhere else. A wrong `--agent` name is loud at 2.1.325 on the command line; design §8 records that the same mistake in a settings file's `agent` key is silent (E21).

### 3. With the package loaded for one session: the trust dialog, and what the overview shows there

`claude --plugin-dir <dir>` loads a plugin "for this session only" (`claude --help`) and installs nothing. With it, the agents are listed under qualified names only. A name that does not exist prints the list:

```console
$ claude --plugin-dir <pkg> --agent no-such-agent-e31; echo "rc=$?"
--agent 'no-such-agent-e31' not found. Available agents: …, e-colleagues:designer, e-colleagues:developer, e-colleagues:platform, e-colleagues:reviewer, e-colleagues:security, e-colleagues:tech-lead, …
rc=1
```

The bare name still resolves. A probe config, `<tmp>/cfg/a-bare.toml`:

```toml
[hosts.claude]
start = "claude --plugin-dir <pkg> --agent tech-lead"
prompt = "Reply with the single word ready, then stop."
```

```console
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py --config <tmp>/cfg/a-bare.toml start 13 --host claude; echo "rc=$?"
started issue-13
rc=0
```

workmux typed `claude --plugin-dir <pkg> --agent tech-lead -- "$(cat .workmux/PROMPT-issue-13.md)"`, and the new window showed, in a 238 × 63 pane:

```
 Accessing workspace:

 <tmp>/repo__worktrees/issue-13

 Quick safety check: Is this a project you created or one you trust? (Like your own code, a well-known open source project, or work from your team). If not, take a moment to review what's in this folder first.

 Claude Code'll be able to read, edit, and execute files here.

 Security guide

 ❯ No, exit
   Yes, I trust this folder

 Enter to confirm · Esc to cancel
```

The selection starts on "No, exit". The session sat there from 08:14:18 to about 08:19:21. Throughout:

```console
$ workmux status --json          # in <tmp>/repo
  …
  "agents": [],
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py overview; echo "rc=$?"
no sessions
rc=0
```

**A Claude Code session at its trust dialog is not in `workmux status` at all, so the overview has no row for it.** No hook had run: workmux's log has no call from that pane before the dialog was accepted. On Antigravity the same moment read `working` or `done` (E26, E27), because agy's hooks and its start turn run behind the dialog.

The dialog was then accepted in that window, acting as the person (Down, Enter). The hook calls for the pane, and the status polled every 3 s:

```
08:19:22.915  "workmux", "register-agent"
08:19:36.038  "workmux", "set-window-status", "working"
08:19:39.814  "workmux", "set-window-status", "done"
```

```
08:19:25 … 08:19:34   "status": "-"          (no elapsed_secs)
08:19:37              "status": "working"    elapsed_secs 1
08:19:40 … 08:19:46   "status": "done"       elapsed_secs 1, 4, 7
```

Between registering and the start prompt being submitted, 13 s here, the session is listed with `"status": "-"`. The screen afterwards (`#{alternate_on}` 1, `#{history_size}` 0):

```
 ▐▛███▛█   Claude Code v2.1.325
▝▜██████▀  Opus 5.5 with xhigh effort
 ▝▝   ▝▝   @e-colleagues:tech-lead · <tmp>/repo__worktrees/issue-13

❯ Reply with the single word ready, then stop.

● 👨‍💻 Tech-Lead: ready

✻ Cogitated for 16s · done 9:19

──────────────────────────────────────────────────────────── e-colleagues:tech-lead ─
❯
────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · ← 1 agent
```

The bare `--agent tech-lead` became `@e-colleagues:tech-lead`, the prompt arrived, and the reply carried the signature. The start turn began after the dialog was accepted, not behind it: the first hook call came within 2 s of the acceptance. That the model was not called earlier is an inference from that and from the turn's own timer.

One reading of `workmux status --json issue-14` from step 4, trimmed:

```json
{
  "worktree": "issue-14",
  "branch": "issue-14",
  "project": "repo",
  "project_path": "<tmp>/repo",
  "status": "done",
  "elapsed_secs": 20,
  "title": "✳ e-colleagues:tech-lead",
  "pane_id": "%50",
  "workdir": "<tmp>/repo__worktrees/issue-14",
  "agent_kind": "claude",
  "session": "e31-probe",
  …
}
```

**Typing `workmux list` at a shell prompt asked workmux's own question again.** With the terminal as its input, `workmux list` in the first pane stopped at `Install or update status tracking hooks? [Y/n]` for another agent CLI it detected, as `workmux add` did from agy's pseudo-terminal in E26. It was ended with Ctrl-C: no `~/.local/state/workmux/setup.json` was written and that CLI's hooks file has the same hash as before. Every later `workmux list`, `status`, `capture` and `remove` was run with `< /dev/null` and asked nothing, which is how `fleet.py` runs its launcher. This supports E27's inference and does not prove it.

### 4. Trust is kept per repository: after one acceptance, a new worktree opens with no dialog

Accepting the dialog made Claude Code write one record into `~/.claude.json`, and its key is the main checkout, not the worktree the dialog named:

```
projects["<tmp>/repo"] = {"allowedTools": [], …, "hasTrustDialogAccepted": true, …}
```

There is no key for `<tmp>/repo__worktrees/issue-13`. The next start used the same config and the same command:

```console
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py --config <tmp>/cfg/a-bare.toml start 14 --host claude; echo "rc=$?"
started issue-14
rc=0
```

```
08:20:13.398  window created, pane %50
08:20:16.174  "workmux", "register-agent"
08:20:30.384  "workmux", "set-window-status", "working"
08:20:33.861  "workmux", "set-window-status", "done"
```

No dialog, and no key was sent to that window. It registered 2.8 s after the window was created and answered `👨‍💻 Tech-Lead: ready`.

**Control, in a repository Claude Code had never opened.** From `<tmp>/repo2`, the same config and `start 21`: the dialog showed for `<tmp>/repo2__worktrees/issue-21`, and `workmux status --json` read `"agents": []` twice, about 50 s apart. It was answered "No, exit": Claude Code exited, the window stayed open at its shell, and the `projects` records in `~/.claude.json` were the same before and after. Then `claude` was started by hand in the main checkout `<tmp>/repo2`, its dialog accepted, and the session left with `/exit` and no prompt. That wrote `projects["<tmp>/repo2"]` with `"hasTrustDialogAccepted": true`. After it, `start 22` in that repository opened with no dialog:

```
08:38:04 … 08:38:13   "status": "-"
08:38:16              "status": "working"
08:38:19              "status": "done"
```

So the dialog depends on whether the repository is trusted, whichever folder of it the acceptance happened in. A person who already runs Claude Code in a repository, as a dispatching tech-lead in the main checkout does, has answered it.

**No way was found to pre-answer the dialog for one session.** `claude --help` at 2.1.325 lists no trust option for an interactive session. Its only words on the dialog are under `-p`: "The workspace trust dialog is skipped when Claude is run in non-interactive mode (via -p, or when stdout is not a TTY…)". One candidate was tried:

```console
$ claude --plugin-dir <pkg> --agent tech-lead --trust-workspace; echo "rc=$?"      # in <tmp>/repo2, before it was trusted
error: unknown option '--trust-workspace'
rc=1
```

A search of the binary's strings found `--trust-workspace` as an option of `claude ultrareview` only ("Trust the current folder for this run only, without asking (for scripts and CI)"), and an environment variable, `CLAUDE_CODE_SANDBOXED`, read by the code that decides whether to show the dialog. The variable was not tried: it is not an argument, so it cannot go in a `trust` string, it is not in the help, and it states something that is not true of this machine. That is a search, not proof that no other route exists.

### 5. States

A third session was started in manual permission mode, so that it would ask (`<tmp>/cfg/c-manual.toml`: the config of step 3 with `--permission-mode manual` added to `start`). `workmux status --json issue-15` was polled every 2 or 3 s. Prompts were typed into its window, acting as the person.

| moment, in the issue-15 session | `status` | `elapsed_secs` read |
|---|---|---|
| registered, start prompt not yet submitted | `-` | none |
| the start turn | `working` | 3 |
| that turn finished | `done` | 2, 5, 8 |
| "Run the shell command date and show its output.": it ran with no approval | `working`, then `done` | 2; 3 … 24 |
| at the approval for `ls -la probe.txt; echo "exit=$?"`, the first step of "Create a file named probe.txt … then commit it …" | `working`, then `waiting` | 3, 6, 9, 12; then 1, 4, 7, 10, 13 |
| after choosing `4. No` there: the screen showed `⎿  Interrupted · What should Claude do instead?`, input box idle | `waiting` | 25, 28, … 47, 59 |
| the next prompt, model at work | `working` | 2, 6, 9 |
| at the approval for creating `probe.txt` | `waiting` | 3, 6, 9, 16 |
| approved; the approval for `git add probe.txt && git commit …` already on screen | `working`, then `waiting` | 2, 4, 6; then 6, 8, … 24 |
| approved; the turn finished | `working`, then `done` | 2, 4; then 2, 4, 6, 8 |

The hook calls behind the last four rows:

```
08:23:43.959  "workmux", "set-window-status", "working"     <- the prompt
08:23:53.093  "workmux", "set-window-status", "waiting"     <- the approval for the file
08:24:09.775  "workmux", "set-window-status", "working"     <- approved
08:24:16.225  "workmux", "set-window-status", "waiting"     <- the approval for the commit
```

**All three states appear for Claude Code.** A session at an approval reads `waiting`, a few seconds after the prompt is drawn: the commit's approval was on screen at about 08:24:15 with the status still `working`, and `waiting` came at 08:24:16. A declined tool call fires no `Stop`, so the declined session read `waiting`, not `done`, until its next turn. `workmux list` at the first approval showed `issue-15  1m   waiting  ✓    -         ../repo__worktrees/issue-15`.

`fleet.py overview` at that approval:

```
NAME      STATE    HOST    RETURN  QUESTIONS
issue-13  done     claude          no RETURN block on screen
issue-14  done     claude          no RETURN block on screen
issue-15  waiting  claude          no RETURN block on screen
```

and `workmux capture issue-15 --lines 200` there, lines 29–44 of 62, the two dashed rules trimmed with `…`:

```
────────────────────────────────────────────────────────────…
 Bash command
 Tip: auto mode handles these prompts for you — choose "switch to auto mode" below
 Check whether probe.txt already exists
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌…
 ls -la probe.txt; echo "exit=$?"
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌…
 This command requires approval

 Do you want to proceed?
 ❯ 1. Yes
   2. Yes, and don’t ask again for: echo "exit=$?"
   3. Yes, and switch to auto mode · auto mode handles these prompts for you
   4. No

 Esc to cancel · Tab to amend
```

The commit went through after its two approvals:

```console
$ git log --oneline -2          # in <tmp>/repo__worktrees/issue-15
d9e83c5 add probe.txt
7bfd4bd chore: bootstrap contract
```

**The permission mode of a started session.** Every session started without a permission flag showed `⏵⏵ auto mode on` in its status line, and the transcripts record `"permissionMode": "auto"`. Nothing in the start command selects it and the owner's `settings.json` has no `defaultMode`; where this machine's default comes from was not established. In auto mode no approval prompt was shown in any step of this entry.

### 6. The captured screen around a RETURN block

The issue-15 session had no copy of the skill in context, so the prompt listed the fields inline, as in E26:

```
Say in one line that the first ls command was declined, then end your reply with this block in a code fence, one field per line: ### RETURN, status: needs-decision, task: issue-15, changed: none, evidence: ls was declined, findings: none, risks: none, follow-ups: none, questions: <one question of at least 400 characters asking whether to retry the ls command or skip it, with the reasons for each>, knowledge: none
```

`workmux capture issue-15 --lines 200`, after the status turned `done`, returned 61 lines on the 238 × 63 pane with no escape sequences. Lines 40–61, the two rules trimmed with `…`:

```
● 👨‍💻 Tech-Lead: The first ls command, which would have checked whether probe.txt already existed, was declined and never ran.

  ### RETURN
  status: needs-decision
  task: issue-15
  changed: none
  evidence: ls was declined
  findings: none
  risks: none
  follow-ups: none
  questions: The first `ls -la probe.txt` command was declined, so it never checked whether probe.txt already existed before I wrote it. The file has since been created and committed as d9e83c5. Should I retry the ls command or skip it?
  Retrying would show the file's current state, size and permissions in the worktree directly, which fills the gap the declined command left. Skipping is reasonable because the commit output already shows probe.txt was created as a new
  one-line file. A retry would repeat what git has shown and ask you for one more approval.
  knowledge: none

✻ Cooked for 11s · done 9:25

────────────────────────────────────────────────────────────… e-colleagues:tech-lead ─
❯ skip the ls, no need to retry
────────────────────────────────────────────────────────────…
  ⏸ manual mode on · ← 1 agent
```

```
NAME      STATE  HOST    RETURN          QUESTIONS
issue-13  done   claude                  no RETURN block on screen
issue-14  done   claude                  no RETURN block on screen
issue-15  done   claude  needs-decision  The first `ls -la probe.txt` command was declined, so it never checked whether probe.txt already ex…
```

The overview read the block. `last_return` on the saved capture returns the whole question, all three lines joined. What a reader of a Claude Code capture has to handle:

- **No fence and no frame**, as on Antigravity. Every line of the block is indented two spaces, not four, and the signature line starts with `● `.
- **Wrapping is the TUI's own.** A long value breaks at a word boundary near the pane width, and continuation lines carry the same two-space indent as the field lines. The first line of the `questions:` value ends in a trailing space.
- **Text follows the block.** After `knowledge:` come the turn's timer line (`✻ Cooked for 11s · done 9:25`), a rule carrying the agent's name, the input box and the status bar. The input box held a reply Claude Code suggests for the person (`skip the ls, no need to retry`), which the capture returns as ordinary text. The parser takes these lines as part of `knowledge`, which the overview does not show.
- **The capture is the visible screen only**, with the owner's `"tui": "fullscreen"`: `#{alternate_on}` 1, `#{history_size}` 0, and no capture returned more lines than its pane's height (61 and 62 on 63 rows, 93 on 94).

**The nested `findings:` list**, which E26 and E27 did not exercise. In issue-14 the prompt asked for two findings, the second with `body: questions: is a word that also names a field`:

```
  ### RETURN
  status: partial
  task: issue-14
  changed: none
  evidence: none
  findings:
    - severity: blocking
      path: README.md
      line: 1
      body: the title says probe
    - severity: nit
      path: -
      line: -
      body: questions: is a word that also names a field
  risks: none
  follow-ups: none
  questions: Should the parser probe continue (yes or no)?
  knowledge: none
```

The overview row read `issue-14  done  claude  partial  Should the parser probe continue (yes or no)?`. The list items are indented four and six spaces.

**The other renderer.** Claude Code's `tui` setting takes `default` or `fullscreen`. One session was started with the default one for that session only (`start = "claude --agent tech-lead --settings '{\"tui\":\"default\"}'"`, the plugin installed by then, step 7), in a 382 × 94 pane. It drew on the main screen (`#{alternate_on}` 0), under the command workmux had typed. A block with one nested finding and a `questions:` value wrapped over two lines was captured in full (43 lines), rendered the same way, and the overview read it: `issue-19  done  claude  needs-decision  Should we keep the default renderer or switch to the fullscreen one? Keeping the default leaves out…`.

**An older block stays readable.** issue-15 later ran one more turn that ended without a block (step 8), with its block still in view, and its row kept `needs-decision` and the old question. Design §17 already says so.

No capture defeated the parser, so none is offered as a failing fixture. Five raw captures were kept beside this entry's working files, with scrubbed copies: the approval, the three blocks above, and the block of step 7.

### 7. The install, and the default start command end to end

Installed by the README's route, from the export:

```console
$ claude plugin marketplace add "<pkg>"; echo "rc=$?"
Adding marketplace…✔ Successfully added marketplace: e-colleagues (declared in user settings)
rc=0
$ claude plugin install e-colleagues@e-colleagues; echo "rc=$?"
Installing plugin "e-colleagues@e-colleagues"...✔ Successfully installed plugin: e-colleagues@e-colleagues (scope: user)
rc=0
$ claude plugin list
…
  ❯ e-colleagues@e-colleagues
    Version: 0.1.1
    Read from: <pkg>
    Scope: user
    Status: ✔ enabled
    Note: Default agents/ folder is ignored because the manifest sets "agents"
```

What the two commands wrote is under **Host state**. For a marketplace that is a directory, the plugin is read from that directory, not from the copy Claude Code also makes under `~/.claude/plugins/cache/`.

Then the package's default start command, no config file, the skill's real prompt:

```console
$ echo "XDG=${XDG_CONFIG_HOME-unset} ECF=${EC_FLEET_CONFIG-unset}"; python3 <pkg>/skills/ec-fleet/scripts/fleet.py start 16 --host claude; echo "rc=$?"
XDG=unset ECF=unset
started issue-16
rc=0
```

```
08:29:14.685  workmux add issue-16 --background --agent "claude --agent tech-lead" --prompt "Use the ec-fleet skill. Your assignment: issue 16."   cwd=<tmp>/repo
08:29:14.769  window created, pane %63
08:29:17.039  "workmux", "register-agent"
08:29:30.061  "workmux", "set-window-status", "working"      <- the prompt
08:29:32.550  "workmux", "set-window-status", "working"      <- after each of four tool calls
08:29:36.878  "workmux", "set-window-status", "working"
08:29:40.081  "workmux", "set-window-status", "working"
08:29:44.860  "workmux", "set-window-status", "working"
08:29:58.533  "workmux", "set-window-status", "done"
```

```console
$ tr '\0' '|' < /proc/<claude in %63>/cmdline
claude|--agent|tech-lead|--|Use the ec-fleet skill. Your assignment: issue 16.|
```

No dialog, since the repository was trusted (step 4). The session's tool calls, from its transcript:

| time | call |
|---|---|
| 08:29:30 | the start prompt, `Use the ec-fleet skill. Your assignment: issue 16.` |
| 08:29:32 | `Skill {"skill": "e-colleagues:ec-fleet", "args": "issue 16"}` → `Launching skill: e-colleagues:ec-fleet` |
| 08:29:36 | `Bash`: `pwd; git remote -v; echo "exit=$?"; ls -la; git log --oneline -5; git branch -a` |
| 08:29:39 | `Bash`: reads `README.md`, `.git`, `.e-colleagues/*` and `.workmux/*`, and `git config --get-regexp '^remote\.'` |
| 08:29:44 | `Bash`: `git log --all …`, `git grep -n -i -E 'issue\|tracker\|github\|gitlab\|linear'` over every branch, `ls` of the sibling worktrees |
| 08:29:58 | the reply |

None of the three commands asked for approval (auto mode). `workmux capture issue-16 --lines 200` returned 93 lines on a 382 × 94 pane. Lines 1–35, the `evidence:` line cut at `…`:

```
 ▐▛███▛█   Claude Code v2.1.325
▝▜██████▀  Opus 5.5 with xhigh effort
 ▝▝   ▝▝   @e-colleagues:tech-lead · <tmp>/repo__worktrees/issue-16

❯ Use the ec-fleet skill. Your assignment: issue 16.

● Skill(e-colleagues:ec-fleet)
  ⎿  Successfully loaded skill

  Ran 3 shell commands

● 👨‍💻 Tech-Lead: I can't read issue 16, so I've stopped before doing any work on it.

  - The contract doesn't say where issues live. The "Platforms and tools" section of AGENTS.md is empty.
  - The repo doesn't say either. origin has no URL. A search of every branch for "issue", "tracker", "github", "gitlab" or "linear" found nothing. The only history is init, chore: bootstrap contract and add probe.txt on issue-15.

  I won't guess what the issue asks for. I need one of these from you:
  1. Paste the text of issue 16 here, or
  2. Tell me the tracker and how to read it, for example GitHub owner/repo, GitLab, or a Linear team.

  If you choose option 2, I can also add the tracker to the "Platforms and tools" section of AGENTS.md so later sessions find it. That's a change to the contract, so I'll only make it if you say yes.

  ### RETURN
  status: needs-decision
  task: issue 16
  changed: none
  evidence: `git remote -v` → origin has no URL (exit 0); AGENTS.md "Platforms and tools" is empty; `git grep -i -E 'issue|tracker|github|gitlab|linear'` over all branches → no matches (exit 1); …
  findings: none
  risks: origin has no URL, so nothing can be pushed from this repo once the work is done
  follow-ups: record the tracker and its tool under "Platforms and tools" in AGENTS.md (needs approval)
  questions: Where does issue 16 live and how do I read it? Or paste its text here.
  knowledge: none

✻ Baked for 41s · done 9:29
```

```console
$ python3 <pkg>/skills/ec-fleet/scripts/fleet.py overview; echo "rc=$?"
NAME      STATE  HOST    RETURN          QUESTIONS
issue-14  done   claude  partial         Should the parser probe continue (yes or no)?
issue-15  done   claude  needs-decision  The first `ls -la probe.txt` command was declined, so it never checked whether probe.txt already ex…
issue-16  done   claude  needs-decision  Where does issue 16 live and how do I read it? Or paste its text here.
rc=0
```

Loading the skill was its first act, it asked and waited instead of guessing (rule 3), and it ended with the skill's block, complete and last (rule 4). It made no call to read `AGENTS.md`. The file reaches a Claude Code session without one (`CLAUDE.md` is `@AGENTS.md` [CC-14]), and its reply states the file's content correctly. That it had the file in context is inferred from that, not read from the transcript.

### 8. A tech-lead session dispatches

The dispatching tech-lead was started in the first pane, in `<tmp>/repo`, by the documented command. To keep the session it starts to one short turn, the pane's shell first exported `EC_FLEET_CONFIG=<tmp>/cfg/d-short.toml`, a config that sets only `[hosts.claude] prompt = "Reply with the single word ready, then stop."`:

```console
$ claude --agent tech-lead 'use the ec-fleet skill; start 17'
```

It opened with no dialog, in auto mode. Its calls, from its transcript:

| time | call | result |
|---|---|---|
| 08:30:59 | `Skill {"skill": "e-colleagues:ec-fleet", "args": "start 17"}` | `Launching skill: e-colleagues:ec-fleet` |
| 08:31:04 | `Bash`: `python3 <pkg>/skills/ec-fleet/scripts/fleet.py start 17; echo "exit=$?"` | `fleet: no host chosen: pass --host (antigravity, claude, codex, opencode) or set default_host in the config`, `exit=2` |
| 08:31:09 | `Bash`: `python3 <pkg>/skills/ec-fleet/scripts/fleet.py start 17 --host claude; echo "exit=$?"` | `started issue-17`, `exit=0` |

**Neither command asked for approval, and nothing blocked.** It passed no `--host` first and then its own, as the skill says. workmux asked nothing: 40 ms lie between the command's start and `create:start` in its log. The new window registered 2 s after it was created, ran its turn and read `done`. The reply named the worktree and added: "The new session may first ask whether to trust the folder. You need to answer that in its window. I won't answer anything there for you, and that includes its questions."

Sent `overview`, it ran `fleet.py overview` and then `fleet.py overview --json`, "for untruncated questions", again with no approval:

```
NAME      STATE    HOST    RETURN          QUESTIONS
repo      working  claude                  (this session)
issue-14  done     claude  partial         Should the parser probe continue (yes or no)?
issue-15  done     claude  needs-decision  The first `ls -la probe.txt` command was declined, so it never checked whether probe.txt already ex…
issue-16  done     claude  needs-decision  Where does issue 16 live and how do I read it? Or paste its text here.
issue-17  done     claude                  no RETURN block on screen
```

It showed the table, said "You answer each one in its own window", and for issue-17 said the session "may be waiting at a Claude Code prompt, most likely the folder-trust question. Or it stopped without leaving a complete block in view." It sent nothing to any session. Its own row is marked `(this session)`: Claude Code's Bash tool passes `$TMUX_PANE` on.

**In manual mode the start needs one approval.** The issue-15 session (manual mode, step 5) was asked to run `python3 <pkg>/skills/ec-fleet/scripts/fleet.py --config <tmp>/cfg/d-short.toml start 18 --host claude`. It stopped at `This command requires approval`, read `waiting`, and after `1. Yes` reported `started issue-18`, exit code 0. Run from inside a worktree whose branch was one commit ahead, the start still branched from `main` (`base_branch: auto` in this machine's workmux config).

### Verdicts

1. **Start: holds once the plugin is installed, and fails without a word from `fleet.py` when it is not.** With the plugin installed by the documented route, `fleet.py start <ref> --host claude` with the default `claude --agent tech-lead` and no config opens the window, starts `@e-colleagues:tech-lead`, delivers the prompt and registers with `"agent_kind": "claude"`. workmux types `claude --agent tech-lead -- "$(cat .workmux/PROMPT-<name>.md)"`. Without the plugin, Claude Code exits with `--agent 'tech-lead' not found`, `fleet.py` still prints `started <name>` with exit code 0, and the overview has no row. The bare name `tech-lead` resolves to the plugin's agent, loaded by `--plugin-dir` or installed.
2. **First-run prompt: one trust dialog per repository, not per worktree.** A new worktree of a repository Claude Code has never been trusted in stops at the dialog, and the session is then absent from `workmux status --json` and from the overview. Once the dialog has been accepted in any folder of the repository, later worktrees open with no dialog. No session-only pre-answer was found, so no `trust` string is proposed for this host: the interactive command has no trust option, and `--trust-workspace` is rejected.
3. **States: `working`, `waiting` and `done` all appear,** plus `-` for the seconds between a session registering and its first prompt. A session at an approval reads `waiting` within a few seconds, and a session whose tool call was declined keeps reading `waiting`. Whether a started session ever meets an approval depends on its permission mode; on this machine sessions start in auto mode and met none.
4. **The captured screen: the overview reads the block** in both of Claude Code's renderers, with a wrapped `questions:` value and with a nested `findings:` list. No parser change is needed for this host.
5. **End to end: holds.** A tech-lead started with the default command and the default prompt called `Skill e-colleagues:ec-fleet` first, stopped at the missing tracker with a complete RETURN block, and the overview row showed `done`, `needs-decision` and its question. Reading `AGENTS.md` is inferred, not seen as a call.
6. **Dispatch from inside a session: holds.** A Claude Code tech-lead ran `fleet.py start` and `fleet.py overview` through its Bash tool with no approval in auto mode and one approval per command in manual mode. workmux asked nothing.

Against the skill's own text: "Until then the overview shows that session as `working` and nothing more, or as stopped with `no RETURN block on screen`" does not hold on Claude Code. Until the trust dialog is answered the session has no row.

### Not measured

- A machine where Claude Code does not start in auto mode: where a dispatched tech-lead with the real prompt first stops there. Manual mode was used only for the states, the commit and one `fleet.py start`.
- Auto mode refusing a command, and the state a session reads then. A session asking through Claude Code's question dialog (`elicitation_dialog` in the hook's matcher).
- `--agent e-colleagues:tech-lead` in a start command with a model turn. That the qualified name resolves was checked only as far as the trust dialog in an untrusted folder, answered "No, exit".
- A project that carries its own `.claude/agents/tech-lead.md`, which would beat the plugin's [CC-08].
- Trust when the worktrees live somewhere other than workmux's sibling directory, and a repository reached through a symlink.
- `CLAUDE_CODE_SANDBOXED`, and any other route to a session-only trust.
- A block taller than the pane in either renderer, and whether the default renderer's scrollback is returned by `workmux capture`.
- A contract with `### Parallel work` lines, a real issue read from a tracker, any stop after the first, `ready to push`, a push.
- The plan assignment.
- `workmux setup`: the hooks were already installed.
- `claude --remote-control`, and remote use in general.
- Any workmux other than 0.1.281 and any Claude Code other than 2.1.325.

**Host state.** Hashes of every file the probe might change were taken before the first step. The install of step 7 was removed at the end with `claude plugin uninstall e-colleagues@e-colleagues` (`✔ Successfully uninstalled plugin: e-colleagues (scope: user)`) and `claude plugin marketplace remove e-colleagues` (`✔ Successfully removed marketplace: e-colleagues`), and `claude plugin list` no longer lists the package. While installed, `~/.claude/settings.json` held `"e-colleagues@e-colleagues": true` under `enabledPlugins` and an `extraKnownMarketplaces.e-colleagues` entry with a `directory` source, and `installed_plugins.json` and `known_marketplaces.json` under `~/.claude/plugins/` each held one entry. Afterwards:

- `~/.claude/plugins/installed_plugins.json` has the same hash as before.
- `~/.claude/plugins/known_marketplaces.json` has no entry for the package. It differs from before only in the `lastUpdated` time of another marketplace, which Claude Code refreshed on its own.
- **`~/.claude/settings.json` differs by one line that Claude Code left: `"extraKnownMarketplaces": {},`, an empty object where there was no key.** Everything else in the file is byte for byte as before. On this machine the file is a symlink into a directory under version control, and it stayed a symlink. The probe does not edit that file, so the line is still there.
- `~/.claude/plugins/cache/e-colleagues/e-colleagues/0.1.1/` is still there, 89 files, among them the `.orphaned_at` marker Claude Code puts on a cache copy it no longer uses. Other plugins' old versions on the machine carry the same marker. It was left to the tool.

Claude Code wrote into `~/.claude.json`, which the probe did not edit: a `projects` record for `<tmp>/repo` and one for `<tmp>/repo2`, each with `"hasTrustDialogAccepted": true` from the two dialogs accepted, usage counters for the skill and the plugin (`skillUsage["e-colleagues:ec-fleet"]`, `pluginUsage["e-colleagues@inline"]`), and its usual startup counters. It kept a transcript directory under `~/.claude/projects/` for each of the ten folders a session ran in, and its prompt history. All of that was left; `claude purge <path>` is the tool's own command for deleting a project's records and was not run. The two "No, exit" answers saved nothing.

`workmux remove -f` removed ten worktrees and their branches (`✓ Removed worktree 'issue-12' and branch 'issue-12'`, and the same for 13 to 19 in `<tmp>/repo` and for 21 and 22 in `<tmp>/repo2`). Afterwards `workmux status --json` listed `"agents": []` in both repositories, `git worktree list` listed only the main checkout in each, the probe's tmux session was killed, and no Claude Code process the probe started remained. No workmux state file for a probe pane was left under `~/.local/state/workmux/agents/`, and no `setup.json` or `sent/` was created. The workmux config, workmux's saved settings and the other agent CLI's hooks file have the same hashes as before; workmux appended to its log. The hooks in `~/.claude/settings.json` were not changed.
---

## E32 — the Antigravity claims at agy 1.5.3: `AGENTS.md` now reaches every agent, workspace roots deliver agents, five registry names resolve and give no tool, and a re-install replaces

**Date** 2026-11-15. **agy 1.5.3** (`pacman -Q antigravity-cli` → `1.5.3_6604829099950080-1`), model Gemini 4 Argon (High), the configured default, for six sessions; `--model gemini-3.8-flash-low` for the 36 short ones, named where used. **Antigravity desktop 2.29.1** is installed and was **not driven**: only its `language_server` binary was read with `strings`. **tmux 3.8.** Tranche C, with one interactive step.

The Antigravity rows of `SUPPORT-MATRIX.md` were last confirmed at agy 1.2.10 or older (E24), and one had already flipped in passing (E27). This entry re-runs each one's measurement at 1.5.3, as E24 did at 1.2.10. Every probe used a throwaway fixture under `<tmp>`; every plugin was installed under its own name (`e32-probe`, `e32-tools`, `e32-inherit`, and three smaller ones) and uninstalled again, except the re-install test, which E8 ran against a tree named `e-colleagues` and which was run the same way here, from a copy of the package's export at commit `754fce5`. Host state was snapshotted before and compared after; see **Host state**.

A claim's desktop half is marked *not re-verified* throughout. Where a row cites the vendor changelog, that is `agy changelog`'s output, searched by keyword and quoted, not read in full: documentation, not measurement.

| claim | at agy 1.5.3 | what moved |
|---|---|---|
| `AG-02` | **reproduced** (CLI); desktop binary inspected only | nothing: all 18 frontmatter tags are in both binaries, and the body is not sliced at its second H1 |
| `AG-03` | **reproduced** (CLI); desktop selector not re-verified | nothing. New detail: `--agent` takes the frontmatter `name`, not the directory name, and refuses a sub-agent |
| `AG-04` | **partly measured for the first time**; was docs/source only | `TypeName` addressing and "only `subagent: true` is invocable" now rest on a run |
| `AG-05` | **reproduced** (CLI); desktop not re-verified | the allowlist still removes `invoke_subagent`. New: it does not bound MCP tools |
| `AG-06` | **changed** | six names are rejected, not seven; five more resolve and deliver nothing; three arrive under new names |
| `AG-07` | **changed** | the validator's wording and rules; and a global install is no longer the only route for agents (see `AG-12`) |
| `AG-08` | **reproduced, with the E27 flip confirmed by a proper test** | re-install replaces; an install now writes a registry entry; the destination takes the manifest's name. Most target forms were **not re-run** |
| `AG-10` | **partly measured for the first time**; was docs/source only | no placeholder is substituted; a workflow file was not expanded |
| `AG-11` | **changed** | `AGENTS.md` and `GEMINI.md` reach the default agent, a custom agent and a sub-agent |
| `AG-12` | **changed** | four workspace roots deliver agents, and a workspace definition beats a globally installed one of the same name |

### 1. Install, destination, registry, re-install [AG-08]

```console
$ agy plugin install ./e32-probe                    # in <tmp>/fix
  [ok]    e32-probe
          ✔ skills      : 1 installed (e32-skill)
          ✔ agents      : 5 installed (e32-fmname, e32-lead, e32-leaky, e32-nosub, e32-reviewer)
          Installed to ~/.gemini/config/plugins/e32-probe
$ diff -r <tmp>/fix/e32-probe ~/.gemini/config/plugins/e32-probe; echo "diff rc=$?"
diff rc=0
$ ls -la ~/.gemini/antigravity-cli/plugins
ls: cannot access '~/.gemini/antigravity-cli/plugins': No such file or directory
```

The fixture carried `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/marketplace.json` and `dist/` beside the root `plugin.json`, as E7's did. The whole tree was copied verbatim, to the global root. `~/.gemini/config/config.json` had the same hash after every install and uninstall in this entry.

**An install now writes a registry entry.** E8 found no registry file at 1.1.27 (`grep -rl importedAt` found none). At 1.5.3 `~/.gemini/config/import_manifest.json` gained:

```json
{ "name": "e32-probe", "source": "antigravity", "importedAt": "2026-11-15T08:16:51Z", "components": ["skills", "agents"] }
```

The listing is still derived from the directory, and the entry only supplies the `Source:` line. A plugin directory copied into `~/.gemini/config/plugins/` by hand, with no install, was listed (`- e32-handcopy (enabled, 0.0.1)` / `Components: 1 agent`, no `Source:`), delivered its agent to `agy agents`, and got no entry. An installed plugin whose directory was deleted by hand was gone from `agy plugin list` and its entry was gone from the file after that one `list` call.

**The destination takes the manifest's name, not the source folder's.** A source folder `e32-srcdir/` whose `plugin.json` says `"name": "e32-manifestname"`:

```console
$ agy plugin install ./e32-srcdir
  [ok]    e32-manifestname
          ✔ agents      : 1 installed (sd-agent)
          Installed to ~/.gemini/config/plugins/e32-manifestname
```

E8's addendum could not tell the two apart, because the repository's name and the manifest's name are the same string.

**`agy plugin uninstall <name>`** removed the directory and the registry entry (`Uninstalled plugin "e32-tools"`, rc 0). It also printed the same line, rc 0, for a name that was not installed.

**The re-install test, as E8 ran it.** `<tmp>/src/e-colleagues` is a copy of the export; `dest` is `~/.gemini/config/plugins/e-colleagues`:

```console
$ echo modified-marker > <tmp>/src/e-colleagues/skills/ec-tech-lead/MARKER.txt
$ agy plugin install ./e-colleagues
  [ok]    e-colleagues
          ✔ skills      : 5 installed (ec-fleet, ec-init, ec-onboard, ec-status, ec-tech-lead)
          ✔ agents      : 6 installed (designer, developer, platform, reviewer, security, tech-lead)
          Installed to ~/.gemini/config/plugins/e-colleagues (replaced existing installation)
$ ls dest/skills/ec-tech-lead/
MARKER.txt
SKILL.md
$ echo dest-only > dest/DEST-ONLY.txt               # a file the source never had
$ rm <tmp>/src/e-colleagues/skills/ec-tech-lead/MARKER.txt
$ agy plugin install ./e-colleagues                 # the same output, "(replaced existing installation)" included
$ ls dest/skills/ec-tech-lead/
SKILL.md
$ ls dest/DEST-ONLY.txt
ls: cannot access '~/.gemini/config/plugins/e-colleagues/DEST-ONLY.txt': No such file or directory
$ cd ~/.gemini/config/plugins && agy plugin install ./e-colleagues
Error: failed to copy plugin: source and destination are the same directory: ~/.gemini/config/plugins/e-colleagues
```

**Verdict: at 1.5.3 a second install replaces the directory exactly.** The marker deleted from the source did not survive, and neither did a file that existed only in the destination. E8 measured the opposite at 1.1.27, and E27 saw the replacement in passing. The vendor changelog dates the change: under **1.1.28**, "Fixed plugin reinstalls keeping files that had been deleted from the source: installing a plugin now replaces its managed directory exactly, installing a plugin from its own installed directory is refused instead of corrupting it, and uninstalling a plugin no longer leaves its enabled/disabled entry behind in `config.json`." The refusal it names is the last command above. No version between 1.1.27 and 1.5.3 was run here, so 1.1.28 is the vendor's statement.

**The URL install**, the one network action of this entry:

```console
$ agy plugin install https://github.com/gnuruzzi/e-colleagues
Cloning plugin from https://github.com/gnuruzzi/e-colleagues.git...
  [ok]    e-colleagues
          ✔ skills      : 5 installed (ec-fleet, ec-init, ec-onboard, ec-status, ec-tech-lead)
          ✔ agents      : 6 installed (designer, developer, platform, reviewer, security, tech-lead)
          Installed to ~/.gemini/config/plugins/e-colleagues (replaced existing installation)
```

It holds at 1.5.3. The installed directory held 116 files, 29 of them under `.git/`: the clone's own repository data is installed with the plugin. `config.json` was untouched. The install was put back from the export afterwards.

**Target forms.** Only the forms that cannot leave the machine were re-run:

| target | result at 1.5.3 |
|---|---|
| `file://<tmp>/src/e-colleagues` | rc 1, `Error: install target must be a directory: file://<tmp>/src/e-colleagues` — as E8 |
| a path that does not exist | rc 1, `Error: install target must be a directory: <path>` |
| `agy plugin install --help`, `agy plugin link --help` | not flags, as in E8's second addendum: `install target must be a directory: --help`; `link requires marketplace name and target` |

`agy plugin --help` now reads `install <target>       Install a plugin (supports plugin[@marketplace])`, the binary's error string is `install target must be a directory or <plugin>@<marketplace>: %s`, and `agy plugin list` gives 13 of the 15 installed plugins `Source:     antigravity-plugins-official`. A directory `~/.gemini/antigravity-cli/cache/marketplaces` exists. So E8's second addendum, "no marketplace is known", no longer describes this machine: one is. Whether a user can register another, and what `plugin@marketplace`, a bare plugin name, the `owner/repo` shorthand, the SSH form, a non-github URL and `link` do at 1.5.3, is under **Not measured**.

### 2. The validator [AG-07]

```console
$ agy plugin validate <tmp>/fix/e32-probe
Validating e32-probe (<tmp>/fix/e32-probe/plugin.json)

  · plugin.json: no logo: the plugin shows a generic icon. Add "logo": "assets/logo.svg" (a .png, .svg, .jpg, .jpeg or .webp file inside the plugin)

  skills 1 · agents 5 · rules 0 · hooks 0 · mcpServers 0 · sidecars 0

✔ Validation passed
rc=0
$ agy plugin validate <export>                      # this package at 754fce5
  ⚠ AGENTS.md: never loaded: plugins load rules only from rules/. Move it to rules/AGENTS.md
  …
  skills 5 · agents 6 · rules 0 · hooks 0 · mcpServers 0 · sidecars 0

✔ Validation passed with 1 warning
rc=0
$ agy plugin validate <export> --strict
…
Error: validation failed in strict mode: 1 warning
rc=1
```

The three-manifest tree still validates, with the right counts and no word about the foreign directories, as in E7; the `[ok]` line is gone, as E26 recorded. `--strict` fails this package on the root `AGENTS.md` warning. `--json` prints the same report as an object with `components` and `findings`.

AG-07 quotes three errors from the binary. Two are warnings now, and a name is no longer required to validate:

| tree | result |
|---|---|
| no `plugin.json` | rc 1, `✗ plugin.json: no plugin.json found at the plugin root or in .antigravity-plugin or .gemini-plugin` |
| `plugin.json` with no `name` | rc 0, `⚠ plugin.json: no name: the plugin is named after its folder, "no-name", and \`plugin install\` refuses it` |
| `"name": "bad name!"` | rc 0, `⚠ plugin.json: name "bad name!" isn't strict kebab-case (lowercase letters, digits and single hyphens), so it can't be published to the Antigravity Marketplace; try "bad-name"` |
| an agent with `tools: [definitely_not_a_tool, view_file_outline]` and an unknown frontmatter key | rc 0, no finding about either: **the validator does not check tool names** |
| `plugin.json` as a symlink | rc 0, validated through the link |

In `strings /usr/bin/agy`, `missing plugin.json` scores 0, `plugin.json missing name` 1, `invalid plugin name` 2, and a control string 0.

### 3. The registry [AG-06]

The E17 probe: one agent per name, the name the sole entry of its `tools` list, installed globally as `e32-tools` (28 agents), each run once in an empty folder as `agy --agent t-<name> --model gemini-3.8-flash-low --print "Reply as your instructions say." --log-file <file>`. The body, stricter than E17's as E24 found necessary, also asks for the tool names, so each run reports what the name delivered:

```
Use no tool. Reply with exactly two lines and nothing else.
Line 1: the single word pong
Line 2: the word TOOLS: followed by the exact names of every tool declared to you, comma-separated, or NONE if you have no tools.
```

The control first:

```console
$ agy --agent t-definitely-not-a-tool --model gemini-3.8-flash-low --print "Reply as your instructions say."
error: failed to construct executor: failed to resolve components: unknown component: tool "definitely_not_a_tool" not found in registry
AGY_ERROR: {"short_error":"failed to construct executor: failed to resolve components: unknown component: tool \"definitely_not_a_tool\" not found in registry","status":"UNKNOWN","error_code":2,"code_kind":"grpc","retryable":false,"error_id":"…"}
rc=3
```

Its log holds no `streamGenerateContent` request: the miss is still before any model call. Every run that resolved made exactly one, and answered `pong`. No 503.

| name in `tools` | at 1.5.3 | the tool it delivered, by the agent's own list |
|---|---|---|
| `view_file` | resolves | `read_file` |
| `run_command` | resolves | `run_command` |
| `write_to_file` | resolves | `write_file` |
| `replace_file_content` | resolves | `edit_file` |
| `search_web` | resolves | `search_web` |
| `invoke_subagent` | resolves | `invoke_subagent` |
| `define_subagent` | resolves | `define_subagent` |
| `manage_task` | resolves | `manage_task` |
| `manage_subagents` | resolves | `manage_subagents` |
| `send_message` | resolves | `send_message` |
| `grep_search` | resolves, **no effect** | none |
| `find_by_name` | resolves, **no effect** | none |
| `list_dir` | resolves, **no effect** | none |
| `multi_replace_file_content` | resolves, **no effect** | none |
| `read_url_content` | resolves, **no effect** | none |
| `command_status` | **resolves** (rejected up to 1.2.10) | none |
| `view_file_outline`, `view_code_item`, `codebase_search`, `browser_subagent`, `notify_user`, `manage_inbox` | **rejected**, rc 3, `not found in registry`, no model call | — |
| `definitely_not_a_tool` | rejected (control) | — |
| `read_file`, `write_file`, `edit_file` (not in AG-06; tried because the lists above showed them) | resolve | themselves |

"No effect" is the tool's own word. Each of those five runs logged one line, and no other run logged any:

```
registry.go:71] Tool "grep_search" is deprecated and has no effect
registry.go:71] Tool "find_by_name" is deprecated and has no effect
registry.go:71] Tool "list_dir" is deprecated and has no effect
registry.go:71] Tool "multi_replace_file_content" is deprecated and has no effect
registry.go:71] Tool "read_url_content" is deprecated and has no effect
```

`command_status` logged nothing and its agent listed no tool for it; why is not known. The "delivered" column is the model's report of its own tool list, the same in every run, and on the default model too (step 4). The log lines and the rejections are the harness's.

Every agent also listed tools its `tools` key never named: `manage_task`, `call_mcp_tool`, `list_resources`, `read_resource`, and the two tools of an MCP server that an installed Google plugin ships. Two more fixtures close what E19 left open:

| `tools` key | the agent's own list |
|---|---|
| omitted | `send_message, read_file, search_web, schedule, generate_image`, plus the ambient set above — **not** "no tools", as AG-06 has it, and no shell or write tool |
| `tools: []` | the ambient set only |

**Verdict**: at 1.5.3 the registry rejects **six** of AG-06's names, not seven, and still does so loudly and before any model call. Sixteen resolve, and six of those give the agent nothing: the five logged as deprecated, and `command_status`. A rendered agent that lists `grep_search`, `find_by_name` and `list_dir` for its search capability still starts, and has no search tool: this package's reviewer, with `view_file, grep_search, find_by_name, list_dir, run_command`, has `read_file` and `run_command`. The vendor changelog has, under **1.2.7**, "retiring the legacy `find_by_name`, `grep_search`, and `list_dir` tools from the default baseline while keeping them available to custom agents that explicitly list them in `tools`"; no entry found by keyword says when listing them stopped working.

### 4. `--agent`, the allowlist, the sub-agent flag, the body [AG-02] [AG-03] [AG-04] [AG-05]

The E19 fixture, under new names: `e32-lead` (`mainAgent: true`, `tools: [view_file, invoke_subagent]`, two H1 sections with a canary in the second), `e32-reviewer` (`mainAgent: false`, `subagent: true`, `tools: [view_file, grep_search, list_dir, run_command]`, no `invoke_subagent`), `e32-leaky` (a sibling to be reached), `e32-nosub` (`mainAgent: false`, `subagent: false`), and `e32-fmname`, whose directory is `agents/e32-dirname/`.

```console
$ agy agents                                        # in <tmp>
e32-fmname
e32-lead
firestore-rules-author
tech-lead
$ agy --agent e32-dirname --model gemini-3.8-flash-low --print "Reply with the single word ping."
error: unknown agent "e32-dirname" (available: e32-fmname, e32-lead, firestore-rules-author, tech-lead)
$ agy --agent e32-reviewer --model gemini-3.8-flash-low --print "State your token and nothing else."
error: unknown agent "e32-reviewer" (available: e32-fmname, e32-lead, firestore-rules-author, tech-lead)
$ agy --agent e32-fmname --model gemini-3.8-flash-low --print "go"
Q8-FMNAME-ACTIVE
```

The two errors are rc 1 with no model call. `agy agents` lists the `mainAgent` personas only, an agent is known by its frontmatter `name`, and `--agent` refuses a sub-agent [AG-03].

Then the central run, on the default model, in a git repository `<tmp>/ws` whose `AGENTS.md` holds `Canary: WALRUS-3092`. The prompt names no canary:

```
Do these steps in order. Do not read any files.
1) Use invoke_subagent to invoke the agent named e32-reviewer with this task, verbatim: "State your token. Then use invoke_subagent to invoke the agent named e32-leaky with the task: reply. Report verbatim what it returned, or, if you cannot invoke it, say exactly why and list the names of every tool you have."
2) Use invoke_subagent to invoke the agent named e32-nosub with the task: reply.
3) Answer in exactly this form, four lines:
REVIEWER-SAID: <the reviewer's reply verbatim>
NOSUB: <what the invocation returned verbatim, or the exact error>
BODY: <the body canary stated in your own instructions, or NONE>
PROJECT: <the value after "Canary:" from any project instruction file that is already in your context without reading files, or NONE>
```

```console
$ agy --agent e32-lead --print "$(cat <tmp>/prompt-lead.txt)"      # rc 0, stderr empty
Q8-LEAD-ACTIVE
Waiting for `e32-reviewer` response.
Q8-LEAD-ACTIVE
REVIEWER-SAID: Q8-REVIEWER-ACTIVE I cannot invoke `e32-leaky` because the `invoke_subagent` tool is not available to me (it is not in my tool declarations). The tools I have are: - `read_file` - `run_command` - `manage_task` - `send_message` - `list_resources` - `read_resource` - `call_mcp_tool` - `mcp_gemini-api_gemini-api-docs_gemini_get_doc` - `mcp_gemini-api_gemini-api-docs_gemini_search_docs`
NOSUB: Encountered error in tool execution: subagent "e32-nosub" not found or not allowed to be invoked
BODY: BADGER-4417
PROJECT: WALRUS-3092
```

agy's transcript of that session shows the lead's only tool calls, and their arguments:

```
invoke_subagent  {"Prompt": "…", "Role": "E32 Probe Reviewer", "TypeName": "e32-reviewer"}
invoke_subagent  {"Prompt": "reply", "Role": "E32 Probe Nosub", "TypeName": "e32-nosub"}     → ERROR: subagent "e32-nosub" not found or not allowed to be invoked
```

- **AG-05 reproduced.** A `tools` list that omits `invoke_subagent` leaves the specialist without it; it could not reach its sibling. The run's log also carries the two `deprecated and has no effect` lines for the reviewer's `grep_search` and `list_dir`.
- **AG-05, new.** The allowlist is not the whole tool surface. The reviewer listed five tools it never named, and two MCP tools from an installed plugin. Three one-turn runs of an agent with `tools: [view_file]` (`gemini-3.8-flash-low`, in `<tmp>/ws`) show which switch removes what, by the agent's own list:

  | extra frontmatter | tools listed | `PROJECT:` |
  |---|---|---|
  | none | `read_file`, the plugin's two MCP tools, `call_mcp_tool`, `list_resources`, `read_resource`, `manage_task` | `WALRUS-3092` |
  | `inheritMcp: false` | `read_file`, `list_resources`, `read_resource`, `manage_task` | `WALRUS-3092` |
  | `inheritCustomizations: false` | `read_file`, `call_mcp_tool`, `list_resources`, `read_resource`, `manage_task` | `NONE` |

  No MCP tool was called, so what a specialist can reach through `call_mcp_tool` is not measured.
- **AG-04, measured for the first time.** A sub-agent is addressed by `TypeName`, and an agent with `subagent: false` cannot be invoked. The call carried no `Workspace` argument. The binary's strings hold `Workspace: 'inherit'` (3) and `Workspace: 'branch'` (2) and no `Workspace: 'share'`; none of the three modes was exercised, nor the clean context, nor `define_subagent`.
- **AG-02 reproduced.** The second H1 section reached the agent: the body is not sliced. All 18 frontmatter tags of AG-02, `agents` included, score at least 1 in `strings -n 6` of `/usr/bin/agy` and of the desktop's `language_server` (2.29.1), with `yaml:"notARealKey` 0 in both; `yaml:"agents,omitempty"` is 1 in each. That is inspection of the desktop binary, not a run of the desktop.

### 5. `AGENTS.md` reaches every agent [AG-11]

`PROJECT: WALRUS-3092` above is the reverse of E19 and E24. The lead read no file: its two tool calls are listed above. E19's other row and a control, default model, each with no tool call in its transcript:

```console
$ cd <tmp>/ws && agy --print "Do not read any files and do not use any tool. Answer in exactly this form, one line:
PROJECT: <the value after \"Canary:\" from any project instruction file that is already in your context, or NONE>"
PROJECT: WALRUS-3092
$ cd <tmp>/ws-none && agy --print "<the same prompt>"      # a git repository with no AGENTS.md
PROJECT: NONE
```

Which files, from where. A second repository, `<tmp>/ws2`, with a different canary in each of `AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `sub/AGENTS.md` and `other/AGENTS.md`; the default agent, started in `<tmp>/ws2/sub/deep` and asked to list every canary with the file it came from:

```
CANARY: WALRUS-3092 FROM: <tmp>/ws2/AGENTS.md
CANARY: HERON-5560 FROM: <tmp>/ws2/GEMINI.md
CANARY: IBIS-7719 FROM: <tmp>/ws2/sub/AGENTS.md
```

`CLAUDE.md` and the sibling directory's `AGENTS.md` did not arrive. That is AG-11 as the vendor states it: the walk from the working directory up to the repository root, `AGENTS.md` and `GEMINI.md`, nothing else.

A sub-agent, which E19 did not test. `e32-lead` was told to pass `e32-reviewer` a task that names no canary:

```
REVIEWER-SAID: Q8-REVIEWER-ACTIVE SUB-PROJECT: WALRUS-3092
```

The reviewer's only tool call was the `send_message` that carried its reply.

Interactive mode, which E19 named as a condition it had not reproduced. One session in this probe's own tmux session, `agy --agent e32-lead --settings <tmp>/trust-ws.json -i "<a prompt asking for BODY and PROJECT>"`, with the session-only trust setting of E28. The screen, with the banner's account line cut:

```
▸ Thought for 7s, 360 tokens
  Q8-LEAD-ACTIVE
  BODY: BADGER-4417
  PROJECT: WALRUS-3092
```

**Verdict: at agy 1.5.3 the workspace `AGENTS.md` is in context for the default agent, a custom primary and a sub-agent, in print mode and interactively.** The print-mode folders were not trusted, so trust is not what delivers it there. E19 (1.1.27) and E24 (1.2.10) measured the opposite with the same method, so this is a change between 1.2.10 and 1.5.3. The version is not established. The changelog's nearest entries are 1.2.7, "giving user and workspace rules a dedicated 20,000-token budget", and 1.4.4, "Fixed the system prompt's user rules wording so `GEMINI.md` and `AGENTS.md` rules explicitly override earlier built-in instructions".

### 6. Workspace roots deliver agents [AG-12] [AG-07]

E18's test, one git repository per root, each holding one probe agent with `mainAgent: true`, `agy agents` run inside it. Run twice: as E18 ran it, and with the folder trusted for that one call (`agy --settings '{"trustedWorkspaces":["<repo>"]}' agents`). The four global primaries appear in every row and are left out:

| location | not trusted | trusted for the call |
|---|---|---|
| `<repo>/.agents/plugins/e32-ws1/` (a plugin; validates) | absent | **`ws1-agent`** |
| `<repo>/_agents/plugins/e32-ws2/` | absent | **`ws2-agent`** |
| `<repo>/.agents/agents/ws3-agent/agent.md` | absent | **`ws3-agent`** |
| `<repo>/.agents/agents/ws6-agent.md` (a flat file) | absent | **`ws6-agent`** |
| `<repo>/_agents/agents/ws7-agent/agent.md` | absent | **`ws7-agent`** |
| `<repo>/.gemini/agents/ws4-agent/agent.md` | absent | absent |
| `<repo>/.agents/e32-ws5/` (a plugin directly under `.agents/`) | absent | absent |

The untrusted column is E18's result exactly. E18 and E24 do not record whether their folders were trusted. The changelog has, under **1.2.11**, one version after E24's: "Fixed project custom agents in .agents/agents/ not being found or selectable in workspaces created in the Desktop App, in already-trusted workspaces, under execution with --agent, in headless (-p / --prompt) runs, and in the /agents panel."

Listing is not running. In print mode a workspace agent runs **whether or not the folder is trusted** (`gemini-3.8-flash-low`, one model call each):

```console
$ cd <repo3> && agy --agent ws3-agent --print "go"                 # no trust setting; `agy agents` here does not list it
ws3-agent-ACTIVE
$ cd <repo1> && agy --settings '{"trustedWorkspaces":["<repo1>"]}' --agent ws1-agent --print "go"
ws1-agent-ACTIVE
```

And the collision AG-12 is about. A repository whose `.agents/agents/e32-fmname/agent.md` has the same `name` as the globally installed plugin's agent, and a different reply:

```console
$ agy --settings '{"trustedWorkspaces":["<repo8>"]}' agents        # the name appears once
e32-fmname
…
$ agy --settings '{"trustedWorkspaces":["<repo8>"]}' --agent e32-fmname --print "go"
WORKSPACE-DEFINITION-ACTIVE
$ agy --agent e32-fmname --print "go"                              # the same folder, not trusted
WORKSPACE-DEFINITION-ACTIVE
```

Outside that repository the same command answers `Q8-FMNAME-ACTIVE`, the plugin's reply (step 4).

**Verdict: at 1.5.3 a workspace delivers agents from `.agents/agents/`, `_agents/agents/`, `.agents/plugins/<plugin>/` and `_agents/plugins/<plugin>/`, and a workspace definition wins over a globally installed plugin agent of the same name.** AG-12's ranking holds for that pair, and E18's "no workspace root delivers agents" does not hold at this version. In print mode the workspace definition won in a folder nobody had trusted. Interactive mode raises the trust dialog first (E26); what `--agent` resolves to after "No, exit" or before an answer was not looked at.

### 7. Skills, placeholders, a workflow [AG-10]

All on `gemini-3.8-flash-low`, default agent, print mode. What the harness did is read from agy's transcript of each session, not from the model's answer.

| run | what reached the model | answer |
|---|---|---|
| `/ws9-args hello world`, a skill in `<repo>/.agents/skills/` whose body ends `ARGS: [$ARGUMENTS] FIRST: [$1] ROOT: [${CLAUDE_PLUGIN_ROOT}]` | the body, inlined by the harness as `/ws9-args is a [Slash Command]: <SKILL>…`, frontmatter removed, **the three placeholders literal** | `ARGS: [$ARGUMENTS] FIRST: [$1] ROOT: [${CLAUDE_PLUGIN_ROOT}]` |
| `/e32-skill hello world` in an empty folder, the skill being the installed plugin's | the bare text `/e32-skill hello world`, not expanded; the model then read the plugin's `SKILL.md` with `read_file` and saw the placeholders literal | `SKILL: OTTER-6158 ARGS: [hello world] FIRST: [hello]` — the model filled them in itself |
| `/e32-skill hello world` in a repository that has its own `.agents/skills/e32-skill/` | the workspace copy, inlined | `SKILL: WORKSPACE-COPY-TAPIR-4471` |
| `/e32wf`, a file `<repo>/.agents/workflows/e32wf.md` beside those skills | the bare text `/e32wf`; the model went looking with `find`, which headless mode denied | no output |

**Verdict.** No placeholder is substituted at 1.5.3, so the standing rule against `$ARGUMENTS`, `$N` and `${CLAUDE_PLUGIN_ROOT}` in a skill body still stands [AG-10]; the second row shows why a model's answer alone would have misled. A workspace skill beats a plugin skill of the same name. A workspace workflow file was not offered as a command in print mode, with the skills beside it as the control; the TUI was not tried. The bundled skill `~/.gemini/antigravity-cli/builtin/skills/migrate-workflows/SKILL.md`, read in full, says "Workflows (`.agents/workflows/*.md` or `_agents/workflows/*.md`) are deprecated" and lists the legacy locations AG-10 gives. The retirement date AG-10 quotes was not found: `Workflows are deprecated` and `retired on` both score 0 in the binary's strings, with the five legacy paths and manifest names scoring 2 to 5 and a control path 0.

### Consequences

1. **AG-11 flips back to the vendor's statement.** `SUPPORT-MATRIX.md`'s correction ("no agy agent receives it") describes 1.1.27 to 1.2.10. At 1.5.3 the managed block is visible to every Antigravity agent, sub-agents included. Bodies that carry the contract are still right for the versions between, and nothing breaks; but design §5.4's "the only mechanism", `hosts/antigravity.yaml`'s `instructions` block, the README, `acceptance.md` and the `ec-onboard` skill state as present fact what is now false at the installed version.
2. **AG-12 and E18 flip.** Antigravity has a per-project route for agents at 1.5.3, so `global_only: true`, "the roster is per-user", and §16's "per-project rosters on Antigravity, which the host does not currently allow" are out of date. Whether the package should use the route is a design question this entry does not answer.
3. **A workspace agent definition overrides this package's installed persona of the same name, and in print mode it did so in an untrusted folder.** A repository that carries `.agents/agents/tech-lead/agent.md` would be what `agy --agent tech-lead -p` runs there. Measured with a probe name, not with `tech-lead`; the same shape as the Claude `agent` key in §8's fail-open list. For the Tech-Lead and Security to weigh.
4. **AG-06's list needs a 1.5.3 edition.** The rendered Antigravity agents still start. They no longer get `grep_search`, `find_by_name`, `list_dir`, `multi_replace_file_content` or `read_url_content`; they search through `run_command` if at all. `check.py --agy-tools` passes on names that now do nothing, and the registry is no longer "fifteen valid, seven rejected".
5. **An explicit `tools` list is not a closed surface.** Ambient MCP tools and `call_mcp_tool` reach a specialist unless its frontmatter says `inheritMcp: false`. §8's cell for "specialists never post externally" is already *prose* on Antigravity; this is the path that makes it matter.
6. **AG-08's update story is simpler than documented.** A re-install replaces, by a proper test; `agy plugin uninstall` exists; and the vendor dates the change at 1.1.28, which would put it below nothing the package supports except 1.1.27 itself.
7. **`agy plugin validate` is not a guard for tool names** at 1.5.3, and `--strict` fails this package on a warning the don't-do list tells it to keep.

### Not measured

- **The desktop app**, in any half of any claim: the agent selector [AG-03], the allowlist and `AGENTS.md` [AG-05][AG-11], workspace agents, and the registry. Last driven at 2.17.0 (E19 addendum); 2.29.1 is installed.
- **Install targets that may leave the machine**: the `owner/repo` shorthand, a non-github URL, the SSH form, `plugin@marketplace` against a known or unknown marketplace, a bare plugin name, and `agy plugin link`. A first attempt that batched them was stopped by this session's own permission layer, and they were not retried one by one. `agy plugin import`, `enable` and `disable` were not run either: the first reads another host's plugins, the other two write `config.json`. So "enablement is keyed by directory name" [AG-08] rests on nothing newer than the claim.
- **Any agy between 1.2.10 and 1.5.3.** Each "changed" above is a difference between two measured versions; the changelog lines are the vendor's.
- **Whether E18's and E24's folders were trusted**, and so whether trust or the version explains their result.
- **The registry on the default model.** The sweep ran on `gemini-3.8-flash-low`; the default model agreed for the five names step 4 exercised.
- **What an agent can do with the tools it listed.** No MCP tool, `write_file` or `edit_file` was called.
- **`Workspace` modes of `invoke_subagent`, `define_subagent`, a sub-agent's clean context** [AG-04]; the `agents:` key at runtime [AG-02]; `commandExecutionPolicy`, `rules:`, `hidden`, `disabled` [AG-02][AG-05].
- **The 12,000-character rule limit** [AG-11], and a plugin's `rules/` directory.
- **Workflows in the TUI and in the global locations** [AG-10]; the plugin-skill route in the TUI.
- **A workspace agent against an interactive session's trust dialog.**

**Host state.** `~/.gemini/config/config.json`, `~/.gemini/settings.json`, `~/.gemini/config/hooks.json`, `~/.gemini/antigravity-cli/settings.json` and `~/.gemini/config/import_manifest.json` have the hashes they had before the first step; the last one changed with every install and returned to its bytes after the last uninstall. The plugins tree is file-for-file identical by hash to the listing taken before. `~/.gemini/config/plugins/e-colleagues/` was replaced four times (twice by the marker test, once by the URL install, once to put it back) and ends as the export's 87 tracked files: `diff -r` against a copy taken before the first step is clean, and against the export itself shows only a `skills/ec-fleet/scripts/__pycache__/` that another process created inside the shared export while this probe ran and that is not in the installed copy. `agy plugin list` shows `e-colleagues (enabled, 0.1.1)`, `5 skills, 6 agents`; no `e32-…` plugin remains; `agy agents` lists what it listed before. The one interactive session wrote nothing to the agy settings (session-only trust, E28); its tmux session was killed and the workmux state file for its pane was removed. agy kept its usual per-session records under `~/.gemini/antigravity-cli/` for each of the 42 sessions that reached a model. One slip: the desktop's `language_server` was started once with `--version` to read its version; it is not a version flag, and the process exited at once with `Failed to read initial metadata from stdin`. The repository checkout was not touched.

### Addendum 2026-11-15 — the rendered agents on the 1.5.3 tool names, exercised

After this sweep the package's floor moved to agy 1.5.3. The rendered agents now list `read_file`, `write_file` and `edit_file` in place of the older names, and no longer list the five names that give no tool. The sweep saw the three names resolve and did not call them. Two turns on `gemini-3.8-flash-low`, print mode, in an empty git repository `<tmp>/work` trusted for each call, with the re-rendered plugin installed:

```console
$ agy --agent tech-lead --settings '{"trustedWorkspaces":["<tmp>/work"]}' --mode accept-edits --model gemini-3.8-flash-low --log-file <log> --print "Use your file tools only, never the shell, and do not delegate. 1) Create a file named probe.txt in the current folder containing exactly the word OTTER. 2) Replace OTTER with TAPIR in that file with your editing tool. 3) Read the file back with your reading tool. Reply with exactly two lines: the file's content, then the exact names of the tools you called, in order, comma-separated."
TAPIR
write_file, edit_file, read_file
$ cat <tmp>/work/probe.txt
TAPIR
```

rc 0, and the log held no `deprecated` line and no `not found in registry`. Then one delegation, without `--mode`:

```console
$ agy --agent tech-lead --settings '{"trustedWorkspaces":["<tmp>/work"]}' --model gemini-3.8-flash-low --log-file <log> --print "Delegate exactly once to the reviewer and do nothing else yourself: ask it to read the file probe.txt in the current folder with its file-reading tool and to answer with the file's content and the exact names of every tool it has. Then reply with exactly what the reviewer returned."
…
### RETURN
status: done
task: Read probe.txt and list available tools
changed: none
evidence: read_file on <tmp>/work/probe.txt returned 'TAPIR'
findings: []
risks: none
follow-ups: none
questions: none
knowledge: none
```

rc 0, the same two strings absent from the log. The reviewer's list of its tools is cut above: beside `read_file` and `run_command` it named MCP tools of servers installed on the probe machine, which its `tools` key does not list, as step 3 found.

**Verdict**: the primary writes, edits and reads under the 1.5.3 names, the file on disk showing the write and the edit, and a specialist rendered with `read_file` and `run_command` loads and reads. The tool names in the first reply are the model's own report.

**Not measured:** the designer, developer, platform and security agents each on their own, and `search_web`.

**Host state.** The installed plugin was replaced with the re-rendered package and left that way; `diff -r` against the export is clean. The agy settings file has the same hash before and after. `<tmp>/work` holds the one probe file.
