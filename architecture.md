# Sistema de Diligencia Reforzada (EDD) - Architecture

## 1. Overview

AML/CFT compliance application for Panama's "Diligencia Reforzada" (Enhanced Due Diligence) based on:
- **Ley 23/2015** - Money laundering prevention
- **Ley 254/2021** - Tax transparency
- **SBP-RG-PSO-R-2025-00671** - Banking supervision requirements

## 2. Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + TypeScript + Vite + TailwindCSS |
| Backend | FastAPI (Python 3.11) + SQLAlchemy 2.0 |
| Database | PostgreSQL 15 |
| Cache/Queue | Redis 7 |
| Auth | JWT (python-jose) + bcrypt |

## 3. Architecture Diagram

```
+-----------------------------------------------------------------+
|                         DOCKER COMPOSE                          |
|                                                                 |
|  +--------------+  +--------------+  +------------------------+ |
|  |   frontend   |  |   backend    |  |        db (postgres)   | |
|  |  (React :3000)|  |(FastAPI :8000)|  |        (port 5432)     | |
|  +------+-------+  +------+-------+  +------------+------------+ |
|         |                 |                        |            |
|         |    HTTP REST   |                        |            |
|         +----------------+                        |            |
|                    +--------------+              |            |
|                    |    redis     |<-------------+            |
|                    |  (port 6379) |                             |
|                    +--------------+                             |
+-----------------------------------------------------------------+
```

## 4. Backend Structure

```
backend/
+-- app/
|   +-- main.py              # FastAPI app, CORS, startup admin seed
|   +-- api/v1/
|   |   +-- router.py        # Aggregates all endpoint routers
|   |   +-- endpoints/
|   |       +-- auth.py      # POST /login, /register, GET /me
|   |       +-- clientes.py   # CRUD + auto-expediente creation
|   |       +-- expedientes.py # CRUD + approve/reject
|   |       +-- documentos.py  # Upload with SHA-256 hash
|   |       +-- riesgos.py     # POST /calcular
|   |       +-- pep.py         # POST /buscar (fuzzy matching)
|   |       +-- reportes.py     # Dashboard stats, audit, CSV
|   +-- core/
|   |   +-- config.py        # Pydantic Settings (env vars)
|   |   +-- database.py      # SQLAlchemy engine + session
|   |   +-- security.py      # JWT + bcrypt
|   +-- models/
|   |   +-- models.py        # SQLAlchemy models (8 tables)
|   +-- schemas/
|   |   +-- schemas.py       # Pydantic request/response models
|   +-- services/
|       +-- riesgo_service.py      # Weighted risk formula
|       +-- pep_service.py         # Fuzzy matching (RapidFuzz)
|       +-- datos_abiertos_service.py # CKAN API integration
+-- migrations/                # Alembic migrations
+-- Dockerfile
+-- requirements.txt
```

### Database Schema

```
+-----------+       +-----------+       +--------------+
|  Cliente  |------>| Expediente |<-----| EventoAuditoria|
| (clientes)|       |(expedientes)      |(eventos_auditoria)
+-----------+       +-------+-----+       +--------------+
       |                   |
       |            +------+------+-----+
       v            v             v          v
+-----------+   +-----------+ +--------+ +--------+
|Beneficiario|  | Documento | | Alerta | | FuncionarioPublico
|  Final     |  |(documentos)| |(alertas)| |(funcionarios_pub)
+-----------+   +-----------+ +--------+ +--------+
```

### API Endpoints

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/v1/auth/login` | POST | OAuth2 password flow, returns JWT |
| `/api/v1/auth/register` | POST | Create new user |
| `/api/v1/clientes/` | GET, POST | List/create clients |
| `/api/v1/clientes/{id}` | GET, PUT, DELETE | Client operations |
| `/api/v1/expedientes/` | GET, POST | List/create expedientes |
| `/api/v1/expedientes/{id}/aprobar` | POST | Approve with comment |
| `/api/v1/expedientes/{id}/rechazar` | POST | Reject with comment |
| `/api/v1/documentos/{id}/upload` | POST | Upload file (multipart) |
| `/api/v1/riesgos/calcular` | POST | Calculate risk score |
| `/api/v1/pep/buscar` | POST | Fuzzy search PEP database |
| `/api/v1/reportes/dashboard` | GET | Dashboard statistics |

## 5. Frontend Structure

```
frontend/src/
+-- main.tsx                # React entry point
+-- App.tsx                # Router + protected routes
+-- components/layout/
|   +-- Layout.tsx         # Sidebar + navigation
+-- pages/
|   +-- LoginPage.tsx      # Auth form
|   +-- DashboardPage.tsx  # Stats + charts (Recharts)
|   +-- ClientesPage.tsx   # EDD form (6 modulos accordion)
|   +-- ExpedientesPage.tsx # List with filters
|   +-- ExpedienteDetailPage.tsx # Tabs: detail, docs, audit
|   +-- PEPSearchPage.tsx  # Search + match results
|   +-- ReportesPage.tsx   # Audit log + CSV export
|   +-- GrafoPage.tsx      # SVG interactive graph
|   +-- ConfiguracionPage.tsx # Settings panels
+-- services/
|   +-- api.ts             # Axios instance + interceptors
|   +-- authService.ts     # Login/register/logout
|   +-- clienteService.ts  # Client CRUD
|   +-- expedienteService.ts # Expediente CRUD + approve/reject
+-- stores/
|   +-- authStore.ts       # Zustand auth state
+-- types/
    +-- index.ts           # TypeScript interfaces
```

### Routing Flow

```
BrowserRouter
+-- /login (public)
+-- / (protected)
    +-- Layout (sidebar)
        +-- Outlet
            +-- /dashboard
            +-- /clientes
            +-- /expedientes
            +-- /expedientes/:id
            +-- /pep
            +-- /reportes
            +-- /grafo
            +-- /configuracion
```

## 6. Risk Calculation Formula

```
Score = (Pais * 0.25) + (Cargo * 0.30) + (Sector * 0.15) + (Vinculos * 0.20) + (OrigenFondos * 0.10)
```

| Score | Risk Level | Action |
|-------|------------|--------|
| 0-35 | LOW | Standard monitoring, annual review |
| 36-65 | MEDIUM | Enhanced monitoring, semi-annual review |
| 66+ | HIGH | Mandatory EDD + Senior Management approval |

**PEP Auto-flag:** When `es_pep = true`:
- Forces `nivel_riesgo = alto`
- Sets `requiere_aprobacion_gerencial = true`
- Sets `estado = pendiente_gerencia`

## 7. PEP Matching Logic

Uses **RapidFuzz** library with configurable threshold (default 85):

```
1. Exact cedula match -> ALTA (score 95+)
2. Name similarity > 85% -> MEDIA
3. Fuzzy search against FuncionarioPublico table
```

Data source: `https://monitoreo.antai.gob.pa/api/designations/download/{ID}/csv`

## 8. Security

| Feature | Implementation |
|---------|----------------|
| Password | bcrypt (via direct library, not passlib) |
| JWT | HS256, 60min expiry, refresh 7 days |
| CORS | Whitelist: `http://localhost:3000` |
| Auth flow | OAuth2PasswordBearer -> `/api/v1/auth/login` |
| Default admin | `admin` / `admin123` (created on startup) |

## 9. Environment Variables

**Backend:**
- `DATABASE_URL=postgresql://postgres:postgres@db:5432/diligencia_db`
- `SECRET_KEY=<secret>`
- `REDIS_URL=redis://redis:6379/0`

**Frontend:**
- `VITE_API_URL=http://localhost:8000/api/v1`

## 10. Docker Services

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| backend | Build Dockerfile | 8000 | FastAPI app |
| frontend | Build Dockerfile | 3000 | React dev server |
| db | postgres:15-alpine | 5432 | PostgreSQL |
| redis | redis:7-alpine | 6379 | Cache + Celery broker |

## 11. Key Files

| File | Purpose |
|------|---------|
| `PRD.md` | Full requirements document |
| `docker-compose.yml` | Container orchestration |
| `backend/Dockerfile` | Python 3.11 + dependencies |
| `frontend/Dockerfile` | Node 18 + Vite dev |
| `backend/migrations/versions/001_initial_schema.py` | DB schema |

## 12. Development Commands

```bash
# Start all services
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend

# Reset database
docker-compose down -v
docker-compose up --build
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- API Docs: http://localhost:8000/docs
- Login: admin / admin123