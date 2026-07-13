---
name: sync-github
description: Sincronizar tasks.md con GitHub Issues y el tablero Projects #2 — cerrar issues implementados con evidencia, crear issues nuevos, y verificar que el tablero refleje la realidad. Usar cuando se completen tareas, al hacer handoff, o cuando el usuario pida actualizar issues/tablero.
---

# Sync GitHub

Repo: `aaacmsg/debida-diligencia-reforzada` (rama `master`). Tablero: proyecto de usuario #2 (`gh project ... --owner aaacmsg`).

## Estado de referencia

- Issues #1–#68 (`[T-nn]`): verificaciones del kanban; muchas ya implementadas pero OPEN. Cerrarlas solo tras verificar contra el código.
- Issues #69–#88: features cerradas (label `completed`).
- Issues #89–#98: backlog pendiente real.
- `tasks.md` (raíz) es la fuente de verdad local; debe coincidir con los issues.

## Comandos

```bash
# Listado compacto de issues
gh issue list -R aaacmsg/debida-diligencia-reforzada --limit 200 --state all \
  --json number,title,state,labels

# Cerrar con evidencia (SIEMPRE con comentario que apunte a código/test/commit)
gh issue close <n> -R aaacmsg/debida-diligencia-reforzada \
  -c "Verificado: implementado en <archivo:linea>, cubierto por <test>. Cerrado desde tasks.md Fase <N>."

# Crear issue nuevo (usar labels existentes: backend, frontend, security, testing, devops, pep, ...)
gh issue create -R aaacmsg/debida-diligencia-reforzada -t "<titulo>" -b "<descripcion>" -l backend

# Tablero Projects (requiere scope; si falla, pedir al usuario ejecutar:  ! gh auth refresh -s read:project,project )
gh project item-list 2 --owner aaacmsg --format json --limit 200
```

## Reglas

1. Nunca cerrar un issue sin haber verificado la funcionalidad en el código (leer el archivo, correr el test si existe).
2. Cada cierre lleva comentario con evidencia (archivo:línea, test, o commit).
3. Después de cerrar/crear issues, actualizar `tasks.md` para que coincida.
4. Si el tablero Projects no es accesible por scopes, dejarlo anotado en el handoff como pendiente — no bloquear el resto de la sincronización.
