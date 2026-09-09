---
name: ec-status
description: Report the team's contract health — roster, lens coverage, and which knowledge files have gone stale since the commit they were derived from. Use to check whether an onboard is still current before relying on it.
---

# ec-status

Run the script beside this file:

```
python3 scripts/status.py <project-root>
```

Add `--fail-on-stale` in CI to make a stale lens a build failure.

## What it tells you

Staleness is a `git diff`, not a heuristic. Each knowledge file records the commit it was
derived from and the paths that were read, so a lens is stale exactly when one of those
recorded paths changed since that commit. A change elsewhere in the repository leaves it
fresh, which is the point.

Four states per lens:

- **fresh at `<commit>`** — no recorded path has changed
- **STALE since `<commit>`** — the changed paths are listed; re-run `ec-onboard` for that lens
- **indexed -> `<path>`** — the project documents this itself; there is nothing to go stale
- **not audited** — no pass has covered it yet

Two states mean the question cannot be answered rather than answered "no":

- **commit unreachable** — the baseline commit is gone (rebase, squash, shallow clone).
  Re-audit to re-baseline.
- **PROVENANCE MISSING** — the file has no frontmatter. Treat it as unknown, never as fresh.

## What it does not do

It does not refresh anything. Refreshing is `ec-onboard` for the named lens, and it needs the
user's approval like any other write.
