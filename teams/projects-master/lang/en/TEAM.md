# Projects Master Dev Team

Team for building and maintaining software projects of any kind (formerly "CWCDT"). It adds the following specialization on top of the common layer.

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

ECC agents for stacks you do not use may be disabled in `permissions.deny` of `~/.claude/settings.json` (see your EEAS profile). If a project
needs one, remove it there. If something repeats or fails, use `hookify` / `learn` so it becomes a rule, not a memory.

## Workflow
- Flow: research and reuse → plan (`ecc:planner`) → TDD (`ecc:tdd-guide`) → review (`ecc:code-reviewer`, `ecc:security-reviewer`) → verify →
  commit. Invoke agents as `ecc:<name>`.
