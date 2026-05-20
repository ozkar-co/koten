# Frontend Integration Guide

## Overview

El frontend consume dos conjuntos de APIs complementarios:

1. **Symbol API** (`/word/*`) — Genera imágenes de palabras individuales en cualquier idioma de Koten
2. **Lore API** (`/lore/*`) — Renderiza documentos lore como HTML con símbolos integrados

## Images API

### Endpoints

```
GET /api/image/{filename}         — Get image (default: full size)
GET /api/image/{filename}?type=thumb  — Get thumbnail or full if unavailable
GET /api/image/{filename}/meta    — Get image metadata (URLs for thumb + full)
```

### Image Naming Convention

- Full: `mapa.jpg`
- Thumbnail: `mapa_thumb.jpg`

If only full exists, thumbnail endpoint falls back to full.

### Response (meta)

```json
{
  "name": "mapa",
  "full": "/api/image/mapa?type=full",
  "thumb": "/api/image/mapa?type=thumb",
  "has_thumb": true
}
```

### Usage

```html
<!-- Full image -->
<img src="/api/image/mapa?type=full" />

<!-- Thumbnail (or full if thumb not available) -->
<img src="/api/image/mapa?type=thumb" />
```

## Symbol API

### Endpoints

```
GET /api/word/{language}/{word}
GET /api/word?language={language}&text={word}&spacing_x={int}&spacing_y={int}
```

### Languages

```
lapag, goxjix, dekayun, negelch, idoling, jobide, gornach_kagsha
```

### Response

**Content-Type:** `image/png`  
**Dimensions:** Variable (depends on word length and language layout)  
**Background:** Transparent (RGBA)

### Example

```html
<img src="/api/word/lapag/kamama" alt="kamama" loading="lazy" />
```

### Spacing

- Default: `0` (letters flush together, per user design)
- Optional parameters for custom spacing between glyphs

## Lore API

### Index & Navigation Endpoints

```
GET /api/lore/index              — Complete index of all sections
GET /api/lore/races              — List all races
GET /api/lore/lang               — List all languages
```

Response format (index):
```json
{
  "races": [
    {"slug": "alish", "title": "Alish"},
    {"slug": "drayim", "title": "Drayim"},
    ...
  ],
  "languages": [
    {"slug": "lapag", "title": "Lapag"},
    ...
  ],
  "prefixes": {
    "L": "lapag",
    "G": "goxjix",
    ...
  }
}
```

### Document Rendering Endpoints

```
GET /api/lore/races/{slug}          — Render race lore document
GET /api/lore/lang/{slug}           — Render language lore document
GET /api/lore/prefixes              — Get language prefix mappings
POST /api/lore/render               — Render arbitrary markdown
```

### Response

**Content-Type:** `text/html` or `application/json`

### Language Prefixes

Single-letter prefix → language code mapping:

```json
{
  "L": "lapag",
  "G": "goxjix",
  "D": "dekayun",
  "N": "negelch",
  "I": "idoling",
  "J": "jobide",
  "K": "gornach_kagsha"
}
```

### Markdown Syntax (Koten Words)

Within lore markdown documents, reference Koten words using slash notation:

```
/word/           → implicit Lapag (default)
/L/word/         → explicit Lapag
/G/word/         → Gox'jix
/D/, /N/, /I/, /J/, /K/  → other languages
```

Example markdown:
```
Los /alish/ escuchan el llamado de /G/goxjix/.
```

### HTML Output

Each word reference is converted to a `<span>` tag with embedded image:

```html
<p>Los <span class="koten-word" data-language="lapag" data-word="alish">
  <img src="/api/word/lapag/alish" alt="alish" loading="lazy">
</span> escuchan el llamado de <span class="koten-word" data-language="goxjix" data-word="goxjix">
  <img src="/api/word/goxjix/goxjix" alt="goxjix" loading="lazy">
</span>.</p>
```

### Styling

The frontend can style `.koten-word` spans:

```css
.koten-word {
  display: inline-block;
  vertical-align: middle;
  margin: 0 2px;
}

.koten-word img {
  max-height: 1.5em;
  width: auto;
}
```

## Integration Pattern

### Dynamic Navigation (Recommended)

**Do not maintain hardcoded lists.** Load the index on app startup:

```javascript
// On app load
fetch('/api/lore/index')
  .then(res => res.json())
  .then(index => {
    buildRaceMenu(index.races);      // [{"slug":"alish","title":"Alish"},...] 
    buildLanguageMenu(index.languages);
  });

// On menu click
function viewRace(slug) {
  fetch(`/api/lore/races/${slug}`)
    .then(res => res.text())
    .then(html => {
      document.getElementById('content').innerHTML = html;
      // <img> tags pointing to /api/word/... load automatically
    });
}
```

### Markdown Links (Ignore)

The markdown files contain links like `[Ujom](ujom.md)`.  
These are for **documentation purposes only**.  
The frontend should **block or intercept** these and use its own router instead:

```javascript
document.addEventListener('click', (e) => {
  if (e.target.tagName === 'A' && e.target.href.endsWith('.md')) {
    e.preventDefault();
    const slug = e.target.href.split('/').pop().replace('.md', '');
    viewRace(slug); // or viewLanguage(slug)
  }
});
```

Or simpler: just ignore them and build the full menu from the index.

---

### 1. Display a Race/Language Document

```javascript
async function loadRace(raceName) {
  const response = await fetch(`/api/lore/races/${raceName}`);
  const html = await response.text();
  document.getElementById('content').innerHTML = html;
  // Images load from /api/word/... automatically
}
```

### 2. Render Custom Markdown

```javascript
async function renderCustom(markdownText) {
  const response = await fetch('/api/lore/render', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: markdownText })
  });
  const html = await response.text();
  document.getElementById('content').innerHTML = html;
}
```

### 3. Display Standalone Word Image

```javascript
function getWordImageUrl(language, word) {
  return `/api/word/${language}/${word}`;
}

// Usage
<img src="/api/word/lapag/kamama" alt="kamama" />
```

## Special Cases

### Jobid'e (4-syllable circular layout)

Input: `jobid'e` (7 chars)  
Internal: `jobid'e'` (8 chars, apostrophe padded)  
Output: 320×320 px circular arrangement  

User writes naturally; padding is automatic.

### Gox'jix (apostrophe as silence)

The apostrophe `'` in Gox'jix text is treated as silencio (silence marker):

```
/G/sat'ue/  → goxjix word with internal silence
```

### Gornach-Kagsha (columnbreak token)

Hyphen `-` marks column breaks in columnar layout:

```
/K/gar-kag/  → two columns: [gar] [kag]
```

## Error Handling

### 404 — Document/Word Not Found

```json
{
  "detail": "Lore file not found: races/unknown"
}
```

### 400 — Invalid Path (traversal attempt)

```json
{
  "detail": "Invalid path"
}
```

### Missing Word in Language

No error; endpoint attempts to render what's available.  
Tokenizer skips unmapped characters.

## Performance Notes

- Symbol images are generated on-demand; cache them on the frontend if needed
- Lore documents render once; HTML is static + embedded images
- All images use `loading="lazy"` for deferred loading
- Image size typically 300–800 px wide, 160–330 px tall
