---
name: plano-informe
description: Redacta el informe final de viabilidad de un plano (veredicto, hallazgos, correcciones, verificaciones pendientes, anexos) en Markdown y, si se pide, DOCX/PDF.
---

# Informe de viabilidad

Carpeta de salida: `informes/AAAA-MM-DD-<proyecto>/` en el proyecto (`informe.md`, `anexos/`, imágenes marcadas, DXF `_eeas`).

## Estructura (en este orden)
1. **Veredicto** (una frase: VIABLE / VIABLE CON CORRECCIONES / NO VIABLE SIN REDISEÑO / NO CONCLUYENTE) y las 5 cosas que el dueño debe saber. Cuántos hallazgos por severidad.
2. **Alcance y datos de partida**: documentos recibidos (nombre, hojas, formato), escala (declarada vs calibrada), emplazamiento y uso asumidos, **lo ilegible o ausente**, ámbitos analizados y no analizados.
3. **Tabla de hallazgos**: ID · ámbito · severidad · fiabilidad · una línea · hoja.
4. **Hallazgos detallados** con el formato de `plano-viabilidad` (dónde, hecho, exigencia con estado, diferencia, consecuencia, corrección).
5. **Propuestas de corrección**: alternativas, recomendada, efectos y coste orientativo, enlaces a imágenes y DXF.
6. **Verificaciones pendientes**: normas `[VERIFICAR]`/`[NO CONSTA]`, datos a confirmar, documentos que faltan (ficha urbanística, ordenanzas…), cálculos que debe hacer un técnico (estructura, instalaciones).
7. **Anexos**: modelo del plano, cuadro de superficies verificado (`arq areas`), fuentes normativas con documento, página y fecha de consulta, imágenes anotadas.
8. **Descargo**: prechequeo técnico asistido; no certifica cumplimiento ni sustituye al técnico competente que firma el proyecto.

## Estilo
Español claro, frases cortas, números con unidades. Cada afirmación normativa con su fuente. Nada de adjetivos sin dato ("estrecho" → "0,80 m"). Primero lo grave. Sin relleno ni repetición del modelo entero.

## Formatos
Markdown siempre. DOCX solo si el dueño lo pide: usa la skill `anthropic-skills:docx` o `python-docx` del entorno del equipo. PDF: desde DOCX o Markdown con las herramientas disponibles; comprueba que las imágenes anotadas se ven.

## Antes de entregar
Revisa que: el veredicto es coherente con la severidad máxima · todo BLOQUEANTE/GRAVE tiene norma **Verificada** y dato leído o medido · la lista de pendientes está completa · no hay cifras de memoria · las imágenes corresponden a la versión final de los hallazgos.
