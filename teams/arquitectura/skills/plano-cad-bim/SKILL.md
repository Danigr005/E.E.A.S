---
name: plano-cad-bim
description: Inspecciona planos vectoriales (DXF, DWG convertido) y modelos IFC/BIM con las herramientas del equipo: capas, superficies, cotas sospechosas, huecos, validación IDS y marcado sobre copias.
---

# CAD y BIM

Las herramientas viven en el entorno del equipo (`arq`, Python 3.12 con ezdxf, ifcopenshell, shapely). Son de **solo lectura** salvo `arq dxfedit`, que escribe una copia.

## DXF
- `arq dxf summary f.dxf`: unidades, extensión, capas (con apagadas o congeladas) y tipos de entidad. **Comprueba las unidades**: si el DXF no declara `$INSUNITS` (frecuente al exportar desde DWG), `areas`, `dims` y `text` **se niegan a dar cifras**: confirma la unidad con una cota conocida (ancho de puerta, lado de una estancia) y repite con `--assume-units m|cm|mm`. Cada salida imprime la unidad usada en su primera línea.
- `arq dxf areas f.dxf [--layer ESTANCIAS]`: polilíneas cerradas con área y perímetro (m²). Compara con el cuadro de superficies. Las polilíneas con arcos se marcan como área aproximada. Solo se lee el espacio modelo (no bloques ni papel). Si no hay polilíneas cerradas, las estancias están hechas con líneas sueltas: usa `arq dxf render` y lee visualmente.
- `arq dxf dims f.dxf`: cotas cuyo texto escrito a mano no coincide con la geometría (señal clásica de plano sin actualizar).
- `arq dxf text`, `arq dxf blocks`: rótulos y bloques (puertas, ventanas, aparatos), útiles para contar y localizar.
- `arq dxf render f.dxf out.png`: raster para revisar con Read y para `plano-lectura`.

## DWG
No se lee directo. Convierte a DXF con `dwg2dxf` (LibreDWG) o ODA File Converter **si están instalados** (`command -v dwg2dxf ODAFileConverter`). Si no, pide al dueño que exporte a DXF o PDF desde su CAD; no instales nada con `sudo` por tu cuenta.

**La conversión no es de fiar sin comprobarla.** LibreDWG es ingeniería inversa y puede perder entidades, capas o cotas sin avisar (una prueba con el escritor `dxf2dwg` perdió todo). Tras `dwg2dxf -y -o out.dxf f.dwg`, ejecuta `arq dxf summary out.dxf` y comprueba que hay entidades y capas con nombre razonable. Si el resumen sale vacío o con capas mutiladas, no analices ese DXF: pide PDF o DXF exportado desde el CAD original. Aunque salga bien, contrasta alguna cota o superficie con el PDF del mismo plano si existe, y marca los datos como «convertidos desde DWG».

## IFC / BIM
- `arq ifc summary|spaces|openings f.ifc`: plantas, estancias con área (Qto o geometría) y huecos con ancho/alto. Las longitudes y áreas se convierten a metros con las unidades declaradas del modelo (la primera línea las imprime); si el modelo no las declara, la herramienta se niega.
- `arq ifc check f.ifc reglas.ids`: valida contra un IDS (buildingSMART). Para reglas del proyecto (p. ej. toda puerta de evacuación ≥ X m), escribe el IDS con el valor **verificado** en el CTE, nunca de memoria.
- Para editar un IFC, escribe un script aparte con `ifcopenshell.api` sobre una **copia**, y vuelve a pasar `arq ifc check`.

## Marcado
`arq dxfedit f.dxf ops.json` (capas EEAS_CORRECCION / EEAS_PROPUESTA; tamaños en metros convertidos a las unidades del dibujo; nunca sobrescribe el original ni un enlace a él, ni un fichero existente sin `--force`) y `arq markup img.png hallazgos.json out.png` para imágenes. Formato de operaciones: `arq dxfedit --help`.

## Autoprueba
`arq demo <dir>` genera un plano con defectos conocidos (pasillo de 0,80 m, cota con texto falso, superficie mal sumada, puerta de 0,60 m). Úsalo si dudas de que las herramientas funcionan: destapan D2 (`dims`), D3 (`areas`) y D4 (`ifc openings`), y dan los datos para D1 (pasillo de 0,8 × 4,0 m en `dxf areas`, a comprobar contra el mínimo verificado).
