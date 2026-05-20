# Gornash-Kagsha

## Escritura

- Direccion: **columnas de arriba hacia abajo**, nuevas columnas hacia la derecha
- Unidad principal: silaba/particula con sonido propio
- **Sin silencio** declarado
- Tiene un **simbolo especial de guion** (`-`) que indica el cambio de columna y se dibuja al final de la columna actual

## Reglas de composicion

- Los simbolos se apilan verticalmente dentro de una columna
- El token `-` cierra la columna y abre una nueva a la derecha
- Recorte: 32 px simetrico arriba y abajo
- El inventario inicia con `.` y luego `-`

## Ejemplo: `garnash-kagsha`

La palabra se descompone en 5 particulas con raices `km-lp`:

```
Columna 1:         Columna 2:
  gar                 kag
  nash                sha
  [guion -]
```

Tokens: `gar nash - kag sha`

## Nota sobre el diccionario

Este idioma asigna una raiz interna a cada particula/silaba. Las raices de `garnash-kagsha` son `km-lp`.

## Diccionario silaba -> raiz

- ar -> a
- ek -> e
- ug -> u
- esh -> e
- ak -> a
- or -> o
- rag -> c
- lar -> d
- kor -> t
- gor -> s
- gar -> k
- rek -> r
- kag -> l
- lok -> n
- nash -> m
- dur -> j
- tar -> g
- ket -> b
- gul -> f
- lug -> y
- sha -> p
- ruk -> x

## Inventario de simbolos

Orden en la hoja (izquierda a derecha, fila por fila):

., -, ar, ek, ug, esh, ak, or, rag, lar, kor, gor, gar, rek, kag, lok, nash, dur, tar, ket, gul, lug, sha, ruk, [espacio]

Total: 25 simbolos.

## Notas

Documento base para completar con reglas formales, diccionario de particulas y contexto cultural.
