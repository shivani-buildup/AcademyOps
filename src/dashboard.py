import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
from datetime import datetime

# Configure Streamlit page
st.set_page_config(page_title="AcademyOps Dashboard", page_icon="📊", layout="wide")

# Custom CSS for Premium Design
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main Title Styling */
    h1 {
        background: -webkit-linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 30px;
    }
    
    /* KPI Metric Cards (Glassmorphism) */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(78, 205, 196, 0.2);
        border: 1px solid rgba(78, 205, 196, 0.5);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 3rem !important;
        background: -webkit-linear-gradient(45deg, #4ECDC4, #556270);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Subheaders */
    h3 {
        color: #e0e0e0;
        font-weight: 400;
        letter-spacing: 1px;
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

# 4. Funnel Chart (Premium Altair Chart)
st.subheader("Pipeline Funnel")
stage_order = ['New', 'Contacted', 'Qualified', 'Demo', 'Enrolled', 'Lost']
funnel_counts = filtered_df['stage'].value_counts().reindex(stage_order).fillna(0)
funnel_df = pd.DataFrame({'Stage': funnel_counts.index, 'Count': funnel_counts.values})

# Create a beautiful gradient bar chart using Altair
chart = alt.Chart(funnel_df).mark_bar(
    cornerRadiusTopLeft=10,
    cornerRadiusTopRight=10,
    opacity=0.8
).encode(
    x=alt.X('Stage:O', sort=stage_order, title="Pipeline Stage", axis=alt.Axis(labelAngle=0, labelFontSize=12, titleFontSize=14)),
    y=alt.Y('Count:Q', title="Number of Leads", axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    color=alt.Color('Stage:O', scale=alt.Scale(scheme='tealblues'), legend=None),
    tooltip=['Stage', 'Count']
).properties(
    height=400
).configure_view(
    strokeWidth=0
).configure_axis(
    grid=False,
    domainOpacity=0.3
)

st.altair_chart(chart, use_container_width=True)

st.markdown("---")

# 5. Recent Leads Table
st.subheader("Recent Leads")
recent_leads = filtered_df.sort_values(by='created_at', ascending=False).head(50)
display_cols = ['name', 'phone', 'source', 'stage', 'created_at']
st.dataframe(recent_leads[display_cols].reset_index(drop=True), use_container_width=True)
