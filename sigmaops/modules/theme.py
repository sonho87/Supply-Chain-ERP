"""Shared theme management — CSS variable injection.

Call inject_css() at the top of every page render() AND in app.py so the
correct :root variables are always in the DOM, regardless of navigation.
"""
import streamlit as st

# ── Public constants ──────────────────────────────────────────────────────────
THEME_OPTS  = ["🌙 Dark", "☀️ Light", "💻 System"]
LABEL_TO_KEY = {"🌙 Dark": "dark", "☀️ Light": "light", "💻 System": "system"}
KEY_TO_LABEL = {v: k for k, v in LABEL_TO_KEY.items()}

# ── CSS variable sets (exact values from spec) ────────────────────────────────
_DARK_VARS = (
    "--bg:#0a0a0f;"
    "--surface:#161b22;"
    "--surface2:#21262d;"
    "--border:#30363d;"
    "--text:#e6edf3;"
    "--text2:#8b949e;"
    "--accent:#00d4aa;"
    "--danger:#ef4444;"
    "--warning:#f59e0b;"
    "--success:#22c55e;"
    "--sidebar:#0d1117;"
)

_LIGHT_VARS = (
    "--bg:#f5f7fa;"
    "--surface:#ffffff;"
    "--surface2:#f0f2f5;"
    "--border:#d1d5db;"
    "--text:#111827;"
    "--text2:#6b7280;"
    "--accent:#00a884;"
    "--danger:#dc2626;"
    "--warning:#d97706;"
    "--success:#16a34a;"
    "--sidebar:#f0f2f5;"
)


def get_theme() -> str:
    """Return the active theme key: 'dark', 'light', or 'system'."""
    return st.session_state.get("theme", "dark")


def inject_css() -> None:
    """Inject :root CSS variables for the active theme.

    Must be called:
      1. In app.py (after the main component CSS block).
      2. As the very first line of every view render() function.

    Streamlit reruns the full script on every widget interaction, so the
    session_state["theme"] value set by the radio on_change callback is
    already correct when this function executes on the rerun.
    """
    t = get_theme()
    if t == "dark":
        block = f":root{{{_DARK_VARS}}}"
    elif t == "light":
        block = f":root{{{_LIGHT_VARS}}}"
    else:  # system — OS decides; dark is the fallback for browsers that
           # don't support prefers-color-scheme
        block = (
            f":root{{{_DARK_VARS}}}"
            f"@media(prefers-color-scheme:dark){{:root{{{_DARK_VARS}}}}}"
            f"@media(prefers-color-scheme:light){{:root{{{_LIGHT_VARS}}}}}"
        )
    st.markdown(f"<style>{block}</style>", unsafe_allow_html=True)
