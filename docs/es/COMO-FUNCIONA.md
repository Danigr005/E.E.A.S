# Cómo funciona EEAS

[English](../HOW-IT-WORKS.md)

## 1. La idea en un minuto

Describes un resultado. Un **líder** (tu sesión principal de Claude Code) clasifica el encargo, elige especialistas de una caja de herramientas,
escribe un plan y espera tu aprobación. Después construye con tests primero, entrega las piezas acotadas y verificables por máquina a un
**segundo ingeniero** (Codex), lo revisa todo (opcionalmente con los ojos de otro proveedor), verifica y te pide confirmar el commit. Entre esas
dos puertas no te pregunta qué agente o skill usar. Durante todo el proceso el contexto se mantiene pequeño y medido, así que las sesiones van
rápidas y la cuota dura más.

EEAS no es un framework de agentes nuevo. Es un **manual de operación** (`CLAUDE.md`), unas pocas **reglas**, un **perfil de ajustes** y
**scripts** que hacen que Claude Code, la caja de herramientas [ECC](https://github.com/affaan-m/ECC) y Codex funcionen como un solo equipo.

## 2. Roles

| Rol | Quién | Qué hace |
|---|---|---|
| **Dueño** | Tú | Plantea objetivos. Aprueba el plan (puerta 1) y el commit (puerta 2). Decide push, merge y borrados. |
| **Líder** | Tu sesión principal de Claude Code | Clasifica, planifica, integra, revisa diffs y decide qué delegar. Guarda el contexto de la conversación. |
| **Especialistas** | Subagentes de ECC (`planner`, `tdd-guide`, `code-reviewer`, `security-reviewer`, revisores y resolutores de build por lenguaje, `e2e-runner`, …) | Trabajan en su propio contexto y devuelven un resultado corto, así las lecturas pesadas no hinchan al líder. |
| **Segundo ingeniero** | Codex, mediante el plugin oficial de OpenAI para Claude Code | Toma tareas acotadas y verificables por máquina, y revisiones de solo lectura, con su propia cuota. |
| **Sesiones enlazadas («olas»)** | Sesiones hijas de Claude en sus propios worktrees de git | Poseen piezas independientes de un encargo grande; el líder (la «maestra») coordina e integra. |

## 3. El bucle y las dos puertas

1. **Clasificar.** La tabla de enrutado de `CLAUDE.md` asigna cada tipo de encargo (capacidad nueva, bug, refactor, proyecto desde cero, tema de
   seguridad…) a los agentes y skills a usar. Si nada encaja, `ecc:ecc-guide` lista lo que existe.
2. **Investigar y reutilizar.** Antes de escribir código nuevo: busca en el repo, en librerías existentes y en documentación (`search-first`,
   `docs-lookup`).
3. **Planificar.** Un plan con ficheros, pasos, riesgos y cómo se verificará.
4. **Puerta 1.** Apruebas, cambias o rechazas el plan. En trabajo no trivial no se construye nada antes.
5. **Construir, tests primero.** Test que falla, implementación mínima, refactor. Trabajan los especialistas; las piezas acotadas pueden ir a
   Codex (sección 5).
6. **Revisar.** `code-reviewer` y el revisor del lenguaje, más `security-reviewer` en auth, entrada de usuario, ficheros, cripto y pagos.
   Opcionalmente, una revisión cruzada con Codex.
7. **Verificar.** Tests, tipos, build y lint, ejecutados por Claude. «Hecho» significa que las comprobaciones pasan, no que alguien lo diga.
8. **Puerta 2.** El líder resume los cambios y propone el mensaje de commit. Tú confirmas. **Push, PR, merge y borrados vuelven a preguntar.**

**Proporcionalidad.** La ceremonia crece con el tamaño y el riesgo: un cambio de una línea se edita directamente; un bug pequeño lleva primero
un test de regresión (`orch-fix-defect`); una funcionalidad nueva recorre el bucle completo (`orch-add-feature`); un proyecto desde cero
empieza con un PRD y un flujo de MVP (`orch-build-mvp`).

**¿Cómo de firmes son las puertas?** Son instrucciones de `CLAUDE.md` que Claude sigue, respaldadas por el modo plan y las confirmaciones de
permisos de Claude Code. Si necesitas una garantía dura (por ejemplo, ningún `git push` sin confirmación), añade además una regla en
`permissions.ask` o `permissions.deny` de tus ajustes. EEAS no finge que el texto sea por sí solo una frontera de seguridad.

## 4. El enrutador

La tabla de `CLAUDE.md` es el corazón del «modo autónomo»: el dueño nunca elige un agente. Cada fila nombra las skills y agentes de un tipo de
trabajo. Mantenla corta: cada fila cuesta tokens en cada sesión. Para cambiarla, edita `lang/<l>/CLAUDE.md` en el repo (ver
[CUSTOMIZE](../CUSTOMIZE.md), en inglés). Las reglas que valen para todo están en `core/rules/common/core.md`; las de cada lenguaje (`python/`,
`rust/`, `typescript/`, `web/`) solo se cargan al tocar ficheros que coinciden.

## 5. Delegar a Codex

**Por qué.** Dos cuotas en vez de una, un líder cuyo contexto no se llena de trabajo mecánico y un revisor independiente de otro proveedor.
**No** para repartir por repartir.

**La regla: las cuatro, o se queda en Claude.**

1. *Especificada*: qué hacer, qué ficheros, qué interfaz.
2. *Acotada*: ficheros propios; nadie más los escribe (un solo escritor por fichero).
3. *Verificable por máquina*: un test, typecheck, build o lint que Claude ejecuta después.
4. *Sin decisión de diseño ni ambigüedad.*

| Buenos candidatos para Codex | Se queda en Claude |
|---|---|
| Tests a partir de una especificación escrita | Plan, PRD, arquitectura |
| Refactors mecánicos con tests en verde | Decisiones de diseño y ambigüedad |
| CRUD y boilerplate con interfaz definida | Cambios que cruzan módulos |
| Errores de tipos y lint | UI que necesita criterio visual |
| Documentación | La decisión final de seguridad |
| Tareas largas en segundo plano, revisiones de solo lectura | Integración, merge, orquestación |

**Modelos y esfuerzo.** Modelos ligeros para lo mecánico, uno de trabajo diario para lo habitual y el de frontera solo para revisar y casos
difíciles; los niveles de Claude se usan igual (tabla en el [playbook](../../lang/es/skills/eeas-playbook/SKILL.md)). Elige modelo y esfuerzo al
empezar la tarea: cambiarlos a mitad rompe la caché del prompt.

**Flujo.** Brief (objetivo, ficheros propios, interfaz, comando de aceptación, «sin commit ni push») → rama o worktree aparte →
`/codex:rescue --background` → `/codex:status` / `/codex:result` → Claude revisa el diff y **ejecuta él mismo el comando de aceptación** → una
ronda de corrección si hace falta → integrar. Un «hecho» de Codex no cuenta hasta que las comprobaciones pasan.

**Revisión cruzada.** `/codex:review`, `/codex:adversarial-review` o `/astra-review` (veredicto estructurado con ciclo de arreglos) dan una
segunda opinión de otro proveedor. Claude verifica cada hallazgo contra el código antes de actuar.

**Presupuesto.** Si una cuota va justa, el trabajo delegable pasa a la otra; si Codex se agota, la tarea vuelve a Claude sin preguntar. El «review
gate» de Codex queda apagado porque crea bucles Claude↔Codex que vacían la cuota. Apunta cada delegación en el
[registro de calibración](../CODEX-CALIBRATION.md) y ajusta la tabla de modelos con resultados reales.

## 6. Olas (sesiones enlazadas)

En un encargo grande con dos o más piezas independientes y largas que no tocan los mismos ficheros, la sesión maestra lanza una sesión enlazada
por pieza (`start_session`, cada una en su worktree con el contexto limpio). Cada brief indica los ficheros que posee, qué es «hecho» y cómo
comprobarlo, dónde está el plan y que no hace push ni merge. La maestra las sigue (`list_sessions`, notas de las hijas, `SendMessage`), revisa el
diff y los tests de cada una, integra y te pide la aprobación de commit y fusión. Las hijas no hablan entre sí. Esto también resuelve los
límites de contexto: la maestra puede guardar su estado (`save-session`) y tú continúas en otra conversación mientras las hijas siguen.

## 7. Contexto y tokens

Cada petición vuelve a leer el «prompt fijo»: prompt del sistema, definiciones de herramientas, tus ficheros de memoria y las listas de skills y
agentes. EEAS reduce lo que controlas (memoria, lista de skills, lista de agentes) y limita cuánto puede crecer una conversación
(`autoCompactWindow`, instrucciones de compactación, una barra de estado que avisa). Detalles, cifras y método de medida:
[TOKEN-ECONOMY](../TOKEN-ECONOMY.md) (en inglés).

## 8. Barreras: qué hace cumplir qué

| Barrera | Mecanismo | Firmeza |
|---|---|---|
| Dos puertas (plan, commit) | Instrucciones de `CLAUDE.md` + modo plan y confirmaciones de permisos de Claude Code | Blanda; añade reglas de `permissions` para hacerla dura |
| Nunca push / merge / borrar sin OK | `CLAUDE.md` + tus reglas de permisos | Blanda salvo que añadas `permissions.ask` / `deny` |
| Hechos antes de editar; sin secretos en el código | Hooks de ECC (GateGuard, comprobaciones previas al commit) y la regla base | Dura (los hooks bloquean), ajustada por el perfil |
| Codex no puede hacer commit ni push | El brief, `codex/AGENTS.md` y un worktree aparte | Blanda + aislamiento |
| Todo cambio de ajustes es reversible | Copias de `apply.sh` y `revert.sh`, probados con `test-sandbox.sh` | Dura |

## 9. Un ejemplo (ilustrativo)

> Tú: «Añade rate limiting al endpoint /login.»

1. **Clasificar**: capacidad nueva → `orch-add-feature`. `search-first` encuentra una librería de middleware; `docs-lookup` confirma su API.
2. **Plan** (`planner`): cinco pasos, tres ficheros, riesgo: bloquear a usuarios legítimos. → **Puerta 1**: respondes «ok».
3. **Construir**: Codex (`gpt-reserve`) escribe los tests unitarios desde la especificación: acotado y verificable (`pnpm test
   src/auth/rateLimit.test.ts` debe fallar primero). El líder escribe el middleware y lo conecta, porque cruza módulos.
4. **Revisar**: `typescript-reviewer` y `security-reviewer` (autenticación); `/codex:adversarial-review` como comprobación de otro proveedor;
   Claude verifica cada hallazgo.
5. **Verificar**: suite completa, typecheck y lint en verde.
6. **Puerta 2**: el líder muestra el resumen del diff y propone `feat: rate limit login attempts`. Confirmas. El push vuelve a preguntar.

## 10. Dónde vive cada cosa

| Ruta | Para qué |
|---|---|
| `lang/<l>/CLAUDE.md` → `~/.claude/CLAUDE.md` | El manual de operación |
| `lang/<l>/skills/eeas-playbook` → `~/.claude/skills/eeas-playbook` | Detalle bajo demanda |
| `core/rules` → `~/.claude/rules/eeas` | Reglas base y por lenguaje |
| `profiles/*.json` → fusionados en `~/.claude/settings.json` | Ajuste de contexto y hooks, perfiles de stack |
| `codex/AGENTS.md` → `~/.codex/AGENTS.md` | Reglas para Codex al recibir una tarea delegada |
| `~/.claude/eeas.lang`, `eeas.profile` | Recuerdan tus elecciones para que `apply.sh` y `check.sh` coincidan |
| `~/.claude/backups/cwcdt-<fecha>/` | Todo lo que `apply.sh` sustituyó |
