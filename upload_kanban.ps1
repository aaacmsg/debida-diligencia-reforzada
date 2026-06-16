# Upload kanban tasks to GitHub Issues
# Usage: .\upload_kanban.ps1

$REPO = "aaacmsg/debida-diligencia-reforzada"
$TASK_FILE = "kanban-tasks.md"
$COUNTER = 1

function Get-Label {
    param([string]$Section)

    if ($Section -match "ALFA.*LOGICA") { return "alfa-logica" }
    if ($Section -match "ALFA.*SEGURIDAD") { return "alfa-seguridad" }
    if ($Section -match "BACKEND") { return "backend" }
    if ($Section -match "BETA.*USABILIDAD") { return "beta-usabilidad" }
    if ($Section -match "BETA.*CUMPLIMIENTO") { return "beta-cumplimiento" }
    if ($Section -match "BETA.*EXPERIENCIA") { return "beta-ux" }
    if ($Section -match "FRONTEND") { return "frontend" }
    if ($Section -match "INTEGRATION") { return "integration" }
    if ($Section -match "INFRASTRUCTURE") { return "infrastructure" }
    if ($Section -match "DOCUMENTATION") { return "documentation" }
    return "needs-review"
}

$content = Get-Content -Path $TASK_FILE -Raw
$lines = $content -split "`n"

$CURRENT_SECTION = ""

foreach ($line in $lines) {
    $line = $line.Trim()

    if ($line -match "^##\s+(.+)") {
        $CURRENT_SECTION = $matches[1]
        Write-Host "Section: $CURRENT_SECTION" -ForegroundColor Cyan
        continue
    }

    if ($line -match "^-\ \[\s\]\s+(.+)") {
        $TASK = $matches[1].Trim()
        $LABEL = Get-Label -Section $CURRENT_SECTION

        $TITLE = "[T-$COUNTER] $TASK"
        $BODY = "**Categoria:** $CURRENT_SECTION"

        Write-Host "Creating: $TITLE" -ForegroundColor Yellow

        gh issue create `
            --repo $REPO `
            --title $TITLE `
            --body $BODY `
            --label $LABEL

        $COUNTER++
        Start-Sleep -Milliseconds 500
    }
}

Write-Host ""
Write-Host "Completado! $($COUNTER - 1) tareas creadas" -ForegroundColor Green