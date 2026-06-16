# Sistema de Diligencia Debida Reforzada (EDD)

Aplicacion web para cumplimiento AML/CFT en Panama segun Ley 23/2015, Ley 254/2021 y resolucion SBP-RG-PSO-R-2025-00671.

## Stack Tecnologico

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18+ / Vue 3+ (pendiente implementar)
- **Base de Datos**: PostgreSQL 15+
- **Cache/Workers**: Redis + Celery
- **Contenedores**: Docker + Docker Compose

## Funcionalidades Principales

- [x] Formulario EDD con 7 modulos
- [x] Calculo de nivel de riesgo (formula ponderada)
- [x] Busqueda fuzzy de PEPs en datosabiertos.gob.pa
- [x] Upload de documentos con hash SHA-256
- [x] Dashboard de expedientes
- [x] Trazabilidad/auditoria de eventos
- [x] Flujo de aprobacion con niveles

## Requisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (para frontend)
- Docker y Docker Compose (opcional)

## Instalacion Local (Desarrollo)

### 1. Clonar y configurar

```bash
# Clonar repositorio
cd proyecto_diligencia_reforzada

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu configuracion
```

### 2. Base de datos

```bash
# Crear base de datos
createdb diligencia_db

# Ejecutar migraciones (si usa alembic)
alembic upgrade head
```

### 3. Ejecutar

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend (pendiente)

```bash
cd frontend
npm install
npm run dev
```

## Instalacion con Docker

```bash
docker-compose up -d
```

## Endpoints API

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | /api/v1/auth/login | Login (OAuth2 Password) |
| POST | /api/v1/auth/register | Registrar usuario |
| GET | /api/v1/clientes | Listar clientes |
| POST | /api/v1/clientes | Crear cliente |
| GET | /api/v1/expedientes | Listar expedientes |
| POST | /api/v1/expedientes | Crear expediente |
| POST | /api/v1/riesgos/calcular | Calcular riesgo |
| POST | /api/v1/pep/buscar | Buscar PEP en funcionarios |
| POST | /api/v1/documentos/{id}/upload | Subir documento |

## Documentacion API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estructura del Proyecto

```
proyecto_diligencia_reforzada/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Endpoints API
│   │   ├── core/                # Config, security, database
│   │   ├── models/              # Modelos SQLAlchemy
│   │   ├── schemas/             # Schemas Pydantic
│   │   ├── services/            # Logica de negocio
│   │   └── main.py              # FastAPI app
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                    # (pendiente implementar)
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Variables de Entorno Requeridas

Ver `.env.example` para todas las variables.

## Licencia

Proprietario - Solo para uso interno
