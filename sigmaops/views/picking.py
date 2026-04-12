"""Picking Errors Module."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.db import (
    get_all_picking_orders, get_picking_stats_today,
    update_picking_status, get_picker_performance,
    get_picking_error_by_sku, get_fix_checklists, update_fix_item,
)

CHART_BG = dict(paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
                font=dict(color="#e6edf3", family="DM Sans, sans-serif"), margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
                yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")))


def render():
    st.markdown(
        "<div class='module-header'>✅ Picking Error Control</div>"
        "<div class='module-subtitle'>Zero defect picking — right item, right bin, right quantity, first time</div>"
        "<div class='problem-box'>⚠️ Root Cause: Similar SKUs, time pressure, no barcode verification</div>",
        unsafe_allow_html=True
    )

    # ── Live Pick Stats ───────────────────────────────────────────────────────
    stats = get_picking_stats_today()
    sc = st.columns(5)
    acc_color = "#22c55e" if stats["accuracy"] >= 99.5 else ("#f59e0b" if stats["accuracy"] >= 97 else "#ef4444")
    sc[0].markdown(
        f"<div style='background:#161b22;border:1px solid #30363d;border-left:3px solid {acc_color};"
        f"border-radius:8px;padding:16px'><div style='color:#8b949e;font-size:13px'>Accuracy % Today</div>"
        f"<div style='font-size:28px;font-weight:700;color:{acc_color}'>{stats['accuracy']}%</div></div>",
        unsafe_allow_html=True
    )
    sc[1].metric("Pending Picks", stats["pending"])
    sc[2].metric("In Progress", stats["in_progress"])
    sc[3].metric("Errors Today", stats["errors"])
    sc[4].metric("Total Processed", stats["total"])

    st.markdown("")

    # ── Live Pick Queue ───────────────────────────────────────────────────────
    st.markdown("### 🔄 Live Picking Queue")
    active_df = get_all_picking_orders(["pending", "in_progress"])
    if active_df.empty:
        st.success("All picks completed — queue is empty.")
    else:
        st.dataframe(
            active_df[["order_id", "sku", "sku_description", "required_qty",
                        "picked_qty", "bin_code", "picker_id", "pick_method", "status"]],
            use_container_width=True, hide_index=True
        )
        qa1, qa2, qa3, qa4 = st.columns(4)
        with qa1:
            pick_id = st.number_input("Order ID", min_value=1, step=1, key="pick_order_id")
        with qa2:
            if st.button("Start Pick"):
                update_picking_status(int(pick_id), "in_progress")
                st.rerun()
        with qa3:
            picked_qty_val = st.number_input("Picked Qty", min_value=0, step=1, key="picked_qty_val")
            if st.button("Complete Pick"):
                update_picking_status(int(pick_id), "picked", picked_qty=int(picked_qty_val))
                st.rerun()
        with qa4:
            err_type = st.selectbox("Error Type", ["wrong_item", "wrong_qty", "wrong_bin"])
            if st.button("Report Error"):
                update_picking_status(int(pick_id), "error", error_type=err_type)
                st.rerun()

    st.divider()

    # ── Barcode Scan Simulator ────────────────────────────────────────────────
    with st.expander("🔍 Barcode Scan Verification Demo"):
        st.markdown("**Simulate barcode scan verification flow:**")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            scan_order = st.text_input("Step 1: Enter Order ID", placeholder="ORD-2024-3000")
        with sc2:
            scan_sku = st.text_input("Step 2: Scan SKU", placeholder="SKU-ELEC-0021")
        with sc3:
            scan_qty = st.number_input("Step 3: Scan Qty", min_value=0, value=0, key="scan_qty")

        if scan_order:
            all_orders = get_all_picking_orders()
            match = all_orders[all_orders["order_id"] == scan_order]
            if not match.empty:
                order_row = match.iloc[0]
                expected_sku = order_row["sku"]
                expected_qty = order_row["required_qty"]
                sku_ok = scan_sku == expected_sku
                qty_ok = scan_qty == expected_qty

                if scan_sku and scan_qty > 0:
                    if sku_ok and qty_ok:
                        st.markdown(
                            "<div style='background:rgba(34,197,94,0.15);border:2px solid #22c55e;"
                            "border-radius:8px;padding:20px;text-align:center'>"
                            "<div style='font-size:40px'>✅</div>"
                            "<div style='color:#22c55e;font-size:18px;font-weight:700'>VERIFIED — Ready to Pack</div>"
                            "<div style='color:#8b949e;font-size:13px;margin-top:8px'>"
                            "Barcode scan prevents 87% of picking errors</div>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        issues = []
                        if not sku_ok:
                            issues.append(f"SKU mismatch: expected {expected_sku}, got {scan_sku}")
                        if not qty_ok:
                            issues.append(f"Qty mismatch: expected {expected_qty}, got {scan_qty}")
                        st.markdown(
                            f"<div style='background:rgba(239,68,68,0.15);border:2px solid #ef4444;"
                            f"border-radius:8px;padding:20px;text-align:center'>"
                            f"<div style='font-size:40px'>❌</div>"
                            f"<div style='color:#ef4444;font-size:18px;font-weight:700'>MISMATCH DETECTED</div>"
                            f"<div style='color:#e6edf3;font-size:13px;margin-top:8px'>{'<br>'.join(issues)}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.info(f"Order found: SKU {expected_sku}, Qty {expected_qty}. Complete scan fields above.")
            else:
                st.warning("Order ID not found.")

    st.divider()

    # ── Error Analysis Charts ─────────────────────────────────────────────────
    st.markdown("### Error Analysis")
    ch1, ch2 = st.columns(2)

    with ch1:
        sku_err_df = get_picking_error_by_sku()
        if not sku_err_df.empty:
            fig = go.Figure(go.Bar(
                x=sku_err_df["error_count"], y=sku_err_df["sku"],
                orientation="h", marker_color="#ef4444"
            ))
            fig.update_layout(**CHART_BG, height=280, title="Top SKUs with Picking Errors")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        all_picks = get_all_picking_orders(["error"])
        if not all_picks.empty and "error_type" in all_picks.columns:
            err_counts = all_picks["error_type"].value_counts()
            fig2 = go.Figure(go.Pie(
                labels=err_counts.index.tolist(),
                values=err_counts.values.tolist(),
                hole=0.4,
                marker_colors=["#ef4444", "#f59e0b", "#7c3aed"]
            ))
            fig2.update_layout(**CHART_BG, height=280, title="Error Type Breakdown", showlegend=True)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # ── Similar SKU Alert Panel ───────────────────────────────────────────────
    st.markdown("### ⚠️ Confusion-Prone SKU Pairs")
    all_orders = get_all_picking_orders()
    if not all_orders.empty:
        skus = all_orders["sku"].dropna().unique().tolist()
        pairs = []
        seen = set()
        for s1 in skus:
            for s2 in skus:
                if s1 != s2 and s1[:8] == s2[:8]:
                    key = tuple(sorted([s1, s2]))
                    if key not in seen:
                        seen.add(key)
                        err_count = len(all_orders[
                            (all_orders["sku"].isin([s1, s2])) &
                            (all_orders["status"] == "error")
                        ])
                        pairs.append({"SKU A": s1, "SKU B": s2, "Error Count": err_count,
                                      "Recommended Fix": "Color code + separate bin zones"})
        if pairs:
            pairs_df = pd.DataFrame(pairs).sort_values("Error Count", ascending=False).head(10)
            st.dataframe(pairs_df, use_container_width=True, hide_index=True)
        else:
            st.info("No confusion-prone SKU pairs detected.")

    st.divider()

    # ── Picker Performance ────────────────────────────────────────────────────
    st.markdown("### Picker Performance")
    st.caption("Use for coaching, not punishment — errors often indicate systemic issues.")
    perf_df = get_picker_performance()
    if not perf_df.empty:
        st.dataframe(perf_df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Fix Checklist ─────────────────────────────────────────────────────────
    st.markdown("### Six Sigma Fixes — Picking Module")
    fixes_df = get_fix_checklists("picking")
    if not fixes_df.empty:
        done = int(fixes_df["is_done"].sum())
        st.progress(done / len(fixes_df))
        st.markdown(f"**{done} of {len(fixes_df)} fixes implemented**")
        for _, row in fixes_df.iterrows():
            checked = st.checkbox(row["fix_item"], value=bool(row["is_done"]),
                                   key=f"pick_fix_{row['id']}")
            if checked != bool(row["is_done"]):
                update_fix_item(row["id"], int(checked))
                st.rerun()
            if row["is_done"] and row["owner"]:
                st.caption(f"  ✅ {row['owner']} — {row['implemented_date'] or 'N/A'}")
