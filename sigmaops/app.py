"""SigmaOps ERP — Main Entry Point."""
import sys
import os

# ── Fix working directory for Streamlit Cloud ─────────────────────────────────
_app_dir = os.path.dirname(os.path.abspath(__file__))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)
os.chdir(_app_dir)

import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime

from modules.db import init_db
from modules import seed
from modules.theme import inject_css, get_theme, THEME_OPTS, LABEL_TO_KEY, KEY_TO_LABEL

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

# ── Theme state — initialize once (Forced Light Mode for Enterprise Feel) ────
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

# ── Google Fonts ──────────────────────────────────────────────────────────────
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
    '&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

# ── Inject theme CSS variables (:root block) ──────────────────────────────────
inject_css()

# ── Full component CSS (Enterprise SaaS Upgrade) ──────────────────────────────
st.markdown("""<style>
/* ── Global reset & Enterprise Typography ───────────────── */
* { box-sizing: border-box; }
html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Hide default Streamlit chrome ─────────── */
#MainMenu, footer, header, [data-testid="stHeader"], [data-testid="stToolbar"], 
[data-testid="stDecoration"], .stDeployButton, [data-testid="stSidebarNav"], 
nav[data-testid="stSidebarNav"], .st-emotion-cache-1rtdyuf, .st-emotion-cache-qdbtli { 
    display: none !important; visibility: hidden !important; 
}
[data-testid="collapsedControl"] { color: var(--text) !important; }

/* ── Main block padding (Expanded Whitespace) ────────────── */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 3rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar (Clean Corporate Panel) ─────────────────────── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 1px 0 4px rgba(0,0,0,0.02) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* ── Metric cards (Tactile Widgets) ──────────────────────── */
[data-testid="stMetric"],
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    border-radius: 8px !important;
    padding: 20px 24px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--text2) !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 32px !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}

/* ── Dataframes (ERP Grade Tables) ──────────────────────── */
[data-testid="stDataFrame"],
[data-testid="stDataFrameContainer"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
.dataframe thead th {
    background: #f8fafc !important; /* Force a clean header */
    color: #475569 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    padding: 12px 16px !important;
    border-bottom: 2px solid var(--border) !important;
}
.dataframe tbody td {
    padding: 10px 16px !important;
    border-bottom: 1px solid var(--border) !important;
    font-size: 13px !important;
}

/* ── Action Buttons (Workflow Triggers) ─────────────────── */
.stButton > button {
    background: #0f172a !important; /* Deep corporate navy */
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 8px 20px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover { background: #334155 !important; transform: translateY(-1px); }

/* ── Custom Cards (Workflow & Alerts) ───────────────────── */
.sigma-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.sigma-card-critical { border-left: 4px solid #ef4444 !important; }
.sigma-card-warning  { border-left: 4px solid #f59e0b !important; }

/* ── Typography Structure ────────────────────────────────── */
.module-header {
    font-family: 'DM Sans', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}
.module-subtitle { font-size: 15px; color: var(--text2); margin-bottom: 24px; }
</style>""", unsafe_allow_html=True)

# ── Top Header Bar (Clean Sticky Nav) ─────────────────────────────────────────
now = datetime.now()
try:
    from modules.db import get_critical_alert_count
    alert_count = get_critical_alert_count()
except Exception:
    alert_count = 0

st.markdown(
    f"""<div style="background:var(--surface);border-bottom:1px solid var(--border);
    padding:16px 32px;display:flex;align-items:center;justify-content:space-between;
    margin:-8px -48px 32px -48px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
    <div style="display:flex;align-items:center;gap:12px">
        <span style="font-family:'DM Sans',sans-serif;font-size:22px;font-weight:700;
        color:#0f172a;letter-spacing:-0.5px">SigmaOps</span>
        <span style="background:#f1f5f9;color:#475569;border:1px solid #e2e8f0;
        padding:4px 10px;border-radius:6px;font-size:12px;font-weight:600">ERP ENGINE</span>
    </div>
    <div style="display:flex;align-items:center;gap:20px">
        {"<span style='background:#fef2f2;color:#ef4444;border:1px solid #fecaca;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:600;box-shadow:0 1px 2px rgba(0,0,0,0.05)'>🚨 " + str(alert_count) + " Action Required</span>" if alert_count > 0 else ""}
        <span style="color:#64748b;font-size:13px;font-weight:500">{now.strftime('%d %b %Y • %H:%M')} GST</span>
        <span style="display:flex;align-items:center;gap:6px;background:#ecfdf5;color:#059669;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;border:1px solid #a7f3d0">
            <div style="width:6px;height:6px;background:#059669;border-radius:50%"></div> SYSTEM HEALTHY
        </span>
    </div>
    </div>""",
    unsafe_allow_html=True,
)

# ── Sidebar Navigation ────────────────────────────────────────────────────────
def _on_theme_change():
    label = st.session_state.get("_theme_radio", "☀️ Light")
    st.session_state["theme"] = LABEL_TO_KEY.get(label, "light")

with st.sidebar:
    st.markdown(
        "<div style='padding:24px 16px 12px'>"
        "<div style='font-family:DM Sans,sans-serif;font-size:14px;font-weight:600;"
        "color:#64748b;text-transform:uppercase;letter-spacing:1px'>Operations</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    alert_label = f"Dashboard  🔴{alert_count}" if alert_count > 0 else "Dashboard"

    _is_light = get_theme() == "light"
    _nav_text = "#334155" if _is_light else "#e2e8f0"
    _icon_color = "#94a3b8" if _is_light else "#64748b"
    _sel_bg = "#f1f5f9" if _is_light else "#1e293b"
    _sel_color = "#0f172a" if _is_light else "#ffffff"
    _sel_border = "#e2e8f0" if _is_light else "#334155"

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
            "grid-1x2", "box-arrow-in-right", "layers", "check-circle",
            "truck", "arrow-left-right", "archive", "gear-wide",
            "bar-chart", "cpu"
        ],
        default_index=0,
        styles={
            "container": {"padding": "0px 12px", "background-color": "transparent"},
            "icon": {"color": _icon_color, "font-size": "16px"},
            "nav-link": {
                "font-size": "14px",
                "font-weight": "500",
                "font-family": "Inter, sans-serif",
                "color": _nav_text,
                "padding": "10px 16px",
                "border-radius": "8px",
                "margin": "4px 0",
            },
            "nav-link-selected": {
                "background-color": _sel_bg,
                "color": _sel_color,
                "font-weight": "600",
                "border": f"1px solid {_sel_border}",
                "box-shadow": "0 1px 2px rgba(0,0,0,0.02)"
            },
            "menu-title": {"display": "none"},
        },
    )

    # ── Theme Toggle ──────────────────────────────────────────────────────────
    st.markdown("<hr style='margin:24px 16px 12px;border-color:var(--border)'>", unsafe_allow_html=True)
    _current_label = KEY_TO_LABEL.get(st.session_state.get("theme", "light"), "☀️ Light")
    st.radio(
        "Theme",
        THEME_OPTS,
        index=THEME_OPTS.index(_current_label),
        horizontal=True,
        label_visibility="collapsed",
        key="_theme_radio",
        on_change=_on_theme_change,
    )

# ── Page Router ───────────────────────────────────────────────────────────────
def _page_key(s):
    return s.split("  🔴")[0].split(" 🔴")[0].strip()

page = _page_key(selected)

if "Dashboard" in page:
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
