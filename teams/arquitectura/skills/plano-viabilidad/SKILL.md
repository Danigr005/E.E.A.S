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
3. **Revisión adversarial**: `arq-revisor` intenta refutar cada hallazgo (¿el dato está bien leído? ¿la norma aplica a este uso y esta fecha? ¿la cifra está verificada con `arq cte`?). Lo no sostenido se rebaja o se descarta.
4. **Correcciones**: `plano-correcciones` por cada hallazgo no leve (`arq-proponente`). Coste orientativo con `arq-mediciones` si el dueño lo pide o la corrección cambia superficies/estructura.
5. **Informe**: `plano-informe`.

## Ámbitos y qué se pregunta en cada uno
1. **Coherencia interna**: cotas que suman, superficies declaradas vs medidas, plantas/secciones/alzados que concuerdan, nombres y ejes consistentes.
2. **Seguridad y uso (CTE)**: incendio (sectores, evacuación, recorridos, salidas, escaleras, resistencia), utilización y accesibilidad (caídas, itinerarios accesibles, aseos, rampas, escaleras).
3. **Habitabilidad (CTE)**: humedad, residuos, calidad del aire, agua, evacuación de aguas, radón; ruido; ahorro de energía; iluminación y ventilación naturales de estancias.
4. **Urbanismo**: parcela, edificabilidad, ocupación, alturas, retranqueos, usos permitidos, plazas de aparcamiento, protección patrimonial. **Requiere** la ficha urbanística real; sin ella, el ámbito queda "no concluyente".
5. **Estructura y constructabilidad**: camino de cargas, luces, voladizos, continuidad de pilares, huecos en forjado, cimentación, juntas, sistema constructivo realista. Sentido común de ingeniero; no sustituye el cálculo.
6. **Instalaciones**: espacio para patinillos y cuartos técnicos, ventilación, saneamiento con pendientes, claves de climatización, electricidad, protección contra incendios.
7. **Funcional y económico**: circulaciones, privacidad, dimensiones útiles de mobiliario, superficie útil/construida razonable; orden de magnitud de coste y plazo (marcado como orientativo).

## Formato de hallazgo (obligatorio)
```
ID · ámbito · SEVERIDAD · fiabilidad
Dónde:   hoja, estancia, coordenadas (mosaico/px o handle DXF)
Hecho:   lo observado, con valor y procedencia (leído/medido/inferido)
Exigencia: norma + apartado + estado (Verificado con fecha / [VERIFICAR] / [NO CONSTA])
Diferencia: lo que falta o sobra, con cifras
Consecuencia: por qué importa (legalización, seguridad, uso, coste)
Corrección: referencia a la propuesta
```
**Severidad**: `BLOQUEANTE` (incumple exigencia básica o hace inviable la solución) · `GRAVE` (incumple, corregible con cambio relevante) · `MODERADO` (incumple o es dudoso, corrección menor) · `LEVE` (mejora o detalle) · `OBSERVACION` (dato a confirmar).
**Fiabilidad**: `alta` (dato leído + norma verificada) · `media` (medido o norma [VERIFICAR]) · `baja` (inferido o plano dudoso).
Un hallazgo `BLOQUEANTE` o `GRAVE` exige fiabilidad alta o media; si es baja, se emite como `OBSERVACION` pidiendo el dato.

## Veredicto global
- **VIABLE**: sin bloqueantes ni graves.
- **VIABLE CON CORRECCIONES**: hay graves/moderados, todos con corrección razonable.
- **NO VIABLE SIN REDISEÑO**: hay bloqueantes que obligan a cambiar el planteamiento (di cuál y por qué).
- **NO CONCLUYENTE**: faltan datos críticos (planos ilegibles, sin ficha urbanística…); lista exactamente cuáles.
Nunca des un "viable" si algún ámbito crítico quedó sin analizar: dilo en el veredicto.

## Prohibido
Inventar cifras, artículos o fechas de norma · afirmar cumplimiento sin haberlo comprobado · decir "cumple" por ausencia de hallazgos (di "no se han detectado incumplimientos en el alcance X") · dar por válida una escala sin calibrar.
