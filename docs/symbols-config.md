# Configuración de Símbolos

## Estructura de sprites

Cada idioma tiene una hoja de sprites en `src/koten/symbols/sheets/` de **1600×480 px**, con símbolos de **160×160 px** distribuidos en una grilla de **3 filas × 10 columnas**.

```
Col→  0       1       2     ...   9
Row 0 [0,0]  [0,1]  [0,2]  ...  [0,9]   y: 0 – 160
Row 1 [1,0]  [1,1]  [1,2]  ...  [1,9]   y: 160 – 320
Row 2 [2,0]  [2,1]  [2,2]  ...  [2,9]   y: 320 – 480
```

## Convenio de orden de símbolos

El relleno de la grilla sigue siempre este orden, de izquierda a derecha fila por fila:

| Posición | Símbolo |
|----------|---------|
| `[0,0]`  | **Silencio** `_sil` (si el idioma tiene silencio) o primer símbolo del listado |
| `[0,1]`… | Vocales en el orden declarado |
| Siguiente | Consonantes en el orden declarado |
| Penúltimo | `?` (signo de pregunta / punto) |
| **Último** | `" "` (espacio, separador de palabras) — **siempre fijo en la última posición usada** |

Las posiciones no usadas al final de la grilla quedan vacías.

## Formato del archivo de configuración

Cada idioma tiene un JSON en `src/koten/symbols/configs/`:

```json
{
  "sheet_file": "lapeg.png",
  "symbol_size": 160,
  "cols": 10,
  "rows": 3,
  "writing_mode": "horizontal",
  "spacing": { "x": 10, "y": 10 },
  "trim": { "left": 20, "right": 20, "top": 0, "bottom": 0 },
  "overlay": {
    "enabled": true,
    "roots": ["i", "u", "e", "a", "o"],
    "blockers": [],
    "offset_x": 0,
    "offset_y": 0
  },
  "tokenizer": { "separator": " " },
  "description": "Lapag",
  "root_mapping": {
    "_sil": [0, 0],
    "i":    [0, 1],
    "a":    [0, 4],
    "sh":   [0, 6],
    " ":    [2, 3]
  }
}
```

### Campos

| Campo | Descripción |
|-------|-------------|
| `sheet_file` | Nombre del PNG en `sheets/` |
| `symbol_size` | Tamaño en píxeles de cada símbolo (default 160) |
| `writing_mode` | `horizontal`, `columnar_right`, `circular_clockwise_4` |
| `spacing.x` | Separación horizontal entre símbolos compuestos |
| `spacing.y` | Separación vertical (para modos columnar y circular) |
| `trim` | Recorte en píxeles por borde (`left`, `right`, `top`, `bottom`) |
| `trim.per_root` | Recorte específico por token: `{"sh": {"left": 5}}` |
| `overlay.enabled` | Activar sobreposición de vocales |
| `overlay.roots` | Lista de tokens que actúan como overlay (vocales) |
| `overlay.blockers` | Tokens sobre los que NO se puede sobreponer |
| `overlay.offset_x/y` | Desplazamiento del overlay respecto al símbolo base |
| `tokenizer.separator` | Separador de entrada (default espacio) |
| `columnar.break_token` | Token que inicia nueva columna (solo `columnar_right`) |
| `root_mapping` | Mapa token → `[fila, col]` |

## Modos de escritura

### `horizontal`

Símbolos de izquierda a derecha. Con `overlay.enabled = true`, todo token que esté en `overlay.roots` se compone **sobre el símbolo anterior** en vez de añadirse al lado.

```
entrada: "k a"  →  símbolo k + overlay de a sobre k  → un solo glifo compuesto
entrada: "_sil a" →  silencio + overlay de a  →  vocal "a" sola
```

### `columnar_right`

Símbolos apilados de arriba hacia abajo. Cuando el token es `columnar.break_token` (`"-"` por defecto), se inicia nueva columna a la derecha; el símbolo de guion se dibuja al final de la columna actual.

```
"gar nach - kag sha"
↓ columna 1: gar, nach, [guion]   |  columna 2: kag, sha
```

### `circular_clockwise_4`

Exactamente **4 sílabas** compuestas como un círculo. Las sílabas se rotan antes de posicionarse:

| Posición | Rotación | Cuadrante |
|----------|----------|-----------|
| 1ª sílaba | 0°  | Superior izquierdo |
| 2ª sílaba | 90° horario | Superior derecho |
| 3ª sílaba | 180° | Inferior derecho |
| 4ª sílaba | 270° horario | Inferior izquierdo |

## Convenciones de tokens internos

| Token | Significado |
|-------|-------------|
| `_sil` | Silencio (placeholder; asignar a tu carácter especial al rellenar el mapping) |
| `" "` (espacio) | Separador de palabras |
| `ic`, `uc`, `ec`, `ac`, `oc` | Forma **consonántica** de las vocales en Jobid'e |
| `ai`, `oi`, `au`, `eu`, `iu`, `ia` | Vocales compuestas en Gox'jix |

## Tabla resumen por idioma

| Idioma | Hoja | Silencio | Overlay | Vocales | Trim (px) | Modo |
|--------|------|----------|---------|---------|-----------|------|
| Lapag | lapeg.png | `_sil` | ✓ | i u e a o | L/R 20 | horizontal |
| Gox'jix | goxjix.png | `_sil` | ✓ | i u e a o ai oi au eu iu ia | — | horizontal |
| Dekayun | dekayun.png | `_sil` | ✓ | i u e a o | — | horizontal |
| Negelch | negelch.png | — | ✗ | i u e a o | L/R 32 | horizontal |
| Idoling | idoling.png | — | ✗ | a e i o u | L/R 24 | horizontal |
| Jobid'e | jobide.png | `_sil` | ✓ | i u e a o ' | — | circular×4 |
| Gornach-Kagsha | gornach-kagsha.png | — | ✗ | — | T/B 32 | columnar_right |

## API

```
GET /word/{language}/{word}?spacing_x=10&spacing_y=10
GET /word?language=lapag&text=k a m a&spacing_x=10
```

- Los tokens van **separados por espacio** (o el separador configurado en `tokenizer.separator`).
- Respuesta: imagen PNG transparente.

### Ejemplos

```
# Lapag: "ka" → token k luego a (vocal overlay)
GET /word?language=lapag&text=k a

# Gox'jix: consonante + vocal compuesta
GET /word?language=goxjix&text=sh ai

# Jobid'e: 4 sílabas "jo bi d' e'"  →  j o b i d ' _sil '
GET /word?language=jobide&text=j o b i d ' _sil '

# Garnach-Kagsha: gar nach - kag sha
GET /word?language=gornach_kagsha&text=gar nach - kag sha
```
