import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configure Streamlit page
st.set_page_config(page_title="AcademyOps Dashboard", page_icon="📊", layout="wide")
st.title("AcademyOps Operations Dashboard")

# 1. Load Data
@st.cache_data(ttl=60) # Cache data for 60 seconds
def load_data():
    conn = sqlite3.connect("data/academyops.db")
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    
    # Parse dates
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

if df.empty:
    st.warning("No leads found in the database. Please add some leads first.")
    st.stop()

# 2. Filters
st.sidebar.header("Filters")
all_sources = ["All"] + sorted(df['source'].dropna().unique().tolist())
selected_source = st.sidebar.selectbox("Lead Source", all_sources)

# Date filter
min_date = df['created_at'].min().date()
max_date = df['created_at'].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
filtered_df = df.copy()

if selected_source != "All":
    filtered_df = filtered_df[filtered_df['source'] == selected_source]

if len(date_range) == 2:
    start_date, end_date = date_range
    # convert to datetime for comparison
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered_df = filtered_df[(filtered_df['created_at'] >= start_dt) & (filtered_df['created_at'] <= end_dt)]

# 3. KPI Cards
st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3)

total_leads = len(filtered_df)
active_stages = ['New', 'Contacted', 'Qualified', 'Demo']
success_stages = ['Qualified', 'Demo', 'Enrolled']

active_leads = len(filtered_df[filtered_df['stage'].isin(active_stages)])
converted_leads = len(filtered_df[filtered_df['stage'].isin(success_stages)])
conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0

col1.metric("Total Leads", f"{total_leads}")
col2.metric("Conversion Rate", f"{conversion_rate:.1f}%")
col3.metric("Active Pipeline", f"{active_leads}")

st.markdown("---")

# 4. Funnel Chart
st.subheader("Pipeline Funnel")
stage_order = ['New', 'Contacted', 'Qualified', 'Demo', 'Enrolled', 'Lost']
funnel_counts = filtered_df['stage'].value_counts().reindex(stage_order).fillna(0)
funnel_df = pd.DataFrame({'Stage': funnel_counts.index, 'Count': funnel_counts.values})

st.bar_chart(funnel_df.set_index('Stage'), height=300)

st.markdown("---")

# 5. Recent Leads Table
st.subheader("Recent Leads")
recent_leads = filtered_df.sort_values(by='created_at', ascending=False).head(50)
display_cols = ['name', 'phone', 'source', 'stage', 'created_at']
st.dataframe(recent_leads[display_cols].reset_index(drop=True), use_container_width=True)
