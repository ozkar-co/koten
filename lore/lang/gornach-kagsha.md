# Gornach-Kagsha

## Escritura

- Direccion: **columnas de arriba hacia abajo**, nuevas columnas hacia la derecha
- Unidad principal: silaba/particula con sonido propio
- **Sin silencio** declarado
- Tiene un **simbolo especial de guion** (`-`) que indica el cambio de columna y se dibuja al final de la columna actual

## Reglas de composicion

- Los simbolos se apilan verticalmente dentro de una columna
- El token `-` cierra la columna y abre una nueva a la derecha
- Recorte: 32 px simetrico arriba y abajo

## Ejemplo: `garnach-kagsha`

La palabra se descompone en 5 particulas con raices `km-lp`:

```
Columna 1:         Columna 2:
  gar                 kag
  nach                sha
  [guion -]
```

Tokens: `gar nach - kag sha`

## Nota sobre el diccionario

Este idioma asigna una raiz interna a cada particula/silaba. El usuario debe proveer el diccionario de particulas → token interno. Las raices de `garnach-kagsha` son `km-lp`.

## Inventario de simbolos

Pendiente: el usuario proporcionara el listado completo en orden de la hoja.

## Notas

Documento base para completar con reglas formales, diccionario de particulas y contexto cultural.
