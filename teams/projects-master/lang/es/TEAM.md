# Projects Master Dev Team

Equipo para crear y mantener proyectos de software de cualquier tipo (antes «CWCDT»). Añade a la capa común la especialización siguiente.

## Modo autónomo: Claude decide qué usar
El dueño solo dice "haz X". NUNCA le pidas que elija agente, skill, comando o hook, ni se lo preguntes. Antes de una tarea no trivial clasifica el
encargo y elige de la tabla (herramientas Skill y Agent, prefijo `ecc:`); si nada encaja, `ecc:ecc-guide`. Proporcionalidad: un cambio de una
línea se hace directo; la ceremonia crece con el tamaño y el riesgo. Los hooks de ECC son automáticos: no los actives ni los menciones. Pide al
dueño solo: aprobar el plan (puerta 1), confirmar el commit (puerta 2), y push/merge/borrados.

| Encargo | Usar |
|---|---|
| Algo desde cero (juego, app, web, herramienta) | `orch-build-mvp`; sin diseño previo, antes `plan-prd` + `plan` (máx. 3 preguntas) |
| Capacidad nueva / cambio / bug / refactor | `orch-add-feature` / `orch-change-feature` / `orch-fix-defect` / `orch-refine-code` |
| Plan, PRD, arquitectura, decisión técnica | `planner`, `plan-prd`, `architect`, `code-architect`, skills `architecture-decision-records`, `api-design`, `database-migrations` |
| Antes de escribir código | skill `search-first`; docs de librerías `docs-lookup`; investigación amplia `deep-research` |
| Entender código ajeno o heredado | `code-explorer`, `codebase-onboarding`, `code-tour`, `spec-miner` |
| Tests | `tdd-workflow` + `tdd-guide`; E2E `e2e-runner`/`e2e-testing`; cobertura `test-coverage`; navegador `browser-qa` |
| Revisión | `code-review` + `<lenguaje>-reviewer`; PR `review-pr`; según caso `pr-test-analyzer`, `silent-failure-hunter`, `type-design-analyzer`, `code-simplifier`; BD `database-reviewer`; otro proveedor: Codex (ver Delegación) |
| Seguridad (auth, pagos, secretos, entrada, ficheros, cripto) | `security-reviewer` + skill `security-review` (`security-scan` para auditar la config) |
| Build/tipos rotos | `build-fix` o `<lenguaje>-build-resolver` |
| UI/frontend/juegos | `frontend-patterns`, `frontend-design-direction`, `design-system`, `a11y-architect`, `react-/vue-reviewer`, `motion-*`; verificar con `browser-qa`/`e2e-runner` |
| Lentitud, memoria, bundle | `performance-optimizer`, `react-performance`, `benchmark` |
| Despliegue, infra, CI | `deployment-patterns`, `docker-patterns`, `kubernetes-patterns`, `github-ops` |
| Docs, marketing, SEO, contenido | `doc-updater` (`update-docs`, `update-codemaps`), `marketing-agent`, `seo-specialist`, `content-engine` |
| Skills de stack | Al tocar un lenguaje/framework carga sus `*-patterns`, `*-testing`, `*-security` si existen |
| Contexto y memoria | `context-budget`, `strategic-compact` cerca del límite; `save-session` al cerrar trabajo largo; `resume-session` al abrir proyecto con sesión previa; `learn-eval` tras resolver algo no obvio |

Los agentes de ECC de stacks que no usas pueden estar desactivados en `permissions.deny` de `~/.claude/settings.json` (mira tu perfil de EEAS).
Si un proyecto necesita uno, quítalo de ahí. Si algo se repite o falla, usa `hookify` / `learn` para que quede como regla, no como recuerdo.

## Flujo de trabajo
- Flujo: investigar y reutilizar → plan (`ecc:planner`) → TDD (`ecc:tdd-guide`) → revisión (`ecc:code-reviewer`, `ecc:security-reviewer`) →
  verificar → commit. Agentes invocados como `ecc:<nombre>`.
