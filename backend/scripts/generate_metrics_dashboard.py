"""
Generate Metrics Dashboard HTML

Reads outputs from:
  - cloc (metrics/kloc-report.csv)
  - radon cc (metrics/complejidad-ciclomatica.txt)
  - radon mi (metrics/mantenibilidad.txt)
  - flake8 (metrics/flake8-stats.txt)
  - bandit (metrics/bandit-report.html)
  - pytest-cov (metrics/coverage/index.html)
  - pytest (metrics/pytest-results.xml)

Generates: metrics/dashboard.html
"""

import os
import re
from datetime import datetime
import xml.etree.ElementTree as ET
from pathlib import Path

METRICS_DIR = Path(__file__).parent.parent / "metrics"


def safe_read(path: Path) -> str:
    if path.exists():
        return path.read_text()
    return ""


def parse_kloc() -> dict:
    data = {"backend": 0, "frontend": 0}
    csv_path = METRICS_DIR / "kloc-report.csv"
    if not csv_path.exists():
        return data
    for line in csv_path.read_text().splitlines():
        parts = line.split(",")
        if len(parts) >= 5:
            fname = parts[1].strip('"')
            code = int(parts[4]) if parts[4].isdigit() else 0
            if "backend" in fname:
                data["backend"] += code
            elif "frontend" in fname:
                data["frontend"] += code
    return data


def parse_radon_cc() -> dict:
    text = safe_read(METRICS_DIR / "complejidad-ciclomatica.txt")
    scores = re.findall(r"\((\d+)\)", text)
    if scores:
        return {
            "max": max(int(s) for s in scores),
            "avg": sum(int(s) for s in scores) / len(scores),
            "total_functions": len(scores),
        }
    return {"max": 0, "avg": 0, "total_functions": 0}


def parse_radon_mi() -> dict:
    text = safe_read(METRICS_DIR / "mantenibilidad.txt")
    scores = re.findall(r"\(([\d.]+)\)", text)
    if scores:
        nums = [float(s) for s in scores]
        return {"avg": sum(nums) / len(nums), "min": min(nums)}
    return {"avg": 100, "min": 100}


def parse_flake8() -> dict:
    text = safe_read(METRICS_DIR / "flake8-stats.txt")
    errors = 0
    for line in text.splitlines():
        if ":" in line and not line.startswith("#"):
            errors += 1
    return {"errors": errors}


def parse_pytest() -> dict:
    xml_path = METRICS_DIR / "pytest-results.xml"
    if not xml_path.exists():
        return {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    tree = ET.parse(str(xml_path))
    root = tree.getroot()
    testsuite = root.find("testsuite")
    if testsuite is not None:
        return {
            "total": int(testsuite.get("tests", 0)),
            "passed": int(testsuite.get("tests", 0)) - int(testsuite.get("failures", 0)) - int(testsuite.get("errors", 0)),
            "failed": int(testsuite.get("failures", 0)) + int(testsuite.get("errors", 0)),
            "skipped": int(testsuite.get("skipped", 0)),
        }
    return {"total": 0, "passed": 0, "failed": 0, "skipped": 0}


def parse_coverage() -> float:
    html_path = METRICS_DIR / "coverage" / "index.html"
    if not html_path.exists():
        return 0.0
    text = html_path.read_text()
    match = re.search(r"<span class='pc_cov'>([\d.]+)%</span>", text)
    if match:
        return float(match.group(1))
    match = re.search(r"data-value=\"([\d.]+)\"", text)
    if match:
        return float(match.group(1))
    return 0.0


def generate_html(metrics: dict) -> str:
    cov = metrics["coverage"]
    kloc_b = metrics["kloc"]["backend"]
    kloc_f = metrics["kloc"]["frontend"]
    cc = metrics["complexity"]
    mi = metrics["maintainability"]
    flake = metrics["flake8"]
    tests = metrics["tests"]

    cov_bar = int(cov / 10) if cov else 0
    cov_color = "green" if cov >= 80 else "orange" if cov >= 50 else "red"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard de Metricas - Diligencia Reforzada EDD</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',system-ui,sans-serif;background:#f8fafc;color:#1e293b;padding:2rem}}
h1{{font-size:1.5rem;margin-bottom:0.25rem;color:#0f172a}}
.subtitle{{color:#64748b;margin-bottom:2rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;margin-bottom:2rem}}
.card{{background:#fff;border-radius:12px;padding:1.25rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);border:1px solid #e2e8f0}}
.card h3{{font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:#64748b;margin-bottom:0.5rem}}
.card .value{{font-size:2rem;font-weight:700;color:#0f172a}}
.card .sub{{font-size:0.875rem;color:#64748b;margin-top:0.25rem}}
.badge{{display:inline-block;padding:0.25rem 0.75rem;border-radius:9999px;font-size:0.75rem;font-weight:600}}
.badge-green{{background:#dcfce7;color:#166534}}
.badge-yellow{{background:#fef9c3;color:#854d0e}}
.badge-red{{background:#fee2e2;color:#991b1b}}
.charts{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:2rem}}
.chart-card{{background:#fff;border-radius:12px;padding:1.25rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);border:1px solid #e2e8f0;min-height:300px}}
.chart-card.full{{grid-column:1/-1}}
.chart-card h3{{margin-bottom:1rem;font-size:0.875rem;color:#475569}}
table{{width:100%;border-collapse:collapse;font-size:0.875rem}}
th,td{{text-align:left;padding:0.75rem;border-bottom:1px solid #e2e8f0}}
th{{color:#64748b;font-weight:600;font-size:0.75rem;text-transform:uppercase}}
.status{{display:inline-flex;align-items:center;gap:0.375rem}}
.status-dot{{width:8px;height:8px;border-radius:50%;display:inline-block}}
.footer{{text-align:center;padding:2rem;color:#94a3b8;font-size:0.75rem}}
</style>
</head>
<body>
<h1>📊 Dashboard de Metricas</h1>
<p class="subtitle">Sistema de Diligencia Reforzada EDD — Panama AML/CFT</p>

<div class="grid">
  <div class="card">
    <h3>Cobertura de Pruebas</h3>
    <div class="value" style="color:{cov_color}">{cov:.1f}%</div>
    <div class="sub">pytest + pytest-cov</div>
  </div>
  <div class="card">
    <h3>KLOC Backend</h3>
    <div class="value">{kloc_b}</div>
    <div class="sub">Python (FastAPI)</div>
  </div>
  <div class="card">
    <h3>KLOC Frontend</h3>
    <div class="value">{kloc_f}</div>
    <div class="sub">TypeScript (React)</div>
  </div>
  <div class="card">
    <h3>Tests</h3>
    <div class="value">{tests['total']}</div>
    <div class="sub">
      <span class="badge badge-green">{tests['passed']} passed</span>
      {f'<span class="badge badge-red">{tests["failed"]} failed</span>' if tests['failed'] else ''}
      {f'<span class="badge badge-yellow">{tests["skipped"]} skipped</span>' if tests['skipped'] else ''}
    </div>
  </div>
  <div class="card">
    <h3>Complejidad Ciclomatica</h3>
    <div class="value">{cc['max']}</div>
    <div class="sub">Max: {cc['max']} | Promedio: {cc['avg']:.1f} | {cc['total_functions']} funciones</div>
  </div>
  <div class="card">
    <h3>Mantenibilidad</h3>
    <div class="value">{mi['avg']:.0f}</div>
    <div class="sub">MI promedio | Min: {mi['min']:.0f}</div>
  </div>
  <div class="card">
    <h3>Code Smells (flake8)</h3>
    <div class="value">{flake['errors']}</div>
    <div class="sub">Incidencias detectadas</div>
  </div>
  <div class="card">
    <h3>Densidad de Defectos</h3>
    <div class="value">{tests['failed'] / max(kloc_b, 1):.2f}</div>
    <div class="sub">Defectos / KLOC</div>
  </div>
</div>

<div class="charts">
  <div class="chart-card">
    <h3>Distribucion de Cobertura</h3>
    <canvas id="coverageChart"></canvas>
  </div>
  <div class="chart-card">
    <h3>Resultados de Pruebas</h3>
    <canvas id="testsChart"></canvas>
  </div>
</div>

<table>
<thead><tr><th>Metrica</th><th>Valor</th><th>Herramienta</th><th>Estado</th></tr></thead>
<tbody>
<tr><td>Cobertura de pruebas</td><td>{cov:.1f}%</td><td>pytest-cov</td><td><span class="status"><span class="status-dot" style="background:{'#22c55e' if cov >= 80 else '#eab308' if cov >= 50 else '#ef4444'}"></span>{'Aceptable' if cov >= 80 else 'Regular' if cov >= 50 else 'Critico'}</span></td></tr>
<tr><td>Complejidad ciclomatica (max)</td><td>{cc['max']}</td><td>radon cc</td><td><span class="status"><span class="status-dot" style="background:{'#22c55e' if cc['max'] <= 15 else '#eab308' if cc['max'] <= 30 else '#ef4444'}"></span>{'Baja' if cc['max'] <= 15 else 'Moderada' if cc['max'] <= 30 else 'Alta'}</span></td></tr>
<tr><td>Mantenibilidad (promedio)</td><td>{mi['avg']:.1f}</td><td>radon mi</td><td><span class="status"><span class="status-dot" style="background:{'#22c55e' if mi['avg'] >= 80 else '#eab308' if mi['avg'] >= 50 else '#ef4444'}"></span>{'Buena' if mi['avg'] >= 80 else 'Regular' if mi['avg'] >= 50 else 'Mala'}</span></td></tr>
<tr><td>Code smells</td><td>{flake['errors']}</td><td>flake8</td><td><span class="status"><span class="status-dot" style="background:{'#22c55e' if flake['errors'] < 10 else '#eab308' if flake['errors'] < 50 else '#ef4444'}"></span>{'Bajo' if flake['errors'] < 10 else 'Medio' if flake['errors'] < 50 else 'Alto'}</span></td></tr>
<tr><td>Pruebas totales</td><td>{tests['total']} ({tests['passed']} ok, {tests['failed']} fail)</td><td>pytest</td><td><span class="status"><span class="status-dot" style="background:{'#22c55e' if tests['failed'] == 0 else '#ef4444'}"></span>{'Pasando' if tests['failed'] == 0 else 'Fallando'}</span></td></tr>
</tbody>
</table>

<div class="footer">
Generado automaticamente por generate_metrics_dashboard.py — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>

<script>
new Chart(document.getElementById('coverageChart'), {{
  type: 'doughnut',
  data: {{
    labels: ['Cubierto', 'No cubierto'],
    datasets: [{{data: [{cov}, {100 - cov}], backgroundColor: ['#22c55e', '#e2e8f0']}}]
  }}
}});
new Chart(document.getElementById('testsChart'), {{
  type: 'bar',
  data: {{
    labels: ['Passed', 'Failed', 'Skipped'],
    datasets: [{{data: [{tests['passed']}, {tests['failed']}, {tests['skipped']}], backgroundColor: ['#22c55e', '#ef4444', '#eab308']}}]
  }}
}});
</script>
</body>
</html>"""


def main():
    metrics = {
        "kloc": parse_kloc(),
        "complexity": parse_radon_cc(),
        "maintainability": parse_radon_mi(),
        "flake8": parse_flake8(),
        "tests": parse_pytest(),
        "coverage": parse_coverage(),
    }

    from datetime import datetime

    html = generate_html(metrics)
    output_path = METRICS_DIR / "dashboard.html"
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Dashboard generated: {output_path}")
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
