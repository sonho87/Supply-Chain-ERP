"""GRN / Goods Inward Module."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from modules.db import (
    get_all_grn, get_grn_stats_today, get_pending_verification,
    insert_grn_entry, update_grn_verification, update_grn_status,
    get_grn_error_trend, get_fix_checklists, update_fix_item,
)

VENDORS = [
    "Reliance Retail", "Tata CLiQ", "Metro Cash and Carry",
    "Walmart India", "D-Mart", "Big Bazaar Wholesale"
]

CHART_BG = dict(paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
                font=dict(color="#e6edf3", family="DM Sans, sans-serif"), margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
                yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")))


def render():
    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='module-header'>📦 GRN / Goods Inward Control</div>"
        "<div class='module-subtitle'>Eliminate wrong quantity and wrong SKU entry at source</div>"
        "<div class='problem-box'>⚠️ Root Cause: Manual entry errors, no 2-step verification</div>",
        unsafe_allow_html=True
    )

    # ── Section B: Today Stats ───────────────────────────────────────────────
    stats = get_grn_stats_today()
    total = stats["total"] or 1
    error_rate = round(stats["flagged"] / total * 100, 1)
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total GRNs Today", stats["total"])
    s2.metric("Verified", stats["verified"])
    s3.metric("Flagged", stats["flagged"])
    color = "red" if error_rate > 2 else "green"
    s4.markdown(
        f"<div style='background:#161b22;border:1px solid #30363d;border-left:3px solid "
        f"{'#ef4444' if error_rate > 2 else '#22c55e'};"
        f"border-radius:8px;padding:16px'>"
        f"<div style='color:#8b949e;font-size:13px'>Error Rate %</div>"
        f"<div style='font-size:28px;font-weight:700;color:{'#ef4444' if error_rate > 2 else '#22c55e'}'>"
        f"{error_rate}%</div></div>",
        unsafe_allow_html=True
    )

    st.markdown("")

    # ── Section C: Add New GRN Entry ─────────────────────────────────────────
    with st.expander("➕ New GRN Entry", expanded=False):
        with st.form("new_grn_form"):
            c1, c2 = st.columns(2)
            with c1:
                grn_num = st.text_input("GRN Number", placeholder="GRN-2024-XXXX")
                sku = st.text_input("SKU", placeholder="SKU-ELEC-0021")
                vendor = st.selectbox("Vendor", VENDORS)
            with c2:
                expected = st.number_input("Expected Qty", min_value=1, value=100)
                received = st.number_input("Received Qty", min_value=0, value=100)
                method = st.radio("Entry Method", ["Barcode Scan", "Manual"], horizontal=True)

            submitted = st.form_submit_button("Submit GRN Entry")
            if submitted and grn_num and sku:
                discrepancy = received - expected
                method_key = "barcode" if "Barcode" in method else "manual"
                disc_pct = abs(discrepancy / expected * 100) if expected > 0 else 0
                if disc_pct > 5:
                    status = "flagged"
                    st.error(f"❌ Discrepancy {discrepancy:+d} units ({disc_pct:.1f}%) — Entry auto-flagged")
                elif discrepancy != 0:
                    status = "pending"
                    st.warning(f"⚠️ Discrepancy of {discrepancy:+d} units detected")
                elif method_key == "barcode":
                    status = "verified"
                    st.success("✅ Barcode scan verified — Entry confirmed")
                else:
                    status = "pending"

                insert_grn_entry({
                    "grn_number": grn_num, "sku": sku, "vendor": vendor,
                    "expected_qty": int(expected), "received_qty": int(received),
                    "discrepancy": discrepancy, "entry_method": method_key, "status": status
                })
                st.toast("GRN entry saved!", icon="✅")
                st.rerun()

    # ── Section D: 2-Step Verification Queue ─────────────────────────────────
    with st.expander("✅ Pending Verification Queue", expanded=True):
        pending_df = get_pending_verification()
        if pending_df.empty:
            st.info("No entries pending verification.")
        else:
            st.dataframe(
                pending_df[["grn_number", "sku", "vendor", "expected_qty",
                             "received_qty", "discrepancy", "verified_step1",
                             "verified_step2", "status"]],
                use_container_width=True, hide_index=True
            )
            st.markdown("**Quick Actions:**")
            act_cols = st.columns(4)
            with act_cols[0]:
                sel_grn_id = st.number_input("Entry ID for action", min_value=1, step=1,
                                              key="grn_action_id")
            with act_cols[1]:
                if st.button("Step 1 Verify"):
                    update_grn_verification(sel_grn_id, 1)
                    st.rerun()
            with act_cols[2]:
                if st.button("Step 2 Verify"):
                    update_grn_verification(sel_grn_id, 2)
                    st.rerun()
            with act_cols[3]:
                if st.button("Flag Entry"):
                    update_grn_status(sel_grn_id, "flagged")
                    st.rerun()

    # ── Section E: Full GRN Table ─────────────────────────────────────────────
    st.markdown("### GRN Entries")
    f1, f2, f3 = st.columns(3)
    with f1:
        status_filter = st.multiselect("Status", ["verified", "flagged", "pending", "rejected"],
                                        default=["flagged", "pending"])
    with f2:
        vendor_filter = st.selectbox("Vendor", ["All"] + VENDORS, key="grn_vendor_filter")
    with f3:
        method_filter = st.selectbox("Entry Method", ["All", "barcode", "manual"])

    filters = {}
    if status_filter:
        filters["status"] = status_filter
    if vendor_filter != "All":
        filters["vendor"] = vendor_filter
    if method_filter != "All":
        filters["entry_method"] = method_filter

    grn_df = get_all_grn(filters)

    if not grn_df.empty:
        st.dataframe(
            grn_df[["grn_number", "sku", "vendor", "expected_qty", "received_qty",
                     "discrepancy", "entry_method", "status", "created_at"]],
            use_container_width=True, hide_index=True
        )
        csv = grn_df.to_csv(index=False)
        st.download_button("⬇ Export CSV", csv, "grn_entries.csv", "text/csv")

    # ── Section F: Error Analysis Charts ─────────────────────────────────────
    st.divider()
    st.markdown("### Error Analysis")
    chart1, chart2 = st.columns(2)

    with chart1:
        trend_df = get_grn_error_trend(14)
        if not trend_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=trend_df["date"], y=trend_df["error_pct"],
                                  marker_color="#ef4444", name="Error %"))
            fig.add_hline(y=2.0, line_dash="dash", line_color="#22c55e",
                          annotation_text="Target 2%", annotation_font_color="#22c55e")
            fig.update_layout(**CHART_BG, height=250, title="GRN Error Rate (14 Days)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with chart2:
        if not grn_df.empty:
            err_df = grn_df[grn_df["status"].isin(["flagged", "rejected"])]
            if not err_df.empty:
                pos = len(err_df[err_df["discrepancy"] > 0])
                neg = len(err_df[err_df["discrepancy"] < 0])
                zero = len(err_df[err_df["discrepancy"] == 0])
                fig2 = go.Figure(go.Pie(
                    labels=["Qty Excess", "Qty Short", "Wrong SKU"],
                    values=[pos, neg, zero],
                    hole=0.4,
                    marker_colors=["#f59e0b", "#ef4444", "#7c3aed"]
                ))
                fig2.update_layout(**CHART_BG, height=250, title="Error Type Breakdown",
                                   showlegend=True)
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Section G: Entry Method Comparison ───────────────────────────────────
    st.markdown("### Entry Method Comparison")
    if not grn_df.empty:
        manual_df = grn_df[grn_df["entry_method"] == "manual"]
        barcode_df = grn_df[grn_df["entry_method"] == "barcode"]
        manual_err = round(
            len(manual_df[manual_df["status"].isin(["flagged", "rejected"])]) / max(1, len(manual_df)) * 100, 1)
        barcode_err = round(
            len(barcode_df[barcode_df["status"].isin(["flagged", "rejected"])]) / max(1, len(barcode_df)) * 100, 1)
        improvement = round(manual_err - barcode_err, 1) if manual_err > barcode_err else 0

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Manual Entry Error Rate", f"{manual_err}%")
        mc2.metric("Barcode Entry Error Rate", f"{barcode_err}%")
        mc3.metric("Improvement from Barcode", f"{improvement}% reduction")

    # ── Section H: Fix Checklist ──────────────────────────────────────────────
    st.divider()
    st.markdown("### Six Sigma Fixes — GRN Module")
    fixes_df = get_fix_checklists("grn")
    if not fixes_df.empty:
        done_count = int(fixes_df["is_done"].sum())
        st.progress(done_count / len(fixes_df))
        st.markdown(f"**{done_count} of {len(fixes_df)} fixes implemented**")
        for _, row in fixes_df.iterrows():
            checked = st.checkbox(row["fix_item"], value=bool(row["is_done"]),
                                   key=f"grn_fix_{row['id']}")
            if checked != bool(row["is_done"]):
                update_fix_item(row["id"], int(checked))
                st.rerun()
            if row["is_done"] and row["owner"]:
                st.caption(f"  ✅ {row['owner']} — {row['implemented_date'] or 'N/A'}")
