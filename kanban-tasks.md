# Kanban Board - Sistema de Diligencia Reforzada (EDD)

## Instrucciones de Uso
Copiar cada seccion y pegarla en GitHub Projects como items individuales.
Primero crear el proyecto en GitHub.com > Projects > New Project

---

## ALFA - LOGICA INTERNA (5 tareas)

- [ ] Validar sumatoria de participaciones BeneficiarioFinal <= 100%
- [ ] Verificar obligatoriedad de campos criticos: nombre, numero_identificacion, tipo_identificacion
- [ ] Si es_pep=true, obligar campos PEP: cargo_pep, relacion_pep, pais_residencia_fiscal
- [ ] Si nivel_riesgo=alto, no permitir aprobar sin comentario de alta gerencia
- [ ] Validar log de auditoria con fecha UTC, hora, usuario, ip_address

---

## ALFA - SEGURIDAD Y DATOS (4 tareas)

- [ ] Validar autenticacion por roles: admin, oficial_cumplimiento, alta_gerencia
- [ ] Confirmar que hashed_password y mfa_secret nunca se retornan en responses API
- [ ] Verificar que cada PUT genera EventoAuditoria con detalles del cambio
- [ ] Validar que created_at sea server_default=func.now()

---

## BACKEND - CORE (8 tareas)

- [ ] Verificar 8 modelos SQLAlchemy con relaciones back_populates correctas
- [ ] Configurar connection pool: pool_size=10, max_overflow=20, pool_pre_ping=True
- [ ] JWT: HS256, 60min access_token, 7 dias refresh_token
- [ ] CORS: solo http://localhost:3000, no wildcard
- [ ] Startup event: crear admin si no existe (admin/admin123)
- [ ] Migration 001: crear todas las tablas, indices, foreign keys
- [ ] Todos los paquetes en requirements.txt con version fija
- [ ] Verificar config.py con defaults para todos los campos opcionales

---

## BACKEND - API ENDPOINTS (10 tareas)

- [ ] POST /auth/login - OAuth2PasswordRequestForm, retorna JWT
- [ ] POST /auth/register - Username/email unicos, password bcrypt
- [ ] GET /auth/me - Decodifica JWT, retorna UsuarioResponse
- [ ] POST /clientes/ - Crear cliente + auto-crear Expediente con riesgo calculado
- [ ] GET /clientes/ - Lista con skip/limit
- [ ] PUT /clientes/{id} - Update con exclude_unset
- [ ] DELETE /clientes/{id} - Definir: soft delete o hard delete?
- [ ] POST /expedientes/{id}/aprobar - Requiere comentario, cambia estado
- [ ] POST /expedientes/{id}/rechazar - Requiere comentario
- [ ] POST /documentos/{id}/upload - Multipart, SHA-256

---

## BACKEND - SERVICES (3 tareas)

- [ ] riesgo_service.py: Formula Pais(25%)+Cargo(30%)+Sector(15%)+Vinculos(20%)+Origen(10%)
- [ ] Si es_pep=true: nivel=alto, requiere_gerencial=true, estado=pendiente_gerencia
- [ ] pep_service.py: RapidFuzz threshold=85, cedula exacta->score 95+, nombre similar->85+

---

## BETA - USABILIDAD EXTERNA (4 tareas)

- [ ] GrafoPage: navegacion con 3+ niveles de profundidad (drag, zoom, pan)
- [ ] ExpedienteDetailPage: boton exportar PDF/XML
- [ ] Layout: responsivo en 320px (mobile), 768px (tablet), 1024px+ (desktop)
- [ ] LoginPage + ClientesPage: accesibilidad aria-labels, focus visible, contraste 4.5:1

---

## BETA - CUMPLIMIENTO NORMATIVO (4 tareas)

- [ ] Modulo financiera: validar documento origen de fondos adjunto antes de guardar
- [ ] Si es_pep=true, expediente debe tener requiere_aprobacion_gerencial=true
- [ ] OFAC/ONU/UE: marcar como No implementado en docs (sin API gratuita)
- [ ] Cada modelo: comentario con referencia legal (Ley 23 Art.XX)

---

## BETA - EXPERIENCIA DE USUARIO (3 tareas)

- [ ] ClientesPage: feedback imediato en campos obligatorios (react-hook-form)
- [ ] ClientesPage: seccion PEP aparece automaticamente con watch('es_pep')
- [ ] tailwind.config.js: paleta consistente, colores riesgo (bajo/medio/alto)

---

## FRONTEND - PAGES (9 tareas)

- [ ] LoginPage: form username/password, toast error, navigate /dashboard
- [ ] DashboardPage: stats cards + Recharts PieChart + BarChart
- [ ] ClientesPage: accordion 6 modulos, zod validation, watch es_pep
- [ ] ClientesPage: submit llama clienteService.create() (backend crea expediente)
- [ ] ExpedientesPage: lista con filtros por estado y nivel_riesgo
- [ ] ExpedienteDetailPage: 3 tabs (Detalle, Documentos, Trazabilidad)
- [ ] ExpedienteDetailPage: botones aprobar/rechazar con modal comentario
- [ ] PEPSearchPage: buscar por nombre/cedula, matches con color coding
- [ ] ReportesPage: tabla auditoria + exportar CSV

---

## FRONTEND - SERVICES/STORES (5 tareas)

- [ ] api.ts: Axios instance con interceptor Bearer token y 401 redirect to login
- [ ] authService.ts: login URLSearchParams, register, logout, getToken, isAuthenticated
- [ ] clienteService.ts: CRUD list/get/create/update/delete
- [ ] expedienteService.ts: CRUD + aprobar(id,comentario), rechazar(id,comentario)
- [ ] authStore.ts: Zustand con user, isAuthenticated, isLoading, error, login, logout

---

## INTEGRATION (4 tareas)

- [ ] VITE_API_URL=http://localhost:8000/api/v1 en docker-compose.yml
- [ ] CORS backend: allow_origins=["http://localhost:3000"]
- [ ] JWT flow: login almacena token, Authorization header en todas las llamadas
- [ ] Auto-expediente: cliente es_pep=true -> expediente estado=pendiente_gerencia

---

## INFRASTRUCTURE (5 tareas)

- [ ] docker-compose.yml: 4 servicios (backend, frontend, db, redis) con healthchecks
- [ ] backend/Dockerfile: Python 3.11-slim, apt-get postgresql-client, pip install, alembic upgrade
- [ ] frontend/Dockerfile: Node 18-alpine, npm install, npm run dev
- [ ] Volumes: postgres_data, redis_data, uploads
- [ ] Reset: docker-compose down -v para reconstruccion limpia

---

## DOCUMENTATION (4 tareas)

- [ ] README.md: instrucciones docker-compose up --build, login admin/admin123
- [ ] PRD.md: verificar que todos los requisitosesten implementados
- [ ] architecture.md: diagramas y tablas reflejan codigo actual
- [ ] /docs: OpenAPI accurate (revisar todos los endpoints)

---

## Resumen de Tareas

| Categoria | Total |
|-----------|-------|
| Alfa - Logica Interna | 5 |
| Alfa - Seguridad y Datos | 4 |
| Backend - Core | 8 |
| Backend - API Endpoints | 10 |
| Backend - Services | 3 |
| Beta - Usabilidad Externa | 4 |
| Beta - Cumplimiento Normativo | 4 |
| Beta - Experiencia de Usuario | 3 |
| Frontend - Pages | 9 |
| Frontend - Services/Stores | 5 |
| Integration | 4 |
| Infrastructure | 5 |
| Documentation | 4 |
| **TOTAL** | **62** |

---

## Como Importar a GitHub Projects

### Opcion 1: Copiar-Pegar Manual (Recomendado)

1. Ir a https://github.com/users/TU_USUARIO/projects/new
2. Crear nuevo proyecto tipo "Board"
3. Crear columnas: TO DO, IN PROGRESS, IN REVIEW, DONE
4. Copiar cada linea "- [ ] tarea" y pegarla como nuevo item
5. Arrastrar entre columnas segun progreso

### Opcion 2: GitHub CLI

```bash
# Instalar gh si no tienes
brew install gh

# Login
gh auth login

# Crear issue para cada tarea (luego mover a project)
gh issue create --title "Tarea 1" --body "Descripcion"
```

### Opcion 3: Markdown como Checklist

Usar este archivo como referencia. Crear un milestone por fase:
- Milestone 1: Alfa + Backend Core
- Milestone 2: Backend API + Services
- Milestone 3: Beta + Frontend
- Milestone 4: Integration + Docs

---

## Prioridades Sugeridas

| Prioridad | Significado | Tareas |
|-----------|-------------|--------|
| P0 - Critico | Bloquea desarrollo | 1-17 |
| P1 - Alto | Funcionalidad completa | 18-41 |
| P2 - Medio | Quality of life | 42-56 |
| P3 - Bajo | Documentacion | 57-62 |

---

**Fecha creacion:** 2026-05-31
**Proyecto:** Diligencia Reforzada EDD - Panama AML/CFT
**Total tareas:** 62