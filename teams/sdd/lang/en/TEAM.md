# SDD Dev Team

Spec-driven development team built on [GitHub spec-kit](https://github.com/github/spec-kit) (`specify` CLI). The spec rules: code is derived from
it. On top of the common layer (Claude↔Codex split, tokens, waves) it adds this flow.

## Project setup
- If the project has no `.specify/`, run `teams/sdd/setup.sh` from the EEAS repo (installs `specify` via `uv` if missing and scaffolds with
  Claude and Codex integrations). Idempotent. Do not repeat it when `.specify/` exists.
- The cycle commands are project skills: `/speckit-constitution`, `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`,
  `/speckit-analyze`, `/speckit-checklist`, `/speckit-implement`. You invoke them with the Skill tool by phase; the owner only says what they want.

## Cycle (one phase at a time; short summary to the owner after each)
1. **Constitution**: project principles, once. The owner approves it.
2. **Specify**: WHAT and WHY, never the how or the tech. Max 3 questions; use `clarify` for remaining ambiguity.
3. **Plan**: technical HOW (stack, architecture, contracts). Gate 1: the owner approves spec + plan before tasks are generated.
4. **Tasks** and `analyze`: consistency across spec, plan and tasks. Fix the spec or plan, not just the code.
5. **Implement**: see the split. Then verify and review; gate 2: the owner confirms the commit.
- If code and spec diverge, fix the spec first. Scope changes go back to `specify`/`plan`, not ad-hoc patches.
- One branch and one `specs/NNN-name/` directory per feature (spec-kit manages it).

## Claude ↔ Codex split in this team
- **Claude**: constitution, spec, clarification, plan, analysis, design decisions, integration, final review and security.
- **Codex** (common delegation rules, all four conditions): `tasks.md` tasks with a precise spec, own files and an executable acceptance
  command; tests derived from the spec; boilerplate; mechanical refactors. Each delegated task cites `specs/NNN-name/` and its acceptance
  command. Tasks marked `[P]` (parallel) with no shared files are the ideal candidates.
- Claude reviews the diff and runs the acceptance command before ticking a task off.

## Support tools
`ecc:tdd-guide`, `ecc:code-reviewer` + `<language>-reviewer`, `ecc:security-reviewer` (auth, payments, user input), `ecc:code-explorer` on
existing projects (brownfield), `ecc:docs-lookup` for libraries.
