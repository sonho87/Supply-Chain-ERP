"""Dashboard — Main Overview Page."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from modules.db import (
    get_kpi_snapshots, get_latest_kpi, get_yesterday_kpi,
    get_alerts, resolve_alert, get_critical_alert_count,
)
from modules.kpi import (
    calc_picking_accuracy_delta, calc_inventory_accuracy_delta,
    calc_grn_error_delta, calc_dispatch_tat_delta, calc_dead_stock_delta,
    format_inr_crore, get_module_fix_progress,
)

CHART_LAYOUT = dict(
    paper_bgcolor="#161b22", plot_bgcolor="#161b22",
    font=dict(color="#e6edf3", family="sans-serif", size=11),
    margin=dict(l=0, r=0, t=0, b=0),
    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
    showlegend=False,
)


def sparkline(values, color="#00d4aa", height=60):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=f"rgba(0,212,170,0.08)"
    ))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(height=height)
    return fig


def render():
    # ── Section A: Header ────────────────────────────────────────────────────
    col_title, col_live = st.columns([3, 1])
    with col_title:
        st.markdown("## SigmaOps Warehouse Intelligence")
        st.markdown("<span style='color:#8b949e'>Real-time Six Sigma Operations Dashboard</span>",
                    unsafe_allow_html=True)
    with col_live:
        st.markdown(
            f"<div style='text-align:right;padding-top:20px'>"
            f"<span style='color:#8b949e;font-size:13px'>{datetime.now().strftime('%d %b %Y  %H:%M')}</span>"
            f"&nbsp;&nbsp;<span style='background:#22c55e;color:#000;padding:3px 10px;"
            f"border-radius:12px;font-size:12px;font-weight:600'>● LIVE</span></div>",
            unsafe_allow_html=True
        )

    st.divider()

    # ── Section B: KPI Strip ─────────────────────────────────────────────────
    latest = get_latest_kpi()
    yesterday = get_yesterday_kpi()
    snapshots = get_kpi_snapshots(7)

    def safe(field, default=0):
        return latest.get(field, default) if latest else default

    kpi_cols = st.columns(5)
    kpi_defs = [
        ("Picking Accuracy", f"{safe('picking_accuracy_pct'):.1f}%",
         calc_picking_accuracy_delta(latest, yesterday), "picking_accuracy_pct", "#00d4aa"),
        ("Inventory Accuracy", f"{safe('inventory_accuracy_pct'):.1f}%",
         calc_inventory_accuracy_delta(latest, yesterday), "inventory_accuracy_pct", "#3b82f6"),
        ("GRN Error Rate", f"{safe('grn_error_pct'):.1f}%",
         calc_grn_error_delta(latest, yesterday), "grn_error_pct", "#f59e0b"),
        ("Dispatch TAT", f"{safe('dispatch_tat_hours'):.1f} hrs",
         calc_dispatch_tat_delta(latest, yesterday), "dispatch_tat_hours", "#7c3aed"),
        ("Dead Stock", format_inr_crore(safe("dead_stock_value")),
         calc_dead_stock_delta(latest, yesterday), "dead_stock_value", "#ef4444"),
    ]

    for i, (label, value, delta, field, color) in enumerate(kpi_defs):
        with kpi_cols[i]:
            st.metric(label, value, f"{delta:+.2f}")
            if not snapshots.empty and field in snapshots.columns:
                vals = snapshots[field].tolist()
                st.plotly_chart(sparkline(vals, color), use_container_width=True,
                                config={"displayModeBar": False}, key=f"spark_{i}")

    st.divider()

    # ── Section C: DMAIC Phase Summary ───────────────────────────────────────
    st.markdown("#### DMAIC Phase Summary")
    from modules.db import get_all_dmaic_projects
    dmaic_df = get_all_dmaic_projects()

    phase_order = ["define", "measure", "analyze", "improve", "control"]
    phase_colors = {
        "define": "#8b949e", "measure": "#3b82f6", "analyze": "#f59e0b",
        "improve": "#7c3aed", "control": "#22c55e"
    }
    d_cols = st.columns(5)
    for i, phase in enumerate(phase_order):
        with d_cols[i]:
            count = len(dmaic_df[dmaic_df["current_phase"] == phase]) if not dmaic_df.empty else 0
            past_count = 0
            if not dmaic_df.empty:
                for _, row in dmaic_df.iterrows():
                    if phase_order.index(row["current_phase"]) >= phase_order.index(phase):
                        past_count += 1
            pct = int(past_count / max(1, len(dmaic_df)) * 100)
            color = phase_colors[phase]
            st.markdown(
                f"<div class='sigma-card' style='text-align:center;border-left:3px solid {color}'>"
                f"<div style='font-size:28px;font-weight:700;color:{color}'>{phase[0].upper()}</div>"
                f"<div style='font-size:11px;color:#8b949e;text-transform:uppercase'>{phase}</div>"
                f"<div style='font-size:13px;margin:4px 0'>{count} project{'s' if count != 1 else ''}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            st.progress(pct / 100)

    st.divider()

    # ── Section D: 6 Module Status Cards ────────────────────────────────────
    st.markdown("#### Module Status")
    from modules.db import get_alerts as _ga

    modules_info = [
        ("grn", "📦 GRN / Goods Inward", "grn"),
        ("bin", "🗂️ Bin Locations", "bin"),
        ("picking", "✅ Picking", "picking"),
        ("dispatch", "🚛 Dispatch", "dispatch"),
        ("inventory", "📉 Inventory", "inventory"),
        ("deadstock", "💀 Dead Stock", "deadstock"),
    ]

    for row_start in range(0, 6, 3):
        m_cols = st.columns(3)
        for j in range(3):
            idx = row_start + j
            mod_key, mod_label, mod_fix = modules_info[idx]
            with m_cols[j]:
                alerts_df = _ga(resolved=False, severity="critical", limit=5)
                mod_alerts = alerts_df[alerts_df["module"] == mod_key] if not alerts_df.empty else pd.DataFrame()
                crit_count = len(mod_alerts)
                top_alert = mod_alerts.iloc[0]["title"] if not mod_alerts.empty else "No critical alerts"
                fix_prog = get_module_fix_progress(mod_fix)
                badge_color = "#ef4444" if crit_count > 0 else "#22c55e"
                badge_text = f"🔴 {crit_count} Critical" if crit_count > 0 else "🟢 Clean"
                st.markdown(
                    f"<div class='sigma-card sigma-card-{'critical' if crit_count > 0 else 'success'}'>"
                    f"<div style='font-weight:700;font-size:15px'>{mod_label}</div>"
                    f"<div style='margin:6px 0'><span style='background:{'rgba(239,68,68,0.15)' if crit_count > 0 else 'rgba(34,197,94,0.15)'};"
                    f"color:{badge_color};padding:2px 8px;border-radius:10px;font-size:12px'>{badge_text}</span></div>"
                    f"<div style='color:#8b949e;font-size:12px;margin:4px 0'>{top_alert[:60]}{'...' if len(top_alert) > 60 else ''}</div>"
                    f"<div style='font-size:12px;color:#8b949e;margin-top:6px'>{fix_prog['done']}/{fix_prog['total']} fixes implemented</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.progress(fix_prog["pct"] / 100)

    st.divider()

    # ── Section E: Activity Feed + Critical Alerts ───────────────────────────
    col_feed, col_alerts = st.columns([65, 35])

    with col_feed:
        st.markdown("#### Recent Activity")
        activity_df = get_alerts(limit=20)
        if not activity_df.empty:
            color_map = {"critical": "#ef4444", "warning": "#f59e0b", "info": "#22c55e"}
            for _, row in activity_df.iterrows():
                dot_color = color_map.get(row["severity"], "#8b949e")
                st.markdown(
                    f"<div style='padding:6px 0;border-bottom:1px solid #21262d'>"
                    f"<span style='color:{dot_color}'>●</span> "
                    f"<span style='background:#21262d;color:#8b949e;padding:1px 6px;"
                    f"border-radius:4px;font-size:11px'>{row['module'].upper()}</span>"
                    f"&nbsp;<span style='font-size:13px'>{row['title']}</span>"
                    f"&nbsp;<span style='color:#8b949e;font-size:11px;float:right'>{str(row['created_at'])[:16]}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    with col_alerts:
        st.markdown("#### 🚨 Unresolved Critical Alerts")
        crit_df = get_alerts(resolved=False, severity="critical", limit=10)
        if crit_df.empty:
            st.success("No critical alerts — warehouse is clean.")
        else:
            for _, row in crit_df.iterrows():
                with st.container():
                    st.markdown(
                        f"<div class='sigma-card sigma-card-critical'>"
                        f"<div style='font-weight:600;font-size:13px'>{row['title']}</div>"
                        f"<div style='color:#8b949e;font-size:12px;margin-top:4px'>{row['description']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    if st.button("Resolve", key=f"res_{row['id']}"):
                        resolve_alert(row["id"])
                        st.rerun()

    st.divider()

    # ── Section F: Bottom Charts ─────────────────────────────────────────────
    chart_col1, chart_col2 = st.columns(2)
    snapshots_14 = get_kpi_snapshots(14)

    with chart_col1:
        st.markdown("##### GRN Error Rate — Last 14 Days")
        if not snapshots_14.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=snapshots_14["snapshot_date"], y=snapshots_14["grn_error_pct"],
                marker_color="#ef4444", name="GRN Error %"
            ))
            fig.add_hline(y=2.0, line_dash="dash", line_color="#22c55e",
                          annotation_text="Target 2%", annotation_font_color="#22c55e")
            fig.update_layout(
                paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                font=dict(color="#e6edf3"), margin=dict(l=20, r=20, t=30, b=20),
                height=200,
                xaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
                yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with chart_col2:
        st.markdown("##### Inventory vs Picking Accuracy — Last 14 Days")
        if not snapshots_14.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=snapshots_14["snapshot_date"], y=snapshots_14["inventory_accuracy_pct"],
                mode="lines", name="Inventory Acc %",
                line=dict(color="#3b82f6", width=2.5)
            ))
            fig2.add_trace(go.Scatter(
                x=snapshots_14["snapshot_date"], y=snapshots_14["picking_accuracy_pct"],
                mode="lines", name="Picking Acc %",
                line=dict(color="#00d4aa", width=2.5)
            ))
            fig2.update_layout(
                paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                font=dict(color="#e6edf3"), margin=dict(l=20, r=20, t=30, b=20),
                height=200,
                legend=dict(bgcolor="#21262d", bordercolor="#30363d", borderwidth=1),
                xaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
                yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
