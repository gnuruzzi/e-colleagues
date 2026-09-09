# e-colleagues


<!-- e-colleagues:begin v=0.1.0 profile=library -->
## E-Colleagues

| Colleague | Signature | Spawn name |
|---|---|---|
| Tech-Lead | `👨‍💻 Tech-Lead:` | (primary) |
| Developer | `🛠️ Developer:` | developer |
| Reviewer | `🕵️ Reviewer:` | reviewer |
| Security | `🛡️ Security:` | security |
| Platform | `⚙️ Platform:` | platform |

The Tech-Lead delegates by spawning sub-agents of exactly these types: developer, reviewer, security, platform. Specialists never spawn.
Specialists never post externally: findings return to the Tech-Lead, who posts them.
If no Tech-Lead persona is active in this session, invoke the `ec-tech-lead` skill first.

<!-- e-colleagues:index -->
| lens | where it lives | derived from |
|---|---|---|
| architecture | docs/design.md (§§1-9) | — (the project's own) |
| build-and-test | AGENTS.md (Workflow and permissions) + tests/ | — (the project's own) |
| standards-and-coverage | docs/design.md §13 + tests/ | — (the project's own) |
| security-posture | docs/design.md §8 (enforcement matrix and fail-open risks) | — (the project's own) |
| design-system | — | not yet audited |
| ci-cd-and-infra | .github/workflows/check.yml | — (the project's own) |

<!-- e-colleagues:project-bindings -->
### Platforms and tools

Work is tracked in this repository only — there is no external board or issue tracker, and
the remote is not yet published. **The Tech-Lead therefore posts nowhere external**: findings
are reported to the user in the session. Do not invent a destination.

The decision record is `docs/design.md`; the evidence base is `docs/experiments.md` and
`docs/SUPPORT-MATRIX.md`. A claim in any of them carries a claim id or the word UNVERIFIED.

### Workflow and permissions

- Verify before claiming: `python3 tools/check.py`, `python3 tools/gen.py --check`, and
  `python3 -m unittest discover -s tests`. All three must pass before a change is reported done.
- Never hand-edit a generated tree (`dist/`, `skills/ec-tech-lead/`); change `personas/` and
  re-render. The drift gate will catch it either way.
- Commits use Conventional Commits with a milestone scope, e.g. `feat(m4): …`.
- Only the user may push, tag or publish. This repository is publish-ready by rule (D8):
  no absolute paths, no machine-specific assumptions, no private project names, no secrets.
- A gate that has never failed is not a gate. Prove a new check catches its failure before
  trusting a green run.

<!-- e-colleagues:end -->

A team of AI personas — tech-lead, developer, reviewer, security, designer, platform — packaged so one repository installs into OpenAI Codex CLI, Claude Code, opencode and Google Antigravity, bootstraps any project's operating contract with `ec-init`, and learns an existing project from six angles with `ec-onboard`.

**Status (2026-09-09): M0 complete bar two visual checks; M1–M5 met.** All six personas render into four host dialects from one source, behind a drift gate, five host gates and 43 tests. `docs/experiments.md` E4–E23 carries every verdict; `docs/SUPPORT-MATRIX.md` maps each claim id to the version it was last confirmed at. This repository runs on its own contract (`--profile library`). Next is **M6** (publish: acceptance.md, CHANGELOG, visibility flip). Read `docs/design.md` §0, §15 and §16. **E17 is the load-bearing correction**: seven Antigravity tool names AG-06 lists are not in the registry and abort the agent at startup. `hosts/antigravity.yaml` carries the 15 measured names and `check.py --agy-tools` enforces them; re-derive that list by running one agent per name at each supported version, never by grepping the binary.

## Working rules for this repository

- `docs/design.md` is the decision record. When you change a decision, change the document in the same commit. Every path, key, flag and command in it carries a claim id from `docs/research/facts-digest.md` or the word UNVERIFIED; keep that discipline in code comments and README text too.
- The eight **decisions of record** in design §0 are binding. Reversing one is a design change: update §0 and everything downstream of it in the same commit.
- Before writing generator or bootstrap code, run the M0 sweep from design §15 and record every outcome in `docs/experiments.md` with the exact command, the installed version and the raw output. An unknown with no entry there is still open, and no code may depend on it.
- Check installed tool versions first. Four of the five tools moved within a day of the research (see `docs/experiments.md` E2), so any claim carrying a version gate must be re-verified before it is relied on — E3 is an example of one that had already flipped.
- Generated trees (`dist/`, `agents/`, `skills/ec-tech-lead/`) are never hand-edited. `tools/gen.py` renders them from `personas/`; `tools/check.py --drift` must pass before any commit.
- `personas/` never contains a tool's vocabulary. Tool names, permission keys and spawn syntax live in `hosts/*.yaml`.
- This repository is **publish-ready**: no absolute paths, no machine-specific assumptions (no stow, no `pass`, no Arch), no private project names. `docs/research/` has been sanitized to `~`-relative paths for exactly this reason — keep it that way.
- Never write `~/.codex/config.toml` from any script here; Codex rewrites it itself and on the maintainer's machine it is deliberately untracked state. `~/.claude/settings.json` is a stowed, tracked file in the maintainer's dotfiles, so a user-scope Claude plugin install dirties that working tree by design.
- Secrets never reach a manifest, a fixture or a test. Not one token, not in an example.

## Standing don't-do list

- Do not hand-write any per-tool agent file; render it.
- Do not use `$ARGUMENTS`, `$N`, `!cmd`, `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}` in a skill body; only Claude expands them and the literal token reaches the other three models [CX-12][AG-10].
- Do not add `memory` to a read-only Claude agent; it re-enables Write and Edit [CC-07].
- Do not give the Claude tech-lead a `tools` allowlist; an allowlist strips every tool it does not name, including all MCP tools, `Skill` and `AskUserQuestion` [CC-09].
- Do not ship a plugin-root `settings.json` with an `agent` key; it would make every session of every user the tech-lead, and its precedence against a user's own `agent` key is undocumented [CC-10].
- Do not ship `rules/AGENTS.md` in the Antigravity plugin; the invariants are already compiled into every agent body [AG-05].
- Do not let a read-only persona be adopted as a skill in a thread that can write — that is the fail-open this redesign exists to remove (design §0 D7).
- Do not let a specialist post to an external platform; findings return to the tech-lead (design §0 D6).
- Do not run `/import codex` in a bootstrapped project; it appends a copy of AGENTS.md into CLAUDE.md [CC-14].
- Do not rely on the `agy plugin install` destination, on `agy plugin install <url>`, or on a second install overwriting the first, until Q11 and Q12 are answered [AG-08].
