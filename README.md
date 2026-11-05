# CWCDT — Code With Codex Dev Team

An autonomous, two-gate development methodology for AI coding agents. **You say what you want. Claude Code leads a team of specialist
subagents, hands the mechanical, machine-verifiable parts to Codex, and stops you only twice: to approve the plan and to confirm the
commit.** All of it runs inside a lean, measured context budget.

English · [Español](README.es.md)

> Independent community project. Not affiliated with or endorsed by Anthropic, OpenAI or the authors of ECC. "Claude" and "Claude Code" are
> trademarks of Anthropic; "Codex" and "ChatGPT" are trademarks of OpenAI. See [NOTICE](NOTICE).

## Why

Agent setups tend to grow into a pile of agents, skills, hooks and rules that nobody can explain, and that quietly eat your context window and
quota before you type a word. CWCDT is the opposite: a small, opinionated operating manual plus a few scripts that

- decide **who does what** (a router table and a four-point delegation rule),
- keep **you in control** where it matters (two gates; never push, merge or delete without your OK),
- spend **fewer tokens** (the fixed prompt of the reference setup went from 81.3k to 60.4k tokens, −26%, measured on real requests), and
- are **reproducible and reversible** (one repo, symlinks, backups, a sandbox test).

## The loop

```
 you: "add rate limiting to the API"
        │
        ▼
 CLASSIFY (router table) ─▶ RESEARCH & REUSE ─▶ PLAN ───────▶ ◆ GATE 1: you approve the plan
                                                                    │
        ┌───────────────────────────────────────────────────────────┘
        ▼
 BUILD test-first ── specialists (planner, tdd-guide, …)
        │             └─ Codex for bounded, machine-verifiable pieces (four-point rule)
        ▼
 REVIEW  code + language + security reviewers; optional cross-provider review by Codex
        ▼
 VERIFY (tests, build, lint) ─▶ COMMIT ──────────────────────▶ ◆ GATE 2: you confirm the commit
                                                                push / merge / delete: always ask
```

## What you get

| Piece | What it does |
|---|---|
| `lang/{en,es}/CLAUDE.md` | The operating manual Claude reads every session: router table, delegation rule, waves, token habits, compaction instructions. Small on purpose (≈3.5k tokens). |
| `lang/{en,es}/skills/cwcdt-playbook` | The long-form detail (models and effort, brief template, waves protocol, token tips), loaded only when needed. |
| `rules/cwcdt/` | One core rule (style, testing, security, review, git) plus per-language rules that load only when you touch matching files. |
| `profiles/` | Settings merged into `~/.claude/settings.json`: auto-compact window, skill-listing budget, hook tuning; stack profiles that switch off agents you never use. |
| `codex/AGENTS.md` | What Codex must do when Claude delegates a task to it. |
| `statusline.mjs` | `ctx used/window · cache · 5h · 7d` and a hint to `/compact`. |
| `scripts/` | `apply`, `check`, `revert`, `measure`, `ecc-update`, `test-sandbox`. |

## Quick start (about 10 minutes)

Requirements: [Claude Code](https://claude.com/claude-code), `git`, `python3`, Node 18+. Optional, for delegation: a ChatGPT plan with the Codex CLI.
Tested on Linux; macOS should work (the scripts avoid GNU-only features) but is untested; on Windows use WSL.

```bash
# 1. The toolbox: ECC (MIT) provides the agents and skills CWCDT routes to
claude plugin marketplace add affaan-m/ECC
claude plugin install ecc@ecc

# 2. (Optional) Codex as the second engineer
npm i -g @openai/codex && codex login
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex

# 3. Get CWCDT, preview, then apply
git clone https://github.com/Danigr005/CWCDT.git ~/CWCDT
~/CWCDT/scripts/apply.sh --dry-run --lang en
~/CWCDT/scripts/apply.sh --lang en            # Spanish: --lang es ; TS/Python/Rust stack: --profile ts-py-rust

# 4. Restart Claude Code, then check and measure
~/CWCDT/scripts/check.sh
~/CWCDT/scripts/measure.sh first --real
```

Then just ask for something. `apply.sh` keeps a backup of whatever it replaces (`~/.claude/backups/cwcdt-<date>/`) and
`scripts/revert.sh --original` puts everything back.

Your existing `~/.claude/CLAUDE.md` is moved to that backup, not merged. Copy your own preferences into the "Owner preferences" section of
`lang/<l>/CLAUDE.md`. Edit the repo, never the symlink: Claude Code refuses to write through symlinks.

## New laptop (restore everything)

Everything that defines the methodology lives in this repo. On a fresh machine:

```bash
git clone https://github.com/Danigr005/CWCDT.git ~/CLAUDE-PROJECTS/CWCDT
~/CLAUDE-PROJECTS/CWCDT/scripts/bootstrap.sh --lang en --profile ts-py-rust
codex login        # and open `claude` to sign in
```

`bootstrap.sh` installs ECC and the Codex plugin, applies CWCDT and checks it. Deliberately **not** in git: conversation
history, logins and secrets (redo them with `claude` / `codex login`).

## Learn more

- [How it works](docs/HOW-IT-WORKS.md) · [Cómo funciona](docs/es/COMO-FUNCIONA.md)
- [Customize it](docs/CUSTOMIZE.md): profiles, router, languages, models
- [Token economy](docs/TOKEN-ECONOMY.md): what was measured and why it works
- [Troubleshooting and FAQ](docs/TROUBLESHOOTING.md)
- [Codex calibration log](docs/CODEX-CALIBRATION.md)

## Status

v0.1.0. Built and measured on one machine (Linux, Claude Code 2.1.234, ECC 2.2.3 at commit `b38be6a`, Codex CLI 0.164 with plugin 1.0.6).
Model names in the docs are examples from November 2026: adjust them to what your account offers. Issues and PRs are welcome, see
[CONTRIBUTING](CONTRIBUTING.md).

## License

MIT © 2026 Danigr005. Contains material derived from ECC (MIT © Affaan Mustafa); see [NOTICE](NOTICE).
