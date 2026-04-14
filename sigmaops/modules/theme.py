"""Shared theme management — CSS variable injection.

Call inject_css() at the top of every page render() AND in app.py so the
correct :root variables are always in the DOM, regardless of navigation.
"""
import streamlit as st

# ── Public constants ──────────────────────────────────────────────────────────
THEME_OPTS  = ["🌙 Dark", "☀️ Light", "💻 System"]
LABEL_TO_KEY = {"🌙 Dark": "dark", "☀️ Light": "light", "💻 System": "system"}
KEY_TO_LABEL = {v: k for k, v in LABEL_TO_KEY.items()}

# ── CSS variable sets ─────────────────────────────────────────────────────────
_DARK_VARS = (
    "--bg:#0a0a0f;"
    "--surface:#161b22;"
    "--surface2:#21262d;"
    "--border:#30363d;"
    "--text:#e6edf3;"
    "--text2:#8b949e;"
    "--text3:#6e7681;"
    "--accent:#00d4aa;"
    "--accent-hover:#00b894;"
    "--danger:#ef4444;"
    "--warning:#f59e0b;"
    "--success:#22c55e;"
    "--sidebar:#0d1117;"
    "--shadow:0 1px 3px rgba(0,0,0,0.4),0 1px 2px rgba(0,0,0,0.3);"
)

# SAP Analytics Cloud / Salesforce enterprise light mode
_LIGHT_VARS = (
    "--bg:#f4f6f9;"
    "--surface:#ffffff;"
    "--surface2:#f0f4f8;"
    "--border:#e2e8f0;"
    "--text:#1a202c;"
    "--text2:#64748b;"
    "--text3:#94a3b8;"
    "--accent:#0066cc;"
    "--accent-hover:#0052a3;"
    "--danger:#dc2626;"
    "--warning:#d97706;"
    "--success:#16a34a;"
    "--sidebar:#ffffff;"
    "--shadow:0 1px 3px rgba(0,0,0,0.08),0 1px 2px rgba(0,0,0,0.06);"
)


def get_theme() -> str:
    """Return the active theme key: 'dark', 'light', or 'system'."""
    return st.session_state.get("theme", "dark")


def get_chart_theme() -> dict:
    """Return Plotly layout kwargs matching the active theme.

    Usage::
        fig.update_layout(**get_chart_theme(), height=250)
    """
    t = get_theme()
    if t == "light":
        return dict(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#f8fafc",
            font=dict(color="#1a202c", family="DM Sans, sans-serif"),
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(gridcolor="#e2e8f0", tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="#e2e8f0", tickfont=dict(color="#64748b")),
        )
    else:  # dark or system — default to dark
        return dict(
            paper_bgcolor="#161b22",
            plot_bgcolor="#0d1117",
            font=dict(color="#e6edf3", family="DM Sans, sans-serif"),
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
            yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
        )


def inject_css() -> None:
    """Inject :root CSS variables for the active theme.

    Must be called:
      1. In app.py (after the main component CSS block).
      2. As the very first line of every view render() function.
    """
    t = get_theme()
    if t == "dark":
        block = f":root{{{_DARK_VARS}}}"
    elif t == "light":
        block = f":root{{{_LIGHT_VARS}}}"
    else:  # system
        block = (
            f":root{{{_DARK_VARS}}}"
            f"@media(prefers-color-scheme:dark){{:root{{{_DARK_VARS}}}}}"
            f"@media(prefers-color-scheme:light){{:root{{{_LIGHT_VARS}}}}}"
        )
    st.markdown(f"<style>{block}</style>", unsafe_allow_html=True)
