# Codex ↔ Claude calibration log

Log every real delegation to correct the model table in `lang/<l>/skills/cwcdt-playbook/SKILL.md`.

| Date | Task (type) | Model / effort | Rounds | Accepted on the 1st try? | Notes (quota spent, failures) |
|---|---|---|---|---|---|
| | | | | | |

## How to adjust
- A task type fails on the 1st try in 2 of 3 delegations → go one step up (model or effort), or give it back to Claude.
- Accepted on the 1st try 5 times in a row → try one step cheaper (`gpt-6.1-sol` → `gpt-reserve` → `gpt-6-luna`).
- If Codex's quota runs out before the weekend repeatedly, reserve the frontier model for review only.
