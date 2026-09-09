---
name: ec-onboard
description: Learn this project from every angle the roster covers — index what it already documents, audit only the gaps, and record provenance so staleness is detectable. Use after ec-init, or when the team's knowledge of a project has gone stale.
---

# ec-onboard

`ec-init` owns the contract, which must be interviewed. This owns the **knowledge**, which is
derivable from the repository — so it is audited, never asked.

## 1. Inventory, read-only

Stack, manifests, CI configuration, test layout, directory shape. Touch nothing.

## 2. Index what already exists, first

Read the README, `docs/`, any ADRs, CONTRIBUTING and an existing `AGENTS.md`, and map each
lens to its existing home. **A lens the project already documents is indexed, not authored.**
A pointer beats a copy, because a copy goes stale silently and nothing says so.

## 3. Present the gap list and the roster together

Show which lenses have a home, which are gaps, and the roster you propose to cover them.
**The user approves both before any file is written.**

## 4. Dispatch one specialist per gap lens, in waves

Delegate each gap lens to the persona that owns it. Every brief is a full delegation brief
and names the files to read; knowledge is never assumed to arrive ambiently, which is
measured — on Antigravity `AGENTS.md` reaches no agent at all.

**Size the waves.** On Codex the concurrency cap counts the primary, so the default of 4
permits **three** spawned children, and a fourth is **refused** — `collab spawn failed: agent
thread limit reached` — not queued. Six lenses is two waves. Treat that error as a wave
boundary and retry the lens in the next wave; it is not a failure of the lens. If the project
sets `[agents] max_concurrent_threads_per_session`, size the wave to that minus one instead.

## 5. Consolidate

You, the Tech-Lead, write the files — the specialists return findings. For each lens, run the
script beside this file:

```
# a lens the project has no home for
python3 scripts/knowledge.py <root> --lens <lens> --persona <persona> \
    --paths <comma-separated paths that were read> --body-file <file>

# a lens the project already documents
python3 scripts/knowledge.py <root> --lens <lens> --persona <persona> --index-only <where>
```

`--paths` is mandatory for an authored lens, because staleness is computed from it. Record
the paths actually read, not the paths you hoped to read. Inside a file, cite the path each
non-obvious claim came from.

The script writes the file with its provenance, updates the index row in `AGENTS.md`, and
records the lens in `lock.json` — so an interrupted pass resumes instead of restarting.

## 6. Report

What was found, what was authored, what was left to the project's own documentation, and what
stayed uncertain. Name anything you marked `confidence: low` and say why.
