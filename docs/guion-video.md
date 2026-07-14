# Guion del video Scrum Review (formato slides, máx. 10 min)

**Equipo:** César Santiago, Roberto López, Jean Suárez | Ing. de Software IV | Prof. María Mosquera | 1GS242

**Antes de grabar:** `FRONTEND_PORT=3002 docker-compose up -d` + seed cargado + probar el recorrido una vez. Usuarios: `oficial/oficial123`, `gerencia/gerencia123`.

**Regla de tiempo:** si se pasan de 10 min, recortar de la demo (slides 4 a 9), nunca del bloque Spick (slides 12 a 14).

---

## Slide 1 · Portada (0:00, los tres en cámara) — César

- Sistema de Diligencia Debida Reforzada (EDD)
- Cumplimiento AML/CFT en Panamá (Ley 23 de 2015)
- César Santiago · Roberto López · Jean Suárez — 1GS242
- Scrum Review: incremento del Parcial 2

## Slide 2 · Qué es el sistema (0:30) — César

- Registra clientes y calcula su riesgo (bajo / medio / alto)
- Detecta PEP con datos abiertos del gobierno
- Alto riesgo: aprueba solo la Alta Gerencia
- Todo queda en auditoría inmutable

## Slide 3 · Qué agregamos en el cierre (1:00) — César

- Seguridad por roles (RBAC) y límite de intentos de login
- Auditoría WORM y renovación de tokens
- Exportar expediente a PDF
- 25 pruebas E2E corriendo en GitHub Actions
- 7 defectos reales encontrados y corregidos

---

# DEMO EN VIVO (pantalla compartida)

## Slide 4 · Login y dashboard (1:30) — Roberto

- Entrar como `oficial`
- Decir: doble token (acceso 60 min + refresh 7 días), 429 tras 10 intentos
- Dashboard: 8 expedientes, 3 alto / 2 medio / 3 bajo

## Slide 5 · Cliente PEP (2:15) — Roberto

- Nuevo Cliente → marcar casilla PEP
- Mostrar campos obligatorios que aparecen
- Decir: PEP = riesgo alto + gerencia obligatoria, sin excepción (Ley 23)

## Slide 6 · Búsqueda PEP y grafo (3:00) — Roberto

- Buscar cédula `8-702-3355` → match exacto, score 100
- Grafo: nodo naranja (ministro) accionista de 2 empresas
- Decir: redes societarias que en una tabla no se ven

## Slide 7 · Aprobación gerencial (3:45) — Jean

- Cambiar a usuario `gerencia`
- Decir: el oficial ya no puede aprobar (403 por RBAC)
- Aprobar SEED0003 → comentario obligatorio

## Slide 8 · Exportar PDF (4:30) — Jean

- Expediente SEED0002 → botón Exportar PDF
- Abrir el PDF: riesgo, beneficiarios, hash de documentos
- Decir: sirve para archivo o para el regulador

## Slide 9 · Auditoría inmutable (5:15) — Jean

- Pestaña Trazabilidad: cada acción con usuario y fecha
- Decir: modificar o borrar un evento lanza excepción (WORM, Ley 23 Art. 21)

---

# ESTADO TÉCNICO (pantalla: GitHub)

## Slide 10 · Verificación automática (5:45) — César

- Pestaña Actions: 4 workflows en verde
- 91 pruebas backend + 25 E2E en cada Pull Request
- PR #101: checks verdes, issues cerrados con el merge

## Slide 11 · Los números (6:30) — César

- 116 pruebas automatizadas, 100% en verde
- Cobertura backend: 70% (antes 26%)
- Complejidad promedio 2.48 (A) · 0 vulnerabilidades
- Tablero: entregado en Done, futuro en Backlog

---

# SPICK (cada uno en cámara, ~1 min)

## Slide 12 · César (7:00)

- **Avances:** 5 fases entregadas por PR con CI verde
- **Aprendí:** el entorno es parte del producto; cerrar = tener evidencia
- **Problemas:** CI días caído por apuntar a una rama inexistente

## Slide 13 · Roberto (8:00)

- **Avances:** PDF en UI, accesibilidad, grafo con leyenda, 25 E2E estables
- **Aprendí:** probar piezas ≠ probar el sistema (el bug del formulario solo lo vio una E2E)
- **Problemas:** 17 de 25 E2E corrían sin login; al arreglarlas destaparon 3 defectos críticos

## Slide 14 · Jean (9:00)

- **Avances:** RBAC, WORM, rotación de tokens + 28 pruebas nuevas
- **Aprendí:** la seguridad se diseña pensando en el atacante (el registro era público)
- **Problemas:** un PostgreSQL local interceptaba el puerto de Docker; solución documentada

---

## Slide 15 · Cierre (9:40, los tres en cámara)

- Producto con controles de la Ley 23, medido y verificado
- Repositorio, tablero y documento final en los enlaces de la entrega
- Gracias, profesora

---

**Al terminar:** subir a YouTube (oculto) o Drive público y probar el enlace en ventana de incógnito.
