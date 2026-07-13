# Handoff — 2026-07-13 — Setup del sistema de contexto y consolidación de tareas

## Estado en una frase

El software está funcionalmente completo para el alcance del curso (backend + frontend + CI + métricas); lo urgente es la **Fase 6 (entregables académicos — la plataforma cierra hoy 2026-07-13 a las 20:00)** y, después, cerrar los ~65 issues de verificación abiertos.

## Qué se hizo esta sesión

- `git pull` verificado: repo local sincronizado con https://github.com/aaacmsg/debida-diligencia-reforzada (rama `master`, limpio).
- Auditoría de los 98 issues de GitHub: #69–#88 cerrados (features hechas), #1–#68 mayormente abiertos pero ya implementados (son verificaciones), #89–#98 backlog real.
- Creado **CLAUDE.md** (guía para sesiones de Claude: comandos, reglas de negocio, gotchas, sistema de contexto).
- Creado **tasks.md** (fuente de verdad por fases 0–6, mapeado a issues; reemplaza a `kanban-tasks.md` y `tasks-github.md` como referencia activa).
- Creado **docs/context/PROJECT_CONTEXT.md** (decisiones, entrega académica, mapa de issues, métricas).
- Creado **docs/handoffs/** con TEMPLATE.md y este handoff.
- Creados skills de proyecto en `.claude/skills/`: `session-handoff`, `sync-github`, `run-app`.

## Decisiones tomadas (y por qué)

- `tasks.md` en la raíz es la fuente de verdad; los archivos kanban previos quedan como históricos (evita 3 listas divergentes).
- Fases 4–5 se plantean como trabajo breve (verificar+cerrar issues, P0 de seguridad); P1/P2 se documentan como trabajo futuro — acorde a la instrucción de que no sea una app comercializable.

## Qué quedó pendiente / a medias

- **Fase 6 completa** (video, documento PDF, evidencias) — ver `tasks.md` Fase 6. Es lo más urgente.
- **Tablero GitHub Projects #2 sin verificar**: el token de `gh` no tiene scope `read:project`. Correr `gh auth refresh -s read:project,project` (interactivo) y luego `gh project item-list 2 --owner aaacmsg` para comparar contra `tasks.md`.
- Cierre masivo de issues #1–#66 tras verificación (Fase 4).
- Commit/push de los archivos creados en esta sesión.

## Bloqueos y gotchas descubiertos

- `gh project ...` falla con "missing required scopes [read:project]" — requiere refresh interactivo del token.
- Los issues [T-nn] duplican el kanban y no reflejan el estado real (features hechas siguen OPEN); no usar el conteo de issues abiertos como medida de avance.

## Estado de verificación

- Tests backend: no corridos esta sesión (último estado conocido: 63/63 passing).
- Build frontend: no corrido esta sesión.
- App levantada manualmente: no.

## Archivos actualizados de contexto

- [x] `tasks.md` creado/actualizado
- [ ] Issues de GitHub cerrados/creados (pendiente Fase 4)
- [x] `PROJECT_CONTEXT.md` creado
