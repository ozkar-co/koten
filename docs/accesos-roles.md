# Accesos y Roles

Este documento define la estructura base de usuarios y permisos para el sistema de Koten.

## Objetivo

Controlar acceso a herramientas sensibles (editor de diccionario, creador de palabras, secretos del mundo) sin bloquear el flujo de juego.

## Tipos de Usuario

### Admin

Rol reservado para el creador del mundo.

Permisos:
- Acceso total a todas las secciones y herramientas
- Crear, editar y eliminar contenido de lore, reglas y lenguas
- Gestionar usuarios, roles y permisos
- Ver y editar secciones secretas
- Administrar partidas

### Master

Rol para direccion de partidas y supervision narrativa.

Permisos:
- Ver secretos del mundo
- Administrar partidas (crear, editar estado, cerrar)
- Gestionar personajes de su partida
- Consultar herramientas de referencia

Restricciones:
- No puede crear ni modificar contenido canon (lore, lenguas, reglas base)
- No puede gestionar usuarios globalmente

### Jugador

Rol orientado a participacion en partidas.

Permisos:
- Administrar su hoja de personaje
- Crear y gestionar sus personajes
- Ver y participar en partidas donde tenga acceso

Restricciones:
- No accede a secretos del mundo
- No accede a herramientas de edicion canon (diccionario, creador de palabras, lore global)

## Recursos Sensibles

Recursos que requieren control estricto de acceso:

- Editor de diccionario
- Creador de palabras
- Seccion de secretos del mundo
- Administracion global de partidas

## Politica de Autenticacion

- Acceso mediante usuario y contrasena
- Contrasenas almacenadas solo en formato hash
- Sesiones con expiracion
- Registro de actividad para acciones de administracion

## Politica de Autorizacion

Regla general:
- Todo acceso denegado por defecto
- Se habilita por rol y permiso explicito

Tabla resumen:

| Recurso | Admin | Master | Jugador |
|---------|-------|--------|---------|
| Ver secretos | Si | Si | No |
| Editar secretos | Si | No | No |
| Editor diccionario | Si | No | No |
| Creador de palabras | Si | No | No |
| Administrar partidas | Si | Si | Parcial |
| Gestionar personajes propios | Si | Si | Si |
| Editar lore canonico | Si | No | No |
| Gestionar usuarios y roles | Si | No | No |

## Notas de Implementacion

- Mantener separadas las rutas de lectura publica y de gestion interna.
- Validar permisos en backend, no solo en interfaz.
- Si una accion mezcla recursos (por ejemplo, partida + secreto), aplicar el permiso mas restrictivo.