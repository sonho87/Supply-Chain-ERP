"""Bin Location Errors Module."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from modules.db import (
    get_all_bins, get_mismatch_bins, get_zone_summary,
    update_bin_mapping, update_bin_audited, insert_bin,
    get_fix_checklists, update_fix_item,
)

CHART_BG = dict(paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                font=dict(color="#e6edf3"), margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
                yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")))


def render():
    st.markdown("## 🗂️ Bin Location Control")
    st.markdown("<span style='color:#8b949e'>Eliminate stock mismatch through fixed bin system and audit discipline</span>",
                unsafe_allow_html=True)
    st.markdown(
        "<div style='background:rgba(245,158,11,0.1);border-left:3px solid #f59e0b;"
        "padding:10px 14px;border-radius:6px;color:#f59e0b;font-size:13px'>"
        "⚠️ Root Cause: Wrong bin mapping / no system update after movement</div>",
        unsafe_allow_html=True
    )
    st.markdown("")

    # ── Zone Summary ─────────────────────────────────────────────────────────
    zone_df = get_zone_summary()
    z_cols = st.columns(4)
    for i, zone in enumerate(["A", "B", "C", "D"]):
        with z_cols[i]:
            if not zone_df.empty:
                row = zone_df[zone_df["zone"] == zone]
                if not row.empty:
                    r = row.iloc[0]
                    mismatch = int(r["mismatch_count"])
                    total = int(r["total_bins"])
                    empty = int(r["empty_count"])
                    audit_pct = max(0, 100 - int(mismatch / max(1, total) * 100))
                    st.markdown(
                        f"<div class='sigma-card'>"
                        f"<div style='font-size:28px;font-weight:700;color:#00d4aa'>Zone {zone}</div>"
                        f"<div style='font-size:13px;color:#8b949e'>{total} bins total</div>"
                        f"<div style='color:#ef4444;font-size:13px'>⚠️ {mismatch} mismatches</div>"
                        f"<div style='color:#8b949e;font-size:12px'>Empty: {empty}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    st.progress(audit_pct / 100, text=f"{audit_pct}% clean")

    st.divider()

    # ── Warehouse Grid Heatmap ────────────────────────────────────────────────
    st.markdown("### Warehouse Bin Status Map")
    zone_sel = st.selectbox("Select Zone", ["A", "B", "C", "D"], key="bin_zone_map")
    bins_df = get_all_bins(zone_sel)

    if not bins_df.empty:
        status_color = {
            "active": "#22c55e", "mismatch": "#ef4444",
            "empty": "#f59e0b", "locked": "#8b949e"
        }
        fig = go.Figure()
        for _, row in bins_df.iterrows():
            try:
                rack_num = int(row["rack"].replace("R", ""))
                level_num = int(row["level"].replace("L", ""))
                aisle_num = int(row["aisle"])
            except (ValueError, AttributeError):
                continue
            color = status_color.get(row["status"], "#8b949e")
            fig.add_trace(go.Scatter(
                x=[aisle_num], y=[rack_num + level_num * 0.2],
                mode="markers+text",
                marker=dict(size=18, color=color, symbol="square"),
                text=[row["bin_code"]],
                textfont=dict(size=7, color="#e6edf3"),
                textposition="top center",
                hovertext=f"{row['bin_code']}<br>SKU: {row['sku']}<br>"
                          f"Mapped: {row['mapped_qty']}, Actual: {row['actual_qty']}<br>"
                          f"Variance: {row['variance']}<br>Status: {row['status']}",
                hoverinfo="text",
                name=row["status"],
                showlegend=False
            ))
        fig.update_layout(
            **CHART_BG, height=300,
            title=f"Zone {zone_sel} Bin Layout",
            xaxis_title="Aisle", yaxis_title="Rack/Level",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        legend_cols = st.columns(4)
        for i, (status, color) in enumerate(status_color.items()):
            legend_cols[i].markdown(
                f"<span style='color:{color}'>■</span> {status.capitalize()}",
                unsafe_allow_html=True
            )

    st.divider()

    # ── Mismatch Bins Table ───────────────────────────────────────────────────
    st.markdown("### ⚠️ Bins with Stock Mismatch")
    zone_filter = st.selectbox("Filter by Zone", ["All", "A", "B", "C", "D"], key="mismatch_zone")
    mismatch_df = get_mismatch_bins(zone_filter if zone_filter != "All" else None)

    if mismatch_df.empty:
        st.success("No mismatch bins found.")
    else:
        st.markdown(f"<span style='color:#ef4444;font-weight:600'>{len(mismatch_df)} mismatch bins</span>",
                    unsafe_allow_html=True)
        st.dataframe(
            mismatch_df[["bin_code", "zone", "sku", "mapped_qty", "actual_qty",
                          "variance", "last_audited", "abc_class", "status"]],
            use_container_width=True, hide_index=True
        )
        act_c1, act_c2, act_c3 = st.columns(3)
        with act_c1:
            fix_bin_id = st.number_input("Bin ID", min_value=1, step=1, key="fix_bin_id")
        with act_c2:
            new_mapped = st.number_input("Correct Mapped Qty", min_value=0, step=1, key="fix_mapped_qty")
            if st.button("Fix Mapping"):
                update_bin_mapping(int(fix_bin_id), int(new_mapped))
                st.success("Bin mapping updated.")
                st.rerun()
        with act_c3:
            if st.button("Mark Audited"):
                update_bin_audited(int(fix_bin_id))
                st.success("Audit timestamp updated.")
                st.rerun()

    st.divider()

    # ── ABC Class Audit Tracker ───────────────────────────────────────────────
    st.markdown("### ABC Class Audit Compliance")
    all_bins = get_all_bins()
    if not all_bins.empty:
        abc_cols = st.columns(3)
        abc_info = [
            ("A", "Daily", 1), ("B", "Weekly", 7), ("C", "Monthly", 30)
        ]
        for i, (cls, freq_label, days) in enumerate(abc_info):
            with abc_cols[i]:
                class_bins = all_bins[all_bins["abc_class"] == cls]
                total = len(class_bins)
                from datetime import datetime, timedelta
                cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                audited = len(class_bins[
                    class_bins["last_audited"].notna() &
                    (class_bins["last_audited"] >= cutoff)
                ])
                compliance = int(audited / max(1, total) * 100)
                st.markdown(
                    f"<div class='sigma-card'>"
                    f"<div style='font-size:18px;font-weight:700;color:#00d4aa'>{cls}-Class</div>"
                    f"<div style='font-size:12px;color:#8b949e'>Required: {freq_label}</div>"
                    f"<div style='font-size:13px'>{total} bins | {audited} audited</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.progress(compliance / 100, text=f"{compliance}% compliant")

    st.divider()

    # ── Add/Update Bin ────────────────────────────────────────────────────────
    with st.expander("➕ Add / Update Bin Mapping"):
        with st.form("add_bin_form"):
            bc1, bc2 = st.columns(2)
            with bc1:
                bin_code = st.text_input("Bin Code (e.g. A-03-R2-L1)")
                zone_inp = st.selectbox("Zone", ["A", "B", "C", "D"])
                sku_inp = st.text_input("SKU")
            with bc2:
                mapped_inp = st.number_input("Mapped Qty", min_value=0, value=0)
                actual_inp = st.number_input("Actual Qty", min_value=0, value=0)
                abc_inp = st.selectbox("ABC Class", ["A", "B", "C"])
            if st.form_submit_button("Save Bin"):
                insert_bin({
                    "bin_code": bin_code, "zone": zone_inp, "sku": sku_inp,
                    "mapped_qty": int(mapped_inp), "actual_qty": int(actual_inp),
                    "abc_class": abc_inp
                })
                st.success(f"Bin {bin_code} saved.")
                st.rerun()

    # ── Fix Checklist ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### Six Sigma Fixes — Bin Location Module")
    fixes_df = get_fix_checklists("bin")
    if not fixes_df.empty:
        done = int(fixes_df["is_done"].sum())
        st.progress(done / len(fixes_df))
        st.markdown(f"**{done} of {len(fixes_df)} fixes implemented**")
        for _, row in fixes_df.iterrows():
            checked = st.checkbox(row["fix_item"], value=bool(row["is_done"]),
                                   key=f"bin_fix_{row['id']}")
            if checked != bool(row["is_done"]):
                update_fix_item(row["id"], int(checked))
                st.rerun()
            if row["is_done"] and row["owner"]:
                st.caption(f"  ✅ {row['owner']} — {row['implemented_date'] or 'N/A'}")
