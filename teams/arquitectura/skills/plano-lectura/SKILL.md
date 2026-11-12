---
name: plano-lectura
description: Lee planos de edificación (PDF, imagen, DXF, IFC) y construye un modelo estructurado y auditable (escala, niveles, estancias, huecos, estructura, instalaciones). Úsala antes de cualquier análisis de viabilidad.
---

# Lectura de planos

Objetivo: convertir un plano en un **modelo de datos con procedencia**: cada dato dice de dónde sale y cuánto se fía uno de él. Sin este paso no hay análisis fiable.

## 1. Datos de partida (pregunta solo lo que falte, máx. 3)
Tipo de actuación (obra nueva, reforma, cambio de uso, ampliación) · emplazamiento (municipio y comunidad autónoma) · uso y número de plantas. Si el dueño no lo sabe, anótalo como hipótesis explícita.

## 2. Ingesta
- PDF/imagen: `arq ingest <fichero> --out work/ingesta --dpi 200` (A0/A1: `--dpi 150`; plano pequeño o con cotas diminutas: `--dpi 300`). Si no hay capa de texto se hace OCR solo (español+inglés si `spa` está instalado, si no inglés y avisa de que los acentos pueden fallar).
- DXF/DWG: ver skill `plano-cad-bim`. IFC: idem. Si hay vectorial **y** PDF, el vectorial manda para geometría; el PDF, para lo que el dibujante quiso mostrar.
- Abre primero `pNN_overview.png` con Read: identifica qué hoja es cada cosa (situación, plantas, secciones, alzados, cuadros de superficies, cajetín, leyenda).
- Lee después los **mosaicos** `pNN_tiles/` en resolución completa: ahí se leen cotas, rótulos y símbolos. No saques cotas del overview.
- **El OCR de cifras no es fiable**: en una prueba real leyó «34,2» como «342» y «134,2», y omitió cotas como «14,70» (texto pequeño o vertical). Un número que sale solo del OCR es **inferido**: no pasa a «leído» hasta verlo en el mosaico, y no sostiene ningún hallazgo BLOQUEANTE/GRAVE. Si las cotas son diminutas, repite la ingesta a más resolución (`--dpi 300`, o dibuja el plano al doble de tamaño).
- `pNN_words.json` da el texto con coordenadas; `pNN_vectors.json`, los segmentos más largos (útil para comprobar longitudes de muros).

## 3. Escala: nunca fiarse solo del rótulo
1. Anota la escala declarada (1:50, 1:100…) y el formato de papel (`mm_size` en meta).
2. Busca una cota impresa larga y mídela en píxeles → `arq scale check --scale 100 --dpi 200 --px <px> --meters <m>`.
3. Si no cuadra (>3 %), el PDF se reescaló al imprimir o el rótulo miente: **usa la cota impresa**, marca la escala como no fiable y vuelve a calibrar con `arq scale from-ref`.
4. Medir en píxeles solo con escala calibrada: `arq scale measure` / `arq scale area`.
5. Si una cota impresa y la medida geométrica discrepan, es un hallazgo (incoherencia), no un error tuyo: documenta ambas.

## 4. Qué extraer (modelo del plano)
- **Hoja**: tipo, escala (declarada/calibrada), fecha, revisión, autor, orientación (norte).
- **Niveles**: cotas de nivel por planta (+0,00…), alturas libres y de forjado, cota de rasante.
- **Estancias**: nombre, uso, superficie declarada, superficie medida, dimensiones, ventilación/iluminación natural (huecos), relación con vestíbulos y circulaciones.
- **Huecos**: puertas (ancho libre, sentido de apertura, hacia dónde evacua) y ventanas (ancho, alto, antepecho).
- **Circulaciones**: pasillos (ancho libre), escaleras (nº peldaños, huella, contrahuella, ancho, mesetas), rampas (pendiente), ascensores.
- **Estructura**: tipología (muros, pilares, pantallas), retícula de ejes, luces, voladizos, huecos en forjado, continuidad de pilares entre plantas, cimentación si aparece.
- **Instalaciones**: patinillos y shafts, cuartos técnicos, bajantes, chimeneas, ventilación, extintores/BIE/detección, cuadros eléctricos.
- **Accesibilidad**: itinerarios, diámetros de giro, aseos adaptados, plazas.
- **Textos y leyendas**: notas, cuadros de superficies, calificaciones, cumplimientos que el propio proyecto declara.

## 5. Reglas de procedencia
Cada dato lleva `valor`, `fuente` (hoja, mosaico, coordenadas px) y `fiabilidad`:
- **leído** (cota impresa, texto) · **medido** (escala calibrada) · **inferido** (deducido de otro dato; di cuál) · **ilegible/ausente**.
Lo ilegible o ausente **no se rellena**: va a la lista "información faltante" y limita las conclusiones. Un símbolo dudoso se describe, no se interpreta con seguridad.

## 6. Cruces obligatorios entre hojas
Planta vs sección (alturas, niveles, escaleras) · planta vs alzado (huecos, cotas) · cuadro de superficies vs suma de estancias (`arq areas`) · cotas parciales vs total · numeración y nombres de estancias iguales en todas las hojas · ejes estructurales iguales en todas las plantas.

## 7. Salida
Escribe `work/modelo-plano.md` (legible) y `work/modelo-plano.json` (datos) con las secciones anteriores, y `work/cuadro-superficies.csv` (cabecera `name;declared_m2;width_m;depth_m`, ancho y fondo solo si son rectángulos leídos) para `arq areas work/cuadro-superficies.csv [--built-total X]`, y una lista final: **hojas procesadas · escala calibrada sí/no · datos ilegibles · incoherencias detectadas**. Termina con el resumen de 5 líneas para el dueño.
