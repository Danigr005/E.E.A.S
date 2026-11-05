# Contributing

Issues and pull requests are welcome, especially: results from other machines (macOS, other stacks), calibration data for Codex models, and
corrections to the documentation.

- Keep `lang/en` and `lang/es` in step; `scripts/check.sh` warns when their lengths drift apart.
- Keep `CLAUDE.md` small. Every line is paid for in every session; long detail belongs in the playbook skill.
- Before opening a PR run `scripts/test-sandbox.sh` (apply → check → idempotent re-apply → revert for every language and profile, on throwaway
  copies; it never touches your real config) and `bash -n scripts/*.sh`.
- Do not commit secrets, personal paths, or backups. `.gitignore` already excludes `backups/`; the toolbox clone lives outside the repo (`../toolbox-src`).
- Measurements: include the command (`scripts/measure.sh <label> --real`) and your Claude Code and ECC versions.
- Commit messages: `<type>: <description>` (feat, fix, refactor, docs, test, chore, perf, ci).
