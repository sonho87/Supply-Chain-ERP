"""Inventory Mismatch Module."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.db import (
    get_all_inventory, get_inventory_accuracy, get_inventory_stats,
    update_inventory_count, get_overdue_cycle_counts,
    get_root_cause_log, insert_root_cause, update_root_cause_status,
    get_fix_checklists, update_fix_item, insert_alert,
)

CHART_BG = dict(paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
                font=dict(color="#e6edf3", family="DM Sans, sans-serif"), margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
                yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")))

CATEGORIES = ["All", "Electronics", "FMCG", "Apparel", "Pharma", "Auto Parts"]


def render():
    st.markdown(
        "<div class='module-header'>📉 Inventory Mismatch Control</div>"
        "<div class='module-subtitle'>System quantity must equal physical quantity — every SKU, every day</div>"
        "<div class='problem-box'>⚠️ Root Cause: Process leakages at inward and picking — system ≠ physical</div>",
        unsafe_allow_html=True
    )

    # ── Accuracy Gauge + Stats ────────────────────────────────────────────────
    accuracy = get_inventory_accuracy()
    inv_stats = get_inventory_stats()

    g1, g2, g3 = st.columns(3)

    with g1:
        color = "#22c55e" if accuracy >= 98 else ("#f59e0b" if accuracy >= 90 else "#ef4444")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=accuracy,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Inventory Accuracy %", "font": {"color": "#e6edf3"}},
            gauge={
                "axis": {"range": [80, 100], "tickcolor": "#8b949e"},
                "bar": {"color": color},
                "bgcolor": "#21262d",
                "steps": [
                    {"range": [80, 90], "color": "rgba(239,68,68,0.2)"},
                    {"range": [90, 98], "color": "rgba(245,158,11,0.2)"},
                    {"range": [98, 100], "color": "rgba(34,197,94,0.2)"},
                ],
                "threshold": {"line": {"color": "#22c55e", "width": 3}, "value": 98}
            },
            number={"font": {"color": color, "size": 36}, "suffix": "%"}
        ))
        fig.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
                          font=dict(color="#e6edf3", family="DM Sans, sans-serif"), margin=dict(l=10, r=10, t=30, b=10),
                          height=220)
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    with g2:
        st.markdown("<div class='sigma-card'>", unsafe_allow_html=True)
        st.metric("Total SKUs", inv_stats["total"])
        st.markdown(f"<span style='color:#22c55e'>🟢 Matched: {inv_stats['matched']}</span>",
                    unsafe_allow_html=True)
        st.markdown(f"<span style='color:#f59e0b'>🟡 Minor Variance: {inv_stats['minor']}</span>",
                    unsafe_allow_html=True)
        st.markdown(f"<span style='color:#ef4444'>🔴 Critical Variance: {inv_stats['critical']}</span>",
                    unsafe_allow_html=True)
        st.markdown(f"<span style='color:#8b949e'>⚪ Unresolved: {inv_stats['unresolved']}</span>",
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with g3:
        crit_df = get_all_inventory(["variance_critical"])
        val_at_risk = (crit_df["system_qty"] * 50).sum() if not crit_df.empty else 0
        overdue_df = get_overdue_cycle_counts()
        st.markdown(
            f"<div class='sigma-card'>"
            f"<div style='font-size:13px;color:#8b949e'>Value at Risk</div>"
            f"<div style='font-size:22px;font-weight:700;color:#ef4444'>~₹{val_at_risk/1e5:.1f}L est.</div>"
            f"<div style='margin-top:8px;font-size:13px;color:#8b949e'>Overdue Cycle Counts</div>"
            f"<div style='font-size:22px;font-weight:700;color:#f59e0b'>{len(overdue_df)}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.divider()

    # ── Cycle Count Planner ───────────────────────────────────────────────────
    st.markdown("### 📅 Cycle Count Schedule")
    cc1, cc2, cc3 = st.columns(3)
    freq_info = [
        ("Daily", "daily", cc1), ("Weekly", "weekly", cc2), ("Monthly", "monthly", cc3)
    ]
    for label, freq, col in freq_info:
        with col:
            overdue = overdue_df[overdue_df["count_frequency"] == freq] if not overdue_df.empty else pd.DataFrame()
            st.markdown(
                f"<div class='sigma-card'>"
                f"<div style='font-size:16px;font-weight:700;color:#00d4aa'>{label} Count</div>"
                f"<div style='color:#ef4444;font-size:13px'>⚠️ {len(overdue)} overdue</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            if not overdue.empty:
                for _, r in overdue.head(5).iterrows():
                    with st.expander(f"Count Now: {r['sku']}", expanded=False):
                        with st.form(f"count_form_{r['id']}"):
                            st.text(f"SKU: {r['sku']} | System Qty: {r['system_qty']}")
                            physical = st.number_input("Physical Count", min_value=0,
                                                        value=int(r["system_qty"]),
                                                        key=f"phys_{r['id']}")
                            notes = st.text_area("Notes", key=f"notes_{r['id']}")
                            if st.form_submit_button("Submit Count"):
                                new_status = update_inventory_count(r["id"], int(physical), int(r["system_qty"]))
                                if new_status == "variance_critical":
                                    insert_alert("inventory", "critical",
                                                 f"Critical variance on {r['sku']}",
                                                 f"Variance detected on cycle count. Notes: {notes}")
                                st.success(f"Count recorded — Status: {new_status}")
                                st.rerun()

    st.divider()

    # ── Variance Tracking Sheet ───────────────────────────────────────────────
    st.markdown("### ⚠️ Variance Report")
    vf1, vf2 = st.columns(2)
    with vf1:
        status_filter = st.multiselect(
            "Status", ["matched", "variance_minor", "variance_critical", "unresolved"],
            default=["variance_minor", "variance_critical", "unresolved"]
        )
    with vf2:
        cat_filter = st.selectbox("Category", CATEGORIES, key="inv_cat_filter")

    inv_df = get_all_inventory(status_filter if status_filter else None,
                               cat_filter if cat_filter != "All" else None)

    if not inv_df.empty:
        status_colors = {
            "matched": "#22c55e", "variance_minor": "#f59e0b",
            "variance_critical": "#ef4444", "unresolved": "#8b949e"
        }
        st.dataframe(
            inv_df[["sku", "description", "category", "system_qty", "physical_qty",
                     "variance", "variance_pct", "status", "root_cause", "last_cycle_count"]],
            width='stretch', hide_index=True
        )
        csv = inv_df.to_csv(index=False)
        st.download_button("⬇ Export CSV", csv, "inventory_variance.csv", "text/csv")

    st.divider()

    # ── 5-Why Entry Form ──────────────────────────────────────────────────────
    with st.expander("📝 Log Root Cause Analysis (5-Why)", expanded=False):
        with st.form("inv_5why_form"):
            issue = st.text_area("Issue Description")
            c1, c2 = st.columns(2)
            with c1:
                w1 = st.text_input("Why 1: Why did the variance occur?")
                w2 = st.text_input("Why 2: Why did that happen?")
                w3 = st.text_input("Why 3: Why?")
            with c2:
                w4 = st.text_input("Why 4: Why?")
                w5 = st.text_input("Why 5 (Root Cause): Why?")
                logged_by = st.text_input("Logged By")
            corrective = st.text_area("Corrective Action")
            preventive = st.text_area("Preventive Action")
            if st.form_submit_button("Save Root Cause"):
                insert_root_cause({
                    "module": "inventory", "issue_description": issue,
                    "root_cause": w5, "why_1": w1, "why_2": w2, "why_3": w3,
                    "why_4": w4, "why_5": w5, "corrective_action": corrective,
                    "preventive_action": preventive, "logged_by": logged_by
                })
                st.success("Root cause logged.")
                st.rerun()

    # ── Root Cause Log ────────────────────────────────────────────────────────
    st.markdown("### Root Cause Log")
    rc_df = get_root_cause_log("inventory")
    if not rc_df.empty:
        st.dataframe(
            rc_df[["issue_description", "root_cause", "corrective_action",
                    "logged_by", "status", "created_at"]],
            width='stretch', hide_index=True
        )
        close_id = st.number_input("Close Log ID", min_value=1, step=1, key="inv_close_id")
        if st.button("Close Root Cause"):
            update_root_cause_status(int(close_id), "closed")
            st.rerun()

    st.divider()

    # ── Fix Checklist ─────────────────────────────────────────────────────────
    st.markdown("### Six Sigma Fixes — Inventory Module")
    fixes_df = get_fix_checklists("inventory")
    if not fixes_df.empty:
        done = int(fixes_df["is_done"].sum())
        st.progress(done / len(fixes_df))
        st.markdown(f"**{done} of {len(fixes_df)} fixes implemented**")
        for _, row in fixes_df.iterrows():
            checked = st.checkbox(row["fix_item"], value=bool(row["is_done"]),
                                   key=f"inv_fix_{row['id']}")
            if checked != bool(row["is_done"]):
                update_fix_item(row["id"], int(checked))
                st.rerun()
            if row["is_done"] and row["owner"]:
                st.caption(f"  ✅ {row['owner']} — {row['implemented_date'] or 'N/A'}")
