# Create labels for kanban board
# Usage: .\create_labels.ps1

$REPO = "aaacmsg/debida-diligencia-reforzada"

$labels = @{
    "alfa-logica" = @{color="FF6B6B"; desc="Alfa - Logica Interna"}
    "alfa-seguridad" = @{color="FFA500"; desc="Alfa - Seguridad"}
    "backend" = @{color="22C55E"; desc="Backend implementation"}
    "frontend" = @{color="3B82F6"; desc="Frontend implementation"}
    "beta-usabilidad" = @{color="EAB308"; desc="Beta - Usabilidad"}
    "beta-cumplimiento" = @{color="A855F7"; desc="Beta - Cumplimiento normativo"}
    "beta-ux" = @{color="94A3B8"; desc="Beta - Experiencia usuario"}
    "integration" = @{color="06B6D4"; desc="Integration"}
    "infrastructure" = @{color="78716C"; desc="Infrastructure"}
    "documentation" = @{color="14B8A6"; desc="Documentation"}
}

foreach ($label in $labels.Keys) {
    $color = $labels[$label].color
    $desc = $labels[$label].desc

    Write-Host "Creating label: $label" -ForegroundColor Yellow

    gh label create $label `
        --repo $REPO `
        --color $color `
        --description $desc
}

Write-Host "Labels creados!" -ForegroundColor Green