---
name: session-handoff
description: Cerrar una sesión de trabajo dejando el contexto listo para la siguiente — escribe el handoff en docs/handoffs/, actualiza tasks.md y sincroniza issues. Usar al final de cada sesión, antes de compactar contexto, o cuando el usuario pida "handoff", "cierra la sesión" o "deja todo documentado".
---

# Session Handoff

Objetivo: que la próxima sesión (u otro agente/persona) continúe el trabajo sin re-descubrir nada.

## Pasos

1. **Escribir el handoff**: copiar `docs/handoffs/TEMPLATE.md` a `docs/handoffs/AAAA-MM-DD-<tema-kebab>.md` (fecha de hoy) y completarlo con:
   - Estado en una frase + lo siguiente más importante.
   - Qué se hizo (archivos, commits), decisiones (con el porqué), pendientes con el punto exacto donde se quedó, bloqueos/gotchas, y estado de verificación real (pytest / npm run build / prueba manual — decir "no corrido" si no se corrió; nunca inventar).
2. **Actualizar `tasks.md`**: marcar `[x]` lo completado, agregar tareas nuevas descubiertas en la fase correcta, y agregar fila al "Registro de cambios".
3. **Sincronizar GitHub** (skill `sync-github`): cerrar issues completados con comentario de evidencia; crear issues para tareas nuevas relevantes.
4. **Decisiones permanentes**: si en la sesión se tomó una decisión de arquitectura/alcance, agregarla a `docs/context/PROJECT_CONTEXT.md` §3.
5. **Commit**: commitear los archivos de contexto junto con el trabajo de la sesión (mensaje `docs: handoff sesion AAAA-MM-DD`). Push a `master` si el usuario ya autorizó push en la sesión.

## Reglas

- El handoff se escribe aunque la sesión haya sido corta o fallida — un handoff de 5 líneas vale más que ninguno.
- No duplicar contenido: detalles de decisión van en PROJECT_CONTEXT.md, estado de tareas en tasks.md; el handoff enlaza, no repite.
