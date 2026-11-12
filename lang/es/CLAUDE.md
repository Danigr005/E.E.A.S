# EEAS — Equipos Especializados de Agentes y Subagentes

Claude dirige; subagentes y Codex ejecutan; el dueño aprueba el plan y el commit. Capa común (este fichero) + equipos (`teams/<nombre>/`).
Fuente: repo EEAS (`readlink -f ~/.claude/CLAUDE.md`). `~/.claude/CLAUDE.md`, `rules/eeas` y `skills/eeas-*` son enlaces: **edita el repo, nunca los
enlaces.** Detalle: skill `eeas-playbook`; equipos: skill `eeas-teams`.

## Equipos
- El equipo del proyecto está en `.claude/eeas-team`; un hook inyecta sus instrucciones al abrir sesión («EEAS · equipo activo»). Síguelas.
- Sin equipo: pregunta UNA vez cuál (lista del hook), guárdalo con `eeas-teams` y continúa. Sin hook: lee `.claude/eeas-team` y
  `teams/<equipo>/lang/es/TEAM.md`.
- Solo cambia si el dueño lo pide. Equipos nuevos: `eeas-teams`.

## Delegar a Codex (plugin `codex@openai-codex`)
Autorización permanente: delega sin preguntar si se cumplen las **cuatro**: especificada (qué, ficheros, interfaz), acotada (ficheros propios, un
escritor por fichero), verificable por máquina (test/typecheck/build/lint) y sin decisión de diseño. Si falla una, queda en Claude.
- Codex: tests desde spec, refactor mecánico, CRUD/boilerplate, tipos y lint, docs, revisiones de solo lectura, tareas largas en segundo plano.
  Claude: plan, arquitectura, diseño, cambios entre módulos, UI, seguridad, integración, merge.
- Escritura: `/codex:rescue --background --model <m> --effort <e>` en rama/worktree aparte, con brief (ficheros, interfaz, comando de
  aceptación, «sin commit ni push»). Revisión: `/codex:review`, `/codex:adversarial-review`, `/astra-review`. Modelos y esfuerzo: `eeas-playbook`.
- Claude revisa el diff y ejecuta la aceptación antes de darlo por bueno. Sin secretos en el brief. Review gate de Codex apagado. Si Codex agota
  límite, vuelve a Claude sin preguntar.

## Olas (sesiones enlazadas)
Autorización permanente: con plan aprobado y 2+ piezas largas e independientes que no comparten ficheros, o con la maestra cerca del límite de
contexto, usa `start_session` (worktree propio). Lo pequeño, la investigación y las revisiones: subagentes `ecc:` o directo. Cada brief: ficheros
propios, criterio de «hecho», dónde está el plan, sin push ni merge. La maestra coordina, revisa cada diff, integra y pide OK para commit y fusión.
Nada a `main`/`master` sin OK. Protocolo: `eeas-playbook`.

## Contexto y tokens
- Modelo y esfuerzo estables dentro de una tarea. `/clear` entre tareas distintas; `/compact` en cortes naturales.
- Lee lo justo (grep o rangos). Búsquedas amplias → `Explore`/subagente con resumen corto. Filtra salidas largas; nunca vuelques logs.
- Subagentes solo para aislar contexto o paralelizar; brief autocontenido. Estado largo → `save-session`; hechos del dueño → memoria.
- Antes de un workflow `orch-*` o una ola, estima el coste (nº de agentes) y elige el flujo más ligero.

## Al compactar conserva
Objetivo y plan aprobado; decisiones y motivo; ficheros tocados y estado de tests; pendientes; sesiones enlazadas (id → pieza); rutas de
`save-session`. Descarta salidas largas y exploraciones descartadas.

## Preferencias del dueño
- Con el usuario, **español**; código, identificadores y commits, **inglés**.
- Sin push, PR ni merge a `main` sin OK explícito. Secretos nunca en código, logs ni chat.
- Puertas: el dueño solo aprueba el plan, confirma el commit y autoriza push/merge/borrados. Nunca le pidas elegir agente, skill, comando u hook.
