# Upload tasks to GitHub Issues + Project #2
# Requisito: gh CLI instalado y autenticado (gh auth login)
# Uso: .\upload_tasks.ps1

$repo = "aaacmsg/debida-diligencia-reforzada"
$projectNumber = 2

# Crear labels que no existen
$newLabels = @(
    @{name="completed"; color="22C55E"; desc="Tarea completada"}
    @{name="security"; color="EF4444"; desc="Seguridad y hardening"}
    @{name="testing"; color="A855F7"; desc="Pruebas y calidad"}
    @{name="devops"; color="06B6D4"; desc="CI/CD e infraestructura"}
    @{name="metrics"; color="F59E0B"; desc="Métricas y mediciones"}
    @{name="pep"; color="F97316"; desc="PEP y datos abiertos"}
    @{name="auth"; color="6366F1"; desc="Autenticación y autorización"}
    @{name="ux"; color="94A3B8"; desc="Experiencia de usuario"}
)

foreach ($l in $newLabels) {
    $existing = gh label list --repo $repo 2>$null | Select-String "^$($l.name)`t"
    if (-not $existing) {
        gh label create $l.name --repo $repo --color $l.color --description $l.desc
        Write-Host "  + Label creado: $($l.name)" -ForegroundColor Cyan
    }
}

# Tasks
$tasks = @(
    # ✅ COMPLETADAS
    @{title="Backend FastAPI completo (8 módulos API)"; label="backend,completed"}
    @{title="Modelos SQLAlchemy (9 tablas)"; label="backend,completed"}
    @{title="Auth JWT + bcrypt (login/register/me)"; label="backend,auth,completed"}
    @{title="CRUD Clientes + auto-creación de Expediente con riesgo"; label="backend,completed"}
    @{title="CRUD Expedientes + flujo aprobar/rechazar"; label="backend,completed"}
    @{title="Upload documentos SHA-256 + endpoint descarga"; label="backend,completed"}
    @{title="Cálculo de riesgo (fórmula ponderada 5 variables)"; label="backend,completed"}
    @{title="Búsqueda PEP con RapidFuzz (fuzzy matching)"; label="backend,pep,completed"}
    @{title="Sincronización datosabiertos.gob.pa vía API CKAN"; label="backend,pep,completed"}
    @{title="Reportes (dashboard, auditoría, CSV export, grafo)"; label="backend,completed"}
    @{title="CRUD Alertas + generación automática"; label="backend,completed"}
    @{title="Configuración persistente key-value"; label="backend,completed"}
    @{title="Endpoint listado cargos PEP según Ley de Panamá"; label="backend,pep,completed"}
    @{title="Tests unitarios pytest (63 tests) + CI GitHub Actions"; label="testing,devops,completed"}
    @{title="Dashboard React con Recharts (PieChart + BarChart)"; label="frontend,completed"}
    @{title="Formulario EDD 7 módulos con Zod + react-hook-form"; label="frontend,completed"}
    @{title="Grafo interactivo SVG con simulación de fuerzas"; label="frontend,completed"}
    @{title="Layout con sidebar + dropdown alertas en vivo"; label="frontend,completed"}
    @{title="Script generador de dashboard de métricas"; label="testing,metrics,completed"}
    @{title="PEPSearchPage con búsqueda fuzzy + cargos PEP"; label="frontend,pep,completed"}

    # 🔜 MVP PENDIENTES
    @{title="Implementar control de acceso por roles (RBAC) en login y endpoints"; label="backend,security"}
    @{title="Rate limiting por IP/usuario (slowapi o similar)"; label="backend,security"}
    @{title="Logs de auditoría inmutables (protección WORM en backend)"; label="backend,security"}
    @{title="Exportar expediente individual a PDF"; label="frontend,backend"}
    @{title="Ejecutar Playwright E2E tests en GitHub Actions CI"; label="testing,devops"}
    @{title="Celery task programada para descarga automática de CSVs PEP"; label="backend"}
    @{title="Panel de administración de usuarios (CRUD desde UI)"; label="frontend,backend"}
    @{title="Notificaciones reales (email) para alertas de alto riesgo"; label="backend"}
    @{title="Manejo de expiración y refresh de tokens JWT"; label="backend,security"}
    @{title="Feature flags para despliegues progresivos"; label="backend,devops"}
)

Write-Host "`nCreando $($tasks.Count) issues en $repo y agregando al Project #$projectNumber ..." -ForegroundColor Cyan

foreach ($t in $tasks) {
    Write-Host "  → $($t.title)" -ForegroundColor Yellow

    $issueUrl = gh issue create --repo $repo --title "$($t.title)" --body "." --label "$($t.label)" 2>&1 | Select-Object -Last 1

    if ($issueUrl -match "^https://github.com/") {
        gh project item-add $projectNumber --owner aaacmsg --url $issueUrl 2>$null
        Write-Host "    ✓ Issue + Project" -ForegroundColor Green
    } else {
        Write-Host "    ✗ Error: $issueUrl" -ForegroundColor Red
    }
}

Write-Host "`n✅ Listo! Ve a tu project: https://github.com/users/aaacmsg/projects/$projectNumber" -ForegroundColor Green
