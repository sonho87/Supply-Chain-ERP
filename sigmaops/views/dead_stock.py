"""Dead Stock / Slow Moving Module."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

from modules.db import (
    get_all_dead_stock, get_dead_stock_summary,
    update_dead_stock_action, get_kpi_snapshots,
    get_fix_checklists, update_fix_item,
)
from modules.kpi import format_inr_crore
from modules.theme import inject_css, get_chart_theme

AGING_COLORS = {
    "30_days": "#22c55e", "60_days": "#f59e0b",
    "90_days": "#f97316", "90_plus": "#ef4444"
}
CATEGORIES = ["All", "Electronics", "FMCG", "Apparel", "Pharma", "Auto Parts"]
AGING_BUCKETS = ["30_days", "60_days", "90_days", "90_plus"]
ACTIONS = ["monitor", "discount", "liquidate", "write_off", "return_vendor"]


def render():
    inject_css()
    st.markdown(
        "<div class='module-header'>💀 Dead Stock Control</div>"
        "<div class='module-subtitle'>Free up capital — every idle SKU has a cost</div>"
        "<div class='problem-box'>⚠️ Root Cause: Over-ordering, no velocity tracking, no aging review process</div>",
        unsafe_allow_html=True
    )

    # ── Capital at Risk Overview ──────────────────────────────────────────────
    summary = get_dead_stock_summary()
    total_val = summary["total_value"]
    total_count = summary["count"]

    ov1, ov2, ov3, ov4 = st.columns(4)
    ov1.markdown(
        f"<div style='background:var(--surface);border:1px solid var(--border);border-left:3px solid #ef4444;"
        f"border-radius:8px;padding:16px'>"
        f"<div style='color:var(--text2);font-size:13px'>Total Dead Stock Value</div>"
        f"<div style='font-size:24px;font-weight:700;color:#ef4444'>{format_inr_crore(total_val)}</div>"
        f"</div>",
        unsafe_allow_html=True
    )
    ov2.metric("Dead Stock SKUs", total_count)

    all_inv = get_all_dead_stock()
    total_inv_val = total_val * 5 if total_val else 1
    blocked_pct = round(total_val / total_inv_val * 100, 1)
    ov3.metric("% Capital Blocked", f"{blocked_pct}%")

    actioned_val = sum(
        row["total_value"] for _, row in all_inv.iterrows()
        if not all_inv.empty and row.get("status") == "actioned"
    ) if not all_inv.empty else 0
    ov4.metric("Value Actioned (Est.)", format_inr_crore(actioned_val))

    st.divider()

    # ── Aging Breakdown Cards ─────────────────────────────────────────────────
    st.markdown("### Aging Breakdown")
    ag_cols = st.columns(4)
    aging_labels = ["30 Days", "60 Days", "90 Days", "90+ Days"]
    aging_actions = ["Monitor", "Discount / Return", "Liquidate", "Write Off"]

    for i, (bucket, label, action) in enumerate(zip(AGING_BUCKETS, aging_labels, aging_actions)):
        with ag_cols[i]:
            b_data = summary["buckets"].get(bucket, {"count": 0, "value": 0})
            pct = round(b_data["value"] / max(1, total_val) * 100)
            color = AGING_COLORS[bucket]
            st.markdown(
                f"<div class='sigma-card' style='border-left:3px solid {color}'>"
                f"<div style='font-size:16px;font-weight:700;color:{color}'>{label}</div>"
                f"<div style='font-size:13px'>{b_data['count']} SKUs</div>"
                f"<div style='color:#ef4444;font-size:13px'>{format_inr_crore(b_data['value'])}</div>"
                f"<div style='color:var(--text2);font-size:11px;margin-top:4px'>→ {action}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            st.progress(pct / 100)

    st.divider()

    # ── Aging Value Chart ─────────────────────────────────────────────────────
    st.markdown("### Dead Stock by Category and Aging")
    ch1, ch2 = st.columns([60, 40])

    with ch1:
        if not all_inv.empty:
            cats = all_inv["category"].unique().tolist()
            fig = go.Figure()
            for bucket in AGING_BUCKETS:
                bucket_data = []
                for cat in cats:
                    val = all_inv[(all_inv["aging_bucket"] == bucket) &
                                  (all_inv["category"] == cat)]["total_value"].sum()
                    bucket_data.append(val / 1e7)
                fig.add_trace(go.Bar(
                    x=cats, y=bucket_data, name=bucket.replace("_", " "),
                    marker_color=AGING_COLORS[bucket]
                ))
            fig.update_layout(
                **get_chart_theme(), height=280, title="Dead Stock Value by Category (₹ Cr)",
                barmode="stack",
                legend=dict(bgcolor="#21262d", bordercolor="#30363d"),
            )
            st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    with ch2:
        snap_df = get_kpi_snapshots(30)
        if not snap_df.empty and "dead_stock_value" in snap_df.columns:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=snap_df["snapshot_date"], y=snap_df["dead_stock_value"] / 1e7,
                mode="lines", name="Dead Stock (₹Cr)",
                line=dict(color="#ef4444", width=2.5),
                fill="tozeroy", fillcolor="rgba(239,68,68,0.08)"
            ))
            fig2.update_layout(**get_chart_theme(), height=280, title="Dead Stock Trend (₹Cr)")
            st.plotly_chart(fig2, width='stretch', config={"displayModeBar": False})

    st.divider()

    # ── Dead Stock Table ──────────────────────────────────────────────────────
    st.markdown("### Dead Stock Register")
    tf1, tf2, tf3 = st.columns(3)
    with tf1:
        aging_filter = st.multiselect("Aging Bucket", AGING_BUCKETS, key="ds_aging_filter")
    with tf2:
        cat_filter = st.selectbox("Category", CATEGORIES, key="ds_cat_filter")
    with tf3:
        action_filter = st.multiselect("Recommended Action", ACTIONS, key="ds_action_filter")

    ds_df = get_all_dead_stock(
        aging_filter if aging_filter else None,
        cat_filter if cat_filter != "All" else None,
        action_filter if action_filter else None
    )

    if not ds_df.empty:
        st.dataframe(
            ds_df[["sku", "description", "category", "warehouse_location", "qty_on_hand",
                    "unit_cost", "total_value", "last_movement_date", "days_no_movement",
                    "aging_bucket", "recommended_action", "status"]],
            width='stretch', hide_index=True
        )
        csv = ds_df.to_csv(index=False)
        st.download_button("⬇ Export CSV", csv, "dead_stock.csv", "text/csv")

        st.markdown("**Quick Actions:**")
        act_c1, act_c2, act_c3, act_c4 = st.columns(4)
        with act_c1:
            ds_action_id = st.number_input("Item ID", min_value=1, step=1, key="ds_act_id")
        with act_c2:
            if st.button("Mark Discounted"):
                update_dead_stock_action(int(ds_action_id), "actioned", "discount")
                st.rerun()
        with act_c3:
            if st.button("Return to Vendor"):
                update_dead_stock_action(int(ds_action_id), "actioned", "return_vendor")
                st.rerun()
        with act_c4:
            if st.button("Write Off"):
                update_dead_stock_action(int(ds_action_id), "actioned", "write_off")
                st.rerun()

    st.divider()

    # ── Monthly Review Summary ────────────────────────────────────────────────
    st.markdown("### Monthly Review Summary")
    next_review = (datetime.now() + timedelta(days=30)).strftime("%d %b %Y")
    added_count = len(all_inv[all_inv["days_no_movement"] <= 30]) if not all_inv.empty else 0
    added_val = all_inv[all_inv["days_no_movement"] <= 30]["total_value"].sum() if not all_inv.empty else 0
    st.markdown(
        f"<div class='sigma-card'>"
        f"<div style='font-size:15px;font-weight:600;color:#00d4aa;margin-bottom:8px'>Monthly Dead Stock Report</div>"
        f"<div style='display:flex;gap:40px'>"
        f"<div><div style='color:var(--text2);font-size:12px'>Added This Month</div>"
        f"<div style='font-size:18px;color:#ef4444'>{added_count} SKUs | {format_inr_crore(added_val)}</div></div>"
        f"<div><div style='color:var(--text2);font-size:12px'>Next Review Date</div>"
        f"<div style='font-size:18px;color:#22c55e'>{next_review}</div></div>"
        f"</div></div>",
        unsafe_allow_html=True
    )

    st.divider()

    # ── Fix Checklist ─────────────────────────────────────────────────────────
    st.markdown("### Six Sigma Fixes — Dead Stock Module")
    fixes_df = get_fix_checklists("deadstock")
    if not fixes_df.empty:
        done = int(fixes_df["is_done"].sum())
        st.progress(done / len(fixes_df))
        st.markdown(f"**{done} of {len(fixes_df)} fixes implemented**")
        for _, row in fixes_df.iterrows():
            checked = st.checkbox(row["fix_item"], value=bool(row["is_done"]),
                                   key=f"ds_fix_{row['id']}")
            if checked != bool(row["is_done"]):
                update_fix_item(row["id"], int(checked))
                st.rerun()
            if row["is_done"] and row["owner"]:
                st.caption(f"  ✅ {row['owner']} — {row['implemented_date'] or 'N/A'}")
