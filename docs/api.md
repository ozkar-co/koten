# API (inicio)

- Endpoint inicial: GET /health.
- Imagenes: GET /image/{filename}
- Lexico:
	- POST /lexicon/analyze
	- POST /lexicon/words
	- GET /lexicon/roots/{root}
	- GET /lexicon/words/search
- Objetivo de la API: exponer entidades del mundo (historias, razas, idiomas, recursos y reglas).
- Estilo: rutas simples, nombres directos, sin capas innecesarias.

## Imagenes

- Directorio servido: data/images.
- Formatos esperados para servir: .jpg.
- Se admite extension opcional:
	- /image/elfo.jpg
	- /image/elfo
	- /image/elfo_thumb
