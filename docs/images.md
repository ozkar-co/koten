# Imagenes (KISS)

- Carpeta principal: data/images.
- Regla de formatos: todo termina en .jpg.
- Miniaturas: si falta {nombre}_thumb.jpg, se genera automaticamente.
- Script: scripts/process_images.py.

## Flujo

1. Colocar imagenes en data/images (jpg, jpeg, png o webp).
2. Ejecutar el script de procesamiento.
3. Consumir via API con /image/nombre o /image/nombre.jpg.
