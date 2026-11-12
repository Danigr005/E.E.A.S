---
name: cte-verificacion
description: Verifica normativa española de edificación (CTE DB-SE/SI/SUA/HS/HR/HE, RITE, REBT, accesibilidad, urbanismo) contra el texto oficial, sin citar de memoria. Úsala siempre que se afirme una exigencia o cifra normativa.
---

# Verificación de normativa (España)

**Regla n.º 1: ninguna cifra, apartado ni fecha normativa sale de la memoria.** Se busca en el texto oficial con `arq cte` y se cita con su procedencia. Detalle del protocolo y de los estados: `references/01-protocolo-normativa.md`; índice de dónde mirar: `references/02-mapa-normativo-espana.md` (ambos de arquitectura-es-skill, MIT).

## Base local del CTE
- `arq cte list` → qué está almacenado y la fecha de descarga. Si está vacío: `arq cte fetch` (DB-SE y sus documentos, SI, SUA, HS, HR, HE y Parte I, desde codigotecnico.org).
- `arq cte search "<regex>" --doc SUA --context 2` → texto con documento y página PDF. `arq cte page SI 40` lee una página entera.
- Cita así: `DB-SUA, sección SUA 1, apartado 2, PDF p.13 (codigotecnico.org, descargado 2026-11-12)`. La página es la del PDF, no el folio impreso.
- Las exigencias dependen del **uso**, la **superficie**, la **altura de evacuación**, la **ocupación** y si es obra nueva o reforma: comprueba el ámbito de aplicación del apartado antes de aplicarlo.

## Qué cubre cada DB (índice de temas, sin cifras)
- **SE**: resistencia y estabilidad; aptitud al servicio. Documentos: acciones (AE), cimientos (C), acero (A), fábrica (F), madera (M). El hormigón se rige por el Código Estructural: no está en la base; búscalo.
- **SI**: propagación interior (sectores), exterior, evacuación de ocupantes, instalaciones de protección, intervención de bomberos, resistencia al fuego de la estructura.
- **SUA**: caídas, impacto y atrapamiento, aprisionamiento, iluminación inadecuada, alta ocupación, ahogamiento, vehículos, rayo, **accesibilidad**.
- **HS**: humedad, residuos, calidad del aire interior, suministro de agua, evacuación de aguas, protección frente al radón.
- **HR**: protección frente al ruido (un solo documento).
- **HE**: limitación de consumo, envolvente térmica, instalaciones térmicas, iluminación, ACS renovable, fotovoltaica.
- **Fuera de la base** (búsqueda web oficial, fuente BOE o boletín autonómico): RITE, REBT, RIPCI, Código Estructural, accesibilidad autonómica, normas urbanísticas, ordenanzas municipales, normativa de habitabilidad autonómica (a veces más exigente que el CTE).

## Procedimiento
1. Define el **supuesto**: uso, plantas, superficie, obra nueva/reforma, emplazamiento.
2. Localiza el apartado con `arq cte search`; lee el contexto (excepciones, tablas, notas) con `arq cte page`.
3. Compara con el dato del plano **con sus unidades** y su procedencia (leído/medido/inferido).
4. Etiqueta el resultado: **Verificado** (leído hoy en el texto oficial) · **[VERIFICAR]** (existe, no contrastado) · **[NO CONSTA]** (no se sabe si aplica). Solo "Verificado" sostiene un hallazgo BLOQUEANTE o GRAVE.
5. Para lo que no está en la base, busca en la web (BOE/boletín oficial/ayuntamiento), anota URL y fecha. Sin acceso, deja `[VERIFICAR]` visible y añádelo a la lista de verificaciones pendientes.
6. Texto del CTE puede haber sido modificado después de la descarga: revisa la sección *Actualidad* de codigotecnico.org si el dato es crítico y anota la comprobación.

## Qué decir cuando no se puede aplicar
"No puedo confirmar cómo aplica esta norma a este caso", más el documento que haría falta (ficha urbanística, ordenanza, texto consolidado). No extrapoles desde una norma parecida.

## Lista final obligatoria
Normas citadas con: nombre · apartado · estado · fuente y fecha · y las **verificaciones pendientes** para el técnico.
