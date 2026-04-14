"""Dispatch Delays Module."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.db import (
    get_all_dispatch_orders, get_dispatch_stats_today,
    update_dispatch_status, get_delay_by_carrier,
    get_fix_checklists, update_fix_item,
)
from modules.theme import inject_css, get_chart_theme

STATUS_ORDER = ["pending", "staged", "loading", "dispatched"]
STATUS_NEXT = {"pending": "staged", "staged": "loading", "loading": "dispatched"}


def render():
    inject_css()
    st.markdown(
        "<div class='module-header'>🚛 Dispatch Control</div>"
        "<div class='module-subtitle'>On-time dispatch every time — no exceptions, no excuses</div>"
        "<div class='problem-box'>⚠️ Root Cause: Poor pre-staging, document delay, no time slot discipline</div>",
        unsafe_allow_html=True
    )

    # ── Today Stats ───────────────────────────────────────────────────────────
    stats = get_dispatch_stats_today()
    ds1, ds2, ds3, ds4 = st.columns(4)
    ds1.metric("Scheduled Today", stats["total"])
    ds2.metric("Dispatched", stats["dispatched"])
    ds3.metric("Delayed", stats["delayed"])
    ds4.metric("Avg Delay (mins)", stats["avg_delay"])

    st.divider()

    # ── Kanban Board ──────────────────────────────────────────────────────────
    st.markdown("### Dispatch Board")
    all_orders = get_all_dispatch_orders()

    k_cols = st.columns(4)
    col_labels = ["Pending", "Staged", "Loading", "Dispatched"]
    col_statuses = ["pending", "staged", "loading", "dispatched"]
    col_colors = ["#8b949e", "#3b82f6", "#f59e0b", "#22c55e"]

    for i, (label, status, color) in enumerate(zip(col_labels, col_statuses, col_colors)):
        with k_cols[i]:
            col_df = all_orders[all_orders["status"] == status] if not all_orders.empty else pd.DataFrame()
            st.markdown(
                f"<div style='border-bottom:2px solid {color};padding-bottom:6px;margin-bottom:10px'>"
                f"<span style='color:{color};font-weight:700'>{label}</span> "
                f"<span style='background:{color}20;color:{color};padding:1px 8px;"
                f"border-radius:10px;font-size:12px'>{len(col_df)}</span></div>",
                unsafe_allow_html=True
            )
            if not col_df.empty:
                for _, row in col_df.iterrows():
                    is_delayed = row["delay_minutes"] > 0
                    border = "#ef4444" if is_delayed else color
                    delay_badge = (f"<span style='color:#ef4444;font-size:11px'>⏰ +{row['delay_minutes']}m</span>"
                                   if is_delayed else "")
                    docs_icon = "✅" if row["docs_ready"] else "❌"
                    staging_icon = "✅" if row["staging_done"] else "❌"
                    st.markdown(
                        f"<div style='background:var(--surface);border:1px solid {border};"
                        f"border-radius:6px;padding:8px;margin-bottom:6px;font-size:12px'>"
                        f"<div style='font-weight:600;color:var(--text)'>{row['order_id']}</div>"
                        f"<div style='color:var(--text2)'>{row['carrier']} | {row['scheduled_slot']}</div>"
                        f"<div>Docs {docs_icon} | Staged {staging_icon} {delay_badge}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    next_status = STATUS_NEXT.get(status)
                    if next_status and st.button(f"→ {next_status.capitalize()}",
                                                  key=f"disp_{row['id']}_{next_status}"):
                        update_dispatch_status(row["id"], next_status)
                        st.rerun()

    st.divider()

    # ── Time Slot Timeline ────────────────────────────────────────────────────
    st.markdown("### Dispatch Time Slot Overview")
    if not all_orders.empty:
        slots_data = all_orders.groupby(["scheduled_slot", "status"]).size().reset_index(name="count")
        if not slots_data.empty:
            fig = go.Figure()
            status_color_map = {
                "dispatched": "#22c55e", "loading": "#f59e0b",
                "staged": "#3b82f6", "pending": "#8b949e", "delayed": "#ef4444"
            }
            for status in col_statuses:
                sd = slots_data[slots_data["status"] == status]
                if not sd.empty:
                    fig.add_trace(go.Bar(
                        x=sd["scheduled_slot"], y=sd["count"],
                        name=status.capitalize(),
                        marker_color=status_color_map.get(status, "#8b949e")
                    ))
            fig.update_layout(
                **get_chart_theme(), height=250, title="Orders by Time Slot",
                barmode="stack",
                legend=dict(bgcolor=get_chart_theme()["xaxis"]["gridcolor"], bordercolor=get_chart_theme()["xaxis"]["gridcolor"]),
            )
            st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    st.divider()

    # ── Pre-Staging Checklist ─────────────────────────────────────────────────
    st.markdown("### Pre-Staging Checklist")
    if not all_orders.empty:
        order_ids = all_orders["order_id"].tolist()
        sel_order = st.selectbox("Select Order", order_ids, key="disp_checklist_order")
        order_row = all_orders[all_orders["order_id"] == sel_order].iloc[0]

        checklist_items = [
            ("SKUs picked and consolidated to staging area", bool(order_row["staging_done"])),
            ("Invoice + packing list printed", bool(order_row["docs_ready"])),
            ("LR / AWB number obtained from carrier", bool(order_row["docs_ready"])),
            ("Loading bay allocated", bool(order_row["staging_done"])),
            ("Truck slot confirmed with carrier 24 hrs ahead", bool(order_row["staging_done"])),
        ]
        for label, val in checklist_items:
            st.checkbox(label, value=val, key=f"check_{sel_order}_{label[:20]}", disabled=True)

        col_action1, col_action2 = st.columns(2)
        with col_action1:
            if st.button("Mark Staging Done", key=f"staging_{sel_order}"):
                from modules.db import get_connection
                conn = get_connection()
                conn.execute("UPDATE dispatch_orders SET staging_done=1 WHERE order_id=?", (sel_order,))
                conn.commit()
                conn.close()
                st.rerun()
        with col_action2:
            if st.button("Mark Docs Ready", key=f"docs_{sel_order}"):
                from modules.db import get_connection
                conn = get_connection()
                conn.execute("UPDATE dispatch_orders SET docs_ready=1 WHERE order_id=?", (sel_order,))
                conn.commit()
                conn.close()
                st.rerun()

    st.divider()

    # ── Delay Analysis Charts ─────────────────────────────────────────────────
    st.markdown("### Delay Analysis")
    da1, da2 = st.columns(2)

    with da1:
        delay_df = get_delay_by_carrier()
        if not delay_df.empty:
            fig = go.Figure(go.Bar(
                x=delay_df["avg_delay"], y=delay_df["carrier"],
                orientation="h", marker_color="#ef4444"
            ))
            fig.update_layout(**get_chart_theme(), height=250, title="Avg Delay by Carrier (mins)")
            st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    with da2:
        reasons = {
            "No pre-staging": 38, "Docs not ready": 28,
            "Truck no-show": 17, "Bay occupied": 12, "System issue": 5
        }
        sorted_r = dict(sorted(reasons.items(), key=lambda x: x[1], reverse=True))
        labels = list(sorted_r.keys())
        values = list(sorted_r.values())
        total = sum(values)
        cumulative = [sum(values[:i+1]) / total * 100 for i in range(len(values))]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=labels, y=values, marker_color="#f59e0b", name="Count"))
        fig2.add_trace(go.Scatter(
            x=labels, y=cumulative, mode="lines+markers",
            line=dict(color="#00d4aa", width=2), yaxis="y2", name="Cumulative %"
        ))
        fig2.update_layout(
            **get_chart_theme(), height=250, title="Pareto: Dispatch Delay Reasons",
            yaxis2=dict(overlaying="y", side="right", showgrid=False,
                        tickfont=dict(color=get_chart_theme()["xaxis"]["tickfont"]["color"]), range=[0, 110]),
            showlegend=True,
            legend=dict(bgcolor="#21262d", bordercolor="#30363d"),
        )
        st.plotly_chart(fig2, width='stretch', config={"displayModeBar": False})

    # ── TAT Trend ─────────────────────────────────────────────────────────────
    st.markdown("### TAT Trend — Last 14 Days")
    from modules.db import get_kpi_snapshots
    snap_df = get_kpi_snapshots(14)
    if not snap_df.empty:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=snap_df["snapshot_date"], y=snap_df["dispatch_tat_hours"],
            mode="lines+markers", name="TAT (hrs)",
            line=dict(color="#00d4aa", width=2.5),
        ))
        fig3.add_hline(y=24, line_dash="dash", line_color="#22c55e",
                       annotation_text="Target 24h")
        fig3.update_layout(**get_chart_theme(), height=220)
        st.plotly_chart(fig3, width='stretch', config={"displayModeBar": False})

    st.divider()

    # ── Fix Checklist ─────────────────────────────────────────────────────────
    st.markdown("### Six Sigma Fixes — Dispatch Module")
    fixes_df = get_fix_checklists("dispatch")
    if not fixes_df.empty:
        done = int(fixes_df["is_done"].sum())
        st.progress(done / len(fixes_df))
        st.markdown(f"**{done} of {len(fixes_df)} fixes implemented**")
        for _, row in fixes_df.iterrows():
            checked = st.checkbox(row["fix_item"], value=bool(row["is_done"]),
                                   key=f"disp_fix_{row['id']}")
            if checked != bool(row["is_done"]):
                update_fix_item(row["id"], int(checked))
                st.rerun()
            if row["is_done"] and row["owner"]:
                st.caption(f"  ✅ {row['owner']} — {row['implemented_date'] or 'N/A'}")
