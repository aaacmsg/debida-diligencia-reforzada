# PRD - Sistema de Diligencia Debida Reforzada (EDD)

## Panama AML/CFT Compliance Application

---

## 1. Contexto Legal

### 1.1 Marco Normativo Aplicable (Panama)

| Normativa | Descripcion | Aplicacion |
|-----------|-------------|------------|
| **Ley 23 de 2015** | Prevencion blanqueo capitales, financiamiento terrorismo y armas de destruccion masiva | Base del sistema EDD - enfoque basado en riesgo (EBR) |
| **Ley 254 de 2021** | Transparencia fiscal internacional y fortalecimiento AML/CFT | Beneficiario final, mayor exigencia probatoria, transparencia societaria |
| **Resolucion SBP-RG-PSO-R-2025-00671** | Superintendencia de Bancos de Panama - Otros Sujetos Obligados Financieros | Requerimientos tecnicos especificos para instituciones financieras |
| **GAFI/GAFILAT** | Estandares internacionales | Recomendaciones 10, 12, 19, 24 - base para clasificacion PEP y riesgo |

### 1.2 Principios Clave del Marco Legal

- **Enfoque Basado en Riesgo (EBR)**: Medidas proporcionales al nivel de riesgo del cliente
- **Identificacion y Verificacion**: Con documentacion valida y confiable
- **Beneficiario Final**: Persona natural con control real o propiedad significativa
- **Monitoreo Continuo**: Evaluacion permanente de la relacion comercial
- **Conservacion de Registros**: Minimo 5 anos segun Ley 23
- **Diligencia Reforzada**: Obligatoria para clientes clasificados como alto riesgo

---

## 2. Alcance Funcional

### 2.1 Modulos del Formulario EDD (7 Secciones)

El formulario debe estructurarse en siete modulos funcionales:

| Modulo | Descripcion | Fundamento Legal |
|--------|-------------|------------------|
| **I - Identificacion del Cliente** | Datos personales, identificacion, informacion PEP | Ley 23 Art. 15 |
| **II - Informacion Financiera y Origen de Fondos** | Actividad economica, ingresos, patrimonio, origen fondos | Ley 23 Art. 16, 18 |
| **III - Beneficiario Final** | Identificacion con >10% participacion, estructura societaria | Ley 23 Art. 17, Rec. 24 |
| **IV - Perfil de Riesgo** | Variables geografico, producto, canal, cliente | Rec. 10, 19 |
| **V - Documentacion Adjunta** | Evidencia PDF/JPG/PNG con hash SHA-256 | Resolucion SBP 2025 |
| **VI - Aprobacion y Control Interno** | Flujo de aprobacion gerencial | Ley 254, Resolucion SBP |
| **VII - Registro de Auditoria** | Trazabilidad completa de eventos | Ley 23 Art. 21 |

---

## 3. Requerimientos Funcionales

### 3.1 Funcionalidades Principales (No Negociables)

| ID | Funcionalidad | Descripcion |
|----|---------------|-------------|
| **F-01** | Formulario de ingreso de cliente | Formulario digital EDD con 7 modulos, validacion en tiempo real de campos obligatorios segun plantilla legal |
| **F-02** | Upload de documentos | Carga de archivos PDF, PNG, JPG con tamano maximo configurable (default 10MB), verificacion de integridad (hash SHA-256), registro de fecha/hora/usuario |
| **F-03** | Dashboard de expedientes | Vista general del estado de todos los clientes/expedientes con filtros por riesgo, estado, fechas |
| **F-04** | Trazabilidad historica | Ver todos los cambios de datos de los expedientes (creacion, ediciones, cargas, validaciones, aprobaciones) |
| **F-05** | Grafo de relaciones (PyVis/Plotly) | Mapa de nodos y aristas para identificar clientes que sean accionistas de otras empresas juridicas o relacionados entre si |
| **F-06** | Calculo de nivel de riesgo | Formula ponderada basada en: pais de residencia/origen + cargo politico + sector economico + vinculos familiares/empresariales + origen de fondos |
| **F-07** | Alertas predictivas | Notificaciones automaticas por nivel de riesgo y tiempos de actualizacion de documentacion |
| **F-08** | Consulta datosabiertos.gob.pa | Descarga automatica de CSVs con listado de personas en altos cargos (SBP, CSS, MINGOB, CGR) y busqueda fuzzy por nombre/cedula para encontrar similitudes |
| **F-09** | Listado de cargos PEP | Pagina con el listado oficial de cargos considerados PEP segun la ley de Panama |

### 3.2 12 Requisitos Funcionales Adicionales (del documento)

| ID | Descripcion |
|----|-------------|
| RF-01 | Pantalla principal |
| RF-02 | Formulario de solicitud |
| RF-03 | Analisis de riesgo |
| RF-04 | Gestion de expedientes |
| RF-05 | Actualizacion de estado |
| RF-06 | Revision de cumplimiento |
| RF-07 | Autorizacion |
| RF-08 | Reportes |
| RF-09 | Historial de cambios |
| RF-10 | Configuracion |
| RF-11 | Notificaciones |
| RF-12 | Integracion con sistemas externos |

---

## 4. Validaciones del Sistema

### 4.1 Validaciones Funcionales (No Negociables)

| Validacion | Regla de Negocio |
|------------|------------------|
| Campos obligatorios | No permite envio del formulario si existen campos obligatorios vacios |
| Seccion PEP | Si respuesta es "Si" -> activar seccion ampliada obligatoria |
| Beneficiario final | Participacion minima >10%, suma total debe ser 100%, documento de estructura societaria si persona juridica |
| Documentos | Formatos permitidos: PDF, PNG, JPG; tamano max: 10MB; hash SHA-256 por archivo |
| Alto riesgo | Bloquea aprobacion simple, requiere flujo obligatorio de Alta Gerencia |
| Aprobacion gerencial | No permite registro sin comentario de justificacion |

### 4.2 Validaciones de Seguridad

| Validacion | Implementacion |
|------------|----------------|
| Autenticacion | OAuth2/JWT con expiracion configurable; MFA obligatorio para roles criticos |
| Control de acceso | RBAC con principio de menor privilegio |
| Cifrado | TLS 1.2+ en transito; AES-256 en reposo |
| Logs de auditoria | WORM (Write Once, Read Many) - inmutables |
| Trazabilidad | Historial completo de modificaciones con usuario, fecha, hora |

---

## 5. Integraciones Externas

### 5.1 Fuentes de Datos (100% Gratuitas y Automatizadas)

| Fuente | Datos Obtenidos | Metodo | Estado |
|--------|-----------------|--------|--------|
| **datosabiertos.gob.pa** | CSVs de Designacion de Funcionarios de Altos Mandos (SBP) | API CKAN | **CONFIRMADO FUNCIONANDO** |
| **datosabiertos.gob.pa** | Planillas institucionales (CSS, MINGOB, CGR, etc.) | API CKAN | Disponible |
| **SBP** | Listado mensual de Designaciones de Funcionarios | Descarga CSV | Endpoint: `https://monitoreo.antai.gob.pa/api/designations/download/{ID}/csv` |

### 5.2 Estructura de Datos - Funcionarios

Los CSVs contienen las siguientes columnas:

| Campo | Tipo | Descripcion |
|-------|------|------------|
| Posicion | Entero | Numero correlativo |
| Nombre | Texto | Primer nombre |
| Apellido | Texto | Apellido |
| Cedula | Texto | Identificacion (formato X-XXX-XXXX) |
| Cargo permanente | Texto | Cargo en la institucion |
| Cargo designacion | Texto | Cargo de alto mando actual |
| Fecha inicio | Fecha | Inicio del cargo |
| Fecha final | Fecha | Fin del cargo (si aplica) |
| Numero resolucion | Texto | Resolucion de designation |

### 5.3 Logica de Matching PEP

```
1. Descargar CSVs mensualmente (automatizado)
2. Normalizar datos (nombre, cedula, cargo)
3. Marcar como PEP si cargo contiene:
   - Director, Gerente, Secretario, Viceministro, Presidente, Vicepresidente
   - Ministro, Subdirector, Jefe, Magistrado, Vocal, Embajador
4. Matching contra cliente:
   - Cedula exacta -> ALERTA ALTA
   - Nombre + Apellido con similitud > 85% -> ALERTA MEDIA
```

---

## 6. Calculo de Nivel de Riesgo

### 6.1 Formula Ponderada

```
Score Riesgo = (Pais * 0.25) + (Cargo * 0.30) + (Sector * 0.15) + (Vinculos * 0.20) + (OrigenFondos * 0.10)
```

### 6.2 Variables y Ponderacion

| Variable | Peso | Criterios |
|----------|------|-----------|
| **Pais/Region** | 25% | Alto riesgo = paises sanctioned, territorios offshore |
| **Cargo Publico (PEP)** | 30% | Alto = Ministro,Director; Medio = Jefe,Gerente; Bajo = otros |
| **Sector Economico** | 15% | Alto = construccion,real estate, metales preciosos; Medio = comercio; Bajo = servicios |
| **Vinculos** | 20% | Alto = multiples PEP relacionados, estructuras complejas; Medio = 1 PEP; Bajo = ninguno |
| **Origen de Fondos** | 10% | Alto = fuentes no documentadas; Medio = parcialmente doc; Bajo = completamente doc |

### 6.3 Clasificacion Final

| Score | Nivel | Accion |
|-------|-------|--------|
| 0-35 | **Bajo** | Monitoreo estandar, revision anual |
| 36-65 | **Medio** | Monitoreo intensificado, revision semestral |
| 66-100 | **Alto** | Diligencia Reforzada obligatoria, aprobacion Alta Gerencia |

---

## 7. Requisitos No Funcionales

### 7.1 Seguridad

| ID | Requisito |
|----|-----------|
| RNF-01 | Cifrado AES-256 en reposo, TLS 1.2+ en transito |
| RNF-02 | Autenticacion OAuth2/JWT con MFA para roles criticos (Oficial Cumplimiento, Alta Gerencia, Admin) |
| RNF-03 | Logs de auditoria inmutables (WORM), retencion minima 5 anos |

### 7.2 Usabilidad

| ID | Requisito |
|----|-----------|
| RNF-04 | Tiempo promedio llenado formulario EDD <= 20 minutos (usuario entrenado) |
| RNF-04 | Tasa de error de validacion en envio <= 5% |
| RNF-04 | Cumplimiento WCAG 2.1 nivel AA |

### 7.3 Rendimiento

| ID | Requisito |
|----|-----------|
| RNF-05 | Escenario normal: 200 usuarios concurrentes |
| RNF-05 | Escenario pico: 1000 usuarios concurrentes |
| RNF-05 | Operaciones de guardado/validacion <= 2 segundos |
| RNF-05 | Busqueda (primera pagina) <= 3 segundos |
| RNF-05 | Subida de PDF (hasta 20MB) visible en UI <= 5 segundos |

### 7.4 Disponibilidad y Conservacion

| ID | Requisito |
|----|-----------|
| RNF-06 | Retencion de registros minima de 5 anos (Ley 23/2015) |
| RNF-06 | Respaldo: diario incremental, semanal completo |
| RNF-06 | RTO <= 4 horas, RPO <= 1 hora |
| RNF-06 | Disponibilidad minima 99.5% mensual |

---

## 8. Actores y Roles

| Rol | Actor | Permisos |
|-----|-------|----------|
| **Cliente/Solicitante** | Persona natural o representante legal | Llenar formulario EDD, adjuntar documentacion |
| **Oficial de Cumplimiento** | Revisor primario | Validar informacion, ejecutar consultas de riesgo, marcar niveles |
| **Alta Gerencia** | Decisor final | Aprobar/rechazar expedientes de alto riesgo |
| **Administrador del Sistema** | TI/Gestion | Configurar sistema, gestionar roles, supervisar integridad |

---

## 9. Casos de Uso Principales

### 9.1 Llenar Formulario EDD

```
Actor: Cliente/Solicitante
Precondicion: Cliente autenticado
Flujo:
  1. Inicia nuevo formulario EDD
  2. Completa secciones (I - VII)
  3. Sistema valida campos obligatorios en tiempo real
  4. Guarda como borrador o envia para revision
Excepciones:
  - Campos obligatorios vacios -> bloqueo con mensaje
  - Beneficiario Final incompleto -> bloqueo de envio
Postcondicion: Formulario almacenado; si enviado, notificacion al Oficial de Cumplimiento
```

### 9.2 Aprobar Expediente de Alto Riesgo

```
Actor: Alta Gerencia
Precondicion: Expediente marcado como alto riesgo
Flujo:
  1. Oficial notifica y remite expediente a Alta Gerencia
  2. Alta Gerencia revisa formulario, documentos y trazabilidad
  3. Decide: aprobar, rechazar o solicitar informacion adicional
  4. Registra decision con comentario de justificacion obligatorio
Excepciones:
  - Falta de informacion -> solicitud de complemento
Postcondicion: Decision registrada en trazabilidad con sello temporal
```

### 9.3 Consultar PEP en Datos Abiertos

```
Actor: Oficial de Cumplimiento
Precondicion: Acceso autenticado con permisos
Flujo:
  1. Ingresa nombre o cedula del cliente a consultar
  2. Sistema busca en base local de funcionarios (datosabiertos)
  3. Si encuentra coincidencias fuzzy > 85%:
     - Muestra resultado con cargo, institucion, score similitud
  4. Oficial clasifica como PEP o no
Postcondicion: Consulta registrada en logs de auditoria
```

---

## 10. Criterios de Aceptacion Clave

| Criterio | Condicion |
|----------|-----------|
| CA-01.1 | No permite envio con campos obligatorios vacios |
| CA-01.2 | Valida porcentaje beneficiarios suma 100% y identifica >10% |
| CA-02.1 | Solo acepta PDF/PNG/JPG, max 10MB por archivo |
| CA-02.2 | Genera y almacena hash SHA-256 por documento |
| CA-03.1 | Alto riesgo -> flujo obligatorio Alta Gerencia |
| CA-03.2 | No permite decision sin comentario de justificacion |
| CA-04.1 | Trazabilidad solo roles Oficiales Cumplimiento y Admin |
| CA-04.2 | Logs inmutables (WORM) - nadie puede borrar/modificar |

---

## 11. Stack Tecnologico

### 11.1 Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React o Vue)                  │
│   - Formularios con validacion en tiempo real             │
│   - Dashboard con filtros y metricas                       │
│   - Grafo interactivo con PyVis/Plotly                    │
│   - Notificaciones y alertas                               │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (FastAPI)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI - Python)              │
│   - Endpoints RESTful                                     │
│   - Logica de negocio (validaciones, calculo riesgo)       │
│   - Integracion con PostgreSQL                             │
│   - Descarga y procesamiento de CSVs externos              │
│   - Fuzzy matching con RapidFuzz                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS (PostgreSQL)                │
│   - Clientes, Expedientes, Documentos                       │
│   - Logs de auditoria (WORM)                               │
│   - Base de datos de Funcionarios publicos                  │
│   - Tablas de configuracion                                │
└─────────────────────────────────────────────────────────────┘
```

### 11.2 Componentes Tecnologicos

| Capa | Tecnologia | Justificacion |
|------|------------|---------------|
| **Frontend** | React 18+ o Vue 3+ | SPA moderna, componentes reutilizables, buena UX |
| **UI Components** | TailwindCSS + shadcn/ui o Vuetify | Diseño profesional, compliance con WCAG 2.1 |
| **Grafos** | PyVis (NetworkX) o Plotly | Visualizacion interactiva de relaciones |
| **Backend** | FastAPI (Python 3.11+) | Alto rendimiento, async, documentacion automatica |
| **Base de Datos** | PostgreSQL 15+ | Robusto, ACID, ideal para datos financieros |
| **ORM** | SQLAlchemy 2.0 + Pydantic | Type safety, validacion de datos |
| **Auth** | OAuth2/JWT (python-jose, passlib) | Estandar industrial, MFA |
| **File Storage** | Local storage| Documentos con hash SHA-256 |
| **Fuzzy Matching** | RapidFuzz | Busqueda de similitud rapida |
| **Descarga CSVs** | httpx (async) + API CKAN | Consumo de datosabiertos.gob.pa |
| **Background Jobs** | Celery + Redis | Tareas programadas (descarga CSVs, alertas) |
| **API Documentation** | OpenAPI/Swagger (FastAPI built-in) | Documentacion automatica |

### 11.3 Estructura de Proyecto

```
diligencia-reforzada/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── clientes.py
│   │   │   │   │   ├── expedientes.py
│   │   │   │   │   ├── documentos.py
│   │   │   │   │   ├── riesgos.py
│   │   │   │   │   ├── pep.py
│   │   │   │   │   ├── reportes.py
│   │   │   │   │   └── auth.py
│   │   │   │   └── router.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── cliente.py
│   │   │   ├── expediente.py
│   │   │   ├── documento.py
│   │   │   ├── riesgo.py
│   │   │   ├── usuario.py
│   │   │   └── auditoria.py
│   │   ├── schemas/
│   │   │   ├── cliente.py
│   │   │   ├── expediente.py
│   │   │   ├── documento.py
│   │   │   ├── riesgo.py
│   │   │   └── auditoria.py
│   │   ├── services/
│   │   │   ├── cliente_service.py
│   │   │   ├── expediente_service.py
│   │   │   ├── documento_service.py
│   │   │   ├── riesgo_service.py
│   │   │   ├── pep_service.py
│   │   │   ├── alertas_service.py
│   │   │   └── datos_abiertos_service.py
│   │   ├── tasks/
│   │   │   ├── descargar_csvs.py
│   │   │   └── alertas_predictivas.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── alembic/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── formulario/
│   │   │   ├── dashboard/
│   │   │   ├── grafo/
│   │   │   └── layout/
│   │   ├── pages/
│   │   │   ├── clientes/
│   │   │   ├── expedientes/
│   │   │   ├── reportes/
│   │   │   ├── pep/
│   │   │   ├── configuracion/
│   │   │   └── auth/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   └── App.vue
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 12. Exclusiones Conocidas

| Item | Razon |
|------|-------|
| OFAC API | No existe API gratuita publica |
| ONU/UE API en tiempo real | No existen APIs gratuitas publicas |
| Firma digital avanzada (XAdES/PAdES) | Requiere proveedor comercial (DocuSign, HelloSign) |

---

## 13. Referencias Normativas

1. Ministerio de Economia y Finanzas de Panama. (2020). Ley 23 de 27 de abril de 2015
2. Asamblea Nacional de Panama. (2021). Ley N. 254 de 11 de noviembre de 2021
3. Superintendencia de Bancos de Panama. (2025). Resolucion General SBP-RG-PSO-R-2025-00671
4. GAFILAT. (2024). Estandares internacionales - Recomendacionesmetodologia-actDIC2023.pdf

---

**Version:** 1.0
**Fecha:** 2026-05-31
**Estado:** Borrador
