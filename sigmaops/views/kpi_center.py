"""KPI Command Center."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

from modules.db import (
    get_kpi_snapshots, get_latest_kpi,
    get_alerts, resolve_alert,
    get_picker_performance, get_all_grn, get_all_inventory,
    get_delay_by_carrier,
)
from modules.kpi import format_inr_crore
from modules.theme import inject_css, get_chart_theme


def kpi_trend_chart(snap_df, field, color, target, target_label, height=200):
    fig = go.Figure()
    if not snap_df.empty and field in snap_df.columns:
        fig.add_trace(go.Scatter(
            x=snap_df["snapshot_date"], y=snap_df[field],
            mode="lines", name=field,
            line=dict(color=color, width=2.5),
            fill="tozeroy", fillcolor=f"rgba(0,212,170,0.06)"
        ))
        fig.add_hline(y=target, line_dash="dash", line_color="#22c55e",
                      annotation_text=target_label, annotation_font_color="#22c55e")
    fig.update_layout(**get_chart_theme(), height=height, showlegend=False)
    return fig


def render():
    inject_css()
    st.markdown(
        "<div class='module-header'>📈 KPI Command Center</div>"
        "<div class='module-subtitle'>"
        "If you're not tracking these, you're not managing a warehouse — you're firefighting."
        "</div>",
        unsafe_allow_html=True
    )

    date_cols = st.columns([3, 1])
    with date_cols[1]:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            key="kpi_date_range"
        )

    snap_df = get_kpi_snapshots(30)
    latest = get_latest_kpi()

    st.divider()

    # ── KPI 1: Picking Accuracy ───────────────────────────────────────────────
    with st.expander("📊 KPI 1: Picking Accuracy %", expanded=True):
        k1c1, k1c2, k1c3 = st.columns(3)
        val = latest.get("picking_accuracy_pct", 0) if latest else 0
        color = "#22c55e" if val >= 99.5 else ("#f59e0b" if val >= 97 else "#ef4444")
        k1c1.markdown(
            f"<div style='border-left:3px solid {color};padding:12px;background:var(--surface);border-radius:8px'>"
            f"<div style='color:var(--text2);font-size:12px'>Current Value</div>"
            f"<div style='font-size:32px;font-weight:700;color:{color}'>{val:.1f}%</div></div>",
            unsafe_allow_html=True
        )
        k1c2.metric("vs Target", f"{val - 99.5:+.2f}pp", "Target: ≥ 99.5%")
        trend_dir = "↑ Improving" if not snap_df.empty and snap_df["picking_accuracy_pct"].iloc[-1] > snap_df["picking_accuracy_pct"].iloc[0] else "↓ Declining"
        k1c3.markdown(
            f"<div style='border-left:3px solid #3b82f6;padding:12px;background:var(--surface);border-radius:8px'>"
            f"<div style='color:var(--text2);font-size:12px'>Formula</div>"
            f"<div style='color:#3b82f6;font-size:12px'>Correct Picks / Total Picks × 100</div>"
            f"<div style='font-size:16px;margin-top:8px'>{trend_dir}</div></div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(kpi_trend_chart(snap_df, "picking_accuracy_pct", "#00d4aa", 99.5, "Target 99.5%"),
                        width='stretch', config={"displayModeBar": False})
        st.markdown("**Drill-down: Accuracy by Picker (Last 7 Days)**")
        perf_df = get_picker_performance()
        if not perf_df.empty:
            st.dataframe(perf_df.head(10), width='stretch', hide_index=True)

    # ── KPI 2: Inventory Accuracy ─────────────────────────────────────────────
    with st.expander("📊 KPI 2: Inventory Accuracy %", expanded=True):
        k2c1, k2c2, k2c3 = st.columns(3)
        val2 = latest.get("inventory_accuracy_pct", 0) if latest else 0
        color2 = "#22c55e" if val2 >= 98 else ("#f59e0b" if val2 >= 90 else "#ef4444")
        k2c1.markdown(
            f"<div style='border-left:3px solid {color2};padding:12px;background:var(--surface);border-radius:8px'>"
            f"<div style='color:var(--text2);font-size:12px'>Current Value</div>"
            f"<div style='font-size:32px;font-weight:700;color:{color2}'>{val2:.1f}%</div></div>",
            unsafe_allow_html=True
        )
        k2c2.metric("vs Target", f"{val2 - 98.0:+.2f}pp", "Target: ≥ 98%")
        k2c3.markdown(
            "<div style='border-left:3px solid #3b82f6;padding:12px;background:var(--surface);border-radius:8px'>"
            "<div style='color:var(--text2);font-size:12px'>Formula</div>"
            "<div style='color:#3b82f6;font-size:12px'>(Matched SKUs / Total SKUs) × 100</div></div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(kpi_trend_chart(snap_df, "inventory_accuracy_pct", "#3b82f6", 98.0, "Target 98%"),
                        width='stretch', config={"displayModeBar": False})
        st.markdown("**Drill-down: Accuracy by Category**")
        inv_df = get_all_inventory()
        if not inv_df.empty:
            cat_acc = inv_df.groupby("category").apply(
                lambda x: round(len(x[x["status"] == "matched"]) / len(x) * 100, 1)
            ).reset_index(name="accuracy_pct")
            st.dataframe(cat_acc, width='stretch', hide_index=True)

    # ── KPI 3: GRN Error % ────────────────────────────────────────────────────
    with st.expander("📊 KPI 3: GRN Error %", expanded=True):
        k3c1, k3c2, k3c3 = st.columns(3)
        val3 = latest.get("grn_error_pct", 0) if latest else 0
        color3 = "#22c55e" if val3 <= 2 else ("#f59e0b" if val3 <= 5 else "#ef4444")
        k3c1.markdown(
            f"<div style='border-left:3px solid {color3};padding:12px;background:var(--surface);border-radius:8px'>"
            f"<div style='color:var(--text2);font-size:12px'>Current Value</div>"
            f"<div style='font-size:32px;font-weight:700;color:{color3}'>{val3:.1f}%</div></div>",
            unsafe_allow_html=True
        )
        k3c2.metric("vs Target", f"{val3 - 2.0:+.2f}pp", "Target: ≤ 2%")
        k3c3.markdown(
            "<div style='border-left:3px solid #3b82f6;padding:12px;background:var(--surface);border-radius:8px'>"
            "<div style='color:var(--text2);font-size:12px'>Formula</div>"
            "<div style='color:#3b82f6;font-size:12px'>(Erroneous GRNs / Total GRNs) × 100</div></div>",
            unsafe_allow_html=True
        )
        if not snap_df.empty:
            fig_grn = go.Figure()
            fig_grn.add_trace(go.Bar(x=snap_df["snapshot_date"], y=snap_df["grn_error_pct"],
                                      marker_color="#ef4444", name="GRN Error %"))
            fig_grn.add_hline(y=2.0, line_dash="dash", line_color="#22c55e",
                               annotation_text="Target 2%")
            fig_grn.update_layout(**get_chart_theme(), height=200)
            st.plotly_chart(fig_grn, width='stretch', config={"displayModeBar": False})

        st.markdown("**Drill-down: Error Rate by Vendor**")
        grn_df = get_all_grn()
        if not grn_df.empty:
            vendor_err = grn_df.groupby("vendor").apply(
                lambda x: round(len(x[x["status"].isin(["flagged", "rejected"])]) / len(x) * 100, 1)
            ).reset_index(name="error_pct").sort_values("error_pct", ascending=False)
            st.dataframe(vendor_err, width='stretch', hide_index=True)

    # ── KPI 4: Dispatch TAT ───────────────────────────────────────────────────
    with st.expander("📊 KPI 4: Dispatch TAT (hours)", expanded=True):
        k4c1, k4c2, k4c3 = st.columns(3)
        val4 = latest.get("dispatch_tat_hours", 0) if latest else 0
        color4 = "#22c55e" if val4 <= 24 else ("#f59e0b" if val4 <= 30 else "#ef4444")
        k4c1.markdown(
            f"<div style='border-left:3px solid {color4};padding:12px;background:var(--surface);border-radius:8px'>"
            f"<div style='color:var(--text2);font-size:12px'>Current Value</div>"
            f"<div style='font-size:32px;font-weight:700;color:{color4}'>{val4:.1f} hrs</div></div>",
            unsafe_allow_html=True
        )
        k4c2.metric("vs Target", f"{val4 - 24.0:+.1f}h", "Target: ≤ 24 hrs")
        k4c3.markdown(
            "<div style='border-left:3px solid #3b82f6;padding:12px;background:var(--surface);border-radius:8px'>"
            "<div style='color:var(--text2);font-size:12px'>Formula</div>"
            "<div style='color:#3b82f6;font-size:12px'>Avg(dispatched_at - order_release_time)</div></div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(kpi_trend_chart(snap_df, "dispatch_tat_hours", "#7c3aed", 24.0, "Target 24h"),
                        width='stretch', config={"displayModeBar": False})
        st.markdown("**Drill-down: TAT by Carrier**")
        carrier_df = get_delay_by_carrier()
        if not carrier_df.empty:
            st.dataframe(carrier_df, width='stretch', hide_index=True)

    # ── KPI 5: Dead Stock Value ───────────────────────────────────────────────
    with st.expander("📊 KPI 5: Dead Stock Value (₹)", expanded=True):
        k5c1, k5c2, k5c3 = st.columns(3)
        val5 = latest.get("dead_stock_value", 0) if latest else 0
        k5c1.markdown(
            f"<div style='border-left:3px solid #ef4444;padding:12px;background:var(--surface);border-radius:8px'>"
            f"<div style='color:var(--text2);font-size:12px'>Current Value</div>"
            f"<div style='font-size:28px;font-weight:700;color:#ef4444'>{format_inr_crore(val5)}</div></div>",
            unsafe_allow_html=True
        )
        k5c2.markdown(
            "<div style='padding:12px;background:var(--surface);border-radius:8px'>"
            "<div style='color:var(--text2);font-size:12px'>Target</div>"
            "<div style='color:#22c55e;font-size:14px'>Decreasing trend month-on-month</div></div>",
            unsafe_allow_html=True
        )
        k5c3.markdown(
            "<div style='border-left:3px solid #3b82f6;padding:12px;background:var(--surface);border-radius:8px'>"
            "<div style='color:var(--text2);font-size:12px'>Formula</div>"
            "<div style='color:#3b82f6;font-size:12px'>SUM(qty × cost) for aging ≥ 60 days</div></div>",
            unsafe_allow_html=True
        )
        if not snap_df.empty:
            fig_ds = go.Figure()
            fig_ds.add_trace(go.Scatter(
                x=snap_df["snapshot_date"], y=snap_df["dead_stock_value"] / 1e7,
                mode="lines", line=dict(color="#ef4444", width=2.5),
                fill="tozeroy", fillcolor="rgba(239,68,68,0.08)"
            ))
            fig_ds.update_layout(**get_chart_theme(), height=200, yaxis_title="₹ Crore")
            st.plotly_chart(fig_ds, width='stretch', config={"displayModeBar": False})

    st.divider()

    # ── KPI Scorecard Table ───────────────────────────────────────────────────
    st.markdown("### KPI Summary Scorecard")
    if latest:
        kpi_data = [
            ("Picking Accuracy %", "≥ 99.5%", f"{latest.get('picking_accuracy_pct', 0):.1f}%",
             "🟢" if latest.get("picking_accuracy_pct", 0) >= 99.5 else "🔴"),
            ("Inventory Accuracy %", "≥ 98%", f"{latest.get('inventory_accuracy_pct', 0):.1f}%",
             "🟢" if latest.get("inventory_accuracy_pct", 0) >= 98 else "🔴"),
            ("GRN Error %", "≤ 2%", f"{latest.get('grn_error_pct', 0):.1f}%",
             "🟢" if latest.get("grn_error_pct", 0) <= 2 else "🔴"),
            ("Dispatch TAT", "≤ 24 hrs", f"{latest.get('dispatch_tat_hours', 0):.1f} hrs",
             "🟢" if latest.get("dispatch_tat_hours", 0) <= 24 else "🔴"),
            ("Dead Stock Value", "Decreasing", format_inr_crore(latest.get("dead_stock_value", 0)), "🟡"),
        ]
        scorecard_df = pd.DataFrame(kpi_data, columns=["KPI", "Target", "Current", "Status"])
        st.dataframe(scorecard_df, width='stretch', hide_index=True)

    st.divider()

    # ── Alerts ────────────────────────────────────────────────────────────────
    st.markdown("### Active KPI Alerts")
    alert_df = get_alerts(resolved=False, limit=20)
    if alert_df.empty:
        st.success("No unresolved alerts.")
    else:
        severity_groups = {"critical": [], "warning": [], "info": []}
        for _, row in alert_df.iterrows():
            sev = row.get("severity", "info")
            if sev in severity_groups:
                severity_groups[sev].append(row)

        for sev, rows in severity_groups.items():
            if rows:
                color = {"critical": "#ef4444", "warning": "#f59e0b", "info": "#22c55e"}[sev]
                st.markdown(f"**{sev.capitalize()} ({len(rows)})**")
                for row in rows:
                    acol1, acol2 = st.columns([4, 1])
                    acol1.markdown(
                        f"<div style='border-left:3px solid {color};padding:8px;"
                        f"background:var(--surface);border-radius:4px;font-size:13px'>"
                        f"<b>{row['title']}</b> "
                        f"<span style='color:var(--text2)'>— {row['module'].upper()}</span></div>",
                        unsafe_allow_html=True
                    )
                    with acol2:
                        if st.button("Resolve", key=f"kpi_res_{row['id']}"):
                            resolve_alert(row["id"])
                            st.rerun()
