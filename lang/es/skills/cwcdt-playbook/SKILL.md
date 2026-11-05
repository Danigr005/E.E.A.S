---
name: cwcdt-playbook
description: Playbook de CWCDT para encargos grandes: delegación Claude↔Codex (modelos, esfuerzo, plantilla de brief, calibración), protocolo de olas (sesiones enlazadas) y hábitos de ahorro de tokens y retención de contexto. Úsalo antes de delegar a Codex, de lanzar sesiones enlazadas o de planificar un encargo grande.
---

# Playbook de CWCDT

Detalle de lo que `CLAUDE.md` solo resume. Se carga bajo demanda para no pagar estos tokens en cada turno.

## 1. Delegación Claude ↔ Codex

Cuotas independientes: tu plan de Claude y tu plan de Codex (ChatGPT). Se delega para ampliar capacidad y mantener limpio el contexto del líder.

### Regla: las cuatro, o se queda en Claude
1. **Especificada**: qué hacer, qué ficheros, qué interfaz.
2. **Acotada**: ficheros propios; nadie más los escribe.
3. **Verificable por máquina**: test, typecheck, build o lint que Claude ejecuta después. Sin criterio de aceptación no se delega.
4. **Sin decisión de diseño ni ambigüedad.**

### Modelos y esfuerzo
Esfuerzo por defecto de Claude: `medium` en Sonnet 5.5 y Opus 5.5 (sube a `high` si la verificación es crítica). Cambiar modelo o esfuerzo a
mitad de tarea rompe la caché: elige al principio. Las filas de Codex son ejemplos de una cuenta (noviembre de 2026): lee la tuya con el
selector de modelos de `codex` o en `~/.codex/models_cache.json` y ajusta.

| Quién | Modelo (esfuerzo) | Para qué |
|---|---|---|
| Claude | Opus 5.5 (high) | Plan, arquitectura, ambigüedad, orquestar, integrar, revisar diffs |
| Claude | Fable 5.1 | Solo problemas difíciles o fixes que Sonnet/Codex no resuelven |
| Claude | Sonnet 5.5 (medium) | Implementación estándar que no se delega: cruza módulos, UI, necesita skills/hooks |
| Claude | Haiku 5.5 (low) | Mecánico pequeño que ya está en la conversación |
| Codex | `gpt-6-luna` (low–medium) | Mecánico: renombrados, boilerplate, formato, docs, lint |
| Codex | `gpt-reserve` (medium) | Código ágil y barato: tests desde una especificación, CRUD, errores de tipos |
| Codex | `gpt-6.1-sol` (medium; high si el bug no es trivial) | Trabajo diario: refactor acotado con tests en verde, feature con interfaz definida, bug ya reproducido |
| Codex | `gpt-6-astra` (medium–high) | Revisión cruzada y casos difíciles; gasta mucha cuota, no para rutina |

`xhigh`/`max`/`ultra` solo de forma excepcional y anotada: vacían la ventana de 5 h. Corrige esta tabla con el uso real (`docs/CODEX-CALIBRATION.md`).

### Plantilla de brief (a Codex)
```
OBJETIVO: <una frase>
FICHEROS QUE POSEES (solo estos): <rutas>
INTERFAZ / CONTRATO: <firmas, tipos, comportamiento esperado>
HECHO CUANDO: <comando exacto, p. ej. `pnpm test src/foo && pnpm typecheck`>
RESTRICCIONES: sin commit ni push; no toques otros ficheros; sin dependencias nuevas salvo <...>; no leas .env ni secretos
SALIDA: resumen de ≤10 líneas: ficheros cambiados, resultado del comando de aceptación, dudas
```

### Flujo de una delegación de escritura
1. Comprueba la regla de las cuatro. Si falla una, hazlo en Claude.
2. Rama o worktree aparte: `git worktree add ../wt-<tarea> -b codex/<tarea>`.
3. `/codex:rescue --background --model <m> --effort <e> "<brief>"`.
4. `/codex:status` y `/codex:result` (sin sondear en bucle; sigue con otro trabajo).
5. Revisa `git diff`, ejecuta el comando de aceptación, aplica el `<lenguaje>-reviewer`. Si falla: una ronda de corrección con `--resume`; si
   vuelve a fallar, lo hace Claude.
6. Integra en la rama de trabajo, limpia el worktree y apunta el resultado en `docs/CODEX-CALIBRATION.md`.

### Revisión cruzada (solo lectura)
Úsala cuando el revisor sería el mismo modelo que escribió el código, o en cambios de riesgo medio/alto: `/codex:review` (rutina),
`/codex:adversarial-review` (diseño, seguridad, supuestos), `/astra-review` (veredicto estructurado con ciclo de arreglos). Claude verifica cada
hallazgo contra el código antes de tocar nada: Codex también se equivoca.

### Presupuesto
Claude: la barra de estado muestra uso 5h/7d (`/usage` da el desglose). Codex: ventana de 5 h y tope semanal propios; consulta su estado en su app.
Si una cuota va justa, empuja el trabajo delegable a la otra; si Codex se agota, vuelve a Claude (Sonnet/Haiku) sin preguntar. El review gate de
Codex (`--enable-review-gate`) queda apagado: crea bucles Claude↔Codex que vacían la cuota.

## 2. Olas (sesiones enlazadas)
- **Cuándo**: encargo grande con 2+ piezas independientes y largas que no tocan los mismos ficheros (p. ej. modelado, HUD, rendimiento,
  servidor), o la maestra se acerca al límite de contexto. Lo pequeño, la investigación y las revisiones son subagentes `ecc:` o trabajo directo.
- **Cómo**: tras el plan aprobado, la maestra lanza una sesión por pieza con `start_session` (worktree propio, contexto limpio). El brief dice:
  ficheros que posee (un solo escritor por fichero), qué es «hecho» y cómo se comprueba, dónde está el plan o la sesión guardada, y que no hace
  push ni merge. Anota en el plan o en `save-session` qué sesión hace qué.
- **Coordinar**: `list_sessions {"linked": true}`; cada hija avisa al terminar un turno; detalle con `list_events`; correcciones con
  `SendMessage` (id `local_…`); sin sondear. Las hijas no hablan entre sí: todo pasa por la maestra.
- **Integrar**: la maestra revisa diff y tests de cada hija, integra, y pide al dueño el OK de commits y fusión. Nada se fusiona con
  `main`/`master` sin ese OK.
- **Contexto**: cerca del límite, `save-session`; el dueño continúa con `resume-session` en otra conversación; las hijas siguen vivas.
- Una hija puede delegar sub-piezas suyas a Codex con la regla de las cuatro.

## 3. Ahorro de tokens y retención
Qué hace ya la configuración sin que lo pidas:
- Memoria fija mínima (`CLAUDE.md` + 1 regla base); el detalle vive aquí y se carga bajo demanda.
- `autoCompactWindow` = 300k: compacta antes de que cada turno arrastre cientos de miles de tokens; `CLAUDE.md` se reinyecta desde disco tras
  compactar y su sección «Compact instructions» guía qué se conserva.
- Lista de skills con presupuesto reducido; agentes de stacks que no usas se pueden desactivar; plugins LSP para navegar por símbolos en vez de
  leer ficheros.
- Hooks de ECC (guardado de estado antes de compactar, resumen de sesión, carga del contexto previo, calidad tras editar) activos.
- Barra de estado: `ctx usados/ventana · caché · 5h · 7d` y aviso `/compact soon` al 60 % de la ventana.

Qué haces tú (o yo) a mano:
- `/clear` al cambiar de tarea; `/compact <foco>` en cortes naturales; `/rewind` si una vía no funciona (conserva la caché).
- No cambiar de modelo o esfuerzo a mitad de tarea; activar fast mode solo al inicio.
- Lecturas amplias a `Explore`/subagente con resumen corto; salidas de comandos filtradas.
- Medir: `scripts/measure.sh <etiqueta> [--real]` (coste fijo de contexto); `/usage` (desglose por skills, agentes, plugins, MCP); `/doctor` y
  `/skill-doctor` (coste de la lista de skills y skills sin uso).

## 4. Mantenimiento (desde el repo de CWCDT)
- `scripts/apply.sh [--dry-run]`: enlaces + ajustes + Codex (idempotente, con copia de seguridad en `~/.claude/backups/`).
- `scripts/check.sh`: verifica enlaces, ajustes y el plugin de la caja de herramientas.
- `scripts/ecc-update.sh [--pull]`: comprueba si ECC tiene novedades; revisa el diff antes de `--pull`.
- Revertir: `scripts/revert.sh [--original]`.
