# Core rules (condensed from ECC's common rules)

One file instead of ten: same useful content, no duplicates, no agent-roster templates.

## Style
- Immutability: create new objects, do not mutate existing ones.
- Cohesive files: 200–400 lines typical, 800 max (tests, generated and vendored files may exceed it). Functions <50 lines, nesting ≤4 (early return).
- KISS; DRY only for real repetition; YAGNI. Descriptive names; named constants, no magic numbers.
- Errors: explicit at every level; clear messages in the UI, detail in server logs; never swallow them silently.
- Validate all input at system boundaries (schemas) and fail fast.

## Testing
- Minimum 80% coverage: unit, integration and E2E for critical flows.
- TDD: failing test (RED) → minimal implementation (GREEN) → refactor. Fix the implementation, not the test (unless the test is wrong).
- Arrange-Act-Assert structure; names that describe the behavior.

## Security (before any commit)
- No secrets in code, logs or chat (environment variables or a secret manager); validated input; parameterized queries; escaped output (XSS); CSRF and authN/authZ checked; rate limiting; errors that do not leak data.
- Security review is mandatory for auth, user input, databases, files, external APIs, crypto and payments.
- If a problem appears: STOP → `ecc:security-reviewer` → fix CRITICAL → rotate exposed secrets → look for the same flaw elsewhere.

## Review
- After writing or changing code: `ecc:code-reviewer` (+ the `<language>-reviewer`). CRITICAL blocks; HIGH warns; MEDIUM/LOW inform.
- Before asking for review: CI green, no conflicts, branch up to date.

## Git
- Commits `<type>: <description>` (feat, fix, refactor, docs, test, chore, perf, ci). PRs: review the whole branch history; summary and test plan.

## Agents
- Your last message IS the deliverable. If you delegate, collect the results before finishing; never end "waiting for agents". Do not re-delegate what fits in one context.
- Independent tasks → agents in parallel.
