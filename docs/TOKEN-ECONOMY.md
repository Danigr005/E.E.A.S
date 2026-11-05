# Token economy: what was measured and why it works

All numbers come from one machine and one day (Linux, Claude Code 2.1.234, ECC 2.2.3, Sonnet 5.5, a 967k-token context window). Treat them as a
worked example, not a promise: your plugins and skills will differ. The raw snapshots are in [`metrics/`](metrics/); reproduce them with
`scripts/measure.sh`.

## What "fixed prompt" means

Every request to the model starts with the same prefix: Claude Code's system prompt, the tool definitions, your memory files (`CLAUDE.md`, rules),
the skill list, the agent list. It is cached, so re-reading it is cheap but not free, and **every subagent writes its own copy again in its first
request**. Shrinking the prefix therefore pays on every turn and on every subagent launched. It does *not* shrink what you and the model say during
the conversation; that is handled by compaction and habits (below).

## Result

| Measure | Before | After | Change |
|---|---|---|---|
| **Prompt of the first real request** | **81.3k** (81,132 and 81,560) | **60.4k** | **−20.9k (−26%)** |
| Memory files (`CLAUDE.md` + imported file + rules) | 16.7k | 4.5k | −12.2k (−73%) |
| Skill listing | 9.8k | 4.8k | −5.0k |
| Agent list (30 agents denied) | 6.4k | ≈3.3k | −3.1k (measured in isolation) |
| Window before auto-compaction | 967k | 300k | fixed ceiling |

A re-measurement with the final CWCDT layout (`metrics/2026-11-05-after-cwcdt.md`) gave 60.2k, so the result held after the restructuring.

Illustration, not a measurement of your usage: a 100-turn session re-reads about 2.1M fewer cached tokens, and each subagent that loads the memory
files writes about 12k fewer tokens in its first request.

## The levers

| Lever | What it does | Where |
|---|---|---|
| Small memory | One compact `CLAUDE.md` plus one core rule; no imported duplicates; detail in an on-demand skill | `lang/*/CLAUDE.md`, `rules/cwcdt/common/core.md`, the playbook |
| Skill-list budget | `skillListingBudgetFraction` 0.005 and `skillListingMaxDescChars` 220 | `profiles/default.json` |
| Fewer agents | `permissions.deny` for agents of stacks you do not use | stack profiles |
| Compaction ceiling | `autoCompactWindow` 300k, "Compact instructions" in `CLAUDE.md`, status-line hint | `profiles/default.json`, `CLAUDE.md`, `statusline.mjs` |
| Code intelligence | Language-server plugins let Claude navigate by symbol instead of reading files | stack profiles |
| Hook tuning | Smaller session-start injection, no dollar-cost warnings, no fact-forcing on routine Bash | `profiles/default.json` |
| Habits | Stable model/effort, `/clear` between tasks, filtered command output, subagents only when they isolate context | `CLAUDE.md` "Context and tokens" |

## Method (so you can check me)

1. `scripts/measure.sh <label>` runs `claude -p /context` and stores the breakdown by category. It is free, but it **underestimates** savings: it
   moves part of what was trimmed into the "System tools" row.
2. `scripts/measure.sh <label> --real` also sends one tiny request and reads `usage` (input + cache-creation + cache-read tokens) from the JSON
   reply: that is the true size of the first prompt, and the number to trust. It costs a little quota.
3. To test a setting without touching your config: `claude -p "Reply only: ok" --output-format json --settings '{"skillListingBudgetFraction":0.004}'`.
4. Inside a session, `/usage` attributes real usage to skills, subagents, plugins and MCP servers and suggests changes; `/doctor` and
   `/skill-doctor` estimate the skill list's cost and find unused skills.

## Caveats

- One sample per scenario; run-to-run variation is about ±0.5k tokens.
- The fixed prompt is only part of the bill. Long conversations, large tool outputs and thinking dominate in long sessions; that is what the
  compaction ceiling and the habits address, and it is not measured here.
- Savings on a subscription depend on how Anthropic weights cached tokens in your plan's limits; the direction is certain, the size is not.
- A reduced skill-list budget means rarely used skills show as names only. The router table in `CLAUDE.md` names the skills that matter.
- `permissions.deny` on agents removes them from the list *and* from use. Keep the list in step with your projects.
- Delegating to Codex adds capacity from a second quota; it does not reduce Claude's tokens per task by itself, and it adds brief-writing and
  review overhead. Use the four-point rule so the trade is worth it.
