---
name: ec-fleet
description: Run several tech-leads at once, one per issue, each in its own git worktree and terminal window. Start them, and see in one table which are working and why each stopped. Also the rules a tech-lead follows when it was started this way, or told to load this skill with an assignment. Needs workmux.
---

# ec-fleet

Each tech-lead asks and waits in its own session, and the person answers there.

## Which part applies

If you were given an assignment (your start prompt says "Your assignment: issue <ref>", or
the person told you "plan"), follow it under **Your assignment**. An issue tech-lead ignores
**Dispatching**. A plan tech-lead also uses it: to start the issues the person picks, and for
the overview. With no assignment, you are the dispatching session.

Whichever part applies, read `AGENTS.md` first if it is not in context.

## Dispatching

### Start

From the project's directory, run the script beside this file by its full path, once per
issue the person names:

```
python3 scripts/fleet.py start <reference>
```

- Pass `--host` only when the person names a host. If the script then says `no host chosen`,
  run it again with your own: `antigravity`, `codex`, `opencode` or `claude`.
- Pass `--base` (what to branch from) only when the contract or the person gives it.
- Pass `--name` when the person gives a name. Otherwise, if the contract has a naming line,
  build the name from it, with no spaces, and pass `--name`. Leave it out, and the script
  names the worktree from the reference (`12` becomes `issue-12`), only when there is no
  naming line, or the line needs the issue's title and you cannot read the tracker.

It prints `started <name>` once the session is listed. `opened <name>, host not confirmed`
means it is not: the host exited, or it waits at a first-run prompt such as a trust question.
Say so, and show any `fleet:` line. If it fails any other way, show its message; do not
retry with other flags.

Where it can, the script trusts the new worktree for that one session; otherwise the person
answers there. You never answer it. Until then that session reads `working` or
`no RETURN block on screen`, or has no row.

### Overview

```
python3 scripts/fleet.py overview
```

Show the table as printed; `--json` gives rows as data. One row per session:

- `working`: leave it alone. On some hosts a session at a first-run prompt or an approval
  also reads `working`; say that it may be.
- `waiting`: it is at one of its host's approvals, or just past one. The person answers there.
- Any other state means it stopped. `RETURN` and `QUESTIONS` come from its last RETURN block:
  why it stopped, and what it needs.
- `no RETURN block on screen`: the session may be at one of its host's own prompts, or it
  stopped without a complete block in view. Say so.
- `could not read its screen`: capture failed. Say so.
- `(this session)`: your own row.

### What you never do

Never send text or keys to another session. Never answer a tech-lead's question or approve
anything for the person, a host's own prompt included. The person answers in that session,
in its window or through that host's remote feature.

## Your assignment

### issue

You work on one issue, in its own worktree.

1. The issue is your brief. Read it yourself, with the tools the contract names.
2. The person picked this issue: that is their approval to implement what it describes. T1
   still applies to anything beyond its scope, to writing `AGENTS.md`, and to restricted
   actions.
3. When you need the person, ask in this session and wait. Never guess and carry on.
4. Every time you stop, end your message with the RETURN block below in a code fence, its
   keys unchanged and in this order, each filled in for this stop: under `questions`, the
   decision you need or `ready to push`. The overview reads only what is visible on your
   screen, and only a complete block from `### RETURN` through `knowledge:`. So give every
   key, put the block at the very end with nothing after it, and keep it short enough to fit
   on one screen. It is your own block; relay your specialists' blocks as T5 says.
5. Do not push unless the contract grants pushing to your role (R6). Otherwise finish
   everything else, then stop with `ready to push`.
6. After a push, open the change request if the contract grants that, then stay in this
   session. Act on review feedback or a failed pipeline when the person tells you; do not poll.
7. Record follow-ups, your specialists' included, under the heading `## Follow-ups` in your
   change request's description, or on your issue where the contract allows, so they outlive
   the worktree. Create follow-up issues only if the contract allows it. Where the contract
   lets you post nothing, list them under `follow-ups` in your final RETURN block; the person
   carries them on.

### plan

You work in the main checkout. The person starts you there; dispatch does not.

1. Groom, brainstorm, research, suggest what to take next, and create or edit issues when the
   person asks.
2. Write no file in the checkout, and delegate no work that would. Plans go where the
   contract says plans live, in the project's own management system. A document that belongs
   in the repository becomes an issue and is written in a worktree. This is trusted to you.
   It does not cover `ec-init` and `ec-onboard`, which the person invokes and which write at
   the project root.
3. Collect follow-ups: find the `## Follow-ups` heading in open and recently merged change
   requests and their issues, merge duplicates, and propose issues. The person picks.
4. Before you answer a question about the whole fleet, such as "can we release?", run the
   overview.

### One voice per assignment

T1 to T6 still apply. With several tech-leads, each is the one voice and poster for its own
assignment: an issue tech-lead posts only on its own issue and change request, a specialist
only where the contract grants it.

## The contract

The lines this skill uses are under **Parallel work** in the project bindings of `AGENTS.md`.
Where a line is absent, its default applies, and a start never fails for it: the name comes
from the reference unless the person gives one; plans go to the tracker the contract names,
and if it names none, ask; post nothing the contract does not already grant; record
follow-ups, do not create issues; stop at `ready to push`.

## The RETURN block

```
### RETURN
status: done | partial | blocked | needs-decision
task: <reference as delegated>
changed: <files, branch, MR/issue refs, or none>
evidence: <commands run, exit codes, output excerpts>
findings:
  - severity: blocking | nit
    path: <file, or "-" for a whole-change finding>
    line: <number, or "-">
    body: <the comment, written to be posted verbatim>
risks: <unresolved>
follow-ups: <suggested delegations for the Tech-Lead>
questions: <decisions only the user can take>
knowledge: <lens file this run would add or change, or none>
```

## The config

With no config file the launcher is workmux and each host uses its default start command;
only that setup is tested. workmux must be installed, with its status hooks set up
(`workmux setup`) for each host you start: the overview's states come from them. An optional
TOML file, `~/.config/e-colleagues/fleet.toml` (or under `XDG_CONFIG_HOME`) or
the path in `EC_FLEET_CONFIG`, can set `default_host`, each host's `start` and `trust`
(`trust = ""` for none), and the launcher's commands.
