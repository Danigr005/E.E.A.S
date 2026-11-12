# Core rules

## Style
- Immutability; files 200–400 lines (800 max); functions <50 lines, nesting ≤4. KISS, YAGNI, DRY only for real repetition; named constants.
- Explicit errors at every level (clear in UI, detail in logs), never swallowed. Validate input at boundaries and fail fast.

## Testing
- ≥80% coverage (unit, integration, E2E for critical flows). TDD: RED → GREEN → refactor; fix the code, not the test. Arrange-Act-Assert.

## Security (before any commit)
- No secrets in code/logs/chat; validated input; parameterized queries; escaped output; CSRF, authN/authZ, rate limiting; errors that leak nothing.
- Mandatory review for auth, input, DB, files, external APIs, crypto, payments. On a finding: STOP → `ecc:security-reviewer` → fix CRITICAL →
  rotate exposed secrets → search for the same flaw elsewhere.

## Review and Git
- After code changes: `ecc:code-reviewer` + `<language>-reviewer` (CRITICAL blocks, HIGH warns). CI green and branch up to date before review.
- Commits `<type>: <description>` (feat, fix, refactor, docs, test, chore, perf, ci). PRs: review whole branch; summary and test plan.

## Agents
- Your last message is the deliverable; collect delegated results before finishing. Independent tasks in parallel; don't re-delegate what fits one context.
