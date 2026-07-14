"""Genera el dashboard HTML de metricas del proyecto (ISTQB - TMMi - TQM).

Ejecuta las herramientas (pytest-cov, radon, flake8, bandit) y produce
backend/metrics/dashboard.html con las tres dimensiones del plan de pruebas:
requerimientos, diseno y codigo/pruebas.

Uso recomendado (desde la raiz del repositorio, con la base de datos arriba,
para que corran tambien los tests de integracion y se vea el frontend):

    docker run --rm -v "%cd%":/repo -w /repo/backend \
      --network proyecto_diligencia_reforzada_default \
      -e DATABASE_URL=postgresql://postgres:postgres@db:5432/diligencia_db \
      proyecto_diligencia_reforzada-backend \
      python scripts/generate_metrics_dashboard.py

Tambien funciona localmente (cd backend && python scripts/generate_metrics_dashboard.py);
si el frontend o la base de datos no estan disponibles, el dashboard lo indica
como "N/D" en lugar de mostrar un cero enganoso.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
METRICS_DIR = BASE_DIR / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)

PYTHON = str(Path(sys.executable).resolve())

# --- Metricas de registro manual (se actualizan al cerrar cada iteracion) ---
# Requerimientos (plan-de-pruebas.md seccion 1)
REQ_COBERTURA = "20/20 casos del plan con implementacion (100%)"
REQ_VOLATILIDAD = "0 cambios de alcance tras el Parcial 2"
REQ_TRAZABILIDAD = "Controles criticos referenciados a Ley 23/254 en PRD.md"
# Diseno (evaluacion cualitativa y conteo de diagramas)
DIS_ACOPLAMIENTO = "Bajo: capas api/servicios/modelos separadas; servicios sin dependencias cruzadas"
DIS_COHESION = "Alta: un servicio por responsabilidad (riesgo, pep, pdf, datos abiertos)"
DIS_DIAGRAMAS = "2/2 diagramas alineados con el codigo (architecture.md, issue #68)"
# Codigo: defectos reales detectados y corregidos en el cierre (documento-final 3.4)
DEFECTOS_DETECTADOS = int(os.environ.get("DEFECTOS_DETECTADOS", "7"))
DEFECTOS_ABIERTOS = int(os.environ.get("DEFECTOS_ABIERTOS", "0"))


def run(cmd: list, cwd=None) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or str(BASE_DIR), timeout=300)
        return r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        return str(e)


def contar_loc(directorio: Path, extensiones: tuple) -> int:
    total = 0
    for root, _dirs, files in os.walk(str(directorio)):
        if "node_modules" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(extensiones):
                try:
                    with open(os.path.join(root, f), encoding="utf-8") as fh:
                        total += sum(1 for _ in fh)
                except Exception:
                    pass
    return total


def get_loc() -> dict:
    backend = contar_loc(BASE_DIR / "app", (".py",))
    frontend_dir = BASE_DIR.parent / "frontend" / "src"
    frontend = contar_loc(frontend_dir, (".ts", ".tsx", ".css")) if frontend_dir.exists() else None
    tests = contar_loc(BASE_DIR / "tests", (".py",))
    return {"backend": backend, "frontend": frontend, "tests": tests}


def get_complexity() -> dict:
    out = run([PYTHON, "-m", "radon", "cc", "app", "-s", "-a"])
    bloques = re.findall(r"-\s+[A-F]\s+\((\d+)\)", out)
    scores = [int(b) for b in bloques]
    avg_match = re.search(r"Average complexity: ([A-F]) \(([\d.]+)\)", out)
    peor = ""
    if scores:
        max_score = max(scores)
        for linea in out.splitlines():
            if f"({max_score})" in linea:
                peor = linea.strip().split(" ")[-3] if len(linea.split()) >= 3 else ""
                break
    return {
        "max": max(scores) if scores else 0,
        "avg": round(float(avg_match.group(2)), 2) if avg_match else 0,
        "rating": avg_match.group(1) if avg_match else "?",
        "total": len(scores),
        "peor": peor,
    }


def get_maintainability() -> dict:
    out = run([PYTHON, "-m", "radon", "mi", "app", "-s"])
    scores = [float(m) for m in re.findall(r"\(([\d.]+)\)", out)]
    if not scores:
        return {"avg": 0, "min": 0}
    return {"avg": round(sum(scores) / len(scores), 1), "min": round(min(scores), 1)}


def get_flake8() -> int:
    # Una incidencia por linea con formato ruta:linea:col: CODIGO mensaje
    out = run([PYTHON, "-m", "flake8", "app", "--max-line-length=120"])
    return len(re.findall(r"^.+?:\d+:\d+:\s", out, flags=re.MULTILINE))


def get_bandit() -> int:
    # Solo stdout: bandit escribe warnings en stderr que romperian el JSON
    try:
        r = subprocess.run([PYTHON, "-m", "bandit", "-r", "app", "-f", "json", "-q"],
                           capture_output=True, text=True, cwd=str(BASE_DIR), timeout=300)
        data = json.loads(r.stdout)
        return len(data.get("results", []))
    except Exception:
        return -1  # no se pudo medir


def get_tests_y_cobertura() -> dict:
    out = run([PYTHON, "-m", "pytest", "--cov=app", "--cov-report=term",
               "--tb=no", "--quiet", "tests/"])
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", out)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", out)) else 0
    skipped = int(m.group(1)) if (m := re.search(r"(\d+) skipped", out)) else 0
    cov_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", out)
    cobertura = float(cov_match.group(1)) if cov_match else 0.0
    return {"passed": passed, "failed": failed, "skipped": skipped,
            "total": passed + failed + skipped, "coverage": cobertura}


def fmt(valor, sufijo="") -> str:
    return "N/D" if valor is None else f"{valor}{sufijo}"


def generate_html(m: dict) -> str:
    loc = m["loc"]
    cc = m["complexity"]
    mi = m["maintainability"]
    smells = m["flake8"]
    vulns = m["bandit"]
    t = m["tests"]
    cov = t["coverage"]

    loc_total = loc["backend"] + (loc["frontend"] or 0)
    kloc_total = round(loc_total / 1000, 2)
    kloc_backend = round(loc["backend"] / 1000, 3)
    densidad_defectos = round(DEFECTOS_DETECTADOS / kloc_total, 2) if loc["frontend"] else None
    densidad_pruebas = round(t["total"] / kloc_backend, 1) if kloc_backend else 0
    tasa_exito = round(100 * t["passed"] / max(t["passed"] + t["failed"], 1), 1)

    cov_color = "#16a34a" if cov >= 60 else "#ca8a04" if cov >= 40 else "#dc2626"
    vulns_txt = "N/D" if vulns < 0 else str(vulns)
    frontend_nota = "" if loc["frontend"] is not None else \
        "<p style='color:#dc2626;font-size:0.8rem'>⚠ Frontend no disponible en este entorno: ejecutar desde el repositorio completo (ver instrucciones en el script).</p>"
    skips_nota = "" if t["skipped"] == 0 else \
        f"<p style='color:#ca8a04;font-size:0.8rem'>⚠ {t['skipped']} pruebas de integracion omitidas (base de datos no accesible desde este entorno); la cobertura mostrada es parcial.</p>"

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8">
<title>Dashboard de Metricas - Diligencia Reforzada EDD</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:Inter,system-ui,sans-serif;background:#f8fafc;color:#1e293b;padding:2rem;max-width:1100px;margin:auto}}
h1{{font-size:1.6rem;border-bottom:3px solid #3b82f6;padding-bottom:0.5rem}}
h2{{font-size:1.05rem;margin:2rem 0 0.5rem;color:#334155}}
.subtitle{{color:#64748b;margin-bottom:1.5rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin:1rem 0}}
.card{{background:#fff;border-radius:12px;padding:1.1rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);border:1px solid #e2e8f0}}
.card h3{{font-size:0.65rem;text-transform:uppercase;color:#64748b;margin-bottom:0.25rem}}
.card .value{{font-size:1.6rem;font-weight:700}}
.card .detalle{{font-size:0.75rem;color:#64748b}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1)}}
th,td{{text-align:left;padding:0.6rem 0.75rem;border-bottom:1px solid #e2e8f0;font-size:0.85rem}}
th{{color:#64748b;font-weight:600;font-size:0.72rem;text-transform:uppercase;background:#f1f5f9}}
.footer{{text-align:center;color:#94a3b8;font-size:0.75rem;margin-top:2rem;padding-top:1rem;border-top:1px solid #e2e8f0}}
</style>
</head>
<body>
<h1>Dashboard de Metricas (ISTQB - TMMi - TQM)</h1>
<p class="subtitle">Sistema de Diligencia Debida Reforzada (EDD) — {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
{frontend_nota}{skips_nota}

<div class="grid">
  <div class="card"><h3>Cobertura backend</h3><div class="value" style="color:{cov_color}">{cov:.0f}%</div><div class="detalle">pytest-cov</div></div>
  <div class="card"><h3>Pruebas</h3><div class="value">{t['passed']}/{t['total']}</div><div class="detalle">{t['failed']} fallidas, {t['skipped']} omitidas</div></div>
  <div class="card"><h3>Tasa de exito</h3><div class="value">{tasa_exito:.0f}%</div><div class="detalle">passed / (passed+failed)</div></div>
  <div class="card"><h3>Complejidad prom.</h3><div class="value">{cc['avg']} ({cc['rating']})</div><div class="detalle">max {cc['max']} en {cc['total']} bloques</div></div>
  <div class="card"><h3>Mantenibilidad</h3><div class="value">{mi['avg']:.0f}</div><div class="detalle">radon mi (min {mi['min']:.0f})</div></div>
  <div class="card"><h3>Incidencias de estilo</h3><div class="value">{smells}</div><div class="detalle">flake8</div></div>
  <div class="card"><h3>Vulnerabilidades</h3><div class="value">{vulns_txt}</div><div class="detalle">bandit</div></div>
  <div class="card"><h3>LOC producto</h3><div class="value">{loc_total:,}</div><div class="detalle">backend {loc['backend']:,} + frontend {fmt(loc['frontend'])}</div></div>
</div>

<h2>1. Metricas de requerimientos</h2>
<table>
<tr><th>Metrica</th><th>Valor</th><th>Fuente</th></tr>
<tr><td>Cobertura de requisitos</td><td>{REQ_COBERTURA}</td><td>plan-de-pruebas.md + PRD.md (registro manual)</td></tr>
<tr><td>Volatilidad</td><td>{REQ_VOLATILIDAD}</td><td>tasks.md (registro manual)</td></tr>
<tr><td>Trazabilidad legal</td><td>{REQ_TRAZABILIDAD}</td><td>PRD.md (registro manual)</td></tr>
</table>

<h2>2. Metricas de diseno</h2>
<table>
<tr><th>Metrica</th><th>Valor</th><th>Fuente</th></tr>
<tr><td>Complejidad ciclomatica (promedio)</td><td>{cc['avg']} — calificacion {cc['rating']} ({cc['total']} bloques)</td><td>radon cc</td></tr>
<tr><td>Complejidad ciclomatica (maxima)</td><td>{cc['max']}</td><td>radon cc</td></tr>
<tr><td>Mantenibilidad (promedio / minima)</td><td>{mi['avg']:.1f} / {mi['min']:.1f}</td><td>radon mi</td></tr>
<tr><td>Acoplamiento</td><td>{DIS_ACOPLAMIENTO}</td><td>evaluacion cualitativa</td></tr>
<tr><td>Cohesion</td><td>{DIS_COHESION}</td><td>evaluacion cualitativa</td></tr>
<tr><td>Diagramas actualizados</td><td>{DIS_DIAGRAMAS}</td><td>architecture.md (registro manual)</td></tr>
</table>

<h2>3. Metricas de codigo y pruebas</h2>
<table>
<tr><th>Metrica</th><th>Valor</th><th>Fuente</th></tr>
<tr><td>Cobertura de linea (backend)</td><td>{cov:.1f}%</td><td>pytest-cov</td></tr>
<tr><td>Pruebas ejecutadas</td><td>{t['total']} ({t['passed']} aprobadas, {t['failed']} fallidas, {t['skipped']} omitidas)</td><td>pytest</td></tr>
<tr><td>Densidad de pruebas (backend)</td><td>{densidad_pruebas} pruebas/KLOC</td><td>pytest / conteo LOC</td></tr>
<tr><td>Defectos detectados en el cierre</td><td>{DEFECTOS_DETECTADOS} (todos corregidos; {DEFECTOS_ABIERTOS} abiertos)</td><td>documento-final.md 3.4 (registro manual)</td></tr>
<tr><td>Densidad de defectos</td><td>{fmt(densidad_defectos, ' defectos/KLOC')}</td><td>defectos / KLOC total</td></tr>
<tr><td>Incidencias de estilo (code smells)</td><td>{smells}</td><td>flake8 (max-line-length=120)</td></tr>
<tr><td>Vulnerabilidades</td><td>{vulns_txt}</td><td>bandit</td></tr>
<tr><td>LOC producto / pruebas</td><td>{loc_total:,} ({loc['backend']:,} backend + {fmt(loc['frontend'])} frontend) / {loc['tests']:,} en tests</td><td>conteo de lineas</td></tr>
</table>

<div class="footer">
Generado por generate_metrics_dashboard.py — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
Las metricas marcadas como "registro manual" se actualizan al cierre de cada iteracion; el resto se calcula en cada ejecucion.
</div>
</body></html>"""


def main():
    print("Ejecutando herramientas de metricas...")
    metrics = {
        "loc": get_loc(),
        "complexity": get_complexity(),
        "maintainability": get_maintainability(),
        "flake8": get_flake8(),
        "bandit": get_bandit(),
        "tests": get_tests_y_cobertura(),
    }

    loc = metrics["loc"]
    t = metrics["tests"]
    print(("[OK]" if loc["frontend"] is not None else "[WARN] frontend no encontrado —"),
          f"LOC: backend={loc['backend']}, frontend={loc['frontend']}, tests={loc['tests']}")
    cc = metrics["complexity"]
    print(f"[OK] Complejidad: avg={cc['avg']} ({cc['rating']}), max={cc['max']}, bloques={cc['total']}")
    print(f"[OK] Incidencias flake8: {metrics['flake8']}")
    print(("[OK]" if metrics["bandit"] >= 0 else "[WARN]"), f"Vulnerabilidades bandit: {metrics['bandit']}")
    print(("[WARN] hay pruebas omitidas —" if t["skipped"] else "[OK]"),
          f"Tests: {t['passed']} passed, {t['failed']} failed, {t['skipped']} skipped | cobertura {t['coverage']}%")

    html = generate_html(metrics)
    output_path = METRICS_DIR / "dashboard.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"\n[OK] Dashboard generado: {output_path}")


if __name__ == "__main__":
    main()
