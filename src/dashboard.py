import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# Configure Streamlit page
st.set_page_config(page_title="AcademyOps Dashboard", page_icon="📈", layout="wide")

# Custom CSS for Premium Design
st.markdown("""
<style>
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #3b82f6;
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
    }
    /* Headers */
    h1, h2, h3 {
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)
st.title("AcademyOps Operations Dashboard")

# 1. Load Data
@st.cache_data(ttl=60) # Cache data for 60 seconds
def load_data():
    conn = sqlite3.connect("data/academyops.db")
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    
    # Parse dates with mixed formats and normalize to UTC
    df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce', utc=True)
    df['updated_at'] = pd.to_datetime(df['updated_at'], format='mixed', errors='coerce', utc=True)
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
start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

# Apply filters
filtered_df = df.copy()

if selected_source != "All":
    filtered_df = filtered_df[filtered_df['source'] == selected_source]

if True:
    # convert to datetime for comparison, localizing to UTC if needed
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)
    
    # If the dataframe column is tz-aware, we need to tz-localize our filters
    if df['created_at'].dt.tz is not None:
        start_dt = start_dt.tz_localize(df['created_at'].dt.tz)
        end_dt = end_dt.tz_localize(df['created_at'].dt.tz)
        
    filtered_df = filtered_df[(filtered_df['created_at'] >= start_dt) & (filtered_df['created_at'] < end_dt)]

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

fig = px.funnel(funnel_df, x='Count', y='Stage', title='',
                color_discrete_sequence=['#3b82f6'])
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)', 
    font=dict(color='#f8fafc'),
    margin=dict(l=20, r=20, t=20, b=20)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 5. Recent Leads Table
st.subheader("Recent Leads")
recent_leads = filtered_df.sort_values(by='created_at', ascending=False).head(50)
display_cols = ['id', 'name', 'phone', 'source', 'stage', 'created_at']

# Center align text using Pandas Styler
styled_df = recent_leads[display_cols].set_index('id').style.set_properties(**{'text-align': 'center'})

st.dataframe(styled_df, use_container_width=True)
