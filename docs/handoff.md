# Handoff and provenance

Where to pick up, and how far to trust the facts underneath the design.

## Read order

1. [`design.md`](design.md) §0 (decisions of record) and §1 (summary).
2. [`design.md`](design.md) §16 (milestones) for what is done and what is next.
3. [`SUPPORT-MATRIX.md`](SUPPORT-MATRIX.md) whenever a decision needs a fact. Every claim id
   cited anywhere in the repository is stated there in full, with the version it was last
   confirmed at. A claim marked refuted carries a correction, and **the correction is the
   truth**.
4. [`experiments.md`](experiments.md) before relying on anything version-gated. It holds 23
   experiments with the exact command, the installed version and the raw output. **Where an
   experiment contradicts a claim, the experiment wins** — it ran against the installed
   binary.
5. [`acceptance.md`](acceptance.md) for minimum versions, the honest per-host table of which
   rules are mechanical and which are prose, and the known limitations.

## How the facts were produced

Six researchers covered Claude Code, Codex, opencode, Antigravity, cross-tool standards and
prior art, working from official documentation, source at the installed tags, and the local
binaries. Their findings were merged into 58 atomic claims, and each was then fact-checked by
an independent skeptic: 50 confirmed, 8 refuted. Every refutation narrowed a conclusion rather
than overturning a path. Three architects then proposed designs under different lenses; the
synthesis was judged and red-teamed, and the 40 findings that produced are applied.

**Interactive behaviour was not exercised at that stage** — no session was driven, nothing was
installed. That is why the M0 sweep exists, and why it changed the design in nine places
before any code depended on it. The largest of those: seven Antigravity tool names the vendor
documentation lists are absent from the tool registry and abort an agent at startup.

The raw research — the researcher notes, the vendored copies of vendor documentation, and the
previous Codex-only package's prompts — is not carried in this repository. What ships is the
evidence: the claims in `SUPPORT-MATRIX.md` and the experiments in `experiments.md`.

## Trust levels, highest first

1. An experiment in `experiments.md`, run against the installed binary.
2. A claim marked confirmed with local evidence.
3. A confirmed claim resting on documentation only — marked as such in `SUPPORT-MATRIX.md`.
4. Anything the design marks UNVERIFIED.

## What is still open

Listed in full under "Known limitations" in [`acceptance.md`](acceptance.md). In short: three
behaviours need a human at a user interface (the opencode Tab and `@` menus, and the
Antigravity desktop's subagent-inheritance default), and both were recorded as untested
rather than assumed.
