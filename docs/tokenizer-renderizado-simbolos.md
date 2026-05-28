# Tokenizer y Renderizado de Simbolos

Este documento describe el flujo completo desde un token en Markdown (por ejemplo `/N/n/`) hasta la imagen PNG final que devuelve el backend.

## Vista general del flujo

1. El texto de lore se parsea y los tokens Koten se convierten en HTML con imagen embebida.
2. El navegador solicita la imagen en `/word/{language}/{word}`.
3. El endpoint de simbolos normaliza la entrada y delega en `SymbolGenerator`.
4. El generador tokeniza el texto segun el idioma.
5. Cada token se mapea a un glifo de la hoja (`sheet`) usando `root_mapping`.
6. Los glifos se componen segun el `writing_mode` del idioma.

## 1) Parseo en lore Markdown

Archivo clave: `src/koten/lore/md_parser.py`

Sintaxis soportada en Markdown:

- `/word/` usa idioma por defecto (`lapag`)
- `/L/word/` lapag
- `/G/word/` goxjix
- `/D/word/` dekayun
- `/N/word/` negelsh
- `/I/word/` idoling
- `/J/word/` jobide
- `/K/word/` gornash_kagsha

Notas importantes:

- El prefijo es case-insensitive (`/N/` y `/n/` funcionan igual).
- El contenido `word` se normaliza sin acentos para la URL de imagen.
- El parser genera un `<span class="koten-word">` con `<img src="/word/{language}/{word}">`.

## 2) Endpoint de imagen

Archivo clave: `src/koten/api/symbols.py`

Rutas:

- `GET /word/{language}/{word}`
- `GET /word?language=...&text=...`

Comportamiento:

- Decodifica URL (`unquote`).
- Quita diacriticos (tildes) para estandarizar entrada.
- Llama a `SymbolGenerator.generate_word_image(...)`.
- Devuelve PNG (`image/png`).

## 3) Configuracion de simbolos

Archivo clave: `src/koten/symbols/config.py`

Cada idioma tiene un JSON en `src/koten/symbols/configs/` con:

- `sheet_file`: imagen de sprites (hoja de simbolos)
- `symbol_size`, `rows`, `cols`
- `root_mapping`: token -> posicion `[row, col]`
- `overlay`: reglas de sobreposicion (cuando aplica)
- `spacing`, `trim`, `writing_mode`

### Caso especial del espacio

El token de espacio (`" "`) se preserva de forma explicita en normalizacion interna.
Eso permite que, si el idioma define el espacio en `root_mapping`, se pinte como glifo real.

## 4) Tokenizacion por idioma

Archivo clave: `src/koten/symbols/tokenizers.py`

Regla general:

- El tokenizer produce una lista de tokens.
- Solo se emiten tokens que realmente existan en `root_mapping` (o casos especiales como `_` en goxjix).

### Espacios

- Se usa espacio literal (`" "`) como separador de palabra.
- Si el idioma tiene `" "` en `root_mapping`, ese separador se conserva como token y se dibuja.

### Lapag / Dekayun

- Base consonante+vocal.
- Si una palabra empieza en vocal, puede insertar `_` (silencio) cuando aplica.
- Dekayun reutiliza tokenizer de lapag.

### Goxjix

- Similar a lapag pero contempla secuencias vocalicas (ej. `ai`, `oi`, `au`, etc.).
- `'` se interpreta como silencio explicito (`_`).

### Negelsh

- Simbolos independientes (sin overlay).
- Reconoce digrafos como `sh`.
- Admite signos si existen en mapping (ejemplo: `.` y `?` en negelsh).

### Idoling

- Simbolos independientes.
- Reconoce digrafos como `ts`, `sh` cuando existan en mapping.

### Jobid'e

- Trabaja por pares (silabas C+V).
- Si la longitud es impar, agrega `'` al final.
- No usa separador por espacios dentro del parser silabico (el texto se compacta).
- Aplica alias de vocal consonantica (`i -> ih`, `u -> uh`, etc.) cuando hace falta.

### Gornash-Kagsha

- Parsing greedy (longest match) probando longitudes 4, 3, 2, 1.
- `-` se reserva como token de salto de columna en modo columnar.

## 5) Composicion de glifos

Archivo clave: `src/koten/symbols/generator.py`

Pasos:

1. Carga la config del idioma.
2. Tokeniza el texto de entrada.
3. Convierte cada token a glifo con `extract_symbol_for_root`.
4. Aplica overlay cuando este habilitado y el token actual sea overlayable.
5. Renderiza segun `writing_mode`:
   - `horizontal`
   - `columnar_right`
   - `circular_clockwise_4`

### Overlay

El overlay permite superponer una vocal sobre el simbolo base previo (por ejemplo en idiomas tipo lapag/jobide). Se controla por:

- `overlay.enabled`
- `overlay.roots`
- `overlay.blockers`
- offsets `overlay.offset_x`, `overlay.offset_y`

## 6) Modos de render

### Horizontal

- Concatena glifos de izquierda a derecha.
- Respeta `spacing_x`.

### Columnar (`columnar_right`)

- Divide columnas usando `break_token` (normalmente `-`).
- Dibuja cada columna de arriba hacia abajo.
- Luego compone columnas de izquierda a derecha.

### Circular de 4 cuadrantes (`circular_clockwise_4`)

- Requiere exactamente 4 silabas/tokens base.
- Rota y ubica cada cuadrante en orden horario.

## 7) Errores comunes y diagnostico rapido

### "Root 'X' not found in idioma"

Causas tipicas:

- El token no existe en `root_mapping`.
- El tokenizer genero una forma distinta a la esperada.
- Falta mapear un digrafo o un signo de puntuacion.

### "This language requires exactly 4 syllables"

- Aplica a `jobide` en modo circular de 4 cuadrantes.
- Revisar la longitud/paridad de la entrada y tokenizacion resultante.

### El espacio no se dibuja

- Verificar que `" "` exista en `root_mapping` del idioma.
- Verificar que la entrada realmente tenga espacios literales.

## 8) Ejemplos practicos

### Token de lore con prefijo de idioma

- Markdown: `/N/n/`
- Resultado: imagen pedida a `/word/negelsh/n`

### Palabra con espacio en Negelsh

- Entrada al endpoint: `text=n n&language=negelsh`
- Tokenes esperados: `['n', ' ', 'n']`
- Se dibuja el glifo de espacio si `" "` esta mapeado en `negelsh.json`.

### Punto en Negelsh

Si `.` esta en `root_mapping` (como en negelsh):

- `a.b` tokeniza como `['a', '.', 'b']`
- Se renderiza usando el glifo de punto definido en la hoja.
