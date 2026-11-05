# CWCDT — Code With Codex Dev Team

Una metodología de desarrollo autónoma, de dos puertas, para agentes de programación con IA. **Tú dices qué quieres. Claude Code dirige un
equipo de subagentes especialistas, entrega a Codex las partes mecánicas y verificables por máquina, y solo te para dos veces: para aprobar el
plan y para confirmar el commit.** Todo dentro de un presupuesto de contexto reducido y medido.

[English](README.md) · Español

> Proyecto comunitario independiente. Sin afiliación ni respaldo de Anthropic, OpenAI ni los autores de ECC. «Claude» y «Claude Code» son
> marcas de Anthropic; «Codex» y «ChatGPT» son marcas de OpenAI. Ver [NOTICE](NOTICE).

## Por qué

Las configuraciones de agentes suelen crecer hasta ser un montón de agentes, skills, hooks y reglas que nadie sabe explicar, y que se comen en
silencio tu ventana de contexto y tu cuota antes de que escribas nada. CWCDT es lo contrario: un manual de operación pequeño y con criterio, más
unos pocos scripts que

- deciden **quién hace qué** (una tabla de enrutado y una regla de delegación de cuatro puntos),
- te dejan **el control** donde importa (dos puertas; nunca push, merge ni borrados sin tu OK),
- gastan **menos tokens** (el prompt fijo de la configuración de referencia pasó de 81,3k a 60,4k tokens, −26 %, medido con peticiones reales), y
- son **reproducibles y reversibles** (un repo, enlaces simbólicos, copias de seguridad, una prueba aislada).

## El bucle

```
 tú: "añade rate limiting a la API"
        │
        ▼
 CLASIFICAR (tabla) ─▶ INVESTIGAR Y REUTILIZAR ─▶ PLAN ───▶ ◆ PUERTA 1: apruebas el plan
                                                                    │
        ┌───────────────────────────────────────────────────────────┘
        ▼
 CONSTRUIR con tests primero ── especialistas (planner, tdd-guide, …)
        │                        └─ Codex para piezas acotadas y verificables (regla de cuatro puntos)
        ▼
 REVISAR  revisores de código + lenguaje + seguridad; revisión cruzada opcional con Codex
        ▼
 VERIFICAR (tests, build, lint) ─▶ COMMIT ───────────────────▶ ◆ PUERTA 2: confirmas el commit
                                                                push / merge / borrar: siempre se pregunta
```

## Qué incluye

| Pieza | Qué hace |
|---|---|
| `lang/{en,es}/CLAUDE.md` | El manual que Claude lee en cada sesión: tabla de enrutado, regla de delegación, olas, hábitos de tokens, instrucciones de compactación. Pequeño a propósito (≈3,5k tokens). |
| `lang/{en,es}/skills/cwcdt-playbook` | El detalle largo (modelos y esfuerzo, plantilla de brief, protocolo de olas, consejos de tokens), cargado solo cuando hace falta. |
| `rules/cwcdt/` | Una regla base (estilo, pruebas, seguridad, revisión, git) y reglas por lenguaje que solo se cargan al tocar ficheros que coinciden. |
| `profiles/` | Ajustes que se fusionan en `~/.claude/settings.json`: ventana de autocompactado, presupuesto de skills, hooks; perfiles de stack que apagan agentes que no usas. |
| `codex/AGENTS.md` | Qué debe hacer Codex cuando Claude le delega una tarea. |
| `statusline.mjs` | `ctx usados/ventana · cache · 5h · 7d` y aviso para `/compact`. |
| `scripts/` | `apply`, `check`, `revert`, `measure`, `ecc-update`, `test-sandbox`. |

## Inicio rápido (unos 10 minutos)

Requisitos: [Claude Code](https://claude.com/claude-code), `git`, `python3`, Node 18+. Opcional, para delegar: un plan de ChatGPT con el CLI de Codex.
Probado en Linux; en macOS debería funcionar (los scripts evitan lo exclusivo de GNU) pero no está probado; en Windows usa WSL.

```bash
# 1. La caja de herramientas: ECC (MIT) aporta los agentes y skills a los que CWCDT enruta
claude plugin marketplace add affaan-m/ECC
claude plugin install ecc@ecc

# 2. (Opcional) Codex como segundo ingeniero
npm i -g @openai/codex && codex login
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex

# 3. Descarga CWCDT, previsualiza y aplica
git clone https://github.com/Danigr005/CWCDT.git ~/CWCDT
~/CWCDT/scripts/apply.sh --dry-run --lang es
~/CWCDT/scripts/apply.sh --lang es            # inglés: --lang en ; stack TS/Python/Rust: --profile ts-py-rust

# 4. Reinicia Claude Code; comprueba y mide
~/CWCDT/scripts/check.sh
~/CWCDT/scripts/measure.sh primera --real
```

Después, pide lo que quieras. `apply.sh` guarda una copia de lo que sustituye (`~/.claude/backups/cwcdt-<fecha>/`) y
`scripts/revert.sh --original` lo deja todo como estaba.

Tu `~/.claude/CLAUDE.md` actual se mueve a esa copia, no se fusiona. Copia tus preferencias a la sección «Preferencias del dueño» de
`lang/<l>/CLAUDE.md`. Edita el repo, nunca el enlace: Claude Code se niega a escribir a través de enlaces simbólicos.

## Nuevo portátil (restaurar todo)

Todo lo que define la metodología está en este repo. En un equipo nuevo:

```bash
git clone https://github.com/Danigr005/CWCDT.git ~/CLAUDE-PROJECTS/CWCDT
~/CLAUDE-PROJECTS/CWCDT/scripts/bootstrap.sh --lang es --profile ts-py-rust
codex login        # y abre `claude` para iniciar sesión
```

`bootstrap.sh` instala ECC y el plugin de Codex, aplica CWCDT y lo comprueba. **No** está en git, a propósito: el historial de
conversaciones, los inicios de sesión y los secretos (se rehacen con `claude` / `codex login`).

## Más información

- [Cómo funciona](docs/es/COMO-FUNCIONA.md) · [How it works](docs/HOW-IT-WORKS.md)
- [Personalización](docs/CUSTOMIZE.md), [economía de tokens](docs/TOKEN-ECONOMY.md), [problemas y FAQ](docs/TROUBLESHOOTING.md) y
  [registro de calibración de Codex](docs/CODEX-CALIBRATION.md) (en inglés)

## Estado

v0.1.0. Construido y medido en una sola máquina (Linux, Claude Code 2.1.234, ECC 2.2.3 en el commit `b38be6a`, Codex CLI 0.164 con plugin 1.0.6).
Los nombres de modelos de los documentos son ejemplos de noviembre de 2026: ajústalos a lo que ofrezca tu cuenta. Issues y PRs bienvenidos, ver
[CONTRIBUTING](CONTRIBUTING.md).

## Licencia

MIT © 2026 Danigr005. Contiene material derivado de ECC (MIT © Affaan Mustafa); ver [NOTICE](NOTICE).
