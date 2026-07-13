# PROJECT_CONTEXT.md — Contexto profundo del proyecto

> Complemento de `CLAUDE.md`. Aquí vive el contexto que no se deduce del código:
> decisiones tomadas, historia, restricciones académicas y estado de las integraciones.
> Actualizar cuando cambie una decisión, no en cada sesión (para eso están los handoffs).

## 1. Qué es este proyecto

Sistema de **Diligencia Debida Reforzada (EDD)** para cumplimiento AML/CFT en Panamá.
Es el **proyecto semestral de Ingeniería de Software IV** (Unidad II: Medición de la Calidad — ISTQB/TMMi/TQM).

- **Equipo**: Cesar Santiago (aaacmsg / usuario de esta máquina), Jean Suarez, Roberto Lopez. Salón 1GS242.
- **Objetivo real**: demostrar proceso de ingeniería (Scrum, métricas, pruebas, versionamiento), no comercializar. Las decisiones de alcance deben favorecer lo breve y demostrable.

## 2. Entrega final del curso (instrucciones de la profesora)

- Fecha: vencía 2026-07-11 12:00; la plataforma **cierra el 2026-07-13 a las 20:00**.
- Entregables: (1) video Scrum Review máx 10 min con los 3 integrantes en cámara usando "Spick" (3 preguntas: avances / aprendizajes / problemas); (2) documento final PDF con retrospectiva, adecuaciones del Parcial 2, versionamiento y conclusiones individuales+grupales; (3) evidencias: capturas, código, reportes de pruebas, métricas ISTQB-TMMi-TQM, tablero actualizado, enlace al repo.
- Detalle completo de tareas derivadas: `tasks.md` Fase 6.

## 3. Decisiones técnicas y su porqué

| Decisión | Por qué |
|----------|---------|
| bcrypt directo en vez de passlib | Incompatibilidades; se usa la librería `bcrypt` directa |
| SQLAlchemy 2.0.51 (no 2.0.25) | Python 3.14 local requiere wheels cp314 |
| Modelos y schemas en archivos únicos (`models.py`, `schemas.py`) | Proyecto pequeño; se priorizó velocidad sobre la estructura del PRD §11.3 |
| Grafo con SVG propio + simulación de fuerzas (no PyVis/Plotly) | Evitar dependencia Python en el frontend; el PRD menciona PyVis/Plotly pero se decidió implementación React nativa |
| OFAC/ONU/UE **no implementado** | No existen APIs gratuitas — exclusión documentada en PRD §12; debe marcarse "No implementado" en docs (issue #37) |
| Rama `master` (no `main`) | Histórico del repo; los workflows CI disparan sobre `master` |
| Login semilla admin/admin123 | Creado en evento startup del backend para demos |
| Datos PEP de datosabiertos.gob.pa (API CKAN) + antai.gob.pa | Única fuente gratuita confirmada funcionando |

## 4. Estado de integraciones y entornos

- **Docker Compose** levanta todo: backend :8000, frontend :3000, postgres :5432, redis :6379. `docker-compose down -v` = reset.
- **CI GitHub Actions**: backend-ci (pytest), frontend-ci (build), metrics-report (semanal, lunes, genera dashboard como artifact).
- **Playwright**: 20 specs escritas en `frontend/tests/specs/{alfa,beta,ux}` — NO corren en CI aún (#93); requieren backend+DB vivos. Hay `test-results/` con fallos históricos versionados.
- **Celery/Redis**: Redis está en compose pero **no hay tasks Celery implementadas** (`backend/app/tasks/` está vacío salvo `__init__.py`); la descarga de CSVs PEP es manual vía endpoint (#94 pendiente).
- **gh CLI**: autenticado como aaacmsg, pero **sin scope `read:project`** — para leer/actualizar el tablero Projects #2 ejecutar antes: `gh auth refresh -s read:project,project`.

## 5. GitHub: mapa de issues (al 2026-07-13)

- **#1–#68** (`[T-nn]`): 62 tareas de verificación importadas del kanban (`kanban-tasks.md`) mediante `upload_tasks.ps1`/`upload_kanban.ps1`. La mayoría corresponde a funcionalidad **ya implementada** pero los issues siguen OPEN (solo #64, #67, #68 cerrados). Trabajo pendiente = verificar contra código y cerrar con evidencia (Fase 4 de tasks.md).
- **#69–#88**: features completadas, CLOSED con label `completed`.
- **#89–#98**: backlog real pendiente (RBAC, rate limit, WORM, E2E CI, PDF, Celery, admin UI, email, JWT refresh, feature flags) — Fase 5 de tasks.md.
- Labels: backend, frontend, security, testing, devops, pep, metrics, documentation, infrastructure, integration, alfa-*, beta-*, completed.

## 6. Documentos del repo y su rol

| Archivo | Rol |
|---------|-----|
| `PRD.md` | Requisitos completos, marco legal, fórmula de riesgo — referencia normativa |
| `architecture.md` | Arquitectura actual (verificada contra código en issue #68) |
| `plan-de-pruebas.md` | 20 pruebas Alfa/Beta/UX con criterios y estados |
| `daily-scrum-presentacion.md` | Presentación con métricas ISTQB/TMMi/TQM reales — **base para el documento final y el video** |
| `kanban-tasks.md`, `tasks-github.md` | Históricos; superseded por `tasks.md` (raíz) |
| `tasks.md` | **Fuente de verdad actual** por fases |
| `docs/handoffs/` | Bitácora de sesiones de trabajo con Claude |

## 7. Métricas clave ya medidas (para el documento final)

- 63/63 tests unitarios passing; cobertura backend 26%; densidad 27.4 tests/KLOC.
- KLOC: backend 2,337 + frontend 3,689 = 6,026.
- Complejidad ciclomática promedio 2.4 (A); máxima 12 (`pep_service.buscar_funcionario`).
- 0 code smells (flake8), 0 vulnerabilidades (bandit).
- Bloqueos resueltos documentados en `daily-scrum-presentacion.md` §3 (Python 3.14/SQLAlchemy, Alembic CI, labels, workflows master, UTF-8) — sirven directo para la retrospectiva.
- Bloqueo abierto: grafo sin datos reales (falta seed de datos de prueba).
