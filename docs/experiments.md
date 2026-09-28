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
| Q7 | B | opencode runtime: Tab and `@` menus, `default_agent`, subtask `ask`, AGENTS.md in task children | **mostly settled** (E20, re-verified at 2.0.18 in its addendum); Tab and `@` menus still open |
| Q8 | B | Antigravity: `tools` allowlist versus ambient subagent inheritance, `tools: []`, H1 slicing, name collisions | **mostly settled** (E17–E19); desktop inheritance default still open |
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
| — | C | the 2026-09-27 snapshot: Claude 2.1.283, Codex 0.154.0, agy 1.2.10, desktop 2.17.0 | **settled** (E24); opencode 2.0.18 still open (#11) |

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

The **Antigravity desktop's** inheritance default (`inheritCustomizations`) is untested — it needs the desktop app, not the CLI. `tools: []` semantics were not isolated either, because the empty-list agent was superseded by the registry work; the practical answer is covered by AG-06's "an omitted `tools` list means no tools", which remains unverified for the empty-list case.

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
