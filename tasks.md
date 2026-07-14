# tasks.md — Plan por Fases (Diligencia Reforzada EDD)

> Fuente de verdad local del estado del proyecto. Se sincroniza con:
> - Issues: https://github.com/aaacmsg/debida-diligencia-reforzada/issues (98 issues: 23 cerrados, 75 abiertos al 2026-07-13)
> - Tablero: https://github.com/users/aaacmsg/projects/2
>
> Convención: al completar una tarea se marca `[x]` aquí **y** se cierra el issue correspondiente (skill `sync-github`).
> Contexto: proyecto académico — las fases pendientes deben ser breves y demostrables, no producto comercial.
>
> **Flujo de trabajo (definido 2026-07-13):** cada fase pendiente se desarrolla en una rama `fase-<letra>-<tema>` y al completarse se entrega como **Pull Request a `master`**. Nada de commits de features directo a master.
> **Prioridad actual: CÓDIGO** — lo que se implemente debe poder demostrarse en el video de la entrega.

## Fases de código pendientes (orden de prioridad, 1 PR por fase)

| Fase | Contenido | Issues | Estado |
|------|-----------|--------|--------|
| **A — Datos de demo (seed)** | Script de seed: usuarios por rol, clientes (PEP y no PEP) relacionados entre sí, expedientes, alertas — desbloquea el grafo y la demo del video. Incluye fix de `config.py` (REDIS_URL/ALLOWED_ORIGINS rompían el arranque) | [PR #99](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/99) | 🟡 PR abierto — verificado E2E |
| **B — Seguridad P0** | RBAC en endpoints + rate limiting + auditoría WORM. Incluye fix de enums del dashboard (tarjetas en 0) | [PR #100](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/100) (Closes #89, #90, #91) | 🟡 PR abierto — verificado E2E + UI |
| **C — JWT refresh** | Refresh tokens con rotación + interceptor axios que renueva y reintenta | [PR #100](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/100) (Closes #97) | 🟡 PR abierto |
| **D — Export PDF expediente** | pdf_service (fpdf2) + endpoint + botón en UI + evento auditoría | [PR #101](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/101) (Closes #92, #32) | 🟡 PR abierto — 25/25 E2E |
| **E — E2E en CI** | Workflow e2e-tests.yml + fixture auth real + specs corregidos + 4 defectos reales corregidos (NaN submit, 422 payload, toast crash, a11y #34) | [PR #101](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/101) (Closes #93) | 🟡 PR abierto — 25/25 E2E |
| Futuro documentado (no implementar) | Celery CSVs, email, admin UI, feature flags | #94, #95, #96, #98 | ⚪ Trabajo futuro |

---

## Fase 0 — Fundaciones ✅ COMPLETADA

- [x] Scaffolding backend FastAPI + frontend React + PostgreSQL + Redis
- [x] docker-compose con 4 servicios y healthchecks (#60–#64 implementado; issues abiertos pendientes de cerrar)
- [x] Migración Alembic 001 (9 tablas) — fix: env.py lee DATABASE_URL del entorno
- [x] CI GitHub Actions: backend-ci, frontend-ci, metrics-report (trigger en `master`)

## Fase 1 — Backend Core ✅ COMPLETADA (issues #69–#81 cerrados)

- [x] 8 módulos API: auth, clientes, expedientes, documentos, riesgos, pep, reportes, alertas, configuración (#69)
- [x] 9 modelos SQLAlchemy con relaciones (#70)
- [x] Auth JWT + bcrypt: login/register/me (#71)
- [x] CRUD Clientes + auto-creación de Expediente con riesgo calculado (#72)
- [x] CRUD Expedientes + flujo aprobar/rechazar con comentario obligatorio (#73)
- [x] Upload documentos SHA-256 + descarga (#74)
- [x] Cálculo de riesgo — fórmula ponderada 5 variables (#75)
- [x] Búsqueda PEP con RapidFuzz, threshold 85 (#76)
- [x] Sincronización datosabiertos.gob.pa vía API CKAN (#77)
- [x] Reportes: dashboard, auditoría, CSV export, grafo (#78)
- [x] CRUD Alertas + generación automática (#79)
- [x] Configuración persistente key-value (#80)
- [x] Endpoint listado cargos PEP según ley de Panamá (#81)

## Fase 2 — Frontend ✅ COMPLETADA (issues #83–#88 cerrados)

- [x] Dashboard con Recharts: PieChart + BarChart (#83)
- [x] Formulario EDD 7 módulos con Zod + react-hook-form (#84)
- [x] Grafo interactivo SVG con simulación de fuerzas (#85)
- [x] Layout sidebar + dropdown de alertas en vivo (#86)
- [x] PEPSearchPage con búsqueda fuzzy + cargos PEP (#88)
- [x] Páginas: Login, Expedientes (filtros), ExpedienteDetail (3 tabs + aprobar/rechazar), Reportes (CSV), Configuración

## Fase 3 — Calidad y Métricas 🟡 PARCIAL

- [x] 63 tests unitarios pytest (riesgo_service 49 + security 14), 100% passing (#82)
- [x] Script dashboard de métricas: cobertura, KLOC, complejidad, smells, vulnerabilidades (#87)
- [x] 20 specs Playwright E2E escritas (alfa/beta/ux)
- [ ] **Ejecutar Playwright E2E en GitHub Actions CI** (#93) — hoy fallan/no corren sin backend+DB en CI
- [ ] Cargar datos de prueba (seed) para que el grafo y demos tengan datos reales — bloqueo abierto del daily scrum
- [ ] Subir cobertura backend de 26% hacia ≥50% con tests de integración de endpoints (opcional)
- [ ] Refactorizar `pep_service.buscar_funcionario` (complejidad ciclomática 12) (opcional)

## Fase 4 — Verificación Alfa/Beta/UX y limpieza de issues 🔴 PENDIENTE (breve)

Los issues #1–#68 (`[T-nn]`, 62 tareas del kanban) son verificaciones: la mayoría ya está implementada pero sigue OPEN. Trabajo = verificar contra el código y **cerrar issues** con comentario de evidencia.

- [ ] Verificar y cerrar lote alfa-lógica: #1–#5 (sumatoria beneficiarios, campos obligatorios, campos PEP, aprobación alto riesgo, log auditoría)
- [ ] Verificar y cerrar lote alfa-seguridad: #6–#9 (roles, no exponer hashed_password, EventoAuditoria en PUT, created_at server_default)
- [ ] Verificar y cerrar lote backend: #10–#30 (core, endpoints, services)
- [ ] Verificar y cerrar lote beta/UX: #31–#41 (grafo 3 niveles, export PDF/XML, responsive, accesibilidad, validaciones cumplimiento)
- [ ] Verificar y cerrar lote frontend/integración/infra: #42–#63
- [ ] Docs: #65 (README con docker-compose + login), #66 (PRD vs implementado)
- [ ] Ejecutar el plan de pruebas (`plan-de-pruebas.md`, 20 casos) y registrar estados PENDIENTE→APROBADO/FALLIDO
- [ ] **Actualizar tablero GitHub Projects #2** para reflejar la realidad (requiere `gh auth refresh -s read:project,project` — el token actual no tiene el scope)

## Fase 5 — Endurecimiento (backlog abierto #89–#98) 🔴 PENDIENTE — priorizar solo P0

Alcance sugerido para cierre de curso: hacer los P0 si hay tiempo; P1/P2 documentar como "trabajo futuro".

**P0 (seguridad, demostrables en video):**
- [ ] #89 RBAC — control de acceso por roles en login y endpoints
- [ ] #91 Logs de auditoría inmutables (WORM en backend)
- [ ] #90 Rate limiting por IP/usuario (slowapi)

**P1 (opcional):**
- [ ] #93 Playwright E2E en CI (ver Fase 3)
- [ ] #94 Celery task programada para descarga automática de CSVs PEP
- [ ] #97 Expiración y refresh de tokens JWT

**P2 (documentar como trabajo futuro):**
- [ ] #92 Exportar expediente individual a PDF
- [ ] #95 Panel de administración de usuarios (CRUD desde UI)
- [ ] #96 Notificaciones email para alertas de alto riesgo
- [ ] #98 Feature flags para despliegues progresivos

## Fase 6 — Cierre Académico 🔴 PENDIENTE ⚠️ URGENTE (la entrega cierra 2026-07-13 a las 20:00)

**Entregable 1 — Video Scrum Review (máx 10 min):**
- [ ] Guion: demo del software + funcionalidades nuevas/ajustadas del Parcial 2 + estado técnico
- [ ] Formato Spick por integrante: ¿qué avances? / ¿qué aprendieron? / ¿qué problemas? (base: `daily-scrum-presentacion.md` §1–§3)
- [ ] Grabar con los 3 integrantes en cámara, participación equitativa
- [ ] Subir a YouTube/Drive/OneDrive con acceso público y obtener enlace

**Entregable 2 — Documento Final PDF:**
- [x] Contenido completo redactado en **`docs/documento-final.md`** (retrospectiva, adecuaciones fases A–E, métricas, versionamiento, conclusiones, anexos con placeholders de capturas)
- [ ] Insertar capturas donde están los marcadores `<INSERTAR AQUÍ: ...>` (Anexos A–C)
- [ ] Revisar/personalizar conclusiones individuales y tabla de responsabilidades
- [ ] Exportar a PDF

**Entregable 3 — Evidencias:**
- [ ] Capturas del sistema corriendo (login, dashboard, formulario EDD, PEP search, grafo, expediente)
- [ ] Reporte de pruebas: pytest (63/63) + estado Playwright + `plan-de-pruebas.md` con estados
- [ ] Dashboard de métricas (`backend/metrics/dashboard.html`) exportado/capturado
- [ ] Tablero GitHub Projects actualizado (captura)
- [ ] Enlace al repositorio funcional y actualizado

---

## Registro de cambios de este archivo

| Fecha | Cambio |
|-------|--------|
| 2026-07-13 | Creación inicial: consolidación de kanban-tasks.md, tasks-github.md, daily-scrum y 98 issues de GitHub en fases 0–6 |
