import sqlite3
from pathlib import Path
import os

base_dir = Path(__file__).parent.parent
db_path = base_dir / "data" / "academyops.db"

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get Funnel Data
c.execute("SELECT stage, COUNT(*) FROM leads GROUP BY stage")
stages = dict(c.fetchall())
stage_order = ['New', 'Contacted', 'Qualified', 'Demo', 'Enrolled', 'Lost']
funnel_labels = stage_order
funnel_data = [stages.get(s, 0) for s in stage_order]

# Get Source Data
c.execute("""
SELECT source, COUNT(*) as total, 
       SUM(CASE WHEN stage IN ('Qualified', 'Demo', 'Enrolled') THEN 1 ELSE 0 END) as converted
FROM leads
GROUP BY source
ORDER BY total DESC
""")
sources = c.fetchall()
source_labels = [s[0] for s in sources]
source_data = [(s[2] / s[1] * 100) if s[1] > 0 else 0 for s in sources]

# Generate HTML with Chart.js
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AcademyOps Analytics Charts</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; }}
        .chart-container {{ width: 80%; margin: auto; margin-bottom: 50px; }}
    </style>
</head>
<body>
    <h1>AcademyOps: Funnel & Source Analytics</h1>
    
    <div class="chart-container">
        <h2>Lead Funnel Drop-off</h2>
        <canvas id="funnelChart"></canvas>
    </div>

    <div class="chart-container">
        <h2>Conversion Rate by Source (%)</h2>
        <canvas id="sourceChart"></canvas>
    </div>

    <script>
        // Funnel Chart
        new Chart(document.getElementById('funnelChart'), {{
            type: 'bar',
            data: {{
                labels: {funnel_labels},
                datasets: [{{
                    label: 'Number of Leads',
                    data: {funnel_data},
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{ scales: {{ y: {{ beginAtZero: true }} }} }}
        }});

        // Source Chart
        new Chart(document.getElementById('sourceChart'), {{
            type: 'bar',
            data: {{
                labels: {source_labels},
                datasets: [{{
                    label: 'Conversion Rate (%)',
                    data: {source_data},
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{ scales: {{ y: {{ beginAtZero: true }} }} }}
        }});
    </script>
</body>
</html>
"""

charts_path = base_dir / "analytics_charts.html"
with open(charts_path, "w") as f:
    f.write(html_content)

print(f"Successfully generated interactive charts at: {charts_path}")
