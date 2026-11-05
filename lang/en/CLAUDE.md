# CWCDT — Code With Codex Dev Team

Global methodology: Claude Code leads, specialist subagents (the ECC toolbox) and Codex execute, and the owner approves the plan and the
commit. Source of truth: the CWCDT repo (`readlink -f ~/.claude/CLAUDE.md` shows where). `~/.claude/CLAUDE.md`, `~/.claude/rules/cwcdt` and
`~/.claude/skills/cwcdt-playbook` are symlinks to it: **edit the repo, never the links.** Long-form detail (Codex delegation, waves, token
habits): skill `cwcdt-playbook`. Toolbox guide: `ecc:ecc-guide`.

## Autonomous mode: Claude decides what to use
The owner just says "do X". NEVER ask the owner to pick an agent, skill, command or hook. Before any non-trivial task, classify the request and
choose from the table (Skill and Agent tools, `ecc:` prefix); if nothing fits, use `ecc:ecc-guide`. Proportionality: a one-line change is done
directly; ceremony grows with size and risk. ECC hooks run automatically: do not trigger or mention them. Ask the owner only for: approving the
plan (gate 1), confirming the commit (gate 2), and push / merge / deletions.

| Request | Use |
|---|---|
| Build something from scratch (game, app, site, tool) | `orch-build-mvp`; without a design doc first run `plan-prd` + `plan` (max 3 questions) |
| New capability / change / bug / refactor | `orch-add-feature` / `orch-change-feature` / `orch-fix-defect` / `orch-refine-code` |
| Plan, PRD, architecture, technical decision | `planner`, `plan-prd`, `architect`, `code-architect`, skills `architecture-decision-records`, `api-design`, `database-migrations` |
| Before writing code | skill `search-first`; library docs `docs-lookup`; broad research `deep-research` |
| Understand foreign or legacy code | `code-explorer`, `codebase-onboarding`, `code-tour`, `spec-miner` |
| Tests | `tdd-workflow` + `tdd-guide`; E2E `e2e-runner`/`e2e-testing`; coverage `test-coverage`; browser `browser-qa` |
| Review | `code-review` + `<language>-reviewer`; PR `review-pr`; as needed `pr-test-analyzer`, `silent-failure-hunter`, `type-design-analyzer`, `code-simplifier`; DB `database-reviewer`; other provider: Codex (see Delegation) |
| Security (auth, payments, secrets, user input, files, crypto) | `security-reviewer` + skill `security-review` (`security-scan` to audit the config) |
| Broken build / types | `build-fix` or `<language>-build-resolver` |
| UI / frontend / games | `frontend-patterns`, `frontend-design-direction`, `design-system`, `a11y-architect`, `react-/vue-reviewer`, `motion-*`; verify with `browser-qa`/`e2e-runner` |
| Slowness, memory, bundle size | `performance-optimizer`, `react-performance`, `benchmark` |
| Deploy, infra, CI | `deployment-patterns`, `docker-patterns`, `kubernetes-patterns`, `github-ops` |
| Docs, marketing, SEO, content | `doc-updater` (`update-docs`, `update-codemaps`), `marketing-agent`, `seo-specialist`, `content-engine` |
| Stack skills | When touching a language or framework, load its `*-patterns`, `*-testing`, `*-security` if they exist |
| Context and memory | `context-budget`, `strategic-compact` near the limit; `save-session` when closing long work; `resume-session` when opening a project with a saved session; `learn-eval` after solving something non-obvious |

ECC agents for stacks you do not use may be disabled in `permissions.deny` of `~/.claude/settings.json` (see your CWCDT profile). If a project
needs one, remove it there. If something repeats or fails, use `hookify` / `learn` so it becomes a rule, not a memory.

## Delegation to Codex (plugin `codex@openai-codex`)
Two independent quotas (Claude plan, Codex/ChatGPT plan). Delegating adds capacity and keeps the lead's context clean; never delegate just to split
work. Standing authorization (granted by adopting CWCDT; edit this section to revoke it): delegate without asking when **all four** hold:
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
  hits its limit, the task returns to Claude without asking. Full table and brief template: skill `cwcdt-playbook`.

## Big jobs: linked sessions (waves)
Standing authorization (same terms): for big jobs with 2+ independent, long pieces that do not touch the same files, or when the master
conversation nears its context limit, use linked sessions (`start_session`, own worktree) after the plan is approved. Small work, research and
reviews stay as `ecc:` subagents or direct work. Each brief: files it owns, what "done" means and how it is checked, where the plan is, no push or
merge. The master coordinates (`list_sessions {"linked": true}`, child notes, `SendMessage`), reviews each child's diff and tests, integrates, and
asks the owner for commit and merge approval. Nothing is merged into `main`/`master` without that approval. Full protocol: `cwcdt-playbook`.

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
- Flow: research and reuse → plan (`ecc:planner`) → TDD (`ecc:tdd-guide`) → review (`ecc:code-reviewer`, `ecc:security-reviewer`) → verify →
  commit. Invoke agents as `ecc:<name>`.
- No push, PR or merge to `main` without my explicit OK. Secrets never in code, logs or chat.
