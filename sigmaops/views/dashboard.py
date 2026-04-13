"""Dashboard — Main Overview Page."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.db import (
    get_kpi_snapshots, get_latest_kpi, get_yesterday_kpi,
    get_alerts, resolve_alert,
)
from modules.kpi import (
    calc_picking_accuracy_delta, calc_inventory_accuracy_delta,
    calc_grn_error_delta, calc_dispatch_tat_delta, calc_dead_stock_delta,
    format_inr_crore, get_module_fix_progress,
)
from modules.theme import inject_css

_CL = dict(
    paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
    font=dict(color="#e6edf3", family="DM Sans, sans-serif", size=11),
    margin=dict(l=0, r=0, t=0, b=0),
    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
    showlegend=False,
)


def _sparkline(values, color="#00d4aa", height=55):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor="rgba(0,212,170,0.07)"
    ))
    fig.update_layout(**_CL, height=height)
    return fig


def _chart_layout(**kwargs):
    base = dict(
        paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
        font=dict(color="#e6edf3", family="DM Sans, sans-serif"),
        margin=dict(l=20, r=20, t=36, b=20),
        xaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
        legend=dict(bgcolor="#21262d", bordercolor="#30363d", borderwidth=1),
    )
    base.update(kwargs)
    return base


def render():
    inject_css()
    # ── Page title ────────────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-family:Syne,sans-serif;font-size:24px;font-weight:700;"
        "color:#e6edf3;margin-bottom:4px'>Warehouse Intelligence Dashboard</div>"
        "<div style='font-size:13px;color:#8b949e;margin-bottom:20px'>"
        "Six Sigma operational metrics — real-time view</div>",
        unsafe_allow_html=True
    )

    # ── KPI Strip ─────────────────────────────────────────────────────────────
    latest = get_latest_kpi()
    yesterday = get_yesterday_kpi()
    snaps7 = get_kpi_snapshots(7)

    def _s(f, d=0):
        return latest.get(f, d) if latest else d

    kpis = [
        ("Picking Accuracy", f"{_s('picking_accuracy_pct'):.1f}%",
         calc_picking_accuracy_delta(latest, yesterday),
         "↑ Target ≥99.5%", "picking_accuracy_pct", "#00d4aa", "success"),
        ("Inventory Accuracy", f"{_s('inventory_accuracy_pct'):.1f}%",
         calc_inventory_accuracy_delta(latest, yesterday),
         "↑ Target ≥98%", "inventory_accuracy_pct", "#3b82f6", "info"),
        ("GRN Error Rate", f"{_s('grn_error_pct'):.1f}%",
         calc_grn_error_delta(latest, yesterday),
         "↓ Target ≤2%", "grn_error_pct", "#f59e0b", "warning"),
        ("Dispatch TAT", f"{_s('dispatch_tat_hours'):.1f}h",
         calc_dispatch_tat_delta(latest, yesterday),
         "↓ Target ≤24h", "dispatch_tat_hours", "#7c3aed", "info"),
        ("Dead Stock Value", format_inr_crore(_s("dead_stock_value")),
         calc_dead_stock_delta(latest, yesterday),
         "↓ Decreasing target", "dead_stock_value", "#ef4444", "critical"),
    ]

    cols = st.columns(5)
    for i, (label, val, delta, note, field, color, sev) in enumerate(kpis):
        with cols[i]:
            arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "—")
            delta_color = "#22c55e" if delta > 0 else ("#ef4444" if delta < 0 else "#8b949e")
            # For GRN Error & Dispatch TAT, lower is better — invert colors
            if field in ("grn_error_pct", "dispatch_tat_hours", "dead_stock_value"):
                delta_color = "#ef4444" if delta > 0 else ("#22c55e" if delta < 0 else "#8b949e")
            st.markdown(
                f"<div class='kpi-card kpi-card-{sev}'>"
                f"<div style='font-size:11px;color:#8b949e;text-transform:uppercase;"
                f"letter-spacing:0.6px;margin-bottom:6px'>{label}</div>"
                f"<div style='font-family:Syne,sans-serif;font-size:26px;font-weight:700;"
                f"color:{color};line-height:1'>{val}</div>"
                f"<div style='margin-top:6px;display:flex;align-items:center;gap:6px'>"
                f"<span style='color:{delta_color};font-size:12px;font-weight:600'>"
                f"{arrow} {abs(delta):.2f}</span>"
                f"<span style='color:#8b949e;font-size:11px'>{note}</span>"
                f"</div></div>",
                unsafe_allow_html=True
            )
            if not snaps7.empty and field in snaps7.columns:
                st.plotly_chart(
                    _sparkline(snaps7[field].tolist(), color),
                    width='stretch',
                    config={"displayModeBar": False},
                    key=f"spark_{i}"
                )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.divider()

    # ── DMAIC Phase Summary ────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-family:Syne,sans-serif;font-size:16px;font-weight:600;"
        "color:#e6edf3;margin-bottom:12px'>DMAIC Phase Progress</div>",
        unsafe_allow_html=True
    )
    from modules.db import get_all_dmaic_projects
    dmaic_df = get_all_dmaic_projects()
    phases = ["define", "measure", "analyze", "improve", "control"]
    phase_colors = {
        "define": "#8b949e", "measure": "#3b82f6",
        "analyze": "#f59e0b", "improve": "#7c3aed", "control": "#22c55e"
    }
    d_cols = st.columns(5)
    for i, phase in enumerate(phases):
        with d_cols[i]:
            count = len(dmaic_df[dmaic_df["current_phase"] == phase]) if not dmaic_df.empty else 0
            past = len(dmaic_df[dmaic_df.apply(
                lambda r: phases.index(r["current_phase"]) >= i if not dmaic_df.empty else False,
                axis=1
            )]) if not dmaic_df.empty else 0
            pct = int(past / max(1, len(dmaic_df)) * 100)
            c = phase_colors[phase]
            st.markdown(
                f"<div style='background:#161b22;border:1px solid #30363d;border-top:3px solid {c};"
                f"border-radius:8px;padding:12px;text-align:center'>"
                f"<div style='font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:{c}'>"
                f"{phase[0].upper()}</div>"
                f"<div style='font-size:10px;color:#8b949e;text-transform:uppercase;margin:2px 0'>"
                f"{phase}</div>"
                f"<div style='font-size:12px;color:#e6edf3'>{count} project{'s' if count!=1 else ''}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            st.progress(pct / 100)

    st.divider()

    # ── 6 Module Status Cards ──────────────────────────────────────────────────
    st.markdown(
        "<div style='font-family:Syne,sans-serif;font-size:16px;font-weight:600;"
        "color:#e6edf3;margin-bottom:12px'>Module Health Status</div>",
        unsafe_allow_html=True
    )
    modules = [
        ("grn",       "📦 GRN / Goods Inward",  "grn"),
        ("bin",       "🗂️ Bin Locations",        "bin"),
        ("picking",   "✅ Picking",              "picking"),
        ("dispatch",  "🚛 Dispatch",             "dispatch"),
        ("inventory", "📉 Inventory",            "inventory"),
        ("deadstock", "💀 Dead Stock",           "deadstock"),
    ]
    from modules.db import get_alerts as _ga
    all_alerts = _ga(resolved=False, severity="critical", limit=50)

    for row_idx in range(0, 6, 3):
        m_cols = st.columns(3)
        for j in range(3):
            mod_key, mod_label, mod_fix = modules[row_idx + j]
            with m_cols[j]:
                mod_alerts = (
                    all_alerts[all_alerts["module"] == mod_key]
                    if not all_alerts.empty else pd.DataFrame()
                )
                crit = len(mod_alerts)
                top_alert = (
                    mod_alerts.iloc[0]["title"]
                    if not mod_alerts.empty else "No critical alerts"
                )
                fix = get_module_fix_progress(mod_fix)
                border = "#ef4444" if crit > 0 else "#22c55e"
                badge_bg = "rgba(239,68,68,0.12)" if crit > 0 else "rgba(34,197,94,0.12)"
                badge_col = "#ef4444" if crit > 0 else "#22c55e"
                badge_txt = f"🔴 {crit} Critical" if crit > 0 else "🟢 Clean"
                st.markdown(
                    f"<div style='background:#161b22;border:1px solid #30363d;"
                    f"border-left:3px solid {border};border-radius:10px;padding:14px 16px;"
                    f"margin-bottom:4px'>"
                    f"<div style='font-weight:600;font-size:14px;margin-bottom:6px'>{mod_label}</div>"
                    f"<div style='margin-bottom:6px'>"
                    f"<span style='background:{badge_bg};color:{badge_col};"
                    f"padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600'>"
                    f"{badge_txt}</span></div>"
                    f"<div style='color:#8b949e;font-size:12px;margin-bottom:8px'>"
                    f"{top_alert[:58]}{'…' if len(top_alert)>58 else ''}</div>"
                    f"<div style='font-size:11px;color:#8b949e'>"
                    f"{fix['done']}/{fix['total']} fixes</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.progress(fix["pct"] / 100)

    st.divider()

    # ── Activity + Critical Alerts ────────────────────────────────────────────
    col_feed, col_alerts = st.columns([6, 4])

    with col_feed:
        st.markdown(
            "<div style='font-family:Syne,sans-serif;font-size:16px;font-weight:600;"
            "color:#e6edf3;margin-bottom:12px'>Recent Activity</div>",
            unsafe_allow_html=True
        )
        activity = get_alerts(limit=18)
        if not activity.empty:
            dot = {"critical": "#ef4444", "warning": "#f59e0b", "info": "#22c55e"}
            for _, row in activity.iterrows():
                dc = dot.get(row["severity"], "#8b949e")
                st.markdown(
                    f"<div style='padding:6px 0;border-bottom:1px solid #21262d;"
                    f"display:flex;align-items:center;gap:8px'>"
                    f"<span style='color:{dc};font-size:9px'>●</span>"
                    f"<span style='background:#21262d;color:#8b949e;padding:1px 6px;"
                    f"border-radius:4px;font-size:10px;flex-shrink:0'>"
                    f"{str(row['module']).upper()}</span>"
                    f"<span style='font-size:12px;color:#c9d1d9;flex:1'>{row['title']}</span>"
                    f"<span style='color:#8b949e;font-size:10px;flex-shrink:0'>"
                    f"{str(row['created_at'])[:16]}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    with col_alerts:
        st.markdown(
            "<div style='font-family:Syne,sans-serif;font-size:16px;font-weight:600;"
            "color:#ef4444;margin-bottom:12px'>🚨 Unresolved Critical Alerts</div>",
            unsafe_allow_html=True
        )
        from modules.db import get_alerts as _get_crit
        crit_df = _get_crit(resolved=False, severity="critical", limit=8)
        if crit_df.empty:
            st.success("No critical alerts — all clear.")
        else:
            for _, row in crit_df.iterrows():
                st.markdown(
                    f"<div style='background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);"
                    f"border-left:3px solid #ef4444;border-radius:8px;padding:10px 12px;"
                    f"margin-bottom:8px'>"
                    f"<div style='font-weight:600;font-size:12px;color:#ef4444;margin-bottom:3px'>"
                    f"{row['title']}</div>"
                    f"<div style='color:#8b949e;font-size:11px'>{row['description'][:80]}…</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                if st.button("✓ Resolve", key=f"res_{row['id']}"):
                    resolve_alert(row["id"])
                    st.rerun()

    st.divider()

    # ── Bottom Charts ─────────────────────────────────────────────────────────
    snaps14 = get_kpi_snapshots(14)
    bc1, bc2 = st.columns(2)

    with bc1:
        st.markdown("**GRN Error Rate — Last 14 Days**")
        if not snaps14.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=snaps14["snapshot_date"], y=snaps14["grn_error_pct"],
                marker_color="#ef4444", name="GRN Error %"
            ))
            fig.add_hline(y=2.0, line_dash="dash", line_color="#22c55e",
                          annotation_text="Target 2%", annotation_font_color="#22c55e")
            fig.update_layout(**_chart_layout(height=220))
            st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    with bc2:
        st.markdown("**Inventory vs Picking Accuracy — Last 14 Days**")
        if not snaps14.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=snaps14["snapshot_date"], y=snaps14["inventory_accuracy_pct"],
                mode="lines", name="Inventory", line=dict(color="#3b82f6", width=2.5)
            ))
            fig2.add_trace(go.Scatter(
                x=snaps14["snapshot_date"], y=snaps14["picking_accuracy_pct"],
                mode="lines", name="Picking", line=dict(color="#00d4aa", width=2.5)
            ))
            fig2.update_layout(**_chart_layout(height=220))
            st.plotly_chart(fig2, width='stretch', config={"displayModeBar": False})
