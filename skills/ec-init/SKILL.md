---
name: ec-init
description: Set up the e-colleagues operating contract in this project — propose a roster, interview the team for the bindings only a human knows, and write the managed block. Use when a project has no contract yet or its roster needs changing.
---

# ec-init

Establish the team's operating contract for this project. The contract is **interviewed, not
audited**: only a human knows the board, the labels, the branching rule and who may merge.
The knowledge that *is* derivable from the repository is a separate job — that is `ec-onboard`.

Work in this order and do not skip the approval step.

## 1. Read before asking

Read `AGENTS.md` if it exists, plus `README`, `CONTRIBUTING` and any `docs/` index. Never ask
for something the repository already states; confirm it instead.

## 2. Propose a roster from evidence

The catalog is tech-lead, developer, reviewer, security, designer and platform. Propose the
subset this codebase justifies, and say what each choice rests on:

- a UI framework or stylesheets in the manifests argues for **designer**; a project with no
  user interface should drop it
- a CI configuration, Dockerfile or infrastructure directory argues for **platform**
- tech-lead, developer and reviewer are the floor

Present the proposed roster and the reason for each inclusion and omission. **The user
approves it.** Do not proceed on assumption.

## 3. Interview for the bindings

Ask only what the repository cannot tell you, in one round, and accept "skip" for any of them:

- Where does work live — issue tracker, board, project id? Which labels mean ready, in
  progress, in review?
- Branching and commit conventions; who may merge, tag or push
- The commands for build, test and lint, if they are not already in the repository
- Where findings should be posted, and by which tool. If the answer is "nowhere", say so
  explicitly — the Tech-Lead then reports to the user only.

## 4. Write

Run the bootstrap script beside this file:

```
python3 scripts/bootstrap.py <project-root> --write
```

It writes exactly three things: the package region of `AGENTS.md`, a `CLAUDE.md` importing
it, and `.e-colleagues/lock.json`. Everything outside the markers belongs to the project and
is left alone. Then fill in the **Platforms and tools** and **Workflow and permissions**
headings under the project-bindings marker with the interview answers — that region is the
team's, and no future update rewrites it.

Use `--check` in CI or before an update; it exits non-zero when the file would change or when
`AGENTS.md` exceeds 30 KiB.

`--scope user` is a different job and writes no project file: it installs the personas for
this machine — the Codex role files and the tech-lead profile under `~/.codex/`, and the
opencode agents and these four skills under `~/.config/opencode/` — as real files for the
chosen profile.

## 5. Report

State the roster, where the block was placed, what the interview settled, and anything the
script printed as "action needed". If the budget check failed, say what must be trimmed —
do not work around it by shortening the managed block.
