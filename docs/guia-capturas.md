# Guía para obtener cada captura del documento final

Cada sección de esta guía corresponde a un marcador `<INSERTAR IMAGEN: ...>` del documento final (`docs/documento-final.md`). Sigue los pasos en orden y toma la captura con la herramienta de recortes de Windows (tecla `Win + Shift + S`).

## Preparación (hacer una sola vez antes de empezar)

1. Abre Docker Desktop y espera a que arranque.
2. En una terminal, dentro de la carpeta del proyecto:

```bash
docker-compose up --build -d
docker-compose exec backend python scripts/seed_demo.py
```

3. Espera a que el backend responda: abre http://localhost:8000/health y debe decir `{"status":"healthy"}`.
4. El frontend queda en **http://localhost:3000**.

> **Si Docker dice "ports are not available: 3000"** (otro programa usa ese puerto), levanta todo con un puerto alternativo y usa esa dirección en todos los pasos de esta guía:
>
> ```bash
> FRONTEND_PORT=3002 docker-compose up --build -d
> ```
>
> y entra por **http://127.0.0.1:3002** (con `127.0.0.1`, no `localhost`).

Usuarios: `admin/admin123`, `oficial/oficial123`, `gerencia/gerencia123`.

---

## Anexo A. Capturas del sistema

### A.1 Pantalla de Login
1. Abre http://localhost:3000/login (si ya tenías sesión, presiona "Cerrar Sesion" primero).
2. Captura la pantalla completa con el logo, los campos y el pie con la referencia a la Ley 23.

### A.2 Dashboard con datos
1. Inicia sesión como `admin`.
2. Ya estás en el Dashboard. Verifica que se vea: Total Expedientes 8, el gráfico de pastel por estado y el de barras por riesgo (3 alto, 2 medio, 3 bajo).
3. Captura la pantalla completa.

### A.3 Formulario EDD con la sección PEP
1. Menú lateral → **Clientes** → botón **Nuevo Cliente**.
2. Se abre el formulario con los módulos en acordeón (I. Identificación, II. Financiera, etc.).
3. Marca la casilla **PEP**: aparece la sección ámbar "Informacion PEP Obligatoria" con Cargo Político, Tipo de Relación y País de Residencia Fiscal.
4. Captura con la sección PEP visible.

### A.4 Lista de expedientes
1. Menú lateral → **Expedientes**.
2. Verifica que se vean los 8 expedientes `EDD-...-SEED000x` con sus etiquetas de estado (Pendiente Gerencia, Aprobado, Borrador...) y de riesgo (Alto en rojo, Medio en amarillo, Bajo en verde).
3. Captura la lista.

### A.5 Detalle de expediente con pestañas y botón Exportar PDF
1. En Expedientes, haz clic en **EDD-...-SEED0002** (el de Juan Gómez, el ministro PEP).
2. Arriba a la derecha se ve la etiqueta "Alto", el score y el botón azul **Exportar PDF**.
3. Captura mostrando las tres pestañas (Detalle, Documentos, Trazabilidad). Puedes tomar una segunda captura con la pestaña Trazabilidad abierta, donde se ve el historial de eventos.

### A.6 PDF exportado
1. En ese mismo expediente, presiona **Exportar PDF**. Se descarga `EDD-...-SEED0002.pdf`.
2. Abre el archivo descargado y captura la primera página (se ven las secciones I a VI, el nivel de riesgo en rojo y el hash SHA-256 del documento).

### A.7 Búsqueda PEP con coincidencia exacta
1. Menú lateral → **Buscar PEP**.
2. En el campo de cédula escribe `8-702-3355` y busca.
3. Aparece Juan Gómez, Ministro de Obras Públicas, con score de similitud 100 y marca de coincidencia exacta.
4. Captura el resultado.

### A.8 Grafo de relaciones
1. Menú lateral → **Grafo de Relaciones**.
2. Espera a que se acomoden los nodos. Verifica que se vea la **leyenda** (Cliente, PEP, Persona, Documento) en la barra superior y los nodos naranjas con la etiqueta PEP.
3. Si algún nodo tapa a otro, arrástralo con el mouse.
4. Captura el grafo completo.

### A.9 Panel de alertas
1. Haz clic en la **campana** de la esquina superior derecha (tiene un contador rojo).
2. Se despliega el panel con las alertas del seed (PEP detectado, riesgo alto, vínculo PEP...).
3. Captura con el panel abierto.

### A.10 Aprobación con comentario obligatorio
1. Cierra sesión y entra como `gerencia` / `gerencia123`.
2. Ve a **Expedientes** → entra a **EDD-...-SEED0003** (Ana Castillo, Pendiente Gerencia).
3. Presiona **Aprobar**: el navegador pide el comentario obligatorio.
4. Captura con el cuadro de comentario visible. (Si quieres conservar el expediente pendiente para el video, presiona Cancelar después de capturar.)

---

## Anexo B. Evidencias de pruebas

### B.3 Resultado de pytest (91 passed)
1. Con el sistema levantado, en una terminal:

```bash
docker-compose exec backend python -m pytest -v
```

2. Espera a que termine (menos de un minuto) y captura el final de la salida, donde dice `91 passed` (o `90 passed, 1 skipped` si el contenedor tiene el límite de login elevado; ambas son válidas, la nota del documento lo explica).
3. Si quieres que salga también la cobertura del 70%, usa:

```bash
docker-compose exec backend python -m pytest --cov=app -q
```

y captura la tabla final con la línea `TOTAL ... 70%`.

### B.4 Resultado de Playwright (25 passed)
Opción rápida (recomendada), desde GitHub:
1. Abre https://github.com/aaacmsg/debida-diligencia-reforzada/actions
2. Entra al workflow **E2E Tests**, corrida más reciente en verde → job `e2e` → paso "Ejecutar tests E2E (Playwright)".
3. Captura donde se ve la lista de tests con ✓ y el total `25 passed`.

Opción local:
1. Con el sistema levantado: `cd frontend && npm install && npx playwright test`
   (en la máquina de César: `E2E_HOST=127.0.0.1 E2E_PORT=3002 npx playwright test`)
2. Captura la terminal con `25 passed`. El reporte HTML queda en `frontend/tests/report/index.html` si prefieres capturarlo desde ahí.

### B.5 Workflow e2e-tests en verde
1. https://github.com/aaacmsg/debida-diligencia-reforzada/actions → filtro **E2E Tests**.
2. Captura la lista de corridas con el check verde, o entra a una corrida y captura el resumen del job.

---

## Anexo C. Métricas

### C.4 Dashboard de métricas
1. Con el sistema levantado, en PowerShell **desde la raíz del proyecto** (este comando monta el repositorio completo para que se midan backend y frontend, y se conecta a la base de datos para que corran las 91 pruebas):

```powershell
docker run --rm -v "${PWD}:/repo" -w /repo/backend --network proyecto_diligencia_reforzada_default -e DATABASE_URL="postgresql://postgres:postgres@db:5432/diligencia_db" proyecto_diligencia_reforzada-backend python scripts/generate_metrics_dashboard.py
```

2. Abre `backend/metrics/dashboard.html` en el navegador y captura: primero las tarjetas de arriba (c4a) y luego las tres tablas de métricas (c4b).
3. Verifica antes de capturar: cobertura 70%, 91/91 pruebas, frontend con miles de líneas (no cero) e incidencias de estilo 35. Si algo sale en "N/D", el comando no se corrió desde la raíz o la base de datos no estaba arriba.

> No uses `docker-compose exec backend ...` para esta captura: dentro de ese contenedor no existe la carpeta del frontend y el dashboard lo marcaría como no disponible.

---

## Anexo D. Gestión y versionamiento

### D.1 Tablero de GitHub Projects
1. Abre https://github.com/users/aaacmsg/projects/2 (con la cuenta de César, el tablero es privado).
2. Vista Board con las columnas Backlog / In progress / Done.
3. Captura el tablero completo.

### D.2 Issues con etiquetas
1. https://github.com/aaacmsg/debida-diligencia-reforzada/issues?q=is%3Aissue
2. Captura la lista mostrando issues cerrados (morados) con sus etiquetas de colores (backend, security, testing...). Puedes filtrar por `is:closed` para que se vean los completados.

### D.3 Historial de commits
1. https://github.com/aaacmsg/debida-diligencia-reforzada/commits/master
2. Captura mostrando los commits del cierre y los merges de los PRs #99, #100 y #101.

### D.4 Pull Requests con CI en verde
1. https://github.com/aaacmsg/debida-diligencia-reforzada/pulls?q=is%3Apr+is%3Amerged
2. Entra a cada PR (#99, #100, #101) y captura la parte donde se ven los checks en verde y el estado "Merged". Con una captura del #101 (que tiene build, test y e2e) es suficiente si quieres resumir.

### D.5 Workflows de Actions
1. https://github.com/aaacmsg/debida-diligencia-reforzada/actions
2. Captura el panel lateral donde se listan los 4 workflows (Backend CI, Frontend CI, E2E Tests, Metrics Report) con corridas en verde.
