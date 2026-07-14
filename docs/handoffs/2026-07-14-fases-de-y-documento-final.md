# Handoff — 2026-07-14 — Fases D+E (PR #101) y documento final

## Estado en una frase

Las 5 fases de código (A–E) están completas — A/B/C mergeadas, D/E en el [PR #101](https://github.com/aaacmsg/debida-diligencia-reforzada/pull/101) — y el documento final está redactado en `docs/documento-final.md`; falta que el equipo inserte capturas, personalice conclusiones, exporte a PDF y grabe el video.

## Qué se hizo esta sesión

- **PR #101 (Fases D+E)**: export PDF de expediente (`pdf_service.py` con fpdf2, endpoint `GET /expedientes/{id}/pdf`, botón en UI) + Playwright E2E en CI (`e2e-tests.yml`).
- **Suite E2E reparada de raíz**: el fixture `authPage` no se usaba (17/25 tests corrían sin login); ahora hace 1 login por API por corrida. Resultado: **25/25 passing** (antes 0 corridas completas verdes).
- **4 defectos reales corregidos** descubiertos por las E2E: (1) formulario EDD no enviable con numéricos vacíos (NaN vs z.number, error oculto en acordeón); (2) payload con `""` → 422 de EmailStr/datetime; (3) toast crasheaba con detail array de FastAPI; (4) botones solo-ícono sin aria-label + grafo sin leyenda (issue #34 parcial).
- `.gitignore` raíz nuevo; destrackeados `__pycache__`, `dist`, `test-results`, `.coverage`, `backend/.env`.
- **`docs/documento-final.md`**: documento de cierre completo (UTP, prof. María Mosquera, 3 integrantes, salón 1GS242) con retrospectiva, adecuaciones fases A–E, métricas ISTQB/TMMi, 7 defectos documentados, versionamiento, conclusiones y anexos con placeholders `<INSERTAR AQUÍ: ...>` para capturas.
- **Playwright MCP instalado** (`claude mcp add playwright`, ✔ Connected) — sus herramientas estarán disponibles al reiniciar la sesión de Claude.

## Decisiones tomadas (y por qué)

- Fases D y E en un solo PR (pedido del usuario).
- Fixture E2E con login por API + tokens via initScript en vez de login por UI por test: respeta el rate limit y acelera la suite; el login por UI se prueba en su propio spec.
- `webServer.url` con IPv4 explícita en playwright.config: en esta máquina hay servidores ajenos (app "Plug" de Next.js) escuchando en IPv6 en los puertos 3000/3001 y Playwright reutilizaba el servidor equivocado.
- Test de rate limit adaptativo al `LOGIN_RATE_LIMIT` configurado (se salta si >30/min, p. ej. en el entorno E2E).

## Qué quedó pendiente / a medias

- **Merge del PR #101** (CI corriendo al cierre de la sesión — verificar checks).
- Tras el merge: actualizar fila D/E en `tasks.md` a ✅ y mover los issues #92/#93/#32 en el tablero Projects a Done si no se mueven solos.
- **Fase 6 humana**: insertar capturas en los placeholders del documento, personalizar conclusiones individuales/responsabilidades, exportar a PDF, grabar video Scrum Review (guion sugerido: demo con datos del seed — login, dashboard, crear cliente PEP, aprobar como gerencia, grafo, export PDF, búsqueda PEP).
- Backlog abierto restante (P1/P2 documentado como trabajo futuro): #94, #95, #96, #98 + refactor de `pep_service.buscar_funcionario`.

## Bloqueos y gotchas descubiertos

- **Puertos 3000/3001 en IPv6** los ocupa otra app del usuario ("Plug", Next.js) — para el frontend EDD local usar `E2E_HOST=127.0.0.1 E2E_PORT=3002` (o cualquier puerto libre) y URLs con `127.0.0.1`, no `localhost`.
- **PostgreSQL local de Windows intercepta el puerto 5432 del host**: los tests de integración locales se saltan; correrlos dentro del contenedor (`docker-compose exec backend python -m pytest`). En CI corren normal.
- El contenedor backend corre con `LOGIN_RATE_LIMIT=200/minute` (para E2E); en un despliegue real quitar esa variable para volver al default 10/min.
- MCP agregado a mitad de sesión no expone herramientas hasta reiniciar la sesión.

## Estado de verificación

- Backend: **91 passed** dentro del contenedor (85 + 6 de PDF); local 81 passed + 10 skipped (sin DB accesible).
- E2E: **25/25 passed** (2 corridas limpias) contra stack Docker + seed.
- Frontend: `npm run build` OK.
- PDF verificado visualmente (expediente SEED0002 con todas las secciones).
- CI del PR #101: en ejecución al cierre — verificar `gh pr checks 101`.

## Archivos actualizados de contexto

- [x] `tasks.md` actualizado (D/E → PR #101; documento final marcado como redactado)
- [x] Issues: #92, #93, #32 se cierran con el merge del PR #101 (Closes en el body)
- [ ] `PROJECT_CONTEXT.md` — pendiente añadir gotchas de puertos si se repiten
