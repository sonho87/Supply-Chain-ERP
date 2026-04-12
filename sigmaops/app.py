"""SigmaOps ERP — Main Entry Point."""
import streamlit as st
from streamlit_option_menu import option_menu

from modules.db import init_db
from modules import seed

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SigmaOps ERP",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize DB + Seed ─────────────────────────────────────────────────────
init_db()
seed.run_seed()

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
    --bg: #0d1117;
    --surface: #161b22;
    --surface2: #21262d;
    --border: #30363d;
    --accent: #00d4aa;
    --danger: #ef4444;
    --warning: #f59e0b;
    --success: #22c55e;
    --text: #e6edf3;
    --text2: #8b949e;
}
.stApp { background-color: var(--bg) !important; color: var(--text) !important; }
[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid var(--border);
}
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid var(--accent) !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 16px;
}
.dataframe thead th {
    background: var(--surface2) !important;
    color: var(--accent) !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
.stButton > button:hover { background: #00b894 !important; }
.stButton > button[kind="secondary"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
.stAlert { background: var(--surface) !important; border-radius: 8px !important; }
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 8px;
}
.stTabs [data-baseweb="tab"] { color: var(--text2) !important; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; }
.sigma-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.sigma-card-critical { border-left: 4px solid var(--danger) !important; }
.sigma-card-warning { border-left: 4px solid var(--warning) !important; }
.sigma-card-success { border-left: 4px solid var(--success) !important; }
.badge-critical {
    background: rgba(239,68,68,0.15);
    color: #ef4444;
    border: 1px solid rgba(239,68,68,0.3);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
}
div[data-testid="stDataFrame"] { background: var(--surface) !important; }
div[data-testid="stDataFrameContainer"] { background: var(--surface) !important; }
.stSelectbox > div, .stMultiSelect > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}
input, textarea {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}
.stProgress > div > div {
    background-color: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Alert Badge Count ─────────────────────────────────────────────────────────
try:
    from modules.db import get_critical_alert_count
    alert_count = get_critical_alert_count()
except Exception:
    alert_count = 0

alert_badge = f" 🔴{alert_count}" if alert_count > 0 else ""

# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:16px 0 8px'>"
        "<div style='font-size:24px;font-weight:800;color:#00d4aa'>⚙️ SigmaOps</div>"
        "<div style='font-size:11px;color:#8b949e;margin-top:2px'>Six Sigma Warehouse ERP</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.divider()

    selected = option_menu(
        menu_title=None,
        options=[
            f"Dashboard{alert_badge}",
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
            "grid-3x3",
            "check-circle",
            "truck",
            "graph-down",
            "skull",
            "gear",
            "bar-chart-line",
            "robot",
        ],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "#0d1117"},
            "icon": {"color": "#8b949e", "font-size": "14px"},
            "nav-link": {
                "font-size": "13px",
                "color": "#e6edf3",
                "padding": "8px 12px",
                "border-radius": "6px",
                "margin": "2px 0",
            },
            "nav-link-selected": {
                "background-color": "rgba(0,212,170,0.15)",
                "color": "#00d4aa",
                "font-weight": "600",
            },
        },
    )

    st.divider()
    st.markdown(
        "<div style='font-size:10px;color:#8b949e;text-align:center;padding:8px'>"
        "SigmaOps ERP v1.0<br>Six Sigma Warehouse Intelligence<br>Built for Gulf Operations"
        "</div>",
        unsafe_allow_html=True
    )

# ── Page Router ───────────────────────────────────────────────────────────────
# Normalize selected (strip alert badge)
page_key = selected.split(" 🔴")[0].strip()

if page_key == f"Dashboard{alert_badge}".split(" 🔴")[0] or "Dashboard" in page_key:
    from pages.dashboard import render
    render()

elif page_key == "GRN / Goods Inward":
    from pages.grn import render
    render()

elif page_key == "Bin Locations":
    from pages.bin_location import render
    render()

elif page_key == "Picking Errors":
    from pages.picking import render
    render()

elif page_key == "Dispatch":
    from pages.dispatch import render
    render()

elif page_key == "Inventory Mismatch":
    from pages.inventory import render
    render()

elif page_key == "Dead Stock":
    from pages.dead_stock import render
    render()

elif page_key == "DMAIC Engine":
    from pages.dmaic import render
    render()

elif page_key == "KPI Command Center":
    from pages.kpi_center import render
    render()

elif page_key == "AI Assistant":
    from pages.ai_assistant import render
    render()
