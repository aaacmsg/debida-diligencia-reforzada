# Universidad Tecnológica de Panamá

## Facultad de Ingeniería de Sistemas Computacionales

---

# Proyecto Semestral — Documento Final

# Sistema de Diligencia Debida Reforzada (EDD)

### Aplicación de Cumplimiento AML/CFT para Panamá

---

| | |
|---|---|
| **Materia** | Ingeniería de Software IV |
| **Profesora** | María Mosquera |
| **Salón** | 1GS242 |
| **Integrantes** | César Santiago · Roberto López · Jean Suárez |
| **Repositorio** | https://github.com/aaacmsg/debida-diligencia-reforzada |
| **Tablero** | https://github.com/users/aaacmsg/projects/2 |
| **Fecha de entrega** | Julio de 2026 |

---

## Índice

1. [Introducción y descripción del proyecto](#1-introducción-y-descripción-del-proyecto)
2. [Retrospectiva del equipo](#2-retrospectiva-del-equipo)
   - 2.1 Problemas enfrentados
   - 2.2 Lecciones aprendidas
   - 2.3 Ajustes aplicados al proceso
   - 2.4 Responsabilidades individuales y colectivas
3. [Adecuaciones del Parcial 2](#3-adecuaciones-del-parcial-2)
   - 3.1 Funcionalidades ajustadas y nuevas
   - 3.2 Mejoras implementadas
   - 3.3 Métricas aplicadas (ISTQB – TMMi – TQM)
   - 3.4 Defectos corregidos
   - 3.5 Decisiones técnicas y su justificación
4. [Versionamiento](#4-versionamiento)
   - 4.1 Historial de versiones del documento
   - 4.2 Control de versiones del software (Git)
   - 4.3 Flujo de trabajo con Pull Requests
5. [Conclusiones](#5-conclusiones)
   - 5.1 Conclusiones individuales
   - 5.2 Conclusión grupal sobre la calidad del producto
   - 5.3 Evaluación del proceso colaborativo
   - 5.4 Recomendaciones para futuras iteraciones
6. [Referencias normativas y técnicas](#6-referencias-normativas-y-técnicas)
7. [Anexos — Evidencias](#7-anexos--evidencias)

---

## 1. Introducción y descripción del proyecto

El **Sistema de Diligencia Debida Reforzada (EDD)** es una aplicación web para el cumplimiento de las obligaciones de prevención de blanqueo de capitales y financiamiento del terrorismo (AML/CFT) en Panamá, construida sobre el marco normativo de la **Ley 23 de 2015**, la **Ley 254 de 2021** y la **Resolución SBP-RG-PSO-R-2025-00671** de la Superintendencia de Bancos, incorporando las Recomendaciones 10, 12, 19 y 24 del GAFI.

El sistema implementa el ciclo completo de diligencia debida bajo el **Enfoque Basado en Riesgo (EBR)**:

- **Formulario EDD de 7 módulos** (identificación, información financiera, beneficiario final, perfil de riesgo, documentación, aprobación y auditoría) con validación en tiempo real.
- **Cálculo automático del nivel de riesgo** con fórmula ponderada de 5 variables: `Score = País×0.25 + Cargo×0.30 + Sector×0.15 + Vínculos×0.20 + OrigenFondos×0.10`, con clasificación bajo (0–35), medio (36–65) y alto (66–100).
- **Detección de Personas Expuestas Políticamente (PEP)** mediante búsqueda difusa (RapidFuzz, umbral 85%) contra datos oficiales de `datosabiertos.gob.pa` (API CKAN) y la ANTAI. Regla especial: todo cliente PEP fuerza riesgo alto y aprobación obligatoria de Alta Gerencia.
- **Gestión de expedientes** con flujo de estados (borrador → pendiente revisión → pendiente gerencia → aprobado/rechazado), comentario de justificación obligatorio y exportación a PDF.
- **Grafo interactivo de relaciones** que revela vínculos societarios entre clientes, beneficiarios finales y documentos.
- **Trazabilidad inmutable (WORM)**: todo evento queda registrado con usuario, fecha UTC e IP, y no puede modificarse ni eliminarse (Ley 23, Art. 21).
- **Seguridad**: autenticación JWT con refresh tokens, control de acceso por roles (RBAC), rate limiting por IP y documentos con hash SHA-256.

**Stack tecnológico:** FastAPI (Python 3.11) + SQLAlchemy 2.0 + PostgreSQL 15 + Redis 7 en el backend; React 18 + TypeScript + Vite + TailwindCSS en el frontend; Docker Compose para orquestación; GitHub Actions para integración continua (3 workflows de CI + 1 de E2E); pytest (91 pruebas) y Playwright (25 pruebas E2E) para verificación.

**Exclusiones documentadas:** las consultas a listas restrictivas OFAC/ONU/UE no se implementaron por no existir APIs públicas gratuitas; la firma digital avanzada (XAdES/PAdES) requiere proveedores comerciales. Ambas se registran como trabajo futuro.

---

## 2. Retrospectiva del equipo

### 2.1 Problemas enfrentados

| # | Problema | Impacto | Resolución |
|---|----------|---------|------------|
| 1 | **Python 3.14 local incompatible con SQLAlchemy 2.0.25** | Los tests fallaban en las máquinas de desarrollo | Actualización a SQLAlchemy 2.0.51 con wheels cp314 |
| 2 | **Alembic no leía `DATABASE_URL` del entorno en CI** | GitHub Actions fallaba al ejecutar migraciones | `env.py` sobrescribe `sqlalchemy.url` desde la variable de entorno |
| 3 | **Workflows de CI no se disparaban** | Sin integración continua durante días | El repositorio usa rama `master` y los triggers apuntaban a `main`; se corrigieron |
| 4 | **UnicodeEncodeError en Windows** al generar el dashboard de métricas con emojis | Script de métricas inutilizable en Windows | `encoding="utf-8"` explícito en la escritura de archivos |
| 5 | **Grafo de relaciones sin datos reales** | Imposible demostrar la funcionalidad estrella | Se construyó un script de seed idempotente con 8 clientes interrelacionados (PR #99) |
| 6 | **El backend no arrancaba con la configuración de docker-compose**: `Settings` de pydantic rechazaba `REDIS_URL` y `ALLOWED_ORIGINS` | Bloqueo total del despliegue local | Se agregaron los campos faltantes con defaults y `extra="ignore"` (PR #99) |
| 7 | **17 de las 25 pruebas E2E corrían sin autenticación**: los specs importaban el fixture de login pero nunca lo usaban | La suite E2E nunca había pasado completa | Fixture `authPage` reescrito con login por API e inyección de tokens (PR #101) |
| 8 | **El formulario EDD no se podía enviar** si los campos numéricos opcionales quedaban vacíos (defecto crítico, ver §3.4) | Los usuarios no podían crear clientes desde la interfaz | Corregido en PR #101; detectado precisamente por las pruebas E2E |
| 9 | **Conflictos de puertos y de red en entornos de desarrollo** (otros servidores en los puertos 3000/3001, PostgreSQL local interceptando el puerto 5432 de Docker) | Pruebas locales apuntaban a servicios equivocados | Configuración parametrizable (`E2E_HOST`/`E2E_PORT`) y verificación por URL IPv4 explícita |
| 10 | **Incapacidad médica de la profesora** durante la semana de presentaciones | Cambio del formato de entrega (video en lugar de presencial) | Adaptación al formato Scrum Review en video con participación de todo el equipo |

### 2.2 Lecciones aprendidas

1. **Las pruebas E2E encuentran defectos que las unitarias no ven.** El backend tenía 63 pruebas unitarias en verde y aun así el flujo principal de la aplicación (crear un cliente desde la interfaz) estaba roto. Solo al ejecutar la suite de Playwright de punta a punta se descubrió la cadena de defectos NaN → validación silenciosa → 422 del backend.
2. **"Parece que funciona" no es evidencia.** Adoptamos como regla que ninguna tarea se marca completada sin una verificación reproducible: pytest en verde, build del frontend exitoso y, para cambios de comportamiento, una prueba manual o E2E del flujo real.
3. **La paridad entre entornos evita días perdidos.** Las diferencias entre Python 3.14 local y 3.11 en Docker, y entre `main` y `master`, causaron fallos que no eran del código sino del entorno. Fijar versiones (`requirements.txt` con versiones exactas) y usar Docker como fuente de verdad redujo estas fricciones.
4. **El tablero y los issues deben reflejar la realidad.** Durante un periodo los issues de verificación quedaron abiertos aunque el trabajo estaba hecho, lo que distorsionaba la medición del avance. Se estableció la disciplina de cerrar issues con evidencia (archivo, línea, prueba) en el mismo PR que completa el trabajo.
5. **La revisión por Pull Request mejora la calidad.** Al pasar de commits directos a `master` a un flujo de una rama por fase con PR revisable, cada entrega quedó documentada con su verificación, y el CI valida cada cambio antes del merge.

### 2.3 Ajustes aplicados al proceso

| Ajuste | Antes | Después |
|--------|-------|---------|
| Flujo de cambios | Commits directos a `master` | Rama por fase + Pull Request con CI obligatorio (PRs #99, #100, #101) |
| Verificación | Manual y ocasional | 91 pruebas backend + 25 E2E ejecutadas en CI en cada PR |
| Gestión de tareas | Listas dispersas (kanban-tasks.md, tasks-github.md) | `tasks.md` único por fases, sincronizado con GitHub Issues y Projects |
| Continuidad del trabajo | Contexto en la memoria de cada integrante | Documentos de contexto y handoffs de sesión en `docs/` |
| Seguridad | Autenticación básica | RBAC por roles, rate limiting, auditoría WORM y refresh tokens (Parcial 2) |
| Datos de demostración | Base de datos vacía | Seed idempotente con escenarios de riesgo bajo/medio/alto y PEPs |

### 2.4 Responsabilidades individuales y colectivas

> *Nota: ajustar la distribución si el equipo lo considera necesario.*

| Integrante | Responsabilidades principales |
|------------|------------------------------|
| **César Santiago** | Administración del repositorio y del tablero GitHub Projects; integración continua (GitHub Actions); backend FastAPI (módulos de riesgo y PEP); coordinación de los Pull Requests |
| **Roberto López** | Frontend React (formulario EDD de 7 módulos, dashboard, grafo de relaciones); pruebas E2E con Playwright; accesibilidad WCAG |
| **Jean Suárez** | Modelo de datos y migraciones (PostgreSQL/Alembic); seguridad (JWT, RBAC, WORM); plan de pruebas y métricas de calidad |
| **Colectivas** | Revisión cruzada de Pull Requests; retrospectivas; documento final; guion y grabación del video Scrum Review; decisiones de alcance y arquitectura |

---

## 3. Adecuaciones del Parcial 2

El trabajo posterior al Parcial 2 se organizó en **cinco fases**, cada una entregada como un Pull Request independiente con su verificación:

| Fase | Contenido | Pull Request | Issues cerrados |
|------|-----------|--------------|-----------------|
| **A** | Seed de datos de demostración + corrección de arranque | [PR #99](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/99) | Bloqueo del grafo sin datos; escenario del #17 |
| **B** | Seguridad P0: RBAC, rate limiting, auditoría WORM | [PR #100](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/100) | #89, #90, #91 |
| **C** | Manejo de expiración y refresh de tokens JWT | [PR #100](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/100) | #97 |
| **D** | Exportación de expediente individual a PDF | [PR #101](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/101) | #92, #32 |
| **E** | Pruebas E2E de Playwright ejecutándose en GitHub Actions | [PR #101](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/101) | #93 |

### 3.1 Funcionalidades ajustadas y nuevas

**Control de acceso por roles — RBAC (issue #89).** Nueva dependencia `require_roles()` en `backend/app/core/security.py` que aplica el principio de menor privilegio de la Ley 23:

- Aprobar/rechazar expedientes → exclusivo de **Alta Gerencia** (y admin).
- Reporte de auditoría/trazabilidad → exclusivo del **Oficial de Cumplimiento** (y admin), conforme al criterio de aceptación CA-04.1 del PRD.
- Configuración del sistema y registro de usuarios → exclusivo del **Administrador**. Antes de este cambio el endpoint de registro era público, lo que constituía una brecha de seguridad real que fue cerrada.

**Rate limiting (issue #90).** Con `slowapi`, el endpoint de login queda limitado a 10 intentos por minuto por dirección IP (configurable vía `LOGIN_RATE_LIMIT`), respondiendo HTTP 429. Mitiga ataques de fuerza bruta sobre credenciales.

**Auditoría inmutable WORM (issue #91).** Listeners de SQLAlchemy (`before_update`, `before_delete`) sobre la tabla `eventos_auditoria` lanzan `AuditoriaInmutableError` ante cualquier intento de modificación o borrado: los registros de auditoría son de solo escritura, como exige la Ley 23, Art. 21. Verificado con pruebas unitarias y contra la base de datos real.

**Refresh de tokens JWT (issue #97).** El login emite ahora un refresh token de 7 días (claim `type=refresh`) además del access token de 60 minutos. El endpoint `POST /auth/refresh` rota el refresh token en cada uso, y un refresh token no puede utilizarse como credencial de acceso. En el frontend, un interceptor de axios detecta los 401, renueva el token con una única llamada compartida y reintenta la petición: la sesión del usuario ya no se corta cada hora.

**Exportación de expediente a PDF (issues #92 y #32).** Nuevo servicio `pdf_service.py` (fpdf2) que genera un PDF profesional del expediente con: identificación del cliente, información financiera, beneficiarios finales (con marca [PEP]), estado del expediente, documentos adjuntos con su hash SHA-256, los últimos eventos de trazabilidad y pie legal de conservación. El endpoint `GET /expedientes/{id}/pdf` registra un evento de auditoría `EXPORTAR_PDF`, y la interfaz incorpora el botón **Exportar PDF**.

**Pruebas E2E en CI (issue #93).** Nuevo workflow `e2e-tests.yml` que en cada Pull Request levanta el stack completo con Docker Compose, aplica el seed y ejecuta los 25 tests de Playwright con Chromium, publicando el reporte como artefacto.

**Datos de demostración (PR #99).** Script `seed_demo.py` idempotente: 3 usuarios (uno por rol), 8 clientes con niveles de riesgo reales calculados por el motor (3 alto / 2 medio / 3 bajo), beneficiarios finales compartidos entre sociedades (el ministro PEP «Juan Gómez» es accionista de dos empresas, visible en el grafo), expedientes en todos los estados del flujo, documentos con hash SHA-256 real, alertas y 5 funcionarios públicos para la demo de búsqueda PEP con coincidencia exacta de cédula.

### 3.2 Mejoras implementadas

- **Accesibilidad (issue #34, parcial):** atributos `aria-label` en todos los botones de solo ícono (campana de alertas, controles de zoom del grafo, volver, descargar, editar/eliminar) y leyenda de colores en el grafo de relaciones.
- **Robustez de la suite E2E:** fixture de autenticación real por API (un solo login por corrida, respetuoso del rate limiting), selectores estables por `name`/rol en lugar de selectores posicionales frágiles, y esperas explícitas para datos asíncronos.
- **Portabilidad del entorno de pruebas:** `playwright.config.ts` parametrizable con `E2E_HOST`/`E2E_PORT` y verificación del servidor por URL IPv4 explícita.
- **Higiene del repositorio:** creación del `.gitignore` raíz; se retiraron del control de versiones `__pycache__`, `dist/`, resultados de pruebas y el archivo `.env` del backend (que contenía una clave secreta).
- **Documentación de proceso:** `CLAUDE.md` (guía operativa del repo), `tasks.md` (plan por fases sincronizado con issues), `docs/context/PROJECT_CONTEXT.md` (decisiones y su porqué) y bitácora de handoffs por sesión en `docs/handoffs/`.

### 3.3 Métricas aplicadas (ISTQB – TMMi – TQM)

#### Métricas de requerimientos

| Métrica | Valor | Herramienta | Interpretación |
|---------|-------|-------------|----------------|
| Cobertura de requisitos implementados | 20/20 pruebas del plan = 100% ejecutables | plan-de-pruebas.md + PRD.md | Todos los requisitos funcionales del PRD cuentan con implementación y prueba |
| Trazabilidad legal | Fórmula de riesgo, regla PEP, WORM y retención referencian artículos de Ley 23/254 | PRD.md §1–§6 | Cada control crítico tiene fundamento normativo |
| Volatilidad | Sin cambios de alcance en el cierre | Seguimiento en tasks.md | Alcance estable tras el Parcial 2 |

#### Métricas de diseño

| Métrica | Valor | Herramienta | Interpretación |
|---------|-------|-------------|----------------|
| Complejidad ciclomática promedio | 2.4 (rating A) | radon cc | Código simple y mantenible |
| Complejidad ciclomática máxima | 12 (`pep_service.buscar_funcionario`) | radon cc | Único punto caliente identificado; refactorización pendiente como trabajo futuro |
| Funciones totales | 116+ en 29+ archivos Python | radon cc | Tamaño proporcionado al proyecto |
| Diagramas de arquitectura | 2 (arquitectura + entidad-relación) verificados contra el código | architecture.md | Documentación alineada con la implementación (issue #68 cerrado) |

#### Métricas de código y pruebas

| Métrica | Valor inicial (Parcial 2) | Valor final | Herramienta |
|---------|---------------------------|-------------|-------------|
| Pruebas unitarias/integración backend | 63 | **91** (+28: RBAC, WORM, refresh, rate limit, PDF, API) | pytest |
| Pruebas E2E ejecutándose | 0 (20 escritas pero rotas) | **25/25 en verde, integradas a CI** | Playwright |
| Tasa de éxito de pruebas | 100% (63/63) | 100% (91/91 y 25/25) | pytest / Playwright |
| KLOC total (backend + frontend) | 6,026 líneas | ≈ 6,900 líneas | cloc |
| Densidad de pruebas backend | 27.4 tests/KLOC | ≈ 35 tests/KLOC | cálculo manual |
| Code smells | 0 | 0 | flake8 |
| Vulnerabilidades | 0 | 0 | bandit |
| Defectos abiertos conocidos | 1 (grafo sin datos) | 0 | seguimiento en issues |

El dashboard visual de métricas se genera con `python scripts/generate_metrics_dashboard.py` (cobertura, KLOC, complejidad, mantenibilidad, smells y vulnerabilidades) y se publica semanalmente como artefacto del workflow `metrics-report.yml`.

### 3.4 Defectos corregidos

Los siguientes defectos reales fueron detectados y corregidos durante el cierre — la mayoría **descubiertos por las pruebas E2E**, lo que valida la inversión en automatización:

| # | Defecto | Severidad | Cómo se detectó | Corrección |
|---|---------|-----------|-----------------|------------|
| 1 | El backend no arrancaba con la configuración de docker-compose (`Settings` rechazaba `REDIS_URL`/`ALLOWED_ORIGINS`) | **Crítica** | Al ejecutar el seed | Campos agregados a `config.py` con `extra="ignore"` (PR #99) |
| 2 | **El formulario EDD no se podía enviar** con campos numéricos vacíos: `valueAsNumber` produce `NaN`, la validación lo rechaza y el error quedaba oculto en un acordeón colapsado | **Crítica** | Prueba E2E TC-05 | Preprocesamiento de `NaN → undefined` en el esquema Zod (PR #101) |
| 3 | Campos opcionales vacíos viajaban como `""` y el backend respondía 422 (`EmailStr`, `datetime` no aceptan cadena vacía) | **Alta** | Prueba E2E TC-05 (red: POST 422) | Sanitización del payload antes de enviar (PR #101) |
| 4 | El toast de error crasheaba React al intentar renderizar el `detail` de FastAPI (que es un arreglo de objetos) | Media | Consola durante depuración E2E | Extractor seguro de mensajes de error (PR #101) |
| 5 | El dashboard mostraba tarjetas en 0 y etiquetas ilegibles (`EstadoExpediente.BORRADOR`): los enums se serializaban con `str()` en lugar de `.value` | Alta (visual) | Verificación de UI con Playwright | Serialización con `.value` en `reportes.py` (PR #100) |
| 6 | El endpoint de registro de usuarios era **público**: cualquiera podía crearse una cuenta con rol admin | **Crítica** (seguridad) | Revisión de seguridad de la Fase B | Registro restringido a administradores vía RBAC (PR #100) |
| 7 | 17 de 25 pruebas E2E corrían sin autenticación (fixture importado pero no utilizado) y otras usaban selectores/textos que no existían en la UI | Alta (calidad) | Primera ejecución completa de la suite | Fixture y selectores reescritos (PR #101) |

### 3.5 Decisiones técnicas y su justificación

| Decisión | Justificación |
|----------|---------------|
| **Un Pull Request por fase** con CI obligatorio | Cada incremento queda revisado, verificado y documentado; los issues se cierran automáticamente con el merge (`Closes #n`) |
| **bcrypt directo** en lugar de passlib | Incompatibilidades de passlib con versiones recientes de Python |
| **fpdf2** para la exportación a PDF | Librería Python pura (sin dependencias nativas), suficiente para un documento estructurado con estilo corporativo |
| **slowapi** para rate limiting | Integración natural con FastAPI/Starlette; límite configurable por entorno (10/min en producción, 200/min en CI para no interferir con las E2E) |
| **Listeners ORM para WORM** en lugar de triggers de base de datos | Protección en la capa de aplicación, portable entre motores (PostgreSQL en producción, SQLite en pruebas) y verificable con pruebas unitarias |
| **Rotación de refresh tokens** | Reduce la ventana de uso de un token robado; el refresh usado como access token se rechaza explícitamente |
| **Login por API en el fixture E2E** (una vez por corrida) en lugar de login por UI en cada test | Reduce ~20 logins a 1, respeta el rate limiting y acelera la suite; el login por UI se prueba una sola vez en su spec propio |
| **Grafo SVG propio** con simulación de fuerzas en lugar de PyVis/Plotly | Evita dependencias de Python en el frontend; control total de la interacción (drag, zoom, pan) |
| **Regla PEP inflexible** (`es_pep=true` ⇒ riesgo alto + aprobación gerencial) | Exigencia directa de la Ley 23 y la Rec. 12 del GAFI: ningún PEP puede pasar desapercibido, independientemente del score |
| **OFAC/ONU/UE no implementado** | No existen APIs públicas gratuitas; documentado como exclusión (PRD §12) en lugar de simular la funcionalidad |

---

## 4. Versionamiento

### 4.1 Historial de versiones del documento

| Versión | Fecha | Cambios | Justificación |
|---------|-------|---------|---------------|
| 0.1 | 2026-05-31 | PRD inicial, plan de pruebas y kanban de 62 tareas | Definición del alcance del proyecto |
| 0.2 | 2026-06-15 | Daily Scrum con métricas ISTQB/TMMi/TQM del Parcial 2 | Evidencia de medición de calidad (Unidad II) |
| 0.3 | 2026-07-13 | Sistema de contexto y consolidación de tareas por fases | Preparación del cierre; una sola fuente de verdad |
| 1.0 | 2026-07-13/14 | **Documento final**: retrospectiva, adecuaciones del Parcial 2 (fases A–E), métricas actualizadas, conclusiones | Entrega de cierre del curso |

### 4.2 Control de versiones del software (Git)

El repositorio https://github.com/aaacmsg/debida-diligencia-reforzada contiene la historia completa del proyecto en la rama `master`. Hitos principales:

| Commit / PR | Descripción |
|-------------|-------------|
| `234ebe3` scaffolding | Estructura inicial backend/frontend |
| `53cce33`, `95990a2`, `6975b31` | Correcciones de CI: triggers en `master`, Alembic con `DATABASE_URL`, UTF-8 en Windows |
| `3c3edc6` bugfixes | Estabilización previa al cierre |
| `4c63f0e` | Sistema de contexto: CLAUDE.md, tasks.md por fases, handoffs |
| **PR #99** (`0e95f6d`) | Fase A: seed de demostración + fix de arranque |
| **PR #100** (`6212a0f`) | Fases B y C: RBAC, rate limiting, WORM, refresh JWT + fix del dashboard |
| **PR #101** | Fases D y E: exportación PDF + E2E en CI + 4 defectos corregidos + `.gitignore` |

Complementos del versionamiento:

- **GitHub Issues**: 101 elementos numerados; los issues #1–#68 corresponden a las tareas de verificación del kanban original y los #69–#98 al backlog de features, cerrados con evidencia al completarse.
- **GitHub Projects** (tablero #2 «Debida Diligencia R»): columnas Backlog / In progress / Done con los 30 issues de features.
- **GitHub Actions**: cada push y PR ejecuta `backend-ci` (flake8, bandit, radon, alembic, pytest con cobertura), `frontend-ci` (build) y `e2e-tests` (Playwright); `metrics-report` genera el dashboard de métricas semanalmente.

### 4.3 Flujo de trabajo con Pull Requests

Desde el cierre del Parcial 2 ningún cambio de funcionalidad entra directo a `master`: se desarrolla en una rama `fase-<letra>-<tema>`, se abre un Pull Request con descripción de cambios y verificación realizada, el CI debe pasar en verde, y el merge cierra automáticamente los issues correspondientes. Este flujo queda evidenciado en los PRs #99, #100 y #101.

---

## 5. Conclusiones

### 5.1 Conclusiones individuales

> *Borradores para que cada integrante los revise y los haga suyos.*

**César Santiago.** Este proyecto me permitió experimentar el ciclo completo de un producto de software con requisitos regulatorios reales. Lo más valioso fue comprobar que la infraestructura de proceso —integración continua, un tablero honesto y un flujo de Pull Requests— no es burocracia: fue lo que nos permitió detectar que funcionalidades que creíamos terminadas tenían defectos críticos, y corregirlos con evidencia. Aprendí a traducir artículos de ley (Ley 23, Ley 254) en reglas de negocio verificables por pruebas, y que la medición (ISTQB/TMMi) solo sirve si se actúa sobre ella.

**Roberto López.** Mi mayor aprendizaje técnico fue la diferencia entre probar componentes y probar el sistema. El formulario EDD pasaba su validación local y aun así el flujo completo estaba roto por un detalle de conversión de tipos; solo una prueba de punta a punta, con navegador real y backend real, lo hizo visible. También interioricé que la accesibilidad (aria-labels, contraste, foco) no es un extra estético sino un requisito verificable, y que escribir selectores de prueba estables es una habilidad de diseño de UI, no solo de testing.

**Jean Suárez.** Trabajar la capa de seguridad me enseñó que los controles deben diseñarse para fallar de forma segura: la inmutabilidad WORM se implementó de modo que cualquier intento de alteración lance una excepción, el registro de usuarios quedó restringido por rol, y los tokens se rotan y expiran. La lección de proceso fue la paridad de entornos: la mitad de nuestros bloqueos históricos (Python 3.14, `main` vs `master`, codificación en Windows) no eran errores de lógica sino de entorno, y se resuelven con configuración explícita y contenedores.

### 5.2 Conclusión grupal sobre la calidad del producto

El equipo considera que el producto alcanzó un nivel de calidad **verificable y demostrable** para su alcance académico: 91 pruebas de backend y 25 pruebas E2E ejecutándose automáticamente en cada cambio, 0 vulnerabilidades detectadas por bandit, 0 code smells por flake8, complejidad ciclomática promedio de 2.4 (rating A) y los cuatro controles regulatorios centrales (fórmula de riesgo EBR, regla PEP, auditoría WORM y flujo de aprobación gerencial) implementados con su fundamento legal y sus pruebas. La calidad no se afirmó: se midió, se encontraron siete defectos reales —tres de ellos críticos— y se corrigieron con evidencia en los Pull Requests #99–#101.

### 5.3 Evaluación del proceso colaborativo

El proceso evolucionó durante el semestre de un trabajo individual paralelo a una colaboración estructurada: tablero compartido en GitHub Projects, issues con etiquetas y evidencia de cierre, retrospectivas documentadas (daily-scrum-presentacion.md) y, en el cierre, revisión por Pull Request. Los momentos de mayor fricción coincidieron con la falta de una fuente única de verdad sobre el estado del proyecto (tres listas de tareas divergentes); consolidarlas en `tasks.md` sincronizado con los issues resolvió el problema. La adaptación al formato de entrega por video ante la incapacidad de la profesora se gestionó sin pérdida de alcance.

### 5.4 Recomendaciones para futuras iteraciones

1. **Elevar la cobertura de backend por encima del 50%** con pruebas de integración de los endpoints restantes (hoy la cobertura de línea ronda el 26–30% aunque los flujos críticos están cubiertos).
2. **Refactorizar `pep_service.buscar_funcionario`** (complejidad 12) dividiéndolo en funciones de normalización, matching y scoring.
3. **Completar el backlog P1/P2 documentado**: tarea programada de Celery para la descarga mensual automática de CSVs PEP (#94), notificaciones por correo para alertas de alto riesgo (#96), panel de administración de usuarios (#95) y feature flags (#98).
4. **Incorporar SonarQube** al CI para medir deuda técnica de forma continua.
5. **Matriz de trazabilidad formal** requisito → prueba → código, generada automáticamente desde los IDs de los specs.
6. **MFA para roles críticos** (previsto en el modelo de datos con `mfa_secret`, pendiente de implementación) y evaluación de un proveedor de firma digital para los documentos.

---

## 6. Referencias normativas y técnicas

1. Ministerio de Economía y Finanzas de Panamá. (2015). *Ley 23 de 27 de abril de 2015* — Prevención de blanqueo de capitales, financiamiento del terrorismo y proliferación de armas de destrucción masiva.
2. Asamblea Nacional de Panamá. (2021). *Ley N.º 254 de 11 de noviembre de 2021* — Transparencia fiscal internacional y fortalecimiento AML/CFT.
3. Superintendencia de Bancos de Panamá. (2025). *Resolución General SBP-RG-PSO-R-2025-00671* — Otros Sujetos Obligados Financieros.
4. GAFILAT. (2024). *Estándares internacionales — Recomendaciones y metodología* (Recomendaciones 10, 12, 19 y 24).
5. ISTQB. *Certified Tester Foundation Level Syllabus* — métricas y proceso de pruebas.
6. TMMi Foundation. *Test Maturity Model integration* — madurez del proceso de pruebas.
7. Documentación técnica: FastAPI, SQLAlchemy 2.0, React 18, Playwright, pytest, GitHub Actions.

---

## 7. Anexos — Evidencias

> Las capturas se insertan en la versión PDF final. Cada marcador indica la evidencia requerida.

### Anexo A — Capturas del sistema

- **A.1** `<INSERTAR AQUÍ: captura de la pantalla de Login (usuario admin)>`
- **A.2** `<INSERTAR AQUÍ: captura del Dashboard con las tarjetas de totales, el gráfico de pastel por estado y el de barras por nivel de riesgo — con los datos del seed: 8 expedientes, 3 alto / 2 medio / 3 bajo>`
- **A.3** `<INSERTAR AQUÍ: captura del Formulario EDD (ClientesPage) con los módulos en acordeón y la sección PEP ampliada al marcar es_pep>`
- **A.4** `<INSERTAR AQUÍ: captura de la lista de Expedientes con los badges de estado (Pendiente Gerencia) y riesgo (Alto/Medio/Bajo)>`
- **A.5** `<INSERTAR AQUÍ: captura del detalle de un expediente con las 3 pestañas (Detalle, Documentos, Trazabilidad) y el botón Exportar PDF>`
- **A.6** `<INSERTAR AQUÍ: captura del PDF exportado del expediente EDD-…-SEED0002 (Juan Gómez, PEP, riesgo ALTO)>`
- **A.7** `<INSERTAR AQUÍ: captura de la Búsqueda PEP con el match exacto por cédula 8-702-3355 (score 100)>`
- **A.8** `<INSERTAR AQUÍ: captura del Grafo de Relaciones mostrando al PEP Juan Gómez conectado a Constructora Istmo e Inversiones Caribe, con la leyenda de colores>`
- **A.9** `<INSERTAR AQUÍ: captura del dropdown de Alertas en vivo con las alertas del seed>`
- **A.10** `<INSERTAR AQUÍ: captura del modal/flujo de aprobación con comentario obligatorio>`

### Anexo B — Evidencias de pruebas

- **B.1** `<INSERTAR AQUÍ: captura de la terminal con pytest: 91 passed>`
- **B.2** `<INSERTAR AQUÍ: captura de la terminal o del reporte HTML de Playwright: 25 passed>`
- **B.3** `<INSERTAR AQUÍ: captura del workflow e2e-tests en GitHub Actions en verde>`
- **B.4** `<INSERTAR AQUÍ: captura del dashboard de métricas (backend/metrics/dashboard.html): cobertura, KLOC, complejidad, smells, vulnerabilidades>`
- **B.5** `<INSERTAR AQUÍ: captura de la demostración WORM: intento de modificar un evento de auditoría rechazado con AuditoriaInmutableError>`
- **B.6** `<INSERTAR AQUÍ: captura del login respondiendo 429 tras exceder el límite de intentos (rate limiting)>`

### Anexo C — Evidencias de gestión y versionamiento

- **C.1** `<INSERTAR AQUÍ: captura del tablero GitHub Projects #2 con columnas Backlog / In progress / Done>`
- **C.2** `<INSERTAR AQUÍ: captura de la lista de issues cerrados con sus etiquetas (backend, security, testing, completed…)>`
- **C.3** `<INSERTAR AQUÍ: captura del historial de commits de la rama master (git log o pestaña Commits de GitHub)>`
- **C.4** `<INSERTAR AQUÍ: capturas de los Pull Requests #99, #100 y #101 con sus checks de CI en verde>`
- **C.5** `<INSERTAR AQUÍ: captura de los workflows de GitHub Actions (backend-ci, frontend-ci, e2e-tests, metrics-report)>`

### Anexo D — Código relevante (fragmentos citados en el documento)

- **D.1** Fórmula ponderada de riesgo — `backend/app/services/riesgo_service.py`
- **D.2** Regla PEP y auto-creación de expediente — `backend/app/api/v1/endpoints/clientes.py`
- **D.3** RBAC `require_roles()` y refresh tokens — `backend/app/core/security.py`
- **D.4** Inmutabilidad WORM — `backend/app/models/models.py` (listeners al final del archivo)
- **D.5** Generación de PDF — `backend/app/services/pdf_service.py`
- **D.6** Interceptor de refresh automático — `frontend/src/services/api.ts`

---

*Documento generado como parte del cierre del Proyecto Semestral — Ingeniería de Software IV, Universidad Tecnológica de Panamá.*
