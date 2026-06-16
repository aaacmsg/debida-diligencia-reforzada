# start.ps1 — Arranca todo el proyecto sin docker-compose
# Requisito: Docker Desktop corriendo (solo para PostgreSQL)
# Uso: .\start.ps1

$ROOT = $PSScriptRoot
$BACKEND = Join-Path $ROOT "backend"
$FRONTEND = Join-Path $ROOT "frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Diligencia Reforzada EDD — Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. PostgreSQL via Docker
Write-Host "[1/4] PostgreSQL..." -ForegroundColor Yellow
$container = docker ps -a --filter "name=diligencia-db" --format "{{.Names}}" 2>$null
if ($container -eq "diligencia-db") {
    $running = docker ps --filter "name=diligencia-db" --format "{{.Status}}" 2>$null
    if ($running -match "^Up") {
        Write-Host "  => Ya corriendo" -ForegroundColor Green
    } else {
        Write-Host "  => Iniciando contenedor existente..." -ForegroundColor Yellow
        docker start diligencia-db
    }
} else {
    Write-Host "  => Creando contenedor..." -ForegroundColor Yellow
    docker run -d --name diligencia-db `
        -e POSTGRES_USER=postgres `
        -e POSTGRES_PASSWORD=postgres `
        -e POSTGRES_DB=diligencia_db `
        -p 5432:5432 `
        postgres:15-alpine
}

Write-Host "  => Esperando que PostgreSQL este listo..." -ForegroundColor Gray
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    $check = docker exec diligencia-db pg_isready -U postgres 2>$null
    if ($check -match "accepting connections") {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 1
}
if (-not $ready) {
    Write-Host "  => ERROR: PostgreSQL no respondio" -ForegroundColor Red
    exit 1
}
Write-Host "  => Listo" -ForegroundColor Green

# 2. .env
Write-Host "[2/4] Configurando .env..." -ForegroundColor Yellow
$envFile = Join-Path $BACKEND ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $BACKEND ".env.example") $envFile
    Write-Host "  => .env creado desde .env.example" -ForegroundColor Green
} else {
    Write-Host "  => .env ya existe" -ForegroundColor Green
}

# 3. Alembic migrations
Write-Host "[3/4] Migraciones..." -ForegroundColor Yellow
Push-Location $BACKEND
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/diligencia_db"
.\venv\Scripts\python.exe -m alembic upgrade head 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  => Migraciones aplicadas" -ForegroundColor Green
} else {
    Write-Host "  => ERROR en migraciones" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# 4. Backend + Frontend
Write-Host "[4/4] Iniciando servidores..." -ForegroundColor Yellow

# Backend (nueva ventana)
$backendCmd = "cd '$BACKEND'; .\venv\Scripts\Activate.ps1; `$env:DATABASE_URL='postgresql://postgres:postgres@localhost:5432/diligencia_db'; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Write-Host "  => Backend iniciado (http://localhost:8000)" -ForegroundColor Green

# Frontend (nueva ventana)
$frontendCmd = "cd '$FRONTEND'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
Write-Host "  => Frontend iniciado (http://localhost:3000)" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Servidores corriendo!" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Login:    admin / admin123" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para detener: cierra las ventanas de PowerShell"
Write-Host "o ejecuta: docker stop diligencia-db"
