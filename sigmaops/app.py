"""SigmaOps ERP — Main Entry Point."""
import sys
import os

# ── Fix working directory for Streamlit Cloud ─────────────────────────────────
# Streamlit Cloud CWD is repo root; we need sigmaops/ on the path so that
# `from modules.xxx` and `from views.xxx` resolve correctly.
_app_dir = os.path.dirname(os.path.abspath(__file__))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)
os.chdir(_app_dir)

import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime

from modules.db import init_db
from modules import seed

# ── Page Config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="SigmaOps ERP",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize DB + Seed ─────────────────────────────────────────────────────
init_db()
seed.run_seed()

# ── Full CSS Overhaul ─────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
/* ── Variables ─────────────────────────────── */
:root {
    --bg:       #0a0a0f;
    --surface:  #161b22;
    --surface2: #21262d;
    --border:   #30363d;
    --accent:   #00d4aa;
    --danger:   #ef4444;
    --warning:  #f59e0b;
    --success:  #22c55e;
    --text:     #e6edf3;
    --text2:    #8b949e;
}

/* ── Global reset ──────────────────────────── */
* { box-sizing: border-box; }

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Hide default Streamlit chrome ─────────── */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
header { visibility: hidden !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.stDeployButton { display: none !important; }
[data-testid="collapsedControl"] { color: var(--accent) !important; }

/* ── Remove top padding from main block ────── */
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ───────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
/* Hide the default page list Streamlit adds */
[data-testid="stSidebarNav"] { display: none !important; }
.st-emotion-cache-1rtdyuf { display: none !important; }
.st-emotion-cache-qdbtli  { display: none !important; }
nav[data-testid="stSidebarNav"] { display: none !important; }

/* ── Metric cards ──────────────────────────── */
[data-testid="stMetric"],
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: 3px solid var(--accent) !important;
    border-radius: 10px !important;
    padding: 16px 18px 12px !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    color: var(--text2) !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}
[data-testid="stMetricDelta"] svg { display: inline !important; }

/* ── Dataframes ────────────────────────────── */
[data-testid="stDataFrame"],
[data-testid="stDataFrameContainer"],
[data-testid="dataframe"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
.dataframe, .stDataFrame { font-size: 12px !important; }
.dataframe thead th,
thead tr th {
    background: var(--surface2) !important;
    color: var(--accent) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    padding: 8px 12px !important;
    border-bottom: 1px solid var(--border) !important;
}
.dataframe tbody tr:hover { background: rgba(0,212,170,0.04) !important; }
.dataframe tbody td {
    color: var(--text) !important;
    padding: 7px 12px !important;
    border-bottom: 1px solid rgba(48,54,61,0.5) !important;
}

/* ── Buttons ───────────────────────────────── */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 6px 16px !important;
    transition: background 0.15s ease !important;
}
.stButton > button:hover {
    background: #00b894 !important;
    border: none !important;
}
.stButton > button:focus {
    box-shadow: 0 0 0 2px rgba(0,212,170,0.4) !important;
    border: none !important;
}
.stButton > button[kind="secondary"],
.stButton > button.secondary {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* ── Form inputs ───────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
input[type="text"], input[type="number"], textarea {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,212,170,0.2) !important;
}

/* ── Selectbox / Multiselect ───────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}

/* ── Expander ──────────────────────────────── */
.streamlit-expanderHeader,
[data-testid="stExpander"] > div:first-child {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-weight: 500 !important;
}
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    background: var(--surface) !important;
}

/* ── Alerts / Info boxes ───────────────────── */
.stAlert,
[data-testid="stAlert"] {
    background: var(--surface) !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
}
.stInfo { border-left: 3px solid #3b82f6 !important; }
.stWarning { border-left: 3px solid var(--warning) !important; }
.stError { border-left: 3px solid var(--danger) !important; }
.stSuccess { border-left: 3px solid var(--success) !important; }

/* ── Progress bar ──────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--accent), #00b894) !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background: var(--surface2) !important;
    border-radius: 4px !important;
}

/* ── Tabs ──────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 8px !important;
    gap: 4px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text2) !important;
    background: transparent !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,212,170,0.15) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
}

/* ── Divider ───────────────────────────────── */
hr { border-color: var(--border) !important; margin: 16px 0 !important; }

/* ── Checkbox ──────────────────────────────── */
.stCheckbox label span { color: var(--text) !important; }

/* ── Date input ────────────────────────────── */
[data-testid="stDateInput"] input {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* ── Download button ───────────────────────── */
.stDownloadButton > button {
    background: var(--surface2) !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: rgba(0,212,170,0.1) !important;
}

/* ── Form container ────────────────────────── */
[data-testid="stForm"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 16px !important;
}

/* ── Radio buttons ─────────────────────────── */
.stRadio label span { color: var(--text) !important; }
.stRadio [data-testid="stMarkdownContainer"] { color: var(--text2) !important; }

/* ── Scrollbar ─────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text2); }

/* ── Custom component classes ──────────────── */
.sigma-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.sigma-card-critical { border-left: 4px solid var(--danger) !important; }
.sigma-card-warning  { border-left: 4px solid var(--warning) !important; }
.sigma-card-success  { border-left: 4px solid var(--success) !important; }
.sigma-card-info     { border-left: 4px solid #3b82f6 !important; }

.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: 10px;
    padding: 18px 20px 14px;
}
.kpi-card-danger  { border-top-color: var(--danger)  !important; }
.kpi-card-warning { border-top-color: var(--warning) !important; }
.kpi-card-success { border-top-color: var(--success) !important; }

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
}
.badge-critical { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.badge-warning  { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-success  { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.badge-info     { background: rgba(59,130,246,0.15); color: #3b82f6; border: 1px solid rgba(59,130,246,0.3); }
.badge-accent   { background: rgba(0,212,170,0.15);  color: #00d4aa; border: 1px solid rgba(0,212,170,0.3); }

.module-header {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 2px;
}
.module-subtitle {
    font-size: 13px;
    color: var(--text2);
    margin-bottom: 16px;
}
.problem-box {
    background: rgba(245,158,11,0.08);
    border-left: 3px solid var(--warning);
    padding: 10px 14px;
    border-radius: 6px;
    color: #f59e0b;
    font-size: 13px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── Top Header Bar ────────────────────────────────────────────────────────────
now = datetime.now()
try:
    from modules.db import get_critical_alert_count
    alert_count = get_critical_alert_count()
except Exception:
    alert_count = 0

st.markdown(
    f"""<div style="background:#0d1117;border-bottom:1px solid #30363d;
    padding:10px 24px;display:flex;align-items:center;justify-content:space-between;
    margin:-8px -24px 16px -24px;">
    <div style="display:flex;align-items:center;gap:12px">
        <span style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
        color:#00d4aa;letter-spacing:-0.5px">⚙ SigmaOps ERP</span>
        <span style="background:rgba(0,212,170,0.1);color:#00d4aa;border:1px solid rgba(0,212,170,0.3);
        padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">SIX SIGMA</span>
    </div>
    <div style="display:flex;align-items:center;gap:16px">
        {"<span style='background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.3);padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600'>🚨 " + str(alert_count) + " Critical</span>" if alert_count > 0 else ""}
        <span style="color:#8b949e;font-size:12px">{now.strftime('%a, %d %b %Y')}</span>
        <span style="color:#8b949e;font-size:12px">{now.strftime('%H:%M')} GST</span>
        <span style="background:#22c55e;color:#000;padding:3px 10px;border-radius:12px;
        font-size:11px;font-weight:700">● LIVE</span>
    </div>
    </div>""",
    unsafe_allow_html=True
)

# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='padding:16px 12px 8px'>"
        "<div style='font-family:Syne,sans-serif;font-size:18px;font-weight:800;color:#00d4aa'>"
        "⚙ SigmaOps</div>"
        "<div style='font-size:10px;color:#8b949e;margin-top:2px;letter-spacing:0.5px'>"
        "WAREHOUSE INTELLIGENCE</div>"
        "</div>",
        unsafe_allow_html=True
    )

    alert_label = f"Dashboard  🔴{alert_count}" if alert_count > 0 else "Dashboard"

    selected = option_menu(
        menu_title=None,
        options=[
            alert_label,
            "GRN / Goods Inward",
            "Bin Locations",
            "Picking Errors",
            "Dispatch",
            "Inventory Mismatch",
            "Dead Stock",
            "DMAIC Engine",
            "KPI Command Center",
            "AI Assistant",
        ],
        icons=[
            "speedometer2",
            "box-seam",
            "grid-3x3-gap",
            "check2-circle",
            "truck",
            "graph-down-arrow",
            "archive",
            "gear-wide-connected",
            "bar-chart-line-fill",
            "robot",
        ],
        default_index=0,
        styles={
            "container": {
                "padding": "4px 8px",
                "background-color": "transparent",
            },
            "icon": {"color": "#8b949e", "font-size": "14px"},
            "nav-link": {
                "font-size": "13px",
                "font-family": "DM Sans, sans-serif",
                "color": "#c9d1d9",
                "padding": "8px 12px",
                "border-radius": "6px",
                "margin": "1px 0",
                "--hover-color": "rgba(0,212,170,0.08)",
            },
            "nav-link-selected": {
                "background-color": "rgba(0,212,170,0.12)",
                "color": "#00d4aa",
                "font-weight": "600",
                "border": "1px solid rgba(0,212,170,0.2)",
            },
            "menu-title": {"display": "none"},
        },
    )

    st.markdown(
        "<div style='position:absolute;bottom:16px;left:0;right:0;text-align:center;"
        "padding:0 12px'>"
        "<div style='border-top:1px solid #30363d;padding-top:12px'>"
        "<div style='font-size:10px;color:#8b949e;line-height:1.6'>"
        "SigmaOps ERP v1.0<br>"
        "<span style='color:#00d4aa'>Built for Gulf Operations</span>"
        "</div></div></div>",
        unsafe_allow_html=True
    )

# ── Page Router ───────────────────────────────────────────────────────────────
def _page_key(s):
    """Strip alert badge from label for routing."""
    return s.split("  🔴")[0].split(" 🔴")[0].strip()

page = _page_key(selected)

if page == "Dashboard" or "Dashboard" in page:
    from views.dashboard import render; render()

elif page == "GRN / Goods Inward":
    from views.grn import render; render()

elif page == "Bin Locations":
    from views.bin_location import render; render()

elif page == "Picking Errors":
    from views.picking import render; render()

elif page == "Dispatch":
    from views.dispatch import render; render()

elif page == "Inventory Mismatch":
    from views.inventory import render; render()

elif page == "Dead Stock":
    from views.dead_stock import render; render()

elif page == "DMAIC Engine":
    from views.dmaic import render; render()

elif page == "KPI Command Center":
    from views.kpi_center import render; render()

elif page == "AI Assistant":
    from views.ai_assistant import render; render()
