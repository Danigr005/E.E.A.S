# Architecture Review Team

A team to **read building plans, judge whether they are really viable, and propose real corrections**, with the Spanish CTE as the default framework. It adds this specialization to the common layer (Claude↔Codex split, tokens, waves). It is a **technical pre-check**: it does not certify compliance and does not replace the signing architect.

## Preparation
- If the project lacks `.claude/agents/arq-lector-planos.md`, run `teams/arquitectura/setup.sh <project>` from the EEAS repo (idempotent): it sets up the tool environment (`arq`), the CTE text base, and copies agents and skills into the project.
- If `arq` fails: `teams/arquitectura/setup.sh --tools-only`. Verify with `arq demo <dir>`: the tools must expose defects D2, D3 and D4 and give the data for D1 (see the header of `arq_demo.py`).
- The owner just says "review this plan" and hands over the file. **Never ask them to pick an agent or skill.** Ask at most: location (municipality/region), use, and kind of work (new build/refurbishment/change of use) — only if not deducible from the drawings.

## Inputs and outputs
- Inputs: PDF and image (visual reading, OCR when needed), DXF, IFC. DWG: convert to DXF (or ask for a DXF/PDF export). Low-quality plans → ask for better ones before going on.
- Outputs: viability report (`informes/YYYY-MM-DD-<project>/informe.md`, DOCX on request), marked-up images, corrected DXF on a copy (`*_eeas.dxf`), proposals with alternatives and indicative cost.

## Cycle (gate 1: the owner confirms scope; final gate: they receive the report)
1. **Read** — agent `arq-lector-planos`, skill `plano-lectura` (+ `plano-cad-bim`). Result: `work/modelo-plano.md`.
2. **Analyse** (in parallel, only the applicable scopes) — `arq-coherencia`, `arq-incendio-accesibilidad`, `arq-habitabilidad-energia`, `arq-estructura`, `arq-instalaciones`, `arq-urbanismo`. Skill `plano-viabilidad`.
3. **Refute** — `arq-revisor` tries to break every finding; anything unsupported is downgraded or dropped.
4. **Correct** — `arq-proponente`, skill `plano-correcciones`; `arq-mediciones` when cost matters.
5. **Report** — skill `plano-informe`. Verdict: VIABLE / VIABLE WITH CORRECTIONS / NOT VIABLE WITHOUT REDESIGN / INCONCLUSIVE (Spanish labels in the report).
- Launch specialists in parallel (one message, several Agent calls). Give each the plan model and its scope, not the conversation.

## Team rules
- **Regulations only from source**: skill `cte-verificacion`. No figure or article from memory; `arq cte search` over the official CTE text; everything else (RITE, REBT, Código Estructural, regional accessibility, urbanism) via official web search. States: Verified / [VERIFICAR] / [NO CONSTA].
- **Scale**: never trust the label; calibrate with a printed dimension (`arq scale`).
- **Provenance**: every datum is read/measured/inferred/illegible. Illegible data is not filled in.
- BLOCKING or SERIOUS only with a read or measured datum and a Verified rule. Without the real urban-planning sheet, urbanism = INCONCLUSIVE.
- Originals are never touched; corrections go on copies. No "for permit" drawings are issued.
- A "viable" verdict requires every critical scope to have been analysed; otherwise INCONCLUSIVE.

## Claude ↔ Codex split in this team
- **Claude**: plan reading (vision), viability judgment, regulatory interpretation, design proposals, adversarial review, the report, and every decision.
- **Codex** (the four common conditions): maintenance of `teams/arquitectura/tools/*.py` and their tests, mechanical format conversions, bulk extraction of already-specified tables, targeted `ifcopenshell`/`ezdxf` scripts with an acceptance command. **Never** plan reading or regulatory judgment.

## Tools
`arq` (ingest, scale, dxf, ifc, areas, markup, dxfedit, cte, demo), Python 3.12 venv (ezdxf, ifcopenshell, ifctester, pypdfium2, pdfplumber, shapely, opencv, pytesseract, PyNite, python-docx), skills `plano-*` and `cte-verificacion`, 10 `arq-*` agents. Supporting common toolbox: `deep-research`, `anthropic-skills:docx`/`pdf`, `ecc:architecture-decision-records`.
