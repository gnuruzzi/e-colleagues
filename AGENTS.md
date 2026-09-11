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
| security-posture | docs/design.md §8 (enforcement matrix) | — (the project's own) |
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

Six personas are authored once in `personas/` and rendered into four host dialects. Read `docs/design.md` §0 for the decisions that are binding, §15 for how a host fact gets established, and §16 for how to add a host or a persona. `docs/SUPPORT-MATRIX.md` resolves every claim id; `docs/experiments.md` is the evidence and outranks any claim it contradicts.

## Working rules for this repository

- `docs/design.md` is the decision record. When you change a decision, change the document in the same commit. Every path, key, flag and command in it carries a claim id resolved in `docs/SUPPORT-MATRIX.md` or the word UNVERIFIED; keep that discipline in code comments and README text too.
- The eight **decisions of record** in design §0 are binding. Reversing one is a design change: update §0 and everything downstream of it in the same commit.
- Probe before you build. Anything a host does that the code will depend on gets an entry in `docs/experiments.md` with the exact command, the installed version and the raw output. An unknown with no entry there is still open, and no code may depend on it. Design §15 describes the method.
- Check installed tool versions first. Four of the five tools moved within a day of the research (see `docs/experiments.md` E2), so any claim carrying a version gate must be re-verified before it is relied on — E3 is an example of one that had already flipped.
- Generated trees (`dist/`, `agents/`, `skills/ec-tech-lead/`) are never hand-edited. `tools/gen.py` renders them from `personas/`; `tools/check.py --drift` must pass before any commit.
- `personas/` never contains a tool's vocabulary. Tool names, permission keys and spawn syntax live in `hosts/*.yaml`.
- This repository is **publish-ready**: no absolute paths, no machine-specific assumptions, no private project names, no secrets. It is public, so assume every file is read by a stranger with no context.
- Never write `~/.codex/config.toml` from any script here; Codex rewrites it itself, and it mixes real settings with state the tool writes (trust decisions, nag counters), so it is machine-local by nature. `~/.claude/settings.json` may itself be a tracked file in someone's dotfiles, so a user-scope Claude plugin install can dirty that working tree — expected, not a bug.
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
