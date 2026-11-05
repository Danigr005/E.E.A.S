# Troubleshooting and FAQ

## Problems

**"Refusing to write … it is a symbolic link."** `~/.claude/CLAUDE.md` and friends are symlinks into the EEAS repo. Edit the file inside the repo
(`readlink -f ~/.claude/CLAUDE.md` shows where), then start a new session or `/clear`.

**I edited `CLAUDE.md` but Claude behaves the same.** Memory files are read at session start and held in memory. The change applies after `/clear`,
`/compact` or a new session. Rules with `paths:` frontmatter load when you touch a matching file.

**"Agent type not found" / a skill is missing.** The agent may be disabled by your profile's `permissions.deny`. Remove the `Agent(ecc:…)` entry from
`profiles/<yours>.json`, run `scripts/apply.sh`.

**Skills appear without descriptions.** That is the skill-listing budget (`skillListingBudgetFraction`). Names always remain. See
[CUSTOMIZE §6](CUSTOMIZE.md).

**`check.sh` says `ecc@ecc` is not enabled.** Install the toolbox: `claude plugin marketplace add affaan-m/ECC && claude plugin install ecc@ecc`,
then restart Claude Code.

**Codex commands do not exist (`/codex:rescue`).** Install and enable the plugin (`claude plugin marketplace add openai/codex-plugin-cc`,
`claude plugin install codex@openai-codex`), install the CLI (`npm i -g @openai/codex`), sign in (`codex login`) and run `/codex:setup`.
Codex is optional: `apply.sh --no-codex` skips its part.

**Constant "state your facts" prompts from a hook.** That is ECC's GateGuard. The default profile already relaxes it for routine Bash and for
the EEAS repo. Add your scratch folders to `GATEGUARD_EXEMPT_GLOBS`, or see [CUSTOMIZE §7](CUSTOMIZE.md).

**`/context` shows a smaller saving than `measure.sh --real`.** `/context` is a local estimate that mis-assigns part of the trimmed tokens. Trust
the real request. See [TOKEN-ECONOMY](TOKEN-ECONOMY.md).

**Duplicate rules.** If you installed ECC's rules by hand (`~/.claude/rules/ecc/` is a real directory), its `common/` rules duplicate
`core/rules/common/core.md`. Remove `~/.claude/rules/ecc/common`. `check.sh` warns about it.

**"Settings Warning: unknown key".** Your Claude Code is older than the key (`autoCompactWindow`, `skillListingBudgetFraction`, …). Update Claude
Code, or remove the key from the profile.

**Windows.** The scripts are bash. Use WSL.

**I want out.** `scripts/revert.sh --original` restores `CLAUDE.md`, rules, skills link, `settings.json` and the Codex config from the first backup.

## FAQ

**Does it work without ECC?** No. The router table names ECC agents and skills (`ecc:planner`, `ecc:tdd-guide`, …). EEAS is the operating layer on
top of that toolbox. You could rewrite the table for another toolbox, but that is a different project.

**Does it replace ECC?** No. ECC supplies the agents, skills and hooks; EEAS decides how they are used, adds the Codex delegation protocol and the
waves protocol, and trims the context cost of the whole.

**Is it safe to give Claude "standing authorization" to delegate and to launch waves?** The authorizations are scoped (the four-point rule; waves only
after an approved plan), they never cover push, merge or deletion, and you can revoke them by editing the two sections in `CLAUDE.md`. For hard
guarantees, add `permissions` rules; see [HOW-IT-WORKS §8](HOW-IT-WORKS.md).

**Do I need a Codex plan?** Only for the delegation part. The router, gates, context savings and scripts work with Claude Code alone.

**Why 300k and not the full window?** Each turn re-reads the whole conversation (cheaply, from cache, but not free) and quality drops as it grows.
300k leaves room for large tasks while bounding the cost; change it with `/autocompact` or in the profile.

**Why English and Spanish?** The author works in Spanish and shares in English. `--lang` selects the manual; both are kept in step.
