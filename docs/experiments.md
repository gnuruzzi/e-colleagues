# Experiments

The record required by `AGENTS.md`: every unknown from `docs/design.md` §15, with the exact command, the installed tool version, the raw output, the verdict, and the design consequence. An unknown with no entry here is still open, and no code may depend on it.

Tranches are defined in design §15: **A** automated, **B** interactive (needs a TTY or a trust dialog), **C** re-verification of version-gated claims.

## Status

| # | tranche | unknown | status |
|---|---|---|---|
| Q1 | A | Claude ignores the Antigravity-format root `agents/` when the manifest lists files explicitly | open |
| Q2 | A | bare names in `Agent(...)`'s `subagent_type` resolve to plugin agents under `--agent` | open |
| Q3 | B | project `.claude/settings.json` `agent` key: trust-gated, precedence, unresolvable value | open |
| Q4 | A | Codex `O_NOFOLLOW`: symlinked role TOMLs fail at spawn | open |
| Q5 | A | Codex root-as-plugin marketplace entry `path: "./"` | open |
| Q6 | A | `agy plugin validate` / `install` on a tree carrying all three manifests | open |
| Q7 | B | opencode runtime: Tab and `@` menus, `default_agent`, subtask `ask`, AGENTS.md in task children | open |
| Q8 | B | Antigravity: `tools` allowlist versus ambient subagent inheritance, `tools: []`, H1 slicing, name collisions | open |
| Q9 | A | does a spawned Codex child re-run AGENTS.md discovery | open |
| Q10 | A | `-c developer_instructions=""` clears the project value for one session | open |
| Q11 | B | `agy plugin install <github-url>` syntax | open |
| Q12 | A | `agy plugin install <dir>` destination, and second-install behaviour | open |
| Q13 | B | a project-enabled plugin sourced `./`: auto-installed on trust, or external | open |
| Q14 | — | Codex read-only sandbox blocks network, so read-only specialists cannot post | **retired by design** (E1) |
| Q15 | A | Codex plugin cache layout, for locating the bundled bootstrap script | open |
| Q16 | A | V2 concurrency ceiling for the onboarding audit waves | open |
| Q17 | A | does `$ec-tech-lead` resolve from project skills in an untrusted clone | open |
| Q18 | C | agy 1.1.27 `agents:` frontmatter key | **settled** (E3) |
| Q19 | A | does the Codex read-only sandbox permit running the project's tests | open |
| — | C | installed versions versus research targets | **settled** (E2) |

---

## E1 — Q14 retired by design

**Date** 2026-09-07. **Not tested.**

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
