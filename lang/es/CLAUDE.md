# CWCDT — Code With Codex Dev Team

Metodología global: Claude Code dirige, los subagentes especialistas (la caja de herramientas ECC) y Codex ejecutan, y el dueño aprueba el plan y
el commit. Fuente de verdad: el repo de CWCDT (`readlink -f ~/.claude/CLAUDE.md` indica dónde). `~/.claude/CLAUDE.md`, `~/.claude/rules/cwcdt` y
`~/.claude/skills/cwcdt-playbook` son enlaces a él: **edita el repo, nunca los enlaces.** Detalle largo (delegación a Codex, olas, hábitos de
tokens): skill `cwcdt-playbook`. Guía de la caja de herramientas: `ecc:ecc-guide`.

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

Los agentes de ECC de stacks que no usas pueden estar desactivados en `permissions.deny` de `~/.claude/settings.json` (mira tu perfil de CWCDT).
Si un proyecto necesita uno, quítalo de ahí. Si algo se repite o falla, usa `hookify` / `learn` para que quede como regla, no como recuerdo.

## Delegación a Codex (plugin `codex@openai-codex`)
Dos cuotas independientes (plan de Claude, plan de Codex/ChatGPT). Delegar amplía capacidad y mantiene limpio el contexto del líder; nunca se
delega por repartir. Autorización permanente (concedida al adoptar CWCDT; edita esta sección para revocarla): delega sin preguntar si se cumplen
las **cuatro**: (1) especificada: qué, ficheros e interfaz; (2) acotada: ficheros propios, un solo escritor por fichero; (3) verificable por
máquina: test/typecheck/build/lint que Claude ejecuta después; (4) sin decisión de diseño ni ambigüedad. Si falla una, se queda en Claude.
- A Codex: tests desde spec, refactor mecánico, CRUD/boilerplate, errores de tipos y lint, docs, tareas largas en segundo plano, revisiones de
  solo lectura. En Claude: plan/PRD/arquitectura, diseño, cambios entre módulos, UI con criterio visual, decisión final de seguridad,
  integración, merge y orquestación.
- Modelos Codex (ejemplos; mira la lista de modelos de tu cuenta): ligeros (`gpt-6-luna`, `gpt-reserve`) para lo mecánico; el de trabajo diario
  (`gpt-6.1-sol`, medium; high si el bug no es trivial); el de frontera (`gpt-6-astra`) solo para revisar o casos difíciles;
  `xhigh`/`max`/`ultra` solo excepcional. Revisión: `/codex:review`, `/codex:adversarial-review`, `/astra-review`. Escritura:
  `/codex:rescue --background --model <m> --effort <e>` en rama o worktree aparte, con brief (ficheros, interfaz, comando de aceptación,
  «sin commit ni push»).
- Claude revisa el diff y ejecuta la aceptación antes de darlo por bueno. Nunca secretos en el brief. Review gate de Codex siempre apagado. Si
  Codex agota su límite, la tarea vuelve a Claude sin preguntar. Tabla completa y plantilla: skill `cwcdt-playbook`.

## Trabajo grande: sesiones enlazadas (olas)
Autorización permanente (mismos términos): en encargos grandes con 2+ piezas independientes y largas que no tocan los mismos ficheros, o cuando la
conversación maestra se acerca al límite de contexto, usa sesiones enlazadas (`start_session`, worktree propio) tras el plan aprobado. Lo
pequeño, la investigación y las revisiones siguen siendo subagentes `ecc:` o trabajo directo. Cada brief: ficheros que posee, qué es «hecho» y
cómo se comprueba, dónde está el plan, sin push ni merge. La maestra coordina (`list_sessions {"linked": true}`, notas de las hijas,
`SendMessage`), revisa diff y tests de cada hija, integra y pide el OK del dueño para commits y fusión. Nada se fusiona con `main`/`master` sin
ese OK. Protocolo completo: `cwcdt-playbook`.

## Contexto y tokens (siempre)
- Mantén modelo y esfuerzo estables dentro de una tarea (cada cambio rompe la caché). `/clear` entre tareas sin relación; `/compact` en cortes
  naturales, no a mitad de tarea.
- Lee lo justo: grep o rangos antes de ficheros enteros. Lecturas y búsquedas amplias → `Explore` o subagente que devuelva un resumen corto.
  Salidas largas (tests, logs, builds): filtra (`grep`, `tail`); nunca vuelques logs enteros.
- Subagentes solo si aíslan contexto o paralelizan trabajo independiente; brief autocontenido y resultado en pocas líneas.
- Estado de trabajo largo → `save-session` (o nota en el plan); hechos duraderos del dueño → memoria automática. Sin duplicarlos.
- Antes de lanzar un workflow `orch-*` o una ola, estima el coste (nº de agentes) y elige el flujo más ligero que cubra el riesgo.

## Compact instructions
Al compactar conserva: objetivo y plan aprobado; decisiones tomadas y su motivo; ficheros tocados y estado de tests/build; pendientes y siguiente
paso; sesiones enlazadas (id → pieza) y qué falta integrar; rutas de `save-session`. Descarta: salidas largas de comandos, exploraciones
descartadas, texto de skills ya aplicadas.

## Preferencias del dueño (edítame)
- Con el usuario, **español**. Código, identificadores y commits, **inglés**.
- Flujo: investigar y reutilizar → plan (`ecc:planner`) → TDD (`ecc:tdd-guide`) → revisión (`ecc:code-reviewer`, `ecc:security-reviewer`) →
  verificar → commit. Agentes invocados como `ecc:<nombre>`.
- Sin push, PR ni merge a `main` sin OK explícito del dueño. Secretos nunca en código, logs ni chat.
