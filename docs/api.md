# API (inicio)

- Endpoint inicial: GET /health.
- Imágenes: GET /image/{filename}
- Léxico:
	- POST /lexicon/analyze
	- POST /lexicon/words
	- GET /lexicon/roots/{root}
	- GET /lexicon/words/search
- Símbolos (generación de imágenes de palabras):
	- GET /word/{language}/{word}
	- GET /word?language=...&text=...&spacing_x=...&spacing_y=...
- Lore (documentos de lore con renderizado de símbolos):
	- GET /lore/races/{slug}
	- GET /lore/lang/{slug}
	- GET /lore/prefixes
	- POST /lore/render
- Objetivo de la API: exponer entidades del mundo (historias, razas, idiomas, recursos y reglas).
- Estilo: rutas simples, nombres directos, sin capas innecesarias.

## Imagenes

- Directorio servido: data/images.
- Formatos esperados para servir: .jpg.
- Se admite extension opcional:
	- /image/elfo.jpg
	- /image/elfo
	- /image/elfo_thumb
