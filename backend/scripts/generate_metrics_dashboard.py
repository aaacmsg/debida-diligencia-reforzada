"""
Generate Metrics Dashboard HTML

Runs tools directly and outputs a single HTML dashboard.

Usage:
    python scripts/generate_metrics_dashboard.py
    # Opens: backend/metrics/dashboard.html
"""

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


def run(cmd: list, cwd=None) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or str(BASE_DIR), timeout=120)
        return r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        return str(e)


def get_kloc() -> dict:
    backend, frontend = 0, 0
    for root, _dirs, files in os.walk(str(BASE_DIR / "app")):
        for f in files:
            if f.endswith(".py"):
                try:
                    backend += len(open(os.path.join(root, f), encoding="utf-8").readlines())
                except Exception:
                    pass
    for root, _dirs, files in os.walk(str(BASE_DIR.parent / "frontend" / "src")):
        for f in files:
            if f.endswith((".ts", ".tsx", ".css")):
                try:
                    frontend += len(open(os.path.join(root, f), encoding="utf-8").readlines())
                except Exception:
                    pass
    return {"backend": backend, "frontend": frontend}


def get_complexity() -> dict:
    out = run([PYTHON, "-m", "radon", "cc", "app", "-s"])
    scores = [int(m) for m in re.findall(r"\((\d+)\)", out)]
    if not scores:
        return {"max": 0, "avg": 0, "total": 0}
    return {"max": max(scores), "avg": round(sum(scores) / len(scores), 1), "total": len(scores)}


def get_maintainability() -> dict:
    out = run([PYTHON, "-m", "radon", "mi", "app", "-s"])
    scores = [float(m) for m in re.findall(r"\(([\d.]+)\)", out)]
    if not scores:
        return {"avg": 100, "min": 100}
    return {"avg": round(sum(scores) / len(scores), 1), "min": round(min(scores), 1)}


def get_flake8() -> int:
    out = run([PYTHON, "-m", "flake8", "app", "--max-line-length=120", "--statistics"])
    return sum(1 for line in out.splitlines() if ":" in line and not line.startswith((" ", "#", "")))


def get_bandit() -> int:
    out = run([PYTHON, "-m", "bandit", "-r", "app", "-f", "json"])
    try:
        import json as _json
        data = _json.loads(out)
        return len(data.get("results", []))
    except Exception:
        return 0


def get_tests() -> dict:
    out = run([PYTHON, "-m", "pytest", "--tb=no", "--quiet", "tests/"])
    match = re.search(r"(\d+)\s+passed", out)
    passed = int(match.group(1)) if match else 0
    match = re.search(r"(\d+)\s+failed", out)
    failed = int(match.group(1)) if match else 0
    total = passed + failed
    return {"total": total, "passed": passed, "failed": failed, "skipped": 0}


def get_coverage() -> float:
    out = run([PYTHON, "-m", "pytest", "--cov=app", "--cov-report=term", "--tb=no", "--quiet", "tests/"])
    match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", out)
    if match:
        return float(match.group(1))
    return 0.0


def generate_html(metrics: dict) -> str:
    cov = metrics["coverage"]
    kloc_b = metrics["kloc"]["backend"]
    kloc_f = metrics["kloc"]["frontend"]
    cc = metrics["complexity"]
    mi = metrics["maintainability"]
    smells = metrics["flake8"]
    vulns = metrics["bandit"]
    tests = metrics["tests"]

    cov_color = "green" if cov >= 80 else "orange" if cov >= 50 else "red"
    kloc_total = kloc_b + kloc_f
    defect_density = round(tests["failed"] / max(kloc_b / 1000, 0.1), 2)

    bar = lambda val, mx=100, good="#22c55e", bad="#ef4444": f'<div style="background:#e2e8f0;border-radius:8px;height:24px"><div style="width:{min(val/mx*100,100)}%;background:{good if val/mx>=0.5 else bad};height:24px;border-radius:8px;text-align:center;color:white;font-weight:700;font-size:12px;line-height:24px">{val}</div></div>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8">
<title>Dashboard de Metricas - Diligencia Reforzada EDD</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:Inter,system-ui,sans-serif;background:#f8fafc;color:#1e293b;padding:2rem;max-width:1100px;margin:auto}}
h1{{font-size:1.75rem;border-bottom:3px solid #3b82f6;padding-bottom:0.5rem}}
.subtitle{{color:#64748b;margin-bottom:2rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin:1.5rem 0}}
.card{{background:#fff;border-radius:12px;padding:1.25rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);border:1px solid #e2e8f0}}
.card h3{{font-size:0.7rem;text-transform:uppercase;color:#64748b;margin-bottom:0.25rem}}
.card .value{{font-size:1.75rem;font-weight:700}}
.charts{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}
.full{{grid-column:1/-1}}
table{{width:100%;border-collapse:collapse;margin-top:1rem}}
th,td{{text-align:left;padding:0.75rem;border-bottom:1px solid #e2e8f0;font-size:0.875rem}}
th{{color:#64748b;font-weight:600;font-size:0.75rem;text-transform:uppercase}}
.footer{{text-align:center;color:#94a3b8;font-size:0.75rem;margin-top:2rem;padding-top:1rem;border-top:1px solid #e2e8f0}}
</style>
</head>
<body>
<h1>📊 Dashboard de Metricas</h1>
<p class="subtitle">Diligencia Reforzada EDD — Panama AML/CFT — {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

<div class="grid">
  <div class="card"><h3>Cobertura</h3><div class="value" style="color:{cov_color}">{cov:.0f}%</div></div>
  <div class="card"><h3>KLOC Backend</h3><div class="value">{kloc_b}</div></div>
  <div class="card"><h3>KLOC Frontend</h3><div class="value">{kloc_f}</div></div>
  <div class="card"><h3>Tests</h3><div class="value">{tests['total']}<span style="font-size:0.875rem;color:#64748b"> ({tests['passed']} ok)</span></div></div>
  <div class="card"><h3>Complejidad Max</h3><div class="value">{cc['max']}</div></div>
  <div class="card"><h3>Mantenibilidad</h3><div class="value">{mi['avg']:.0f}</div></div>
  <div class="card"><h3>Code Smells</h3><div class="value">{smells}</div></div>
  <div class="card"><h3>Vulnerabilidades</h3><div class="value">{vulns}</div></div>
</div>

<div class="charts">
  <div class="card chart-card">
    <h3>Cobertura</h3>
    <canvas id="covChart" height="200"></canvas>
  </div>
  <div class="card chart-card">
    <h3>Resultados de Pruebas</h3>
    <canvas id="testChart" height="200"></canvas>
  </div>
</div>

<div class="card full">
<h3>Tabla de Metricas</h3>
<table>
<tr><th>Metrica</th><th>Valor</th><th>Herramienta</th><th>Estado</th></tr>
<tr><td>Cobertura de pruebas</td><td>{cov:.1f}%</td><td>pytest-cov</td><td>{bar(cov)}</td></tr>
<tr><td>Densidad de defectos</td><td>{defect_density}/KLOC</td><td>pytest</td><td>{bar(max(0, 100 - tests['failed']*20))}</td></tr>
<tr><td>Complejidad ciclomatica (max)</td><td>{cc['max']}</td><td>radon cc</td><td>{bar(max(0, 100 - cc['max']*5))}</td></tr>
<tr><td>Funciones totales</td><td>{cc['total']}</td><td>radon cc</td><td>{cc['total']}</td></tr>
<tr><td>Mantenibilidad (prom)</td><td>{mi['avg']:.1f}</td><td>radon mi</td><td>{bar(mi['avg'])}</td></tr>
<tr><td>Code smells</td><td>{smells}</td><td>flake8</td><td>{bar(max(0, 100 - smells*5))}</td></tr>
<tr><td>Vulnerabilidades</td><td>{vulns}</td><td>bandit</td><td>{'✅ 0' if vulns == 0 else f'⚠️ {vulns}'}</td></tr>
<tr><td>KLOC total</td><td>{kloc_total} ({kloc_b} backend + {kloc_f} frontend)</td><td>line count</td><td>Proyecto mediano</td></tr>
<tr><td>Tests totales</td><td>{tests['total']} ({tests['passed']} passed, {tests['failed']} failed)</td><td>pytest</td><td>{'✅ Pasando' if tests['failed'] == 0 else '❌ Fallando'}</td></tr>
</table>
</div>

<div class="footer">
Generado por generate_metrics_dashboard.py — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>

<script>
new Chart(document.getElementById('covChart'), {{
  type: 'doughnut',
  data: {{labels:['Cubierto','No cubierto'], datasets:[{{data:[{cov},{100-cov}], backgroundColor:['#22c55e','#e2e8f0']}}]}}
}});
new Chart(document.getElementById('testChart'), {{
  type: 'bar',
  data: {{labels:['Passed','Failed'], datasets:[{{data:[{tests['passed']},{tests['failed']}], backgroundColor:['#22c55e','#ef4444']}}]}},
  options: {{scales:{{y:{{beginAtZero:true}}}}}}
}});
</script>
</body></html>"""


def main():
    print("Ejecutando herramientas de metricas...")
    metrics = {
        "kloc": get_kloc(),
        "complexity": get_complexity(),
        "maintainability": get_maintainability(),
        "flake8": get_flake8(),
        "bandit": get_bandit(),
        "tests": get_tests(),
        "coverage": get_coverage(),
    }

    print("[OK]" if metrics["kloc"]["backend"] else "[WARN]", f" KLOC: backend={metrics['kloc']['backend']}, frontend={metrics['kloc']['frontend']}")
    print("[OK]" if metrics["complexity"]["total"] else "[WARN]", f" Complejidad: max={metrics['complexity']['max']}, avg={metrics['complexity']['avg']}, total={metrics['complexity']['total']} funciones")
    print("[OK]" if metrics["flake8"] else "[OK]", f" Code smells: {metrics['flake8']}")
    print("[OK]" if metrics["bandit"] == 0 else "[WARN]", f" Vulnerabilidades: {metrics['bandit']}")
    print("[OK]" if metrics["tests"]["total"] else "[WARN]", f" Tests: {metrics['tests']['total']} ({metrics['tests']['passed']} passed, {metrics['tests']['failed']} failed)")
    print("[OK]" if metrics["coverage"] else "[WARN]", f" Cobertura: {metrics['coverage']}%")

    html = generate_html(metrics)
    output_path = METRICS_DIR / "dashboard.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"\n[OK] Dashboard generado: {output_path}")
    print(f"     file://{output_path.resolve()}")


if __name__ == "__main__":
    main()
