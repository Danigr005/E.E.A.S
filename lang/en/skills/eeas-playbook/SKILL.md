---
name: eeas-playbook
description: EEAS playbook (common layer) for big jobs: Claude↔Codex delegation (models, effort, brief template, calibration), the linked-sessions (waves) protocol, and habits for saving tokens and keeping context. Use it before delegating to Codex, before launching linked sessions, or before planning a large job.
---

# EEAS playbook (common layer)

The detail that `CLAUDE.md` only summarizes. It loads on demand so these tokens are not paid on every turn.

## 1. Claude ↔ Codex delegation

Independent quotas: your Claude plan and your Codex (ChatGPT) plan. Delegate to add capacity and keep the lead's context clean.

### The rule: all four, or it stays with Claude
1. **Specified**: what to do, which files, which interface.
2. **Bounded**: its own files; nobody else writes them.
3. **Machine-verifiable**: a test, typecheck, build or lint that Claude runs afterwards. No acceptance criterion, no delegation.
4. **No design decision and no ambiguity.**

### Models and effort
Default Claude effort is `medium` on Sonnet 5.5 and Opus 5.5 (raise to `high` when verification is critical). Changing model or effort mid-task
breaks the cache: choose at the start. The Codex rows are examples from one account (November 2026): read your own list with the `codex` model
picker or `~/.codex/models_cache.json` and adjust.

| Who | Model (effort) | For |
|---|---|---|
| Claude | Opus 5.5 (high) | Plan, architecture, ambiguity, orchestration, integration, diff review |
| Claude | Fable 5.1 | Only hard problems, or fixes Sonnet/Codex cannot solve |
| Claude | Sonnet 5.5 (medium) | Standard implementation that is not delegated: cross-module, UI, needs skills/hooks |
| Claude | Haiku 5.5 (low) | Small mechanical work already in the conversation |
| Codex | `gpt-6-luna` (low–medium) | Mechanical: renames, boilerplate, formatting, docs, lint |
| Codex | `gpt-reserve` (medium) | Cheap, quick code: tests from a spec, CRUD, type errors |
| Codex | `gpt-6.1-sol` (medium; high if the bug is non-trivial) | Daily work: scoped refactors with green tests, features with a defined interface, already-reproduced bugs |
| Codex | `gpt-6-astra` (medium–high) | Cross review and hard cases; burns quota fast, not for routine work |

`xhigh`/`max`/`ultra` only exceptionally and noted: they drain the 5-hour window. Correct this table with real use (`docs/CODEX-CALIBRATION.md`).

### Brief template (to Codex)
```
GOAL: <one sentence>
FILES YOU OWN (only these): <paths>
INTERFACE / CONTRACT: <signatures, types, expected behavior>
DONE WHEN: <exact command, e.g. `pnpm test src/foo && pnpm typecheck`>
CONSTRAINTS: no commit or push; do not touch other files; no new dependencies unless <...>; do not read .env or secrets
OUTPUT: summary of ≤10 lines: files changed, result of the acceptance command, open questions
```

### Flow for a write delegation
1. Check the four-point rule. If one fails, do it in Claude.
2. Separate branch or worktree: `git worktree add ../wt-<task> -b codex/<task>`.
3. `/codex:rescue --background --model <m> --effort <e> "<brief>"`.
4. `/codex:status` and `/codex:result` (do not poll in a loop; keep working on something else).
5. Review `git diff`, run the acceptance command, apply the `<language>-reviewer`. If it fails: one correction round with `--resume`; if it fails
   again, Claude does it.
6. Integrate into the working branch, remove the worktree and log the result in `docs/CODEX-CALIBRATION.md`.

### Cross review (read-only)
Use it when the reviewer would be the same model that wrote the code, or on medium/high-risk changes: `/codex:review` (routine),
`/codex:adversarial-review` (design, security, assumptions), `/astra-review` (structured verdict with a fix loop). Claude verifies every finding
against the code before touching anything: Codex is wrong sometimes too.

### Budget
Claude: the status line shows 5h/7d usage (`/usage` gives the breakdown). Codex: its own 5-hour window and weekly cap; check its status in its app.
If one quota runs short, push delegable work to the other; if Codex runs out, work returns to Claude (Sonnet/Haiku) without asking. Codex's review
gate (`--enable-review-gate`) stays off: it creates Claude↔Codex loops that drain the quota.

## 2. Waves (linked sessions)
- **When**: a big job with 2+ independent, long pieces that do not touch the same files (e.g. modeling, HUD, performance, server), or the master
  nears its context limit. Small work, research and reviews are `ecc:` subagents or direct work.
- **How**: after the plan is approved, the master launches one session per piece with `start_session` (own worktree, clean context). The brief says:
  files it owns (one writer per file), what "done" means and how it is checked, where the plan or saved session is, and that it does not push or
  merge. Record in the plan or in `save-session` which session does what.
- **Coordinate**: `list_sessions {"linked": true}`; each child reports when it ends a turn; details with `list_events`; corrections with
  `SendMessage` (id `local_…`); no polling. Children do not talk to each other: everything goes through the master.
- **Integrate**: the master reviews each child's diff and tests, integrates, and asks the owner for commit and merge approval. Nothing is merged
  into `main`/`master` without it.
- **Context**: near the limit, `save-session`; the owner continues with `resume-session` in another conversation; the children stay alive.
- A child may delegate sub-pieces of its own to Codex under the four-point rule.

## 3. Saving tokens and keeping context
What the setup already does for you:
- Minimal fixed memory (`CLAUDE.md` + one core rule); detail lives here and loads on demand.
- `autoCompactWindow` = 300k: compacts before every turn drags hundreds of thousands of tokens; `CLAUDE.md` is re-injected from disk after
  compaction and its "Compact instructions" section guides what is kept.
- Skill listing with a reduced budget; agents for stacks you do not use can be disabled; LSP plugins for symbol navigation instead of reading files.
- ECC hooks (state saved before compaction, session summary, previous-context loading, quality checks after edits) stay active.
- Status line: `ctx used/window · cache · 5h · 7d` and a `/compact soon` hint at 60% of the window.

What you (or I) do by hand:
- `/clear` when switching tasks; `/compact <focus>` at natural breaks; `/rewind` if a path fails (it keeps the cache).
- Do not switch model or effort mid-task; turn fast mode on only at the start.
- Broad reads go to `Explore`/a subagent with a short summary; filter command output.
- Measure: `scripts/measure.sh <label> [--real]` (fixed context cost); `/usage` (breakdown by skills, agents, plugins, MCP); `/doctor` and
  `/skill-doctor` (skill-listing cost and unused skills).

## 4. Maintenance (from the EEAS repo)
- `scripts/apply.sh [--dry-run]`: links + settings + Codex (idempotent, backup in `~/.claude/backups/`).
- `scripts/check.sh`: verifies links, settings and the toolbox plugin.
- `scripts/toolbox-update.sh [--pull]`: checks the ECC toolbox for news; review the diff before pulling.
- Revert: `scripts/revert.sh [--original]`.
