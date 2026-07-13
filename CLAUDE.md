# CLAUDE.md — Sistema de Diligencia Debida Reforzada (EDD)

Aplicación de cumplimiento AML/CFT para Panamá (Ley 23/2015, Ley 254/2021, Resolución SBP-RG-PSO-R-2025-00671). **Proyecto semestral académico** de Ingeniería de Software IV — no busca ser producto comercial; prioriza completar fases breves y demostrables.

## Sistema de contexto entre sesiones (LEER PRIMERO)

Para no perder contexto entre sesiones de Claude:

1. **Al iniciar sesión**: leer `tasks.md` (estado por fases), `docs/context/PROJECT_CONTEXT.md` (decisiones y gotchas) y el handoff más reciente en `docs/handoffs/`.
2. **Al terminar sesión** (o antes de compactar): usar el skill `session-handoff` para escribir un handoff nuevo en `docs/handoffs/AAAA-MM-DD-tema.md` y actualizar `tasks.md`.
3. **Fuente de verdad de tareas**: `tasks.md` ↔ GitHub Issues. Al completar algo, marcar en `tasks.md` Y cerrar el issue (skill `sync-github`).

## Enlaces del proyecto

| Recurso | URL |
|---------|-----|
| Repositorio | https://github.com/aaacmsg/debida-diligencia-reforzada |
| Tablero (GitHub Projects) | https://github.com/users/aaacmsg/projects/2 |
| Issues | https://github.com/aaacmsg/debida-diligencia-reforzada/issues |

- Rama principal: **`master`** (no existe `main`; los workflows disparan sobre `master`).
- Para leer el tablero con `gh` se necesita el scope `read:project`: `gh auth refresh -s read:project,project`.

## Stack y arquitectura

- **Backend**: FastAPI (Python 3.11 en Docker; localmente hay Python 3.14 → requiere SQLAlchemy ≥ 2.0.51), SQLAlchemy 2.0, Pydantic v2, PostgreSQL 15, Redis 7, JWT (python-jose) + bcrypt directo (no passlib).
- **Frontend**: React 18 + TypeScript (strict, sin `any`) + Vite + TailwindCSS + Zustand + react-hook-form + Zod + Recharts.
- **Detalle completo**: ver `architecture.md` (diagramas, 9 tablas, endpoints) y `PRD.md` (requisitos, fórmula de riesgo, validaciones legales).

Estructura: `backend/app/{api/v1/endpoints, core, models, schemas, services, tasks}` y `frontend/src/{pages, components, services, stores, types}`. Modelos en un solo archivo `backend/app/models/models.py`; schemas en `backend/app/schemas/schemas.py`.

## Comandos

```bash
# Todo con Docker (recomendado)
docker-compose up --build          # backend :8000, frontend :3000, db :5432, redis :6379
docker-compose down -v             # reset completo (borra datos)

# Backend local
cd backend && venv/Scripts/activate   # Windows
uvicorn app.main:app --reload --port 8000
pytest                                # 63 tests unitarios (no requieren DB)
python scripts/generate_metrics_dashboard.py   # genera backend/metrics/dashboard.html

# Frontend local
cd frontend && npm install && npm run dev      # :3000
npm run build                                  # verificación obligatoria antes de dar por hecho
npx playwright test                            # E2E (requiere backend + DB corriendo)
```

- Login por defecto: **admin / admin123** (se crea en el startup del backend).
- Swagger: http://localhost:8000/docs

## Reglas de negocio críticas (no romper)

- **Fórmula de riesgo**: `Score = País×0.25 + Cargo×0.30 + Sector×0.15 + Vínculos×0.20 + OrigenFondos×0.10`; niveles: 0-35 bajo, 36-65 medio, 66-100 alto (`riesgo_service.py`, 49 tests).
- **Regla PEP**: si `es_pep=true` → `nivel_riesgo=alto`, `requiere_aprobacion_gerencial=true`, expediente en `pendiente_gerencia`, sin importar el score.
- Aprobar/rechazar expediente **siempre requiere comentario** de justificación.
- Beneficiarios finales: participación individual >10% relevante, sumatoria ≤ 100%.
- Documentos: solo PDF/PNG/JPG, máx 10MB, hash SHA-256 obligatorio.
- Auditoría: cada PUT genera `EventoAuditoria` (usuario, fecha UTC, ip_address).
- Matching PEP: RapidFuzz threshold 85; cédula exacta → alerta ALTA.

## Convenciones

- Código, commits y documentación en **español** (los docs históricos evitan tildes en algunos archivos; mantener consistencia con el archivo que edites).
- Python: flake8 limpio, type hints. TypeScript: strict.
- Commits pequeños y descriptivos (`fix:`, `feat:` estilo ya usado en el historial).
- Verificación antes de dar por completado: backend arranca con uvicorn + `pytest` verde; frontend `npm run build` exitoso.
- `AGENTS.md` describe el workflow por fases (spec → plan → build → verify); los skills reales del repo están en `.claude/skills/`.

## Gotchas conocidos

- **Windows + UTF-8**: escribir archivos con `encoding="utf-8"` explícito (hubo UnicodeEncodeError con emojis).
- **Alembic en CI**: `migrations/env.py` sobrescribe `sqlalchemy.url` desde la variable `DATABASE_URL`.
- **Python 3.14 local** vs 3.11 en Docker: si un paquete falla local, revisar wheels cp314.
- Los issues #1–#68 (`[T-nn]`) son tareas de verificación del kanban: muchas ya están implementadas pero siguen OPEN en GitHub — verificar y cerrar, no re-implementar a ciegas.
- `frontend/dist/` y `frontend/test-results/` están versionados (legado); no tocar salvo limpieza deliberada.

## Contexto académico

Entrega final del curso (ver instrucciones completas en `docs/context/PROJECT_CONTEXT.md` §Entrega):
1. **Video Scrum Review** (máx 10 min, todos los integrantes en cámara).
2. **Documento final PDF**: retrospectiva, adecuaciones Parcial 2, versionamiento, conclusiones individuales/grupales.
3. **Evidencias**: capturas, código, reportes de pruebas, métricas ISTQB/TMMi/TQM, tablero actualizado, repo.

Integrantes: Cesar Santiago, Jean Suarez, Roberto Lopez. Material de apoyo ya existente: `daily-scrum-presentacion.md` (métricas y retrospectiva), `plan-de-pruebas.md` (20 pruebas Alfa/Beta/UX), `backend/metrics/dashboard.html`.
