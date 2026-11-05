# EEAS — Specialized Teams of Agents and Subagents

Claude Code leads, subagents and Codex execute, and the owner approves the plan and the commit. There is a **common layer** (this file: Claude↔Codex
split, waves, token saving, preferences) that always applies, and **teams** (`teams/<name>/`) that add specialization. Source of truth: the EEAS
repo (`readlink -f ~/.claude/CLAUDE.md` shows where). `~/.claude/CLAUDE.md`, `~/.claude/rules/eeas` and `~/.claude/skills/eeas-*` are symlinks to
it: **edit the repo, never the links.** Long-form detail: skill `eeas-playbook`; team management: skill `eeas-teams`.

## Teams: which team works in each environment
- Each project stores its team in `.claude/eeas-team` (one line, the name). At session start a hook injects that team's instructions ("EEAS ·
  active team"). Follow them for the whole session without the owner repeating it.
- If the hook says the project has no team, ask ONCE which to use (show the list the hook gives), save it with skill `eeas-teams`, and carry on.
  If you see no hook message, look for `.claude/eeas-team` yourself and read `teams/<team>/lang/en/TEAM.md` in the EEAS repo.
- The team changes only when the owner explicitly asks (skill `eeas-teams`). Never on your own.
- New teams: skill `eeas-teams` (create). A team cannot remove the common layer.

## Delegation to Codex (plugin `codex@openai-codex`)
Two independent quotas (Claude plan, Codex/ChatGPT plan). Delegating adds capacity and keeps the lead's context clean; never delegate just to split
work. Standing authorization (granted by adopting EEAS; edit this section to revoke it): delegate without asking when **all four** hold:
(1) specified: what, files and interface; (2) bounded: its own files, one writer per file; (3) machine-verifiable: a test/typecheck/build/lint that
Claude runs afterwards; (4) no design decision and no ambiguity. If one fails, it stays with Claude.
- To Codex: tests from a spec, mechanical refactors, CRUD/boilerplate, type and lint errors, docs, long background tasks, read-only reviews.
  Stays with Claude: plan/PRD/architecture, design, cross-module changes, UI needing visual judgement, the final security call, integration,
  merge, orchestration.
- Codex models (examples; check your account's model list): light models (`gpt-6-luna`, `gpt-reserve`) for mechanical work; the workhorse
  (`gpt-6.1-sol`, medium; high if the bug is non-trivial) for daily work; the frontier model (`gpt-6-astra`) only to review or for hard cases;
  `xhigh`/`max`/`ultra` only exceptionally. Review: `/codex:review`, `/codex:adversarial-review`, `/astra-review`. Writing:
  `/codex:rescue --background --model <m> --effort <e>` on a separate branch or worktree, with a brief (files, interface, acceptance command,
  "no commit or push").
- Claude reviews the diff and runs the acceptance command before accepting. Never put secrets in a brief. Keep Codex's review gate off. If Codex
  hits its limit, the task returns to Claude without asking. Full table and brief template: skill `eeas-playbook`.

## Big jobs: linked sessions (waves)
Standing authorization (same terms): for big jobs with 2+ independent, long pieces that do not touch the same files, or when the master
conversation nears its context limit, use linked sessions (`start_session`, own worktree) after the plan is approved. Small work, research and
reviews stay as `ecc:` subagents or direct work. Each brief: files it owns, what "done" means and how it is checked, where the plan is, no push or
merge. The master coordinates (`list_sessions {"linked": true}`, child notes, `SendMessage`), reviews each child's diff and tests, integrates, and
asks the owner for commit and merge approval. Nothing is merged into `main`/`master` without that approval. Full protocol: `eeas-playbook`.

## Context and tokens (always)
- Keep model and effort stable within a task (every change breaks the cache). `/clear` between unrelated tasks; `/compact` at natural breaks, not
  mid-task.
- Read only what you need: grep or line ranges before whole files. Broad reads and searches go to `Explore` or a subagent that returns a short
  summary. Long outputs (tests, logs, builds): filter (`grep`, `tail`); never dump whole logs into context.
- Subagents only to isolate context or parallelize independent work; self-contained brief, short result.
- Long-running state → `save-session` (or a note in the plan); durable facts about the owner → automatic memory. Do not duplicate them.
- Before launching an `orch-*` workflow or a wave, estimate the cost (number of agents) and pick the lightest flow that covers the risk.

## Compact instructions
When compacting, keep: goal and approved plan; decisions taken and why; files touched and test/build status; pending work and next step; linked
sessions (id → piece) and what is left to integrate; `save-session` paths. Drop: long command output, discarded explorations, text of skills
already applied.

## Owner preferences (edit me)
- Talk to me in English. Code, identifiers and commit messages in English.
- No push, PR or merge to `main` without my explicit OK. Secrets never in code, logs or chat.
- Gates (any team): the owner only approves the plan (gate 1), confirms the commit (gate 2) and authorizes push/merge/deletions. Never ask them to pick an agent, skill, command or hook: you decide.
