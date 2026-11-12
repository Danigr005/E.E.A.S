---
name: plano-viabilidad
description: Juzga si un proyecto de edificación es viable de verdad: coherencia, CTE, urbanismo, estructura, instalaciones, funcionalidad y coste. Emite hallazgos con severidad, norma citada y veredicto. Úsala tras leer el plano.
---

# Análisis de viabilidad

Viable = se puede construir, legalizar y usar conforme a normativa **con lo dibujado** o con correcciones razonables. Es un **prechequeo técnico**: no certifica nada y la firma es del técnico competente.

## Flujo (orquestado por Claude)
1. **Lectura**: `plano-lectura` → `work/modelo-plano.md`. Si hay muchos datos ilegibles, para y pide mejores planos antes de seguir.
2. **Análisis en paralelo** (agentes `arq-*`, cada uno con el modelo del plano y solo su ámbito):
   `arq-coherencia` · `arq-incendio-accesibilidad` · `arq-habitabilidad-energia` · `arq-estructura` · `arq-instalaciones` · `arq-urbanismo`. En un plano pequeño o una consulta puntual, haz tú solo los ámbitos que apliquen.
3. **Consolidar y deduplicar** (orquestador): cada especialista escribe `work/hallazgos-<ámbito>.md` con IDs de prefijo propio (`COH-1`, `INC-1`, `HAB-1`, `EST-1`, `INS-1`, `URB-1`) y una sección «No analizado / datos que faltan». El orquestador funde los duplicados (mismo hecho visto por dos ámbitos), renumera `H1…Hn` y escribe `work/hallazgos.md`.
4. **Revisión adversarial**: `arq-revisor` intenta refutar cada hallazgo (¿el dato está bien leído? ¿la norma aplica a este uso y esta fecha? ¿la cifra está verificada con `arq cte`?). Devuelve una tabla ID → MANTENER/REBAJAR/DESCARTAR; el orquestador la aplica sobre `work/hallazgos.md`. Lo no sostenido se rebaja o se descarta.
5. **Correcciones**: `plano-correcciones` por cada hallazgo MODERADO o superior (`arq-proponente`). Coste orientativo con `arq-mediciones` si el dueño lo pide o la corrección cambia superficies/estructura. Ambos leen solo `work/hallazgos.md`.
6. **Informe**: `plano-informe`.

## Ámbitos y qué se pregunta en cada uno
1. **Coherencia interna**: cotas que suman, superficies declaradas vs medidas, plantas/secciones/alzados que concuerdan, nombres y ejes consistentes.
2. **Seguridad y uso (CTE)**: incendio (sectores, evacuación, recorridos, salidas, escaleras, resistencia), utilización y accesibilidad (caídas, itinerarios accesibles, aseos, rampas, escaleras).
3. **Habitabilidad (CTE)**: humedad, residuos, calidad del aire, agua, evacuación de aguas, radón; ruido; ahorro de energía; iluminación y ventilación naturales de estancias.
4. **Urbanismo**: parcela, edificabilidad, ocupación, alturas, retranqueos, usos permitidos, plazas de aparcamiento, protección patrimonial. **Requiere** la ficha urbanística real; sin ella, el ámbito queda "no concluyente".
5. **Estructura y constructabilidad**: camino de cargas, luces, voladizos, continuidad de pilares, huecos en forjado, cimentación, juntas, sistema constructivo realista. Sentido común de ingeniero; no sustituye el cálculo.
6. **Instalaciones**: espacio para patinillos y cuartos técnicos, ventilación, saneamiento con pendientes, claves de climatización, electricidad, protección contra incendios.
7. **Funcional y económico**: circulaciones, privacidad, dimensiones útiles de mobiliario, superficie útil/construida razonable (lo cubre `arq-coherencia`); orden de magnitud de coste y plazo, marcado como orientativo (solo `arq-mediciones`, bajo demanda).

## Formato de hallazgo (obligatorio)
```
ID · ámbito · SEVERIDAD · fiabilidad
Dónde:   hoja, estancia, y fichero de mosaico + bbox [x0,y0,x1,y1] en px (o handle DXF)
Hecho:   lo observado, con valor y procedencia (leído/medido/inferido)
Exigencia: norma + apartado + estado (Verificado con fecha / [VERIFICAR] / [NO CONSTA])
Diferencia: lo que falta o sobra, con cifras
Consecuencia: por qué importa (legalización, seguridad, uso, coste)
Corrección: referencia a la propuesta
```
**Severidad**: `BLOQUEANTE` (incumple exigencia básica o hace inviable la solución) · `GRAVE` (incumple, corregible con cambio relevante) · `MODERADO` (incumple o es dudoso, corrección menor) · `LEVE` (mejora o detalle) · `OBSERVACION` (dato a confirmar).
**Fiabilidad**: `alta` (dato leído o medido **y** norma Verificada) · `media` (medido sin norma verificada, o leído con norma [VERIFICAR]) · `baja` (inferido o plano dudoso).
Un hallazgo `BLOQUEANTE` o `GRAVE` exige fiabilidad **alta**; con `media` el máximo es `MODERADO`; con `baja`, `OBSERVACION` pidiendo el dato.
Con norma [VERIFICAR] no se escribe cifra límite: `Exigencia: DB-xx [VERIFICAR]`, `Diferencia: [valor por verificar]`, y el hallazgo no pasa de `OBSERVACION`/`LEVE`.

## Veredicto global
- **VIABLE**: ningún hallazgo MODERADO o superior abierto.
- **VIABLE CON CORRECCIONES**: al menos un GRAVE o MODERADO, todos con corrección razonable.
- **NO VIABLE SIN REDISEÑO**: al menos un BLOQUEANTE, o un GRAVE sin corrección razonable dentro de la parcela, el programa o el presupuesto (di cuál y por qué).
- **NO CONCLUYENTE**: faltan datos críticos (planos ilegibles, sin ficha urbanística…); lista exactamente cuáles.
**Ámbitos críticos**: coherencia, incendio-accesibilidad, habitabilidad-energía, estructura y urbanismo (instalaciones puede quedar [VERIFICAR]). Nunca des un "viable" si algún ámbito crítico quedó sin analizar. Sin ficha urbanística real, urbanismo es NO CONCLUYENTE y el veredicto máximo es «VIABLE CON CORRECCIONES, condicionado a urbanismo [NO CONCLUYENTE]», listándolo explícitamente.

## Prohibido
Inventar cifras, artículos o fechas de norma · afirmar cumplimiento sin haberlo comprobado · decir "cumple" por ausencia de hallazgos (di "no se han detectado incumplimientos en el alcance X") · dar por válida una escala sin calibrar.
