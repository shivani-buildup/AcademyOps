import sqlite3
import math
from datetime import datetime

conn = sqlite3.connect("data/academyops.db")
c = conn.cursor()

print("Analytics Summary Report (Pure Python)")
print("======================================\n")

# Funnel Counts
c.execute("SELECT stage, COUNT(*) FROM leads GROUP BY stage")
stages = dict(c.fetchall())
stage_order = ['New', 'Contacted', 'Qualified', 'Demo', 'Enrolled', 'Lost']
print("Funnel Stage Counts:")
for s in stage_order:
    print(f"  {s}: {stages.get(s, 0)}")

# Source Conversion
c.execute("""
SELECT source, COUNT(*) as total, 
       SUM(CASE WHEN stage IN ('Qualified', 'Demo', 'Enrolled') THEN 1 ELSE 0 END) as converted
FROM leads
GROUP BY source
ORDER BY total DESC
""")
sources = c.fetchall()

print("\nSource Conversion Rates:")
for source, total, converted in sources:
    rate = (converted / total * 100) if total > 0 else 0
    print(f"  {source}: {converted}/{total} ({rate:.2f}%)")

# Hypothesis test
if len(sources) >= 2:
    source_A, total_A, success_A = sources[0]
    source_B, total_B, success_B = sources[1]
    
    p_A = success_A / total_A if total_A > 0 else 0
    p_B = success_B / total_B if total_B > 0 else 0
    p_pool = (success_A + success_B) / (total_A + total_B)
    
    if p_pool > 0 and p_pool < 1:
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / total_A + 1 / total_B))
        z_stat = (p_A - p_B) / se
        p_value = 2 * (1 - (1.0 + math.erf(abs(z_stat) / math.sqrt(2.0))) / 2.0)
    else:
        z_stat = 0
        p_value = 1.0
        
    alpha = 0.05
    print(f"\nHypothesis Test: {source_A} vs {source_B}")
    print(f"Null Hypothesis: The conversion rates of {source_A} and {source_B} are identical.")
    print(f"P-Value: {p_value:.4f}")
    if p_value < alpha:
        print(f"Conclusion: We REJECT the null hypothesis. There is a statistically significant difference.")
    else:
        print(f"Conclusion: We FAIL TO REJECT the null hypothesis. There is NO statistically significant difference.")
