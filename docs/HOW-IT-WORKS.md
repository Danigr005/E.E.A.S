# How CWCDT works

[Español](es/COMO-FUNCIONA.md)

## 1. The idea in one minute

You describe an outcome. A **lead** (your main Claude Code session) classifies the request, picks specialists from a toolbox, writes a plan and
waits for your approval. It then builds test-first, hands bounded and machine-verifiable pieces to a **second engineer** (Codex), reviews
everything (optionally with a second provider's eyes), verifies, and asks you to confirm the commit. Between those two gates it does not ask you
which agent or skill to use. Throughout, the context is kept small and measured, so sessions stay fast and quota lasts longer.

CWCDT is not a new agent framework. It is an **operating manual** (`CLAUDE.md`), a few **rules**, a **settings profile** and **scripts** that make
Claude Code, the [ECC](https://github.com/affaan-m/ECC) toolbox and Codex behave like one team.

## 2. Roles

| Role | Who | Does |
|---|---|---|
| **Owner** | You | States goals. Approves the plan (gate 1) and the commit (gate 2). Decides push, merge and deletions. |
| **Lead** | Your main Claude Code session | Classifies the request, plans, integrates, reviews diffs, decides what to delegate. Holds the conversation context. |
| **Specialists** | ECC subagents (`planner`, `tdd-guide`, `code-reviewer`, `security-reviewer`, language reviewers and build resolvers, `e2e-runner`, …) | Work in their own context and return a short result, so heavy reading never bloats the lead. |
| **Second engineer** | Codex, through OpenAI's official Claude Code plugin | Takes bounded, machine-verifiable tasks and read-only reviews, using its own quota. |
| **Linked sessions ("waves")** | Child Claude sessions in their own git worktrees | Own independent pieces of a big job; the lead (the "master") coordinates and integrates. |

## 3. The loop and the two gates

1. **Classify.** The router table in `CLAUDE.md` maps the kind of request (new feature, bug, refactor, greenfield, security-sensitive, …) to the
   agents and skills to use. If nothing fits, `ecc:ecc-guide` lists what exists.
2. **Research and reuse.** Before writing new code: search the repo, existing libraries and docs (`search-first`, `docs-lookup`).
3. **Plan.** A plan with files, steps, risks and how it will be verified.
4. **Gate 1.** You approve, change or reject the plan. Nothing is built before this for non-trivial work.
5. **Build, test first.** Failing test, minimal implementation, refactor. Specialists do the work; bounded pieces may go to Codex (section 5).
6. **Review.** `code-reviewer` plus the language reviewer, plus `security-reviewer` for auth, input, files, crypto, payments. Optionally a
   cross-provider review by Codex.
7. **Verify.** Tests, typecheck, build, lint, all run by Claude. "Done" means the checks pass, not that someone said so.
8. **Gate 2.** The lead summarizes what changed and proposes a commit message. You confirm. **Push, PR, merge and deletions always ask again.**

**Proportionality.** Ceremony grows with size and risk: a one-line change is edited directly; a small bug gets a regression test first
(`orch-fix-defect`); a new feature runs the full loop (`orch-add-feature`); a greenfield project starts with a PRD and an MVP workflow
(`orch-build-mvp`).

**How firm are the gates?** They are instructions in `CLAUDE.md` that Claude follows, backed by Claude Code's plan mode and permission prompts.
If you need a hard guarantee (for example, no `git push` ever without a prompt), also add a rule to `permissions.ask` or `permissions.deny` in your
settings. CWCDT does not pretend that text alone is a security boundary.

## 4. The router

The table in `CLAUDE.md` is the heart of the "autonomous mode": the owner never picks an agent. Each row names the skills and agents for a kind of
work. Keep it short: every row costs tokens in every session. To change it, edit `lang/<l>/CLAUDE.md` in the repo (see [CUSTOMIZE](CUSTOMIZE.md)).
Rules that apply to everything live in `rules/cwcdt/common/core.md`; language-specific rules (`python/`, `rust/`, `typescript/`, `web/`) load only
when you touch matching files.

## 5. Delegating to Codex

**Why.** Two quotas instead of one, a lead whose context is not filled with mechanical work, and an independent reviewer from another provider.
**Not** to split work for its own sake.

**The rule: all four, or it stays with Claude.**

1. *Specified*: what to do, which files, which interface.
2. *Bounded*: its own files; nobody else writes them (one writer per file).
3. *Machine-verifiable*: a test, typecheck, build or lint that Claude runs afterwards.
4. *No design decision and no ambiguity.*

| Good fits for Codex | Stays with Claude |
|---|---|
| Tests from a written spec | Plan, PRD, architecture |
| Mechanical refactors with green tests | Design decisions and ambiguity |
| CRUD and boilerplate with a defined interface | Changes that cross modules |
| Type and lint errors | UI that needs visual judgement |
| Docs | The final security call |
| Long background tasks, read-only reviews | Integration, merge, orchestration |

**Models and effort.** Light models for mechanical work, a workhorse model for daily work, the frontier model only for review and hard cases;
Claude's own tiers are used the same way (see the table in the [playbook](../lang/en/skills/cwcdt-playbook/SKILL.md)). Pick model and effort at
the start of a task: switching mid-task breaks the prompt cache.

**Flow.** Brief (goal, owned files, interface, acceptance command, "no commit or push") → separate branch or worktree → `/codex:rescue --background`
→ `/codex:status` / `/codex:result` → Claude reviews the diff and **runs the acceptance command itself** → one correction round if needed →
integrate. A "done" from Codex does not count until the checks pass.

**Cross review.** `/codex:review`, `/codex:adversarial-review` or `/astra-review` (a structured verdict with a fix loop) give a second opinion from a
different provider. Claude verifies each finding against the code before acting.

**Budget.** If one quota runs short, delegable work moves to the other; if Codex runs out, the task returns to Claude without asking. Codex's
"review gate" stays off because it creates Claude↔Codex loops that drain quota. Log each delegation in [the calibration log](CODEX-CALIBRATION.md)
and adjust the model table with real results.

## 6. Waves (linked sessions)

For a big job with two or more independent, long pieces that do not touch the same files, the master session launches one linked session per piece
(`start_session`, each in its own worktree with a clean context). Each brief states the files it owns, what "done" means and how to check it, where
the plan is, and that it does not push or merge. The master tracks them (`list_sessions`, notes from the children, `SendMessage`), reviews every
child's diff and tests, integrates, and asks you for the commit and merge approval. Children do not talk to each other. This also solves context
limits: the master can save its state (`save-session`) and you continue in a new conversation while the children keep running.

## 7. Context and tokens

Every request re-reads the "fixed prompt": system prompt, tool definitions, your memory files, the skill and agent lists. CWCDT shrinks what you
control (memory, skill list, agent list) and caps how large a conversation can grow (`autoCompactWindow`, compaction instructions, a status line
that warns). Details, numbers and the measuring method: [TOKEN-ECONOMY](TOKEN-ECONOMY.md).

## 8. Guardrails: what enforces what

| Guardrail | Mechanism | Strength |
|---|---|---|
| Two gates (plan, commit) | `CLAUDE.md` instructions + Claude Code plan mode and permission prompts | Soft; add `permissions` rules for hard enforcement |
| Never push / merge / delete without OK | `CLAUDE.md` + your permission rules | Soft unless you add `permissions.ask` / `deny` |
| Facts before editing; no hardcoded secrets | ECC hooks (GateGuard, pre-commit checks) and the core rule | Hard (hooks block), tuned by the profile |
| Codex cannot commit or push | The brief, `codex/AGENTS.md` and a separate worktree | Soft + isolation |
| Every settings change is reversible | `apply.sh` backups and `revert.sh`, tested by `test-sandbox.sh` | Hard |

## 9. A worked example (illustrative)

> You: "Add rate limiting to the /login endpoint."

1. **Classify**: new capability → `orch-add-feature`. `search-first` finds an existing middleware library; `docs-lookup` confirms its API.
2. **Plan** (`planner`): five steps, three files, risk: lockout of legitimate users. → **Gate 1**: you answer "ok".
3. **Build**: Codex (`gpt-reserve`) writes the unit tests from the spec: bounded and verifiable (`pnpm test src/auth/rateLimit.test.ts` must fail
   first). The lead writes the middleware and wires it in, because it crosses modules.
4. **Review**: `typescript-reviewer` and `security-reviewer` (authentication); `/codex:adversarial-review` as the cross-provider check; Claude
   verifies each finding.
5. **Verify**: full test suite, typecheck, lint, all green.
6. **Gate 2**: the lead shows the diff summary and proposes `feat: rate limit login attempts`. You confirm. Pushing asks again.

## 10. Where everything lives

| Path | Purpose |
|---|---|
| `lang/<l>/CLAUDE.md` → `~/.claude/CLAUDE.md` | The operating manual |
| `lang/<l>/skills/cwcdt-playbook` → `~/.claude/skills/cwcdt-playbook` | On-demand detail |
| `rules/cwcdt` → `~/.claude/rules/cwcdt` | Core and per-language rules |
| `profiles/*.json` → merged into `~/.claude/settings.json` | Context and hook tuning, stack profiles |
| `codex/AGENTS.md` → `~/.codex/AGENTS.md` | Rules for Codex when it receives a delegated task |
| `~/.claude/cwcdt.lang`, `cwcdt.profile` | Remember your choices so `apply.sh` and `check.sh` agree |
| `~/.claude/backups/cwcdt-<date>/` | Everything `apply.sh` replaced |
