# SDD Dev Team

Equipo de desarrollo guiado por especificaciones con [GitHub spec-kit](https://github.com/github/spec-kit) (CLI `specify`). La especificación manda:
el código se deriva de ella. Añade a la capa común (reparto Claude↔Codex, tokens, olas) este flujo.

## Preparación del proyecto
- Si falta `.specify/` en el proyecto, ejecuta `teams/sdd/setup.sh` del repo EEAS (instala `specify` con `uv` si no existe y crea el andamiaje con
  integraciones Claude y Codex). Es idempotente. No lo repitas si `.specify/` ya existe.
- Los comandos del ciclo son skills del proyecto: `/speckit-constitution`, `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`,
  `/speckit-tasks`, `/speckit-analyze`, `/speckit-checklist`, `/speckit-implement`. Invócalos tú con la herramienta Skill según la fase; el
  dueño solo dice qué quiere («una app que…»).

## Ciclo (una fase cada vez; resumen al dueño al cerrar cada una)
1. **Constitución** (`constitution`): principios del proyecto, una sola vez. Puerta 1 parcial: el dueño la aprueba.
2. **Especificar** (`specify`): QUÉ y POR QUÉ, nunca el cómo ni la tecnología. Máx. 3 preguntas; usa `clarify` si quedan ambigüedades.
3. **Plan** (`plan`): CÓMO técnico (stack, arquitectura, contratos). Puerta 1: el dueño aprueba spec + plan antes de generar tareas.
4. **Tareas** (`tasks`) y `analyze`: consistencia entre spec, plan y tareas. Corrige la spec o el plan, no solo el código.
5. **Implementar** (`implement`): ver reparto. Después, verificación y revisión; puerta 2: el dueño confirma el commit.
- Si el código y la spec divergen, se arregla la spec primero. Cambios de alcance → vuelve a `specify`/`plan`, no parches sueltos.
- Una rama y un directorio `specs/NNN-nombre/` por funcionalidad (lo gestiona spec-kit).

## Reparto Claude ↔ Codex en este equipo
- **Claude**: constitución, spec, clarificación, plan, análisis, decisiones de diseño, integración, revisión final y seguridad.
- **Codex** (reglas de delegación comunes, las cuatro condiciones): las tareas de `tasks.md` que cumplan la especificación precisa con ficheros
  propios y criterio de aceptación ejecutable; los tests a partir de la spec; boilerplate; refactor mecánico. Cada tarea delegada lleva su
  referencia a `specs/NNN-nombre/` y el comando de aceptación. Tareas marcadas `[P]` (paralelas) sin ficheros compartidos son las candidatas ideales.
- Claude revisa el diff y ejecuta la aceptación antes de marcar una tarea como hecha.

## Herramientas de apoyo
`ecc:tdd-guide`, `ecc:code-reviewer` + `<lenguaje>-reviewer`, `ecc:security-reviewer` (auth, pagos, entrada de usuario), `ecc:code-explorer` en
proyectos existentes (brownfield), `ecc:docs-lookup` para librerías.
