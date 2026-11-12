---
name: plano-correcciones
description: Convierte hallazgos de un plano en correcciones y propuestas reales: alternativas con impacto, recomendación, comprobación de efectos secundarios y marcado sobre copia (DXF/PNG), sin tocar el original.
---

# Correcciones y propuestas

Una propuesta solo vale si **resuelve el hallazgo sin crear otro**. Trabaja siempre sobre copias.

## Para cada hallazgo MODERADO o superior
1. **Causa**: ¿es un error de dibujo, de diseño o de programa? La corrección depende de eso.
2. **2–3 alternativas reales** (no una sola; no "rediseñar" sin concretar). Para cada una:
   - Qué cambia exactamente (muro que se mueve, hueco que se ensancha, escalera que cambia, sector que se divide…) con cotas.
   - Efecto en superficie útil, estructura, instalaciones, accesibilidad, luz natural, coste (↑/↓/≈ y orden de magnitud orientativo) y plazo.
   - Riesgo normativo residual y qué verificar.
3. **Recomendación** razonada (una), y por qué las otras no.
4. **Comprobación de efectos**: reaplica los ámbitos afectados (p. ej. ensanchar un pasillo come superficie de una estancia que podría quedar bajo su mínimo; mover un muro puede cargar un forjado). Si aparece un hallazgo nuevo, la propuesta se ajusta o se descarta. Máximo 3 iteraciones; si no converge, dilo: puede que haya que replantear.
5. **Honestidad**: si no hay corrección razonable dentro de la parcela, programa o presupuesto, la conclusión es "requiere rediseño" y se explica qué decisión es del propietario o del arquitecto.

## Marcado y entregables
- **DXF**: `arq dxfedit original.dxf ops.json` escribe `original_eeas.dxf` (capas `EEAS_CORRECCION` en rojo y `EEAS_PROPUESTA` en verde; se pueden apagar o borrar de una vez). Nunca sobrescribe el original.
- **PDF/imagen**: sobre el mosaico o overview, `arq markup tile.png hallazgos.json salida.png` dibuja cajas por severidad con el ID del hallazgo.
- **Croquis alternativo**: si la propuesta cambia la distribución, dibuja el "antes/después" como DXF (polilíneas de las estancias nuevas, con cotas) y renderízalo con `arq dxf render` para revisarlo con Read.
- Numeración coherente: `H1` (hallazgo) → `P1a/P1b` (alternativas) → `P1a` recomendada.
- Cuando el cambio afecta a superficies, recalcula con `arq areas` y deja el cuadro actualizado.

## Límites
No se emiten planos "listos para visado". Los dibujos son **propuestas de trabajo** para el arquitecto, que decide y firma. Las cifras de coste son órdenes de magnitud, nunca presupuesto.
