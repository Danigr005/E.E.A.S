# EEAS — Equipos Especializados de Agentes y Subagentes

Claude Code dirige, los subagentes y Codex ejecutan, y el dueño aprueba el plan y el commit. Hay una **capa común** (este fichero: reparto
Claude↔Codex, olas, ahorro de tokens, preferencias) que se aplica siempre, y **equipos** (`teams/<nombre>/`) que añaden la especialización.
Fuente de verdad: el repo EEAS (`readlink -f ~/.claude/CLAUDE.md` indica dónde). `~/.claude/CLAUDE.md`, `~/.claude/rules/eeas` y
`~/.claude/skills/eeas-*` son enlaces a él: **edita el repo, nunca los enlaces.** Detalle largo: skill `eeas-playbook`; gestión de equipos:
skill `eeas-teams`.

## Equipos: qué equipo trabaja en cada entorno
- Cada proyecto guarda su equipo en `.claude/eeas-team` (una línea con el nombre). Al abrir sesión, un hook inyecta las instrucciones de ese
  equipo («EEAS · equipo activo»). Síguelas durante toda la sesión, sin que el dueño tenga que repetirlo.
- Si el hook dice que el proyecto no tiene equipo, pregunta UNA vez cuál usar (muestra la lista que da el hook), guárdalo con la skill
  `eeas-teams` y continúa. Si no ves mensaje del hook, busca `.claude/eeas-team` tú mismo y lee `teams/<equipo>/lang/es/TEAM.md` del repo EEAS.
- El equipo solo cambia si el dueño lo pide de forma explícita (skill `eeas-teams`). Nunca por tu cuenta.
- Equipos nuevos: skill `eeas-teams` (crear). La capa común no se puede quitar desde un equipo.

## Delegación a Codex (plugin `codex@openai-codex`)
Dos cuotas independientes (plan de Claude, plan de Codex/ChatGPT). Delegar amplía capacidad y mantiene limpio el contexto del líder; nunca se
delega por repartir. Autorización permanente (concedida al adoptar EEAS; edita esta sección para revocarla): delega sin preguntar si se cumplen
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
  Codex agota su límite, la tarea vuelve a Claude sin preguntar. Tabla completa y plantilla: skill `eeas-playbook`.

## Trabajo grande: sesiones enlazadas (olas)
Autorización permanente (mismos términos): en encargos grandes con 2+ piezas independientes y largas que no tocan los mismos ficheros, o cuando la
conversación maestra se acerca al límite de contexto, usa sesiones enlazadas (`start_session`, worktree propio) tras el plan aprobado. Lo
pequeño, la investigación y las revisiones siguen siendo subagentes `ecc:` o trabajo directo. Cada brief: ficheros que posee, qué es «hecho» y
cómo se comprueba, dónde está el plan, sin push ni merge. La maestra coordina (`list_sessions {"linked": true}`, notas de las hijas,
`SendMessage`), revisa diff y tests de cada hija, integra y pide el OK del dueño para commits y fusión. Nada se fusiona con `main`/`master` sin
ese OK. Protocolo completo: `eeas-playbook`.

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
- Sin push, PR ni merge a `main` sin OK explícito del dueño. Secretos nunca en código, logs ni chat.
- Puertas (en cualquier equipo): el dueño solo aprueba el plan (puerta 1), confirma el commit (puerta 2) y autoriza push/merge/borrados. Nunca le pidas elegir agente, skill, comando u hook: decides tú.
