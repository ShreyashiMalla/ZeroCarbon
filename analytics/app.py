import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="ZeroCarbon Analytics",
    layout="wide",
    page_icon="🌍",
    initial_sidebar_state="collapsed"
)

# ================= THEME & CSS =================
st.markdown("""
<style>
/* Global background and typography */
.stApp {
    background-color: #f8fafc;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide Streamlit components */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Modern Glassmorphism Header */
.hero-header {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    padding: 2.5rem 2rem;
    border-radius: 20px;
    margin-bottom: 2.5rem;
    color: white;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    position: relative;
    overflow: hidden;
}

.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(34,197,94,0.15) 0%, transparent 60%);
    z-index: 0;
}

.hero-content {
    position: relative;
    z-index: 1;
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    margin-bottom: 0.5rem;
    background: linear-gradient(to right, #ffffff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: #94a3b8;
    font-weight: 400;
}

/* KPI Cards */
.kpi-container {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2.5rem;
}

.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    flex: 1;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.kpi-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.kpi-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    font-size: 1.25rem;
}

.icon-food { background: #dcfce7; color: #16a34a; }
.icon-energy { background: #e0f2fe; color: #0284c7; }
.icon-travel { background: #fef9c3; color: #ca8a04; }
.icon-waste { background: #ffedd5; color: #ea580c; }

.kpi-title {
    color: #64748b;
    font-size: 0.95rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #0f172a;
    display: flex;
    align-items: baseline;
    gap: 0.25rem;
}

.kpi-unit {
    font-size: 1rem;
    color: #94a3b8;
    font-weight: 500;
}

/* Dashboard Sections */
.dashboard-section {
    margin-top: 3rem;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.section-title::before {
    content: '';
    display: block;
    width: 4px;
    height: 24px;
    background: #10b981;
    border-radius: 4px;
}

/* Chart Containers */
.chart-card {
    background: white;
    border-radius: 20px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    height: 100%;
}

.chart-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #334155;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #f1f5f9;
}

/* Alerts */
.status-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid #e2e8f0;
    text-align: center;
}

.status-positive {
    background: linear-gradient(to right, #ecfdf5, #d1fae5);
    border-color: #34d399;
    color: #065f46;
}

.status-negative {
    background: linear-gradient(to right, #fef2f2, #fee2e2);
    border-color: #f87171;
    color: #991b1b;
}

</style>
""", unsafe_allow_html=True)

# ================= DATA LOADING =================
# Try to construct the DB path dynamically, fallback to current dir
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
    if not os.path.exists(DB_PATH):
        DB_PATH = "db.sqlite3" # Fallback
except NameError:
    DB_PATH = "db.sqlite3"

# Setup connection
try:
    conn = sqlite3.connect(DB_PATH)
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

@st.cache_data(ttl=60) # Cache data for 60 seconds
def load_data(table_name):
    try:
        query = f"SELECT date, carbon_kg FROM {table_name}"
        df = pd.read_sql(query, conn)
        df["date"] = pd.to_datetime(df["date"]).dt.date # Keep just the date part
        return df
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return pd.DataFrame(columns=["date", "carbon_kg"])
    except Exception as e:
        st.warning(f"Error loading {table_name}: {e}")
        return pd.DataFrame(columns=["date", "carbon_kg"])

# Load all categories
df_food = load_data("dashboard_foodconsumption")
df_elec = load_data("dashboard_electricityusage")
df_travel = load_data("dashboard_travel")
df_waste = load_data("dashboard_wastesegregation")

# ================= HERO HEADER =================
st.markdown("""
<div class="hero-header">
    <div class="hero-content">
        <div class="hero-title">ZeroCarbon Analytics</div>
        <div class="hero-subtitle">Comprehensive visualization of your environmental impact and sustainability progress.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= CALCULATE METRICS =================
metrics = [
    {"id": "Food", "label": "Dietary Impact", "val": df_food["carbon_kg"].sum(), "icon": "🍽️", "css_class": "icon-food"},
    {"id": "Electricity", "label": "Energy Usage", "val": df_elec["carbon_kg"].sum(), "icon": "⚡", "css_class": "icon-energy"},
    {"id": "Travel", "label": "Transportation", "val": df_travel["carbon_kg"].sum(), "icon": "🚗", "css_class": "icon-travel"},
    {"id": "Waste", "label": "Waste & Disposal", "val": df_waste["carbon_kg"].sum(), "icon": "♻️", "css_class": "icon-waste"}
]

total_emissions = sum(m["val"] for m in metrics)

# Render KPI Cards
st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
cols = st.columns(4)

for i, m in enumerate(metrics):
    with cols[i]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <div class="kpi-icon {m['css_class']}">{m['icon']}</div>
                <div class="kpi-title">{m['label']}</div>
            </div>
            <div class="kpi-value">
                {m['val']:,.1f} <span class="kpi-unit">kg CO₂e</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================= DATA PREPARATION FOR CHARTS =================
# Combine all data for time series
df_all = pd.concat([
    df_food.assign(Category="Food"),
    df_elec.assign(Category="Electricity"),
    df_travel.assign(Category="Travel"),
    df_waste.assign(Category="Waste")
], ignore_index=True)

has_data = not df_all.empty and total_emissions > 0

# Color palette mapped to categories
color_map = {
    "Food": "#22c55e",       # Green
    "Electricity": "#3b82f6", # Blue
    "Travel": "#f59e0b",      # Amber
    "Waste": "#f97316"        # Orange
}

if not has_data:
    st.info("No emission data found. Start logging activities to see your analytics dashboard.")
    st.stop()

# ================= VISUALIZATIONS ROW 1 =================
st.markdown('<div class="dashboard-section"><div class="section-title">Emissions Breakdown</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-header">Distribution by Source</div>', unsafe_allow_html=True)
    
    # Create donut chart using Plotly
    labels = [m["id"] for m in metrics if m["val"] > 0]
    values = [m["val"] for m in metrics if m["val"] > 0]
    colors = [color_map[l] for l in labels]
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.6,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        textposition='outside'
    )])
    
    fig_donut.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(text=f'<b>{total_emissions:,.0f}</b><br>kg Total', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-header">Aggregate Totals</div>', unsafe_allow_html=True)
    
    # Create horizontal bar chart
    df_bar = pd.DataFrame({"Category": labels, "Value": values}).sort_values(by="Value", ascending=True)
    
    fig_bar = px.bar(
        df_bar, 
        x="Value", 
        y="Category", 
        orientation='h',
        color="Category",
        color_discrete_map=color_map,
        text=df_bar["Value"].apply(lambda x: f"{x:,.1f} kg")
    )
    
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(
        showlegend=False,
        margin=dict(t=10, b=30, l=10, r=50),
        height=300,
        xaxis_title="kg CO₂e",
        yaxis_title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
        yaxis=dict(showgrid=False)
    )
    
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ================= VISUALIZATIONS ROW 2 =================
st.markdown('<div class="dashboard-section"><div class="section-title">Longitudinal Analysis</div></div>', unsafe_allow_html=True)

# Group data by date and category
df_timeline = df_all.groupby(['date', 'Category'])['carbon_kg'].sum().reset_index()
# Sort by date
df_timeline = df_timeline.sort_values('date')

st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="chart-header">Cumulative Emissions Over Time</div>', unsafe_allow_html=True)

if len(df_timeline['date'].unique()) > 1:
    # Create an area chart
    fig_area = px.area(
        df_timeline, 
        x="date", 
        y="carbon_kg", 
        color="Category",
        color_discrete_map=color_map,
        line_shape='spline' # Smooth curves
    )
    
    fig_area.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=350,
        xaxis_title=None,
        yaxis_title="Daily Emissions (kg CO₂e)",
        legend_title="Category",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("Not enough temporal data to render trends. Continue logging daily activities.")

st.markdown('</div>', unsafe_allow_html=True)


# ================= PROGRESS SECTION =================
st.markdown('<div class="dashboard-section"><div class="section-title">Performance Review</div></div>', unsafe_allow_html=True)

daily_totals = df_all.groupby("date")["carbon_kg"].sum().sort_index()

if len(daily_totals) > 1:
    first_day = daily_totals.iloc[0]
    last_day = daily_totals.iloc[-1]
    
    if first_day > 0:
        pct_change = ((last_day - first_day) / first_day) * 100
        
        if pct_change < 0:
            css_class = "status-positive"
            icon = "🎉"
            msg = f"Excellent! Your daily emissions have decreased by {abs(pct_change):.1f}% since you started."
        else:
            css_class = "status-negative"
            icon = "⚠️"
            msg = f"Attention needed: Your daily emissions have increased by {pct_change:.1f}% since you started."
            
        st.markdown(f"""
        <div class="status-card {css_class}">
            <h3 style="margin:0 0 10px 0; font-size: 1.5rem;">{icon} Performance Update</h3>
            <p style="margin:0; font-size: 1.1rem; opacity: 0.9;">{msg}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Initial baseline data is zero. Add more logs to calculate progress.")
else:
    st.markdown("""
    <div class="status-card" style="background: #f8fafc;">
        <h3 style="margin:0 0 10px 0; color: #64748b;">📊 Building Your Profile</h3>
        <p style="margin:0; color: #94a3b8;">Log data over multiple days to unlock performance insights and reduction metrics.</p>
    </div>
    """, unsafe_allow_html=True)

# Close connection at the very end
try:
    conn.close()
except:
    pass