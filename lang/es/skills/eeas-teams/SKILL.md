---
name: eeas-teams
description: Gestiona los equipos EEAS (equipos especializados de agentes y subagentes): listar, asignar o cambiar el equipo de un proyecto y crear equipos nuevos. Úsalo cuando el hook diga que el proyecto no tiene equipo, cuando el dueño pida cambiar de equipo o crear uno nuevo.
---

# Gestión de equipos EEAS

Repo EEAS: `dirname "$(dirname "$(readlink -f ~/.claude/CLAUDE.md)")"` (el script lo resuelve solo). Un equipo = carpeta `teams/<id>/` con `team.json`
y `lang/<es|en>/TEAM.md`. La capa común (reparto Claude↔Codex, tokens, olas) vive en `CLAUDE.md` y vale para todos.

## Asignar o cambiar el equipo de un proyecto
1. Solo cuando el dueño lo pide, o el proyecto no tiene equipo (pregunta una vez, mostrando `list`).
2. `scripts/eeas-team.sh set <id> <dir-del-proyecto>` escribe `.claude/eeas-team` y ejecuta el `setup` del equipo si lo tiene (SDD crea el andamiaje spec-kit).
3. Avisa al dueño de que el cambio se aplica por completo en la próxima sesión; en esta, lee `teams/<id>/lang/es/TEAM.md` y síguelo desde ya.
- Consultar: `scripts/eeas-team.sh list` / `show [dir]`.
- Cambiar de equipo no borra nada del proyecto; el `setup` del equipo anterior deja sus ficheros (`.specify/`…) intactos.

## Crear un equipo nuevo
1. Pregunta al dueño (máx. 3 preguntas) para qué sirve el equipo y qué herramientas/agentes usa.
2. Crea `teams/<id>/team.json` (`id`, `name`, `description`, `setup` opcional) y `teams/<id>/lang/es/TEAM.md` (+ `en/`): especialización, ciclo,
   herramientas. Usa como modelo `teams/projects-master` y `teams/sdd`.
3. El `TEAM.md` NO repite la capa común; solo la especialización. En él, indica qué parte se delega a Codex (misma regla de las cuatro condiciones).
4. Si necesita instalar algo, ponlo en `teams/<id>/setup.sh` (idempotente, recibe el directorio del proyecto).
5. Prueba con `scripts/eeas-team.sh set <id> <carpeta-de-prueba>` y `scripts/check.sh`. Commit solo con el OK del dueño.
