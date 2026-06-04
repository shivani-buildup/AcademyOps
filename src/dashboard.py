import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AcademyOps Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Main Background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #141428 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a3e 0%, #0f0c29 100%) !important;
    border-right: 1px solid rgba(139, 92, 246, 0.2);
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label,
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #c4b5fd !important;
}

/* ── Header ── */
.dashboard-header {
    background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(59,130,246,0.1) 100%);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
}
.dashboard-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.3rem 0;
}
.dashboard-header p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0;
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.kpi-card.purple::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.kpi-card.blue::before   { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.kpi-card.green::before  { background: linear-gradient(90deg, #10b981, #34d399); }
.kpi-card.orange::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }

.kpi-icon {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 40px;
    margin-bottom: 0.75rem;
}
.kpi-icon svg {
    width: 32px;
    height: 32px;
    stroke-width: 2px;
}
.kpi-value {
    font-size: 2.4rem;
    font-weight: 800;
    color: #f1f5f9;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.kpi-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.kpi-delta {
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 0.5rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    display: inline-block;
}
.kpi-delta.up   { background: rgba(16,185,129,0.15); color: #34d399; }
.kpi-delta.down { background: rgba(239,68,68,0.15);  color: #f87171; }

/* ── Section Headers ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-title svg {
    color: #a78bfa;
    stroke-width: 2.2px;
    width: 22px;
    height: 22px;
}

/* ── Chart containers ── */
.chart-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(139,92,246,0.15);
    border-radius: 16px;
    padding: 1.25rem;
    backdrop-filter: blur(5px);
}

/* ── Table styling ── */
.dataframe-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(139,92,246,0.15);
    border-radius: 16px;
    overflow: hidden;
}
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* ── Stage badges ── */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}

/* ── Divider ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.4), transparent);
    margin: 1.5rem 0;
}

/* ── Streamlit overrides ── */
.stMetric { background: transparent !important; }
div[data-testid="metric-container"] {
    background: transparent !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(139,92,246,0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
.stDateInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(139,92,246,0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* Hide the top header/bar (Deploy, MainMenu, theme settings) */
[data-testid="stHeader"] {
    display: none !important;
}
#MainMenu {
    visibility: hidden !important;
}
footer {
    visibility: hidden !important;
}
</style>
""", unsafe_allow_html=True)

SVG_ICONS = {
    "cap": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-graduation-cap"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M6 12v5c0 2 3 3 6 3s6-1 6-3v-5"/><path d="M21.5 12v6"/></svg>""",
    "users": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-users"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
    "target": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-target"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
    "bolt": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-zap"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "check": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check-circle-2"><circle cx="12" cy="12" r="10"/><path d="m9 11 3 3 6-6"/></svg>""",
    "chart-bar": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bar-chart-3"><path d="M3 3v18h18"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/></svg>""",
    "pie-chart": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-pie-chart"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>""",
    "trending": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trending-up"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polygon points="16 7 22 7 22 13"/></svg>""",
    "list": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clipboard-list"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 12h6"/><path d="M9 16h6"/><path d="M9 8h6"/></svg>""",
    "search": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:inline; vertical-align:middle; margin-right:5px;"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>""",
    "refresh": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:inline; vertical-align:middle; margin-right:5px;"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M16 3h5v5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 21H3v-5"/></svg>"""
}

# ─── Load Data ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    conn = sqlite3.connect("data/academyops.db")
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce', utc=True)
    df['updated_at'] = pd.to_datetime(df['updated_at'], format='mixed', errors='coerce', utc=True)
    return df

@st.cache_data(show_spinner=False)
def apply_filters(source, stage, start_date, end_date, tz):
    """Cache filtered results so re-selecting the same filter is instant."""
    df = load_data()
    if source != "All":
        df = df[df['source'] == source]
    if stage != "All":
        df = df[df['stage'] == stage]
    start_dt = pd.to_datetime(start_date)
    end_dt   = pd.to_datetime(end_date) + pd.Timedelta(days=1)
    if tz:
        import pytz
        tzinfo = pytz.timezone(tz) if isinstance(tz, str) else tz
        start_dt = start_dt.tz_localize(tzinfo)
        end_dt   = end_dt.tz_localize(tzinfo)
    df = df[(df['created_at'] >= start_dt) & (df['created_at'] < end_dt)]
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

if df.empty:
    st.warning("⚠️ No leads found. Please add some leads first.")
    st.stop()

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 1rem 0 1.5rem;'>
        <div style='display: flex; justify-content: center; color: #a78bfa; margin-bottom: 0.5rem;'>
            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-graduation-cap"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M6 12v5c0 2 3 3 6 3s6-1 6-3v-5"/><path d="M21.5 12v6"/></svg>
        </div>
        <div style='font-size:1.1rem; font-weight:700; color:#a78bfa;'>AcademyOps</div>
        <div style='font-size:0.75rem; color:#64748b;'>Operations Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <h3 style='color: #c4b5fd; font-size: 1.1rem; font-weight: 600; margin-top: 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;'>
        {SVG_ICONS["search"]} Filters
    </h3>
    """, unsafe_allow_html=True)
    
    all_sources = ["All"] + sorted(df['source'].dropna().unique().tolist())
    selected_source = st.selectbox("Lead Source", all_sources)

    all_stages = ["All"] + sorted(df['stage'].dropna().unique().tolist())
    selected_stage = st.selectbox("Pipeline Stage", all_stages)

    min_date = df['created_at'].min().date()
    max_date = df['created_at'].max().date()
    start_date = st.date_input("From Date", min_date)
    end_date = st.date_input("To Date", max_date)

    st.markdown("---")
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <div style='text-align:center; margin-top: 1.5rem; padding-bottom: 1rem;'>
        <div style='font-size:0.7rem; color:#475569;'>v1.0 · AcademyOps CRM</div>
    </div>
    """, unsafe_allow_html=True)

# ─── Filter Data ────────────────────────────────────────────────────────────
_tz = str(df['created_at'].dt.tz) if df['created_at'].dt.tz is not None else None
filtered_df = apply_filters(selected_source, selected_stage, start_date, end_date, _tz)

# No global stop when empty. Individual components will handle empty state.

# ─── KPI Calculations ───────────────────────────────────────────────────────
total_leads     = len(filtered_df)
active_stages   = ['New', 'Contacted', 'Qualified', 'Demo']
success_stages  = ['Qualified', 'Demo', 'Enrolled']
enrolled_leads  = len(filtered_df[filtered_df['stage'] == 'Enrolled'])
active_leads    = len(filtered_df[filtered_df['stage'].isin(active_stages)])
conversion_rate = (enrolled_leads / total_leads * 100) if total_leads > 0 else 0
lost_leads      = len(filtered_df[filtered_df['stage'] == 'Lost'])
lost_rate       = (lost_leads / total_leads * 100) if total_leads > 0 else 0

# ─── Header ─────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%d %b %Y · %H:%M")
st.markdown(f"""
<div class="dashboard-header" style="display: flex; align-items: center; gap: 1.2rem;">
    <div style="background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.3); border-radius: 12px; padding: 0.8rem; display: flex; align-items: center; justify-content: center; color: #a78bfa;">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-graduation-cap"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M6 12v5c0 2 3 3 6 3s6-1 6-3v-5"/><path d="M21.5 12v6"/></svg>
    </div>
    <div>
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AcademyOps Dashboard</h1>
        <p style="margin: 0.2rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">Real-time lead pipeline & performance insights &nbsp;·&nbsp; Last updated: {now}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI Cards ──────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card purple">
        <div class="kpi-icon">{SVG_ICONS["users"]}</div>
        <div class="kpi-value">{total_leads}</div>
        <div class="kpi-label">Total Leads</div>
        <div class="kpi-delta up">↑ All time</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card green">
        <div class="kpi-icon">{SVG_ICONS["target"]}</div>
        <div class="kpi-value">{conversion_rate:.1f}%</div>
        <div class="kpi-label">Enrolled Rate</div>
        <div class="kpi-delta {'up' if conversion_rate > 5 else 'down'}">{'↑ Good' if conversion_rate > 5 else '↓ Needs work'}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div class="kpi-icon">{SVG_ICONS["bolt"]}</div>
        <div class="kpi-value">{active_leads}</div>
        <div class="kpi-label">Active Pipeline</div>
        <div class="kpi-delta up">↑ In progress</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card orange">
        <div class="kpi-icon">{SVG_ICONS["check"]}</div>
        <div class="kpi-value">{enrolled_leads}</div>
        <div class="kpi-label">Enrolled</div>
        <div class="kpi-delta {'up' if enrolled_leads > 0 else 'down'}">{'↑ Converted' if enrolled_leads > 0 else '— None yet'}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

# ─── Charts Row ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown(f"<div class='section-title'>{SVG_ICONS['chart-bar']} Pipeline Funnel</div>", unsafe_allow_html=True)
    if filtered_df.empty:
        st.info("⚠️ No data available for the selected filters.")
    else:
        stage_order  = ['New', 'Contacted', 'Qualified', 'Demo', 'Enrolled', 'Lost']
        stage_colors = ['#8b5cf6', '#6366f1', '#3b82f6', '#06b6d4', '#10b981', '#ef4444']
        funnel_counts = filtered_df['stage'].value_counts().reindex(stage_order).fillna(0).astype(int)

        fig_funnel = go.Figure(go.Bar(
            x=funnel_counts.index.tolist(),
            y=funnel_counts.values.tolist(),
            marker=dict(
                color=stage_colors,
                line=dict(width=0),
            ),
            text=funnel_counts.values.tolist(),
            textposition='outside',
            textfont=dict(color='#e2e8f0', size=13, family='Inter'),
        ))
        fig_funnel.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#94a3b8'),
            xaxis=dict(
                showgrid=False, zeroline=False,
                tickfont=dict(color='#94a3b8', size=12),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(148,163,184,0.08)',
                zeroline=False,
                tickfont=dict(color='#94a3b8', size=11),
            ),
            margin=dict(l=10, r=10, t=20, b=10),
            height=320,
            showlegend=False,
            bargap=0.35,
        )
        st.plotly_chart(fig_funnel, use_container_width=True, key="funnel_chart")

with col_right:
    st.markdown(f"<div class='section-title'>{SVG_ICONS['pie-chart']} Source Breakdown</div>", unsafe_allow_html=True)
    if filtered_df.empty:
        st.info("⚠️ No data available for the selected filters.")
    else:
        source_counts = filtered_df['source'].value_counts()
        donut_colors  = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4']

        fig_donut = go.Figure(go.Pie(
            labels=source_counts.index.tolist(),
            values=source_counts.values.tolist(),
            hole=0.55,
            marker=dict(colors=donut_colors, line=dict(color='rgba(0,0,0,0)', width=0)),
            textfont=dict(family='Inter', size=12, color='#e2e8f0'),
            hovertemplate='<b>%{label}</b><br>%{value} leads (%{percent})<extra></extra>',
        ))
        fig_donut.add_annotation(
            text=f"<b>{total_leads}</b><br><span style='font-size:10px'>leads</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color='#e2e8f0', family='Inter'),
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#94a3b8'),
            showlegend=True,
            legend=dict(
                font=dict(color='#94a3b8', size=11),
                bgcolor='rgba(0,0,0,0)',
                x=1.02, y=0.5,
            ),
            margin=dict(l=0, r=80, t=20, b=10),
            height=320,
        )
        st.plotly_chart(fig_donut, use_container_width=True, key="donut_chart")

st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

# ─── Trend Chart ─────────────────────────────────────────────────────────────
st.markdown(f"<div class='section-title'>{SVG_ICONS['trending']} Leads Over Time</div>", unsafe_allow_html=True)

if filtered_df.empty:
    st.info("⚠️ No data available for the selected filters.")
else:
    trend_df = filtered_df.copy()
    trend_df['date'] = trend_df['created_at'].dt.date
    daily_counts = trend_df.groupby('date').size().reset_index(name='count')

    if len(daily_counts) > 1:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=daily_counts['date'],
            y=daily_counts['count'],
            mode='lines+markers',
            line=dict(color='#8b5cf6', width=2.5, shape='spline'),
            marker=dict(color='#a78bfa', size=6, line=dict(color='#1a1a3e', width=2)),
            fill='tozeroy',
            fillcolor='rgba(139,92,246,0.08)',
            hovertemplate='<b>%{x}</b><br>%{y} leads<extra></extra>',
        ))
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#94a3b8'),
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color='#94a3b8', size=11)),
            yaxis=dict(showgrid=True, gridcolor='rgba(148,163,184,0.08)', zeroline=False, tickfont=dict(color='#94a3b8', size=11)),
            margin=dict(l=10, r=10, t=10, b=10),
            height=220,
            showlegend=False,
        )
        st.plotly_chart(fig_trend, use_container_width=True, key="trend_chart")
    else:
        st.info("📅 Not enough data points to show a trend. Try widening your date range.")

st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

# ─── Recent Leads Table ──────────────────────────────────────────────────────
st.markdown(f"<div class='section-title'>{SVG_ICONS['list']} Recent Leads</div>", unsafe_allow_html=True)

if filtered_df.empty:
    st.info("⚠️ No leads found matching the selected filters.")
else:
    recent = filtered_df.sort_values('created_at', ascending=False).head(50).copy()
    recent['created_at'] = recent['created_at'].dt.strftime('%d %b %Y %H:%M')
    
    STAGE_BADGES = {
        'New':       '<span class="badge" style="background: rgba(99, 102, 241, 0.15); color: #6366f1; border: 1px solid rgba(99, 102, 241, 0.3);">New</span>',
        'Contacted': '<span class="badge" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3);">Contacted</span>',
        'Qualified': '<span class="badge" style="background: rgba(6, 182, 212, 0.15); color: #06b6d4; border: 1px solid rgba(6, 182, 212, 0.3);">Qualified</span>',
        'Demo':      '<span class="badge" style="background: rgba(139, 92, 246, 0.15); color: #8b5cf6; border: 1px solid rgba(139, 92, 246, 0.3);">Demo</span>',
        'Enrolled':  '<span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3);">Enrolled</span>',
        'Lost':      '<span class="badge" style="background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3);">Lost</span>',
    }

    def _make_row(row):
        badge_html = STAGE_BADGES.get(row['stage'], f'<span class="badge" style="background: rgba(100, 116, 139, 0.15); color: #64748b; border: 1px solid rgba(100, 116, 139, 0.3);">{row["stage"]}</span>')
        return f"<tr><td>{row['id']}</td><td>{row['name']}</td><td>{row['phone']}</td><td>{row['source']}</td><td>{badge_html}</td><td>{row['created_at']}</td></tr>"

    rows_html = "".join(recent.apply(_make_row, axis=1).tolist())

    table_html = f"""<style>
.custom-table-container {{
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.02);
    margin: 1rem 0;
}}
.custom-table {{
    width: 100%;
    border-collapse: collapse;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}}
.custom-table th {{
    position: sticky;
    top: 0;
    background: #141233;
    color: #c4b5fd;
    font-weight: 600;
    padding: 14px 16px;
    border-bottom: 1px solid rgba(139, 92, 246, 0.3);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    text-align: center !important;
    z-index: 10;
}}
.custom-table td {{
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 0.85rem;
    text-align: center !important;
}}
.custom-table tr:hover {{
    background: rgba(139, 92, 246, 0.06);
}}
.custom-table tr:last-child td {{
    border-bottom: none;
}}
.custom-table-container::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
.custom-table-container::-webkit-scrollbar-track {{
    background: rgba(255, 255, 255, 0.01);
}}
.custom-table-container::-webkit-scrollbar-thumb {{
    background: rgba(139, 92, 246, 0.3);
    border-radius: 3px;
}}
.custom-table-container::-webkit-scrollbar-thumb:hover {{
    background: rgba(139, 92, 246, 0.5);
}}
</style>
<div class="custom-table-container">
<table class="custom-table">
<thead>
<tr>
<th>ID</th>
<th>Name</th>
<th>Phone</th>
<th>Source</th>
<th>Stage</th>
<th>Created At</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</div>"""
    st.markdown(table_html, unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class='fancy-divider'></div>
<div style='text-align:center; padding: 1rem 0; color:#475569; font-size:0.78rem;'>
    AcademyOps CRM Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Plotly
</div>
""", unsafe_allow_html=True)
