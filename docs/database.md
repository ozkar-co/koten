# Base de datos

- Motor: SQLite.
- Archivo principal esperado: data/koten.sqlite3.
- Estrategia de versionado: la base vive en git como respaldo de cambios incrementales.
- No se contempla informacion sensible en esta etapa.

## Tablas de idiomas

- languages: catalogo de lenguas y parser de extraccion.
- roots: raiz lapag y significado semantico.
- root_equivalences: equivalencias por idioma (incluye casos no idempotentes).
- words: diccionario incremental de palabras por idioma.
- word_root_matches: raices detectadas por palabra y su mapeo a lapag.
- word_translations: traducciones guardadas para consulta futura.
