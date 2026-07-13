---
name: run-app
description: Levantar y verificar la aplicación EDD (backend FastAPI + frontend React + PostgreSQL + Redis) para desarrollo, demos o verificación de cambios. Usar cuando haya que correr la app, probar un flujo end-to-end, tomar capturas o validar que un cambio funciona de verdad.
---

# Run App — Diligencia Reforzada EDD

## Opción A — Docker (recomendada, levanta todo)

```bash
docker-compose up --build -d
docker-compose ps                      # esperar db healthy y backend arriba
docker-compose logs -f backend        # si algo falla
```

- Frontend: http://localhost:3000 — Backend: http://localhost:8000 — Swagger: http://localhost:8000/docs
- Login semilla: **admin / admin123** (se crea en startup).
- Reset total (borra datos): `docker-compose down -v`.

## Opción B — Local (solo backend o solo frontend)

```bash
# Backend (requiere PostgreSQL y Redis locales o del compose)
cd backend && venv/Scripts/activate
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev   # :3000, espera API en localhost:8000
```

## Verificación mínima de que "funciona"

1. `GET http://localhost:8000/docs` responde 200.
2. Login en :3000 con admin/admin123 llega al dashboard.
3. Flujo clave para demos: crear cliente (formulario EDD) → se auto-crea expediente con riesgo → si `es_pep=true` queda en `pendiente_gerencia` → aprobar requiere comentario.

## Tests

```bash
cd backend && pytest                    # 63 unitarios, no requieren DB
cd frontend && npm run build            # verificación de tipos + build
cd frontend && npx playwright test      # E2E — REQUIERE app corriendo (Opción A)
```

## Gotchas

- Windows: si un script Python falla con UnicodeEncodeError, agregar `encoding="utf-8"`.
- Puertos ocupados 3000/8000/5432/6379: revisar contenedores previos con `docker ps`.
- El grafo se ve vacío sin datos: crear 2-3 clientes relacionados primero (no hay seed automático).
