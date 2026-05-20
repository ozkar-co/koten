# Frontend Integration Guide

## Overview

El frontend consume dos conjuntos de APIs complementarios:

1. **Symbol API** (`/word/*`) — Genera imágenes de palabras individuales en cualquier idioma de Koten
2. **Lore API** (`/lore/*`) — Renderiza documentos lore como HTML con símbolos integrados

## Images API

### Endpoints

```
GET /image/{filename}         — Get image (default: full size)
GET /image/{filename}?type=thumb  — Get thumbnail or full if unavailable
GET /image/{filename}/meta    — Get image metadata (URLs for thumb + full)
```

### Image Naming Convention

- Full: `mapa.jpg`
- Thumbnail: `mapa_thumb.jpg`

If only full exists, thumbnail endpoint falls back to full.

### Response (meta)

```json
{
  "name": "mapa",
  "full": "/image/mapa?type=full",
  "thumb": "/image/mapa?type=thumb",
  "has_thumb": true
}
```

### Usage

```html
<!-- Full image -->
<img src="/image/mapa?type=full" />

<!-- Thumbnail (or full if thumb not available) -->
<img src="/image/mapa?type=thumb" />
```

## Symbol API

### Endpoints

```
GET /word/{language}/{word}
GET /word?language={language}&text={word}&spacing_x={int}&spacing_y={int}
```

### Languages

```
lapag, goxjix, dekayun, negelsh, idoling, jobide, gornash_kagsha
```

### Response

**Content-Type:** `image/png`  
**Dimensions:** Variable (depends on word length and language layout)  
**Background:** Transparent (RGBA)

### Example

```html
<img src="/word/lapag/kamama" alt="kamama" loading="lazy" />
```

### Spacing

- Default: `0` (letters flush together, per user design)
- Optional parameters for custom spacing between glyphs

## Lore API

### Endpoints

```
GET /lore/{section}/{slug}
GET /lore/index
GET /lore/sections
```

### Lore File Format

The `/lore/` API automatically parses Markdown with embedded Koten word references:

```markdown
# World Title

Text with /lapag/ words here. You can also specify language explicitly:

- /L/lapag/
- /G/goxjix/
- /D/dekayun/
- /N/negelsh/
- /I/idoling/
- /J/jobide/
- /K/gornash_kagsha/

Images work with Markdown or standalone:

![alt](filename.png)

filename.png
```

### Parser Behavior

1. **Koten words** (`/word/` or `/LANG/word/`) → `<span class="koten-word"><img src="/word/{language}/{word}"></span>`
2. **Markdown images** (`![alt](file.png)`) → `<img class="lore-image" src="/image/file.png">`
3. **Standalone images** (filename on its own line) → `<img class="lore-image" src="/image/file.png">`

### Response Format

```html
<html>
  <body>
    <h1>World Title</h1>
    <p>Text with <span class="koten-word" data-language="lapag" data-word="lapag">
      <img src="/word/lapag/lapag" alt="lapag" loading="lazy">
    </span> words here. ...</p>
    
    <img class="lore-image" src="/image/filename.png" alt="filename" loading="lazy">
  </body>
</html>
```

### Koten Word Parsing Rules

- `/word/` or `/ word/` → Defaults to **lapag**
- `/L/word/` or `/LANG/word/` → Explicit language (case-sensitive prefix)
- Word extraction stops at `/`, space, or end of line
- Accents are normalized (áéíóú → aeio) for rendering

### Integration Example

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .koten-word {
            display: inline-block;
            vertical-align: middle;
        }
        .koten-word img, .lore-image {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    <!-- Fetch and inject lore -->
    <div id="content"></div>
    
    <script>
        fetch('/lore/koten')
            .then(r => r.text())
            .then(html => {
                document.getElementById('content').innerHTML = html;
                // <img> tags pointing to /word/... load automatically
            });
    </script>
</body>
</html>
```

## Character Encoding

All language/word parameters should be URL-encoded. Accents are stripped during rendering:

```javascript
function encodeWord(word) {
    // Strip accents
    const normalized = word.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    return encodeURIComponent(normalized);
}

// Usage
function buildWordImageUrl(language, word) {
    return `/word/${language}/${encodeWord(word)}`;
}

// Examples
buildWordImageUrl("lapag", "kamama")          // → /word/lapag/kamama
buildWordImageUrl("goxjix", "goxjix")          // → /word/goxjix/goxjix
buildWordImageUrl("dekayun", "néshta")         // → /word/dekayun/neshta (accent stripped)
```

## Performance Notes

- Symbol images are generated on-demand and should be cached by the frontend
- Lore documents are rendered on-demand (consider caching if heavy use)
- Image files (full + thumbnails) should be cached aggressively since they're static

## Debugging

### Check available languages

```bash
curl https://koten-api.ozkr.net/lexicon/languages | jq
```

### Generate a word image directly

```bash
curl https://koten-api.ozkr.net/word/lapag/kamama -o kamama.png
```

### Fetch lore document

```bash
curl https://koten-api.ozkr.net/lore/koten
```

### Check image metadata

```bash
curl https://koten-api.ozkr.net/image/mapa/meta | jq
```
