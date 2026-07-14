# Sistema de Diligencia Debida Reforzada (EDD)

**Universidad Tecnológica de Panamá**
Materia: Ingeniería de Software IV | Profesora: María Mosquera | Salón: 1GS242

**Integrantes:** César Santiago, Jean Suárez, Roberto López

Aplicación web de cumplimiento AML/CFT para Panamá, basada en la Ley 23 de 2015, la Ley 254 de 2021 y la Resolución SBP-RG-PSO-R-2025-00671. Permite registrar clientes, calcular su nivel de riesgo, detectar Personas Expuestas Políticamente (PEP) con datos oficiales de datosabiertos.gob.pa y gestionar expedientes con trazabilidad completa.

---

## Cómo montar y ejecutar el proyecto (paso a paso)

Solo necesitas tener **Docker Desktop** instalado y abierto.

**1. Clonar el repositorio**

```bash
git clone https://github.com/aaacmsg/debida-diligencia-reforzada.git
cd debida-diligencia-reforzada
```

**2. Levantar todo el sistema**

```bash
docker-compose up --build
```

La primera vez tarda unos minutos porque descarga las imágenes y construye el proyecto. Están listos cuando la consola deja de moverse y se ve el mensaje de Uvicorn corriendo.

> **¿Error "ports are not available: 3000"?** Significa que otro programa ya usa ese puerto. Levanta el frontend en otro puerto así:
>
> ```bash
> FRONTEND_PORT=3002 docker-compose up --build
> ```
>
> y entra por http://127.0.0.1:3002 en lugar del puerto 3000. Todo lo demás funciona igual.

**3. Cargar los datos de demostración** (en otra terminal)

```bash
docker-compose exec backend python scripts/seed_demo.py
```

Esto crea 8 clientes de ejemplo (incluye un ministro PEP), expedientes con riesgo bajo, medio y alto, alertas, documentos y los usuarios de prueba.

**4. Entrar a la aplicación**

| Qué | Dónde |
|-----|-------|
| Aplicación web | http://localhost:3000 |
| API (Swagger) | http://localhost:8000/docs |

**Usuarios de prueba:**

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | Administrador (todo permitido) |
| `oficial` | `oficial123` | Oficial de Cumplimiento (revisa expedientes, consulta auditoría) |
| `gerencia` | `gerencia123` | Alta Gerencia (aprueba o rechaza expedientes de alto riesgo) |

**Para apagar todo:** `docker-compose down` (agrega `-v` si quieres borrar la base de datos y empezar de cero).

---

## Cómo usar la aplicación

1. **Inicia sesión** con alguno de los usuarios de prueba.
2. **Dashboard**: resumen de expedientes por estado y por nivel de riesgo.
3. **Clientes**: botón "Nuevo Cliente" abre el formulario EDD por módulos. Si marcas la casilla PEP aparecen campos adicionales obligatorios. Al guardar, el sistema calcula el riesgo y crea el expediente automáticamente.
4. **Expedientes**: lista con filtros por estado y riesgo. Al entrar a uno hay tres pestañas (Detalle, Documentos, Trazabilidad), el botón **Exportar PDF** y, si está pendiente de gerencia y entraste como `gerencia`, los botones Aprobar y Rechazar (piden comentario obligatorio).
5. **Buscar PEP**: escribe un nombre o cédula (prueba con `8-702-3355`) y el sistema busca coincidencias en la base de funcionarios públicos.
6. **Grafo de Relaciones**: mapa visual de clientes, beneficiarios finales y documentos. Los nodos naranjas son PEP. Se puede hacer zoom y arrastrar nodos.
7. **Reportes**: registro de auditoría del sistema y exportación a CSV.
8. La **campana** de la esquina superior muestra las alertas activas.

---

## Funcionalidades principales

- Formulario EDD de 7 módulos con validación en tiempo real (Ley 23, Art. 15-18).
- Cálculo de riesgo con fórmula ponderada: País 25% + Cargo PEP 30% + Sector 15% + Vínculos 20% + Origen de fondos 10%. Niveles: bajo (0-35), medio (36-65), alto (66-100).
- Regla PEP: todo cliente PEP queda en riesgo alto y requiere aprobación de Alta Gerencia, sin importar el score.
- Búsqueda difusa de PEP (RapidFuzz, umbral 85%) contra datos de datosabiertos.gob.pa.
- Beneficiarios finales con porcentaje de participación y grafo de relaciones societarias.
- Carga de documentos (PDF/PNG/JPG, máx. 10 MB) con hash SHA-256.
- Exportación del expediente a PDF con todas sus secciones.
- Flujo de aprobación con comentario obligatorio y control de acceso por roles (RBAC).
- Auditoría inmutable (WORM): los eventos no se pueden modificar ni borrar.
- Tokens JWT con refresh automático y límite de intentos de login por IP.

## Pruebas

```bash
# Backend: 91 pruebas (unitarias + integración)
docker-compose exec backend python -m pytest

# Frontend: 25 pruebas end-to-end con Playwright (requiere el sistema corriendo)
cd frontend && npm install && npx playwright test
```

Ambas suites corren automáticamente en GitHub Actions en cada Pull Request.

## Estructura del proyecto

```
├── backend/            # API FastAPI (Python 3.11)
│   ├── app/            # endpoints, modelos, servicios, seguridad
│   ├── tests/          # 91 pruebas pytest
│   └── scripts/        # seed de demo y dashboard de métricas
├── frontend/           # React 18 + TypeScript + Vite
│   ├── src/            # páginas, servicios, stores
│   └── tests/          # 25 pruebas E2E Playwright
├── docs/               # documento final, contexto y bitácora
├── docker-compose.yml  # backend + frontend + PostgreSQL + Redis
└── PRD.md              # requisitos completos del sistema
```

## Enlaces del proyecto

- Issues: https://github.com/aaacmsg/debida-diligencia-reforzada/issues
- Tablero: https://github.com/users/aaacmsg/projects/2
- Documento final: [`docs/documento-final.md`](docs/documento-final.md)
- Arquitectura: [`architecture.md`](architecture.md)
