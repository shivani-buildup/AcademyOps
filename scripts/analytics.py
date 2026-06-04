import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import math
from pathlib import Path
import os

# Set up paths
base_dir = Path(__file__).parent.parent
db_path = base_dir / "data" / "academyops.db"
artifacts_dir = Path(os.environ.get("APPDATA_DIR", ".")) / "artifacts" # Fallback if not set
if not artifacts_dir.exists():
    artifacts_dir = Path(".") # Fallback to current dir if we can't find it

print(f"Connecting to database at {db_path}")
conn = sqlite3.connect(db_path)

# 1. Load Data
df = pd.read_sql_query("SELECT * FROM leads", conn)
print(f"Loaded {len(df)} leads.")

if len(df) == 0:
    print("No leads in the database. Exiting analytics.")
    exit()

# Parse dates
df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce', utc=True)
df['updated_at'] = pd.to_datetime(df['updated_at'], format='mixed', errors='coerce', utc=True)

# Compute time in stage (simplified as updated_at - created_at)
df['time_in_pipeline'] = (df['updated_at'] - df['created_at']).dt.total_seconds() / 3600.0 # in hours

# 2. Funnel Analytics
stage_order = ['New', 'Contacted', 'Qualified', 'Demo', 'Enrolled', 'Lost']
# Count leads in each stage
stage_counts = df['stage'].value_counts().reindex(stage_order).fillna(0)
print("\n--- Funnel Stage Counts ---")
print(stage_counts)

# Generate Funnel Chart
plt.figure(figsize=(10, 6))
stage_counts.drop('Lost', errors='ignore').plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Lead Funnel Drop-off')
plt.xlabel('Pipeline Stage')
plt.ylabel('Number of Leads')
plt.xticks(rotation=45)
plt.tight_layout()
funnel_chart_path = base_dir / "funnel_chart.png"
plt.savefig(funnel_chart_path)
print(f"Saved funnel chart to {funnel_chart_path}")

# 3. Source Performance & Conversion
print("\n--- Average Time in Pipeline (Hours) ---")
print(f"{df['time_in_pipeline'].mean():.2f} hours")

print("\n--- Source Performance ---")
# Define 'conversion' as reaching 'Qualified', 'Demo', or 'Enrolled'
success_stages = ['Qualified', 'Demo', 'Enrolled']
df['converted'] = df['stage'].isin(success_stages).astype(int)

source_stats = df.groupby('source').agg(
    total_leads=('id', 'count'),
    conversions=('converted', 'sum')
)
source_stats['conversion_rate'] = source_stats['conversions'] / source_stats['total_leads']
source_stats = source_stats.sort_values(by='total_leads', ascending=False)
print(source_stats)

# Generate Source Comparison Chart
plt.figure(figsize=(10, 6))
source_stats['conversion_rate'].plot(kind='bar', color='lightgreen', edgecolor='black')
plt.title('Conversion Rate by Source')
plt.xlabel('Source')
plt.ylabel('Conversion Rate')
plt.xticks(rotation=45)
plt.tight_layout()
source_chart_path = base_dir / "source_comparison.png"
plt.savefig(source_chart_path)
print(f"Saved source comparison chart to {source_chart_path}")

# 4. Hypothesis Testing
# Compare top 2 sources by volume
top_sources = source_stats.head(2).index.tolist()
if len(top_sources) >= 2:
    source_A = top_sources[0]
    source_B = top_sources[1]
    
    success_A = source_stats.loc[source_A, 'conversions']
    total_A = source_stats.loc[source_A, 'total_leads']
    success_B = source_stats.loc[source_B, 'conversions']
    total_B = source_stats.loc[source_B, 'total_leads']
    
    print(f"\n--- Statistical Test: {source_A} vs {source_B} ---")
    
    # 2-proportion Z-test manually since scipy is unavailable
    p_A = success_A / total_A if total_A > 0 else 0
    p_B = success_B / total_B if total_B > 0 else 0
    p_pool = (success_A + success_B) / (total_A + total_B)
    
    if p_pool > 0 and p_pool < 1:
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / total_A + 1 / total_B))
        z_stat = (p_A - p_B) / se
        # p-value from z-score
        p_value = 2 * (1 - (1.0 + math.erf(abs(z_stat) / math.sqrt(2.0))) / 2.0)
    else:
        z_stat = 0
        p_value = 1.0
        
    alpha = 0.05
    print(f"Z-Test Statistic: {z_stat:.4f}")
    print(f"P-Value: {p_value:.4f}")
    
    with open(base_dir / "analytics_report.txt", "w") as f:
        f.write("Analytics Summary Report\n")
        f.write("========================\n\n")
        f.write(f"Total Leads: {len(df)}\n")
        f.write(f"Average Time in Pipeline: {df['time_in_pipeline'].mean():.2f} hours\n\n")
        
        f.write("Source Conversion Rates:\n")
        f.write(source_stats.to_string())
        f.write("\n\n")
        
        f.write(f"Hypothesis Test: {source_A} vs {source_B}\n")
        f.write(f"Null Hypothesis: The conversion rates of {source_A} and {source_B} are identical.\n")
        f.write(f"P-Value: {p_value:.4f}\n")
        if p_value < alpha:
            msg = f"Conclusion: We REJECT the null hypothesis. There is a statistically significant difference in conversion rates between {source_A} and {source_B} at the {alpha} significance level."
        else:
            msg = f"Conclusion: We FAIL TO REJECT the null hypothesis. There is NO statistically significant difference in conversion rates between {source_A} and {source_B} at the {alpha} significance level."
        f.write(msg + "\n")
        print(msg)
        print("Wrote summary to analytics_report.txt")
else:
    print("Not enough sources for hypothesis test.")
