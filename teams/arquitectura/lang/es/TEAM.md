# Architecture Review Team (equipo de arquitectura)

Equipo para **leer planos de edificación, juzgar si son viables de verdad y proponer correcciones reales**, con el CTE español como marco por defecto. Añade a la capa común (reparto Claude↔Codex, tokens, olas) esta especialización. Es un **prechequeo técnico**: no certifica cumplimiento ni sustituye al arquitecto que firma.

## Preparación
- Si el proyecto no tiene `.claude/agents/arq-lector-planos.md`, ejecuta `teams/arquitectura/setup.sh <proyecto>` del repo EEAS (idempotente): prepara el entorno de herramientas (`arq`), la base del CTE y copia agentes y skills al proyecto.
- Si `arq` falla: `teams/arquitectura/setup.sh --tools-only`. Comprueba con `arq demo <dir>`: las herramientas deben destapar los defectos D2, D3 y D4 y dar los datos de D1 (ver cabecera de `arq_demo.py`).
- El dueño solo dice «revisa este plano» y pasa el fichero. **Nunca le pidas elegir agente ni skill.** Pregunta como máximo: emplazamiento (municipio/CCAA), uso y tipo de actuación (obra nueva/reforma/cambio de uso) — solo si no se deducen de los planos.

## Entradas y salidas
- Entradas: PDF e imagen (lectura visual con OCR si hace falta), DXF, IFC. DWG: convertir a DXF (o pedir exportación a DXF/PDF). Planos con baja calidad → pide mejores antes de seguir.
- Salidas: informe de viabilidad (`informes/AAAA-MM-DD-<proyecto>/informe.md`, DOCX si se pide), imágenes marcadas, DXF corregido en copia (`*_eeas.dxf`), propuestas con alternativas y coste orientativo.

## Ciclo (puerta 1: el dueño confirma el alcance; puerta final: él recibe el informe)
1. **Leer** — agente `arq-lector-planos`, skill `plano-lectura` (+ `plano-cad-bim`). Resultado: `work/modelo-plano.md`.
2. **Analizar** (en paralelo, solo los ámbitos que apliquen) — `arq-coherencia`, `arq-incendio-accesibilidad`, `arq-habitabilidad-energia`, `arq-estructura`, `arq-instalaciones`, `arq-urbanismo`. Skill `plano-viabilidad`.
3. **Refutar** — `arq-revisor` intenta romper cada hallazgo; lo no sostenido se rebaja o se descarta.
4. **Corregir** — `arq-proponente`, skill `plano-correcciones`; `arq-mediciones` si importa el coste.
5. **Informar** — skill `plano-informe`. Veredicto: VIABLE / VIABLE CON CORRECCIONES / NO VIABLE SIN REDISEÑO / NO CONCLUYENTE.
- Lanza en paralelo los especialistas (un mensaje, varias herramientas Agent). Dale a cada uno el modelo del plano y su ámbito, no la conversación.

## Reglas del equipo
- **Normativa solo de fuente**: skill `cte-verificacion`. Ninguna cifra o artículo de memoria; `arq cte search` sobre el texto oficial del CTE; lo demás (RITE, REBT, Código Estructural, accesibilidad autonómica, urbanismo) por búsqueda web oficial. Estados: Verificado / [VERIFICAR] / [NO CONSTA].
- **Escala**: nunca fiarse del rótulo; calibrar con una cota impresa (`arq scale`).
- **Procedencia**: cada dato leído/medido/inferido/ilegible. Lo ilegible no se rellena.
- BLOQUEANTE o GRAVE solo con dato leído o medido y norma Verificada (fiabilidad alta). Sin ficha urbanística real, urbanismo = NO CONCLUYENTE.
- **Ámbitos críticos**: coherencia, incendio-accesibilidad, habitabilidad-energía, estructura y urbanismo (instalaciones puede quedar [VERIFICAR]).
- **Traspaso**: cada especialista escribe `work/hallazgos-<ámbito>.md` (IDs `COH-`, `INC-`, `HAB-`, `EST-`, `INS-`, `URB-`); el orquestador deduplica y consolida `work/hallazgos.md`; el revisor devuelve MANTENER/REBAJAR/DESCARTAR por ID; proponente y mediciones leen solo `work/hallazgos.md`. Formato en `plano-viabilidad`.
- Los originales no se tocan; las correcciones van sobre copias. No se emiten planos «para visado».
- Un veredicto «viable» exige haber analizado todos los ámbitos críticos; si no, NO CONCLUYENTE.

## Reparto Claude ↔ Codex en este equipo
- **Claude**: lectura de planos (visión), juicio de viabilidad, interpretación normativa, propuestas de diseño, revisión adversarial, informe y toda decisión.
- **Codex** (las cuatro condiciones comunes): mantenimiento de las herramientas `teams/arquitectura/tools/*.py` y sus tests, conversiones mecánicas de formato, extracción masiva de tablas ya especificadas, scripts `ifcopenshell`/`ezdxf` para tareas concretas con comando de aceptación. **Nunca** lectura de planos ni juicio normativo.

## Herramientas
Scripts propios con las librerías del entorno (ifcopenshell, PyNite, python-docx): `"$HOME/.local/share/eeas/arquitectura-venv/bin/python" -I script.py` (o `$EEAS_ARQ_VENV/bin/python`); pide confirmación como cualquier ejecución de código.
`arq` (ingest, scale, dxf, ifc, areas, markup, dxfedit, cte, demo), venv Python 3.12 (ezdxf, ifcopenshell, ifctester, pypdfium2, pdfplumber, shapely, opencv, pytesseract, PyNite, python-docx), skills `plano-*` y `cte-verificacion`, 10 agentes `arq-*`. De apoyo del toolbox común: `deep-research` (normativa o precedentes), `anthropic-skills:docx`/`pdf` (informes), `ecc:architecture-decision-records` (decisiones de diseño que el dueño adopte).
