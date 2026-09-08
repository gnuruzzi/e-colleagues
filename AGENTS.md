# e-colleagues

A team of AI personas — tech-lead, developer, reviewer, security, designer, platform — packaged so one repository installs into OpenAI Codex CLI, Claude Code, opencode and Google Antigravity, bootstraps any project's operating contract with `ec-init`, and learns an existing project from six angles with `ec-onboard`.

**Status (2026-09-08): M0 complete bar two visual checks; M1 and M2 met.** `docs/experiments.md` E4–E23 carries every verdict; `docs/SUPPORT-MATRIX.md` maps each claim id to the version it was last confirmed at. In place: `team.yaml`, `personas/`, `hosts/codex.yaml`, `tools/{gen,check}.py`, `skills/{ec-init,ec-tech-lead}`, `tests/` and CI. Generated: `dist/codex/`, `dist/team.json`, `skills/ec-tech-lead/`. Next is **M3** (`ec-onboard`, the knowledge store). Read `docs/design.md` §0, §15 and §16. **E17 supersedes E16's tool-list method**: seven Antigravity tool names AG-06 lists are not in the registry and abort the agent at startup, so `check.py --agy-tools` must validate against a list derived by running one agent per name, never by grepping the binary.

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
