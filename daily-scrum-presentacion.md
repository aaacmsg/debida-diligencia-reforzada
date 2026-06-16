# Daily Scrum — Diligencia Reforzada EDD

**Fecha:** 15 de junio de 2026  
**Materia:** Ingenieria de Software IV — Unidad II: Medicion de la Calidad del Software (ISTQB – TMMi – TQM)  
**Grupo:** Debida Diligencia Reforzada

**Integrantes:**
- Cesar Santiago
- Jean Suarez
- Roberto Lopez
- Salon: 1GS242

**Proyecto:** Sistema AML/CFT Panama (Ley 23/2015, Ley 254/2021)  
**Stack:** FastAPI (Python) + React 18 (TypeScript) + PostgreSQL 15 + Redis 7 + TailwindCSS  
**Repo:** [github.com/aaacmsg/debida-diligencia-reforzada](https://github.com/aaacmsg/debida-diligencia-reforzada)

---

## 1. Que hicimos desde el ultimo laboratorio

### Backend (FastAPI + Python)
- Implementacion completa de **8 modulos API**: auth, clientes, expedientes, documentos, riesgos, PEP, reportes, alertas, configuracion
- **9 modelos SQLAlchemy**: Cliente, BeneficiarioFinal, Expediente, Documento, FuncionarioPublico, EventoAuditoria, Usuario, Configuracion, Alerta
- **Calculo de riesgo** con formula ponderada (detalle completo en seccion 1.1)
- **Busqueda PEP** con RapidFuzz (fuzzy matching, threshold 85%)
- **Sincronizacion** con datosabiertos.gob.pa via API CKAN
- **Descarga de documentos** con hash SHA-256
- **Alertas automaticas** para expedientes de alto riesgo y actualizacion pendiente
- **Configuracion persistente** key-value con API REST
- **63 tests unitarios** (pytest) para riesgo_service y security

### 1.1 Calculo de Nivel de Riesgo — Detalle Completo

Implementado en `backend/app/services/riesgo_service.py` con endpoint `POST /api/v1/riesgos/calcular`.

**Formula ponderada:**

```
Score = (Pais x 0.25) + (Cargo PEP x 0.30) + (Sector x 0.15) + (Vinculos x 0.20) + (Origen Fondos x 0.10)
```

**Variables y calculo:**

| Variable | Peso | Input | Score | Condicion |
|----------|------|-------|-------|-----------|
| **Pais/Region** | 25% | `pais_residencia` o `pais_residencia_fiscal` | 100 | Iran, Corea del Norte, Siria, Cuba, Venezuela, Myanmar, Afganistan, Sudan, Zimbabwe, Yemen |
| | | | 80 | Panama, Belize, Islas Caiman, Virgenes Britanicas, Samoa, Mauricio, Seychelles, Dominica |
| | | | 25 | Cualquier otro pais |
| **Cargo PEP** | 30% | `es_pep` + `cargo_pep` | 100 | Presidente, Vicepresidente, Ministro, Director, Gerente General, Magistrado, Embajador, etc. |
| | | | 60 | Jefe, Subjefe, Coordinador, Asesor, Supervisor, Secretario General |
| | | | 40 | PEP con otro cargo no listado |
| | | | 10 | No es PEP (`es_pep = false`) |
| **Sector Economico** | 15% | `sector_economico` o `actividad_economica` | 100 | Construccion, Bienes Raices, Metales Preciosos, Oro, Casinos, Armas, Arte, Yates |
| | | | 50 | Comercio Internacional, Importacion/Exportacion, Transporte, Servicios Financieros |
| | | | 20 | Otros sectores |
| **Vinculos PEP** | 20% | `vinculos_pep` (cantidad) | 10 | 0 vinculos |
| | | | 40 | 1 vinculo |
| | | | 70 | 2-3 vinculos |
| | | | 100 | 4 o mas vinculos |
| **Origen Fondos** | 10% | `origen_fondos_documentado` | 10 | Documentado (`true`) |
| | | | 80 | No documentado (`false`) |

**Clasificacion final:**

| Score | Nivel | Accion Requerida |
|-------|-------|------------------|
| **0 - 35** | Bajo | Monitoreo estandar, revision anual |
| **36 - 65** | Medio | Monitoreo intensificado, revision semestral |
| **66 - 100** | Alto | Diligencia Reforzada obligatoria + aprobacion Alta Gerencia |

**Regla especial PEP:** Si `es_pep = true`, se fuerza `nivel_riesgo = ALTO`, `requiere_aprobacion_gerencial = true`, y el expediente se crea en estado `pendiente_gerencia`, independientemente del score calculado. Esto asegura que ningun cliente PEP pase desapercibido.

**Implementacion:**
- `riesgo_service.py`: 186 lineas, 15 funciones, complejidad ciclomatica maxima 7 (B)
- `test_riesgo_service.py`: **49 tests** cubriendo todos los rangos de cada variable
- Configuracion via `settings.py`: pesos y thresholds modificables por entorno

### Frontend (React 18 + TypeScript + Vite)
- **Formulario EDD** completo con 7 modulos, validacion Zod y react-hook-form
- **Dashboard** con Recharts (PieChart + BarChart)
- **Grafo interactivo** SVG con simulacion de fuerzas (arrastrable)
- **Layout** con sidebar + dropdown de alertas en vivo
- **PEPSearchPage** con busqueda fuzzy + listado de cargos PEP
- **ExpedienteDetailPage** con 3 tabs (detalle, documentos, trazabilidad)
- **ConfiguracionPage** funcional con persistencia

### DevOps y Calidad
- **GitHub Actions**: 3 workflows (backend CI, frontend CI, metrics weekly)
- **Playwright**: 20 tests E2E en frontend
- **Dashboard de metricas**: script que genera HTML con cobertura, KLOC, complejidad, smells, vulnerabilidades

---

## 2. Que haremos para el proximo laboratorio

| Prioridad | Tarea | Responsable |
|-----------|-------|-------------|
| P0 | Implementar RBAC (control de acceso por roles) en endpoints | Grupo |
| P0 | Rate limiting por IP/usuario con slowapi | Grupo |
| P0 | Logs de auditoria inmutables (proteccion WORM) | Grupo |
| P1 | Ejecutar Playwright E2E tests en GitHub Actions CI | Grupo |
| P1 | Celery task programada para descarga automatica de CSVs PEP | Grupo |
| P1 | Notificaciones email para alertas de alto riesgo | Grupo |
| P2 | Exportar expediente individual a PDF | Grupo |
| P2 | Panel de administracion de usuarios desde UI | Grupo |
| P2 | Refresh de tokens JWT | Grupo |

---

## 3. Que problemas o bloqueos tuvimos

| Bloqueo | Estado | Impacto | Mitigacion |
|---------|--------|---------|------------|
| **Python 3.14** incompatible con SQLAlchemy 2.0.25 | ❌ Cerrado | Tests fallaban localmente | Upgrade a SQLAlchemy 2.0.51 con wheel cp314 |
| **Alembic no leia DATABASE_URL del entorno en CI** | ❌ Cerrado | GitHub Actions fallaba en migrations | Fix: `env.py` ahora sobrescribe `sqlalchemy.url` desde `DATABASE_URL` |
| **Labels en GitHub no existian** | ❌ Cerrado | Script upload_tasks no creaba issues | Script ahora crea labels primero |
| **Workflows no se disparaban** | ❌ Cerrado | Branch `main` no existe, solo `master` | Se corrigio trigger a `master` + path `.github/**` |
| **Emojis en dashboard HTML** | ❌ Cerrado | UnicodeEncodeError en Windows | Fix: `encoding="utf-8"` en write_text |
| Grafo sin datos reales | ⚠️ Abierto | No hay clientes/expedientes cargados | Pendiente de carga de datos de prueba |

---

## 4. Metricas del Proyecto (ISTQB / TMMi / TQM)

### 4.1 Metricas en Requerimientos

| Metrica | Valor | Herramienta | Interpretacion | Accion de mejora |
|---------|-------|-------------|----------------|-------------------|
| **Cobertura de reqs implementados** | 20/20 reqs funcionales = 100% | Plan-de-pruebas.md + PRD.md | Todos los requisitos del PRD implementados | Validar contra PRD actualizado |
| **Volatilidad** | 0 cambios en reqs esta semana | Seguimiento manual | Sin cambios en alcance | Documentar en PRD |
| **Trazabilidad** | Pendiente de documentar | Matriz manual | No hay matriz reqs → tests → codigo | **Crear matriz de trazabilidad** |

### 4.2 Metricas en Diseno

| Metrica | Valor | Herramienta | Interpretacion | Accion de mejora |
|---------|-------|-------------|----------------|-------------------|
| **Complejidad ciclomatica (max)** | 12 (B) | radon cc | `pep_service.buscar_funcionario` es el mas complejo | Refactorizar: dividir en 2-3 funciones |
| **Complejidad ciclomatica (prom)** | 2.4 (A) | radon cc | Proyecto mayormente simple, bien estructurado | Mantener asi |
| **Funciones totales** | 116 | radon cc | 29 archivos Python, proporcionado para el tamano | OK |
| **Funciones con rating B** | 7 | radon cc | `buscar_funcionario`(12), `_calcular_score_pais`(7), `_calcular_score_cargo`(7), `_calcular_score_sector`(7), `grafo_relaciones`(9), `reporte_expedientes`(6) | Refactorizar en sprint futuro |
| **Diagramas UML** | 2 (arquitectura + DB) | architecture.md | Diagramas de arquitectura y entidad-relacion documentados | Agregar diagrama de clases y secuencia |

### 4.3 Metricas en Codigo

| Metrica | Valor | Herramienta | Interpretacion | Accion de mejora |
|---------|-------|-------------|----------------|-------------------|
| **KLOC Backend** | 2,337 | Line count | 29 archivos Python (FastAPI + SQLAlchemy) | OK |
| **KLOC Frontend** | 3,689 | Line count | 26 archivos TypeScript/TSX (React + Vite) | OK |
| **KLOC Total** | 6,026 | — | Proyecto mediano-pequeno | OK |
| **Cobertura de pruebas** | 26% | pytest-cov | Cobertura moderada (solo unitarias, sin E2E) | **Agregar tests de integracion** |
| **Tests unitarios** | 63 passed, 0 failed | pytest | 100% de pruebas pasando | Mantener |
| **Code smells** | 0 | flake8 | Sin incidencias de estilo detectadas | OK |
| **Vulnerabilidades** | 0 | bandit | Sin fallos de seguridad detectados | OK |
| **Densidad de defectos** | 0 / KLOC | Calculo manual | Sin defectos abiertos conocidos | OK |

### 4.4 Interpretacion y Acciones de Mejora

**Fortalezas:**
- Complejidad ciclomatica promedio 2.4 (rating A) — codigo simple y mantenible
- 0 vulnerabilidades de seguridad, 0 code smells
- 63/63 tests unitarios pasando
- 100% de requisitos funcionales implementados

**Debilidades:**
- Cobertura de pruebas solo 26% — faltan tests de integracion y E2E
- `pep_service.buscar_funcionario` con complejidad 12 (la mas alta del proyecto)
- Sin matriz de trazabilidad formal
- Sin SonarQube para medicion de deuda tecnica

**Acciones concretas:**
1. Refactorizar `pep_service.buscar_funcionario` (complejidad 12 → dividir en 2-3 funciones)
2. Crear matriz de trazabilidad reqs → tests → codigo
3. Agregar SonarQube en CI para debt ratio automatico
4. Aumentar cobertura a ≥ 50% con tests de integracion

---

## 5. Pruebas Desarrolladas y Resultados

### 5.1 Tests Unitarios Backend (pytest) — 63 tests

Ejecutados con `pytest` + `pytest-cov`. No requieren base de datos ni servicios externos.

| Archivo | Tests | Que cubre |
|---------|-------|-----------|
| `tests/test_riesgo_service.py` | 49 | Score pais (10), Score cargo (8), Score sector (9), Score vinculos (6), Score origen (2), Determinacion nivel (6), Calculo completo integracion (8) |
| `tests/test_security.py` | 14 | Password hashing bcrypt (6), Creacion y validacion JWT (8) |
| **Total** | **63** | **Resultado: 63 passed, 0 failed** |

**Resultado final:** `63 passed in 8.35s` | Cobertura: 26%

### 5.2 Tests E2E Frontend (Playwright) — 20 tests planificados

Definidos en `plan-de-pruebas.md` y `frontend/tests/specs/`. Requieren backend + DB corriendo.

| Suite | Archivo | Tests | Estado |
|-------|---------|-------|--------|
| **ALFA - Logica Interna** | `alfa/01-login.spec.ts` | TC-01 al TC-03 | Planificado |
| | `alfa/02-form-validation.spec.ts` | TC-04 al TC-06 | Planificado |
| | `alfa/03-expediente-workflow.spec.ts` | TC-07, TC-08 | Planificado |
| | `alfa/04-audit-trail.spec.ts` | TC-09, TC-10 | Planificado |
| **BETA - Cumplimiento** | `beta/01-compliance.spec.ts` | TC-11, TC-12 | Planificado |
| **UX - Experiencia** | `ux/01-pep-fields.spec.ts` | TC-13, TC-14 | Planificado |
| | `ux/02-graph.spec.ts` | TC-15 al TC-17 | Planificado |
| | `ux/03-responsive.spec.ts` | TC-18, TC-19 | Planificado |
| | `ux/04-accessibility.spec.ts` | TC-20 | Planificado |
| **Total** | **8 spec files** | **20 tests** | Requieren CI con backend + PostgreSQL |

### 5.3 Metricas de Pruebas (ISTQB)

| Metrica | Valor | Interpretacion |
|---------|-------|----------------|
| **Cobertura de pruebas unitarias** | 26% de lineas, 63 tests | Moderada. Faltan tests de endpoints API |
| **Densidad de pruebas** | 63 tests / 2.3 KLOC = 27.4 tests/KLOC | Buena densidad para el backend |
| **Tasa de exito** | 63/63 = 100% | Todas las pruebas pasan |
| **Tasa de fallo** | 0% | Sin regresiones |

---

## 6. Backlog Completado (20 tareas)

- [x] Backend FastAPI completo (8 modulos API)
- [x] Modelos SQLAlchemy (9 tablas)
- [x] Auth JWT + bcrypt (login/register/me)
- [x] CRUD Clientes + auto-creacion de Expediente con riesgo
- [x] CRUD Expedientes + flujo aprobar/rechazar
- [x] Upload documentos SHA-256 + endpoint descarga
- [x] Calculo de riesgo (formula ponderada 5 variables)
- [x] Busqueda PEP con RapidFuzz (fuzzy matching)
- [x] Sincronizacion datosabiertos.gob.pa via API CKAN
- [x] Reportes (dashboard, auditoria, CSV export, grafo)
- [x] CRUD Alertas + generacion automatica
- [x] Configuracion persistente key-value
- [x] Endpoint listado cargos PEP segun Ley de Panama
- [x] Tests unitarios pytest (63 tests) + CI GitHub Actions
- [x] Dashboard React con Recharts (PieChart + BarChart)
- [x] Formulario EDD 7 modulos con Zod + react-hook-form
- [x] Grafo interactivo SVG con simulacion de fuerzas
- [x] Layout con sidebar + dropdown alertas en vivo
- [x] Script generador de dashboard de metricas
- [x] PEPSearchPage con busqueda fuzzy + cargos PEP

## Backlog Pendiente MVP (10 tareas)

- [ ] Implementar control de acceso por roles (RBAC) en login y endpoints
- [ ] Logs de auditoria inmutables (proteccion WORM en backend)
- [ ] Exportar expediente individual a PDF
- [ ] Ejecutar Playwright E2E tests en GitHub Actions CI
- [ ] Panel de administracion de usuarios (CRUD desde UI)
- [ ] Manejo de expiracion y refresh de tokens JWT

---

## 6. Dashboard de Metricas

El dashboard visual se genera con:

```bash
cd backend
python scripts/generate_metrics_dashboard.py
```

Abrir: `backend/metrics/dashboard.html`

Herramientas integradas:
- `pytest-cov` → cobertura de pruebas
- `radon cc` → complejidad ciclomatica
- `radon mi` → mantenibilidad
- `flake8` → code smells
- `bandit` → vulnerabilidades
- `cloc` → KLOC

En GitHub Actions se genera automaticamente cada lunes y se puede descargar como artifact.
