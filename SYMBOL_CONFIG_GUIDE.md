# Symbol Configuration Reference

> Documentación detallada: [docs/symbols-config.md](docs/symbols-config.md)

## Estado actual de hojas y configs

| Idioma | Hoja | Config JSON | root_mapping |
|--------|------|-------------|--------------|
| Lapag | lapeg.png | lapag.json | ✓ completo |
| Gox'jix | goxjix.png | goxjix.json | ✓ completo |
| Dekayun | dekayun.png | dekayun.json | ✓ completo |
| Negelch | negelch.png | negelch.json | ✓ completo |
| Idoling | idoling.png | idoling.json | ✓ completo |
| Jobid'e | jobide.png | jobide.json | ✓ completo |
| Gornach-Kagsha | gornach-kagsha.png | gornach_kagsha.json | ✓ completo |

## Convenio de orden de símbolos

Para que el usuario provea el orden de una hoja nueva:

1. Si el idioma **tiene silencio**: posición `[0,0]` = `_sil`
2. Luego las **vocales** en orden (estas son los tokens de overlay)
3. Luego las **consonantes** restantes
4. Penúltimo: `?`
5. **Último: `" "` (espacio / separador de palabras)** — siempre fijo

Ejemplo: Lapag tiene silencio + 5 vocales + 16 consonantes + ? + espacio = 24 posiciones usadas.

Excepcion Gornach-Kagsha: el orden inicia con `.` y `-`, seguido por sus silabas/particulas; aun asi mantiene el separador de palabras `" "` al final.

## Convenio para vocales consonanticas (Jobid'e)

En Jobid'e la misma vocal puede ser consonante. Los glífos consonanticos se listan DESPUÉS de las 6 vocales y se mapean con sufijo `c`:

- Vocal `i` → key `"i"` (overlay)  
- Consonante-`i` → key `"ic"` (base, sin overlay)

## API rápida

```
GET /word?language=lapag&text=k a m a&spacing_x=10
GET /word?language=jobide&text=j o b i d ' _sil '
GET /word?language=gornach_kagsha&text=gar nach - kag sha
```

Tokens separados por espacio. Respuesta: PNG transparente.
