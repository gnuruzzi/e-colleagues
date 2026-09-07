# Handoff and provenance

Where to pick up, what exists, and how far to trust the facts underneath the design.

Superseded by `docs/design.md` revision 3: the name decision (now D1), the four gating experiments (now §15 tranche A), the build order (now §16), and the facts-that-shape-the-code list (now distributed through §§3–9 with claim ids). This file keeps what the design does not: read order, what exists on disk today, and research provenance.

## Read order

1. `docs/design.md` §0 (decisions of record) and §1 (summary).
2. `docs/design.md` §15 (the M0 sweep) and §16 (milestones) — that is the work queue.
3. `docs/experiments.md` before relying on anything version-gated. An unknown with no entry there is still open.
4. `docs/research/facts-digest.md` whenever a decision needs a fact. Every claim carries an id such as `[CC-07]`; a refuted claim carries a CORRECTION, and the correction is the truth. Full evidence per claim is in `docs/research/verified-claims.json`.
5. `docs/research/researchers/*.json` for supporting facts that did not make the digest, and `docs/research/snapshots/` for the vendor documentation as it read at research time.

## What exists today

- **Nothing built.** No manifests, no personas, no generator, no bootstrap.
- **The package being replaced** is preserved under `reference/current-codex-package/`: five Codex agent TOMLs (all `sandbox_mode = "workspace-write"`, including reviewer and security) and the `ecolleagues-init` skill with its `AGENTS.template.md`. It is Codex-only and installed from the maintainer's dotfiles, with `~/.codex/agents/*.toml` as **symlinks** — which is what Q4 exists to test [CX-02] — and the skill in the deprecated `~/.codex/skills` root [CX-07].
- **The review that motivated the redesign** found, in those prompts: job descriptions instead of operating rules; no return contract on any delegation; "do not edit source" enforced by prose alone; the tech-lead delegating to built-in agent types rather than the named personas; and peer-to-peer phrasing although every runtime is a tree. Design §4 answers each.

## How the research was produced, and how far to trust it

Six researcher agents covered Claude Code, Codex, opencode, Antigravity, cross-tool standards and prior art, working from official documentation, source at the installed tags, and the local binaries (`--help`, `strings`, live probes that mutate nothing). Their 89 load-bearing facts were merged into 58 atomic claims, and each claim was then fact-checked by an independent skeptic: **50 confirmed, 8 refuted**. Every refutation narrowed a conclusion rather than overturning a path or a key; the corrections are in the digest.

Three architects then proposed designs under different lenses (`docs/research/proposals/`). The synthesis was judged, then red-teamed by two reviewers whose 40 findings (2 blockers, 13 majors, 25 minors) are in `docs/research/redteam-issues-on-design-rev1.json` and are all applied in design revision 2. Revision 3 adds the capability decisions in §0.

The workflow scripts that produced all of this are in `docs/research/workflows/` and can be re-run against newer tool versions.

**Trust levels, highest first**: a claim marked confirmed with local evidence; a confirmed claim with documentation evidence only; a researcher fact not promoted to a claim; anything the design marks UNVERIFIED. **Interactive behaviour was never exercised** — no session was driven, no menu was opened, nothing was installed. That is the entire reason §15 exists, and why its tranche B needs a human at a keyboard.

Documentation roots at research time: Claude Code `https://code.claude.com/docs/en/<page>` (index at `/docs/llms.txt`); Codex `https://learn.chatgpt.com/docs/<path>`; opencode `https://opencode.ai/docs/<page>/` with the schema at `https://opencode.ai/config.json`; Antigravity `https://antigravity.google/docs/<page>/`, whose CLI plugins page disagreed with the binaries about install paths.

Prior art worth re-reading before writing the generator: **litestar-org/litestar-skills** (host-neutral YAML rendered into four host dialects with a CI drift gate — the pattern this design adopts), **wshobson/agents** (Claude-native source with per-host adapters), **rulesync** (plugin-packaging targets), **BMAD-METHOD** (personas as skills — the floor this design deliberately limits to the tech-lead), **vercel-labs/skills** (`npx skills add`), **OpenSpec** (managed-block discipline in a shared `AGENTS.md`).

## Maintainer environment

Context for dogfooding only. The package itself must assume none of it (see `AGENTS.md`).

- Arch Linux; dotfiles managed with GNU Stow; secrets reached only through `pass`; two machines, one of which runs opencode on its own default configuration.
- `~/.codex/config.toml` is untracked, state-mixed, and must never be written by this package.
- `~/.claude/settings.json` is stowed and tracked, so `claude plugin install -s user` dirties that working tree. Accepted by design.
- A real project bootstrapped with the old Codex-only package has a 492-line, ~23.5 KB `AGENTS.md` on a GitLab-hosted Android codebase. It is deliberately not copied into this repository — it holds project-internal content — but it is the fixture the 30 KiB budget gate and the additive audit path are designed against, and its own team-and-signatures section shows how a project legitimately extends the team table.
