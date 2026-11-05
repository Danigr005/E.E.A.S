# Customize CWCDT

Everything lives in the repo; `scripts/apply.sh` pushes it to `~/.claude` and `~/.codex`. After any edit, run `scripts/apply.sh` (idempotent) and
`scripts/check.sh`. Edit the repo, never the symlinks: Claude Code refuses to write through symlinks.

## 1. Your preferences and your language

- Edit the "Owner preferences" section at the end of `lang/<l>/CLAUDE.md`: the language Claude talks to you in, naming and commit conventions,
  your own do-not-touch rules.
- Choose the manual's language with `apply.sh --lang en|es`. To add one, copy `lang/en` to `lang/<xx>`, translate `CLAUDE.md` and the playbook's
  `SKILL.md` (keep `name: cwcdt-playbook`), and run `apply.sh --lang <xx>`. `scripts/check.sh` warns when two translations drift apart in length.

## 2. Profiles: settings per stack

`profiles/default.json` applies to everyone. A stack profile applies on top: `apply.sh --profile ts-py-rust`. A profile is plain JSON merged into
`~/.claude/settings.json` (objects merge, lists are unions, scalars overwrite; keys starting with `_` are comments; `{{MASTER}}` and `{{HOME}}`
expand). Create `profiles/<yours>.json` with only what differs. The shipped example does three things:

- **Disables ECC agents your stack never uses**, with `permissions.deny` entries like `Agent(ecc:kotlin-reviewer)`. Each agent you remove saves
  about 100 tokens of fixed prompt in every session and subagent. List what exists with `claude -p /context`. Remove an entry from the profile when
  a project needs that agent again, then `apply.sh`.
- **Enables language-server plugins** (`typescript-lsp`, `rust-analyzer-lsp`): Claude navigates by symbol instead of reading whole files. They need
  the server installed (`typescript-language-server`, `rust-analyzer`). Python: install `pyright` and enable `pyright-lsp@claude-plugins-official`.
- **Enables `context7`**, the documentation MCP that ECC's `docs-lookup` agent depends on (it may ask you to authorize it once with `/mcp`).

## 3. The router table

It lives in `lang/<l>/CLAUDE.md`. Add rows for your own skills and agents, delete rows for work you never do. Keep each row to one line: the table is
paid for in every session, in every subagent that loads memory.

## 4. Models and effort

The model table is in `lang/<l>/skills/cwcdt-playbook/SKILL.md`. Replace the Codex rows with the models your account lists (`codex` model picker,
or `~/.codex/models_cache.json`). To change Codex's default model for direct use: `apply.sh --codex-default-model <model>`. Claude's default
effort lives in `~/.claude/settings.json` (`modelSettings`, `/effort`). Record what works in [the calibration log](CODEX-CALIBRATION.md).

## 5. Compaction window

`profiles/default.json` sets `autoCompactWindow` to 300000: Claude Code summarizes the conversation when it reaches about 300k tokens instead of near
the model's full window. Lower values keep every turn cheaper but compact more often; higher values keep more raw history at a higher per-turn cost.
Per model: `/autocompact 200k`. What survives compaction is steered by the "Compact instructions" section of `CLAUDE.md`.

## 6. Skill listing

`skillListingBudgetFraction` (default profile: 0.005 of the context window) and `skillListingMaxDescChars` (220) bound how much of the prompt the
skill list may use. Over budget, descriptions are dropped starting with the skills you use least; names always stay. If a skill you rely on shows
without a description, invoke it once (use ranks it higher), raise the fraction, or name it in the router table. `/doctor` shows the listing's cost.

## 7. Hooks (ECC)

CWCDT keeps ECC's hooks and tunes them through environment variables in the profile's `env` block:

| Variable | Default profile | Effect |
|---|---|---|
| `GATEGUARD_BASH_ROUTINE_DISABLED` | `1` | Skips the "state facts" prompt on routine Bash commands; destructive commands are still checked |
| `GATEGUARD_EXEMPT_GLOBS` | the CWCDT repo and `/tmp/claude-*` | Paths where first-touch edits skip the fact-forcing gate. Add your scratch folders; keep real projects out |
| `ECC_SESSION_START_MAX_CHARS` | `3000` | Caps the context ECC injects at session start (ECC's default is 8000) |
| `ECC_CONTEXT_MONITOR_COST_WARNINGS` | `off` | Hides API-rate dollar estimates (not meaningful on a subscription) |
| `ECC_HOOK_PROFILE` / `ECC_DISABLED_HOOKS` | not set | ECC's own switches: `minimal` / `standard` / `strict`, and a list of hook ids to turn off |

## 8. Status line

`statusline.mjs` shows `[model] ctx 142k/300k · cache 91% · 5h 23% · 7d 41%` and `/compact soon` at 60% of the window. To opt out, remove
`statusLine` from `profiles/default.json` and from `~/.claude/settings.json`.

## 9. No Codex?

Run `apply.sh --no-codex` and delete the "Delegation to Codex" section of `lang/<l>/CLAUDE.md`. Everything else works unchanged.

## 10. Updating ECC, uninstalling

- `scripts/ecc-update.sh` reports news; with a local clone, `--pull` fast-forwards it after you reviewed the diff. Without one, it prints the
  marketplace commands. CWCDT records the ECC version it was tested with in `ecc.lock`.
- `scripts/revert.sh` undoes the last apply; `scripts/revert.sh --original` restores the state from before CWCDT.
