import pandas as pd
import sqlite3
import plotly.graph_objects as go
from datetime import datetime

def load_data():
    conn = sqlite3.connect("data/academyops.db")
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce', utc=True)
    df['updated_at'] = pd.to_datetime(df['updated_at'], format='mixed', errors='coerce', utc=True)
    return df

df = load_data()
all_sources = ["All"] + sorted(df['source'].dropna().unique().tolist())
all_stages = ["All"] + sorted(df['stage'].dropna().unique().tolist())

print(f"Sources: {all_sources}")
print(f"Stages: {all_stages}")

min_date = df['created_at'].min().date()
max_date = df['created_at'].max().date()

# Test all combinations of filters
errors = 0
for src in all_sources:
    for stg in all_stages:
        try:
            filtered_df = df.copy()
            if src != "All":
                filtered_df = filtered_df[filtered_df['source'] == src]
            if stg != "All":
                filtered_df = filtered_df[filtered_df['stage'] == stg]
                
            start_dt = pd.to_datetime(min_date)
            end_dt   = pd.to_datetime(max_date) + pd.Timedelta(days=1)
            
            if df['created_at'].dt.tz is not None:
                start_dt = start_dt.tz_localize(df['created_at'].dt.tz)
                end_dt   = end_dt.tz_localize(df['created_at'].dt.tz)
                
            filtered_df = filtered_df[(filtered_df['created_at'] >= start_dt) & (filtered_df['created_at'] < end_dt)]
            
            # KPI Calculations
            total_leads     = len(filtered_df)
            active_stages   = ['New', 'Contacted', 'Qualified', 'Demo']
            enrolled_leads  = len(filtered_df[filtered_df['stage'] == 'Enrolled'])
            active_leads    = len(filtered_df[filtered_df['stage'].isin(active_stages)])
            conversion_rate = (enrolled_leads / total_leads * 100) if total_leads > 0 else 0
            lost_leads      = len(filtered_df[filtered_df['stage'] == 'Lost'])
            
            # Test Bar chart
            stage_order  = ['New', 'Contacted', 'Qualified', 'Demo', 'Enrolled', 'Lost']
            stage_colors = ['#8b5cf6', '#6366f1', '#3b82f6', '#06b6d4', '#10b981', '#ef4444']
            funnel_counts = filtered_df['stage'].value_counts().reindex(stage_order).fillna(0).astype(int)
            
            fig_funnel = go.Figure(go.Bar(
                x=funnel_counts.index.tolist(),
                y=funnel_counts.values.tolist(),
                text=funnel_counts.values.tolist(),
            ))
            
            # Test Donut chart
            source_counts = filtered_df['source'].value_counts()
            fig_donut = go.Figure(go.Pie(
                labels=source_counts.index.tolist(),
                values=source_counts.values.tolist(),
            ))
            
            # Test Trend chart
            trend_df = filtered_df.copy()
            trend_df['date'] = trend_df['created_at'].dt.date
            daily_counts = trend_df.groupby('date').size().reset_index(name='count')
            
            # Test Recent Leads
            recent = filtered_df.sort_values('created_at', ascending=False).head(50).copy()
            recent['created_at'] = recent['created_at'].dt.strftime('%d %b %Y %H:%M')
            
        except Exception as e:
            print(f"Error for Source: {src}, Stage: {stg}")
            import traceback
            traceback.print_exc()
            errors += 1

if errors == 0:
    print("All filter combinations executed successfully without errors!")
else:
    print(f"Found {errors} errors.")
