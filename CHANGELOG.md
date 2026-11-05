# Changelog

## 0.1.0 — 2026-11-05
First public release of CWCDT (Code With Codex Dev Team).

### Methodology
- Operating manual in English and Spanish (`lang/`): router table, two gates, four-point Codex delegation rule, waves, token habits, compaction instructions.
- On-demand `cwcdt-playbook` skill: model and effort table, brief template, delegation flow, waves protocol.
- One core rule (`rules/cwcdt/common/core.md`) replacing ten ECC common rules; per-language rules kept.

### Tooling
- `scripts/`: `apply` (links, profile merge, optional Codex default model), `check`, `revert`, `measure`, `ecc-update`, `test-sandbox`.
- Profiles: `default` and an example `ts-py-rust` stack profile.
- Status line with context, cache, 5h and 7d usage.

### Measured (reference setup)
- Prompt of the first real request 81.3k → 60.4k tokens (−26%); memory files −73%. See `docs/TOKEN-ECONOMY.md`.

### Tested with
Claude Code 2.1.234, ECC 2.2.3 (`b38be6a`), Codex CLI 0.164 with plugin 1.0.6, Linux.
