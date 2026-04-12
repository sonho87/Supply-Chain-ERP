"""DMAIC Engine — Project Tracker."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.db import (
    get_all_dmaic_projects, get_dmaic_project,
    update_dmaic_phase, insert_dmaic_project,
)

PHASE_ORDER = ["define", "measure", "analyze", "improve", "control"]
PHASE_COLORS = {
    "define": "#8b949e", "measure": "#3b82f6",
    "analyze": "#f59e0b", "improve": "#7c3aed", "control": "#22c55e"
}
MODULES = ["grn", "bin", "picking", "dispatch", "inventory", "deadstock"]


def render():
    st.markdown(
        "<div class='module-header'>⚙️ DMAIC Project Engine</div>"
        "<div class='module-subtitle'>Define → Measure → Analyze → Improve → Control</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='background:rgba(0,212,170,0.08);border-left:3px solid #00d4aa;"
        "padding:10px 14px;border-radius:6px;color:#00d4aa;font-size:13px;margin-bottom:16px'>"
        "💡 DMAIC is not a certificate. It is a daily discipline.</div>",
        unsafe_allow_html=True
    )
    st.markdown("")

    # ── Project Overview Table ────────────────────────────────────────────────
    st.markdown("### All DMAIC Projects")
    df = get_all_dmaic_projects()
    if not df.empty:
        def calc_pct(row):
            phases = ["define_complete", "measure_complete", "analyze_complete",
                      "improve_complete", "control_complete"]
            return int(sum(row[p] for p in phases if p in row) / 5 * 100)

        df["progress_pct"] = df.apply(calc_pct, axis=1)

        display_cols = ["project_name", "module", "current_phase", "owner",
                        "baseline_value", "target_value", "current_value", "status", "progress_pct"]
        existing = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing], width='stretch', hide_index=True)

    st.divider()

    # ── Project Detail View ───────────────────────────────────────────────────
    if not df.empty:
        project_names = df["project_name"].tolist()
        project_ids = df["id"].tolist()
        sel_proj_name = st.selectbox("Open Project", project_names, key="dmaic_sel_project")
        sel_proj_id = project_ids[project_names.index(sel_proj_name)]

        project = get_dmaic_project(sel_proj_id)
        if project:
            st.markdown(f"### {project['project_name']}")
            badge_cols = st.columns(4)
            badge_cols[0].markdown(
                f"<span style='background:#21262d;color:#00d4aa;padding:4px 10px;"
                f"border-radius:6px'>{project['module'].upper()}</span>",
                unsafe_allow_html=True
            )
            badge_cols[1].markdown(
                f"<span style='background:{PHASE_COLORS.get(project['current_phase'], '#8b949e')}20;"
                f"color:{PHASE_COLORS.get(project['current_phase'], '#8b949e')};"
                f"padding:4px 10px;border-radius:6px'>Phase: {project['current_phase'].capitalize()}</span>",
                unsafe_allow_html=True
            )
            badge_cols[2].markdown(
                f"<span style='color:#8b949e;font-size:13px'>Owner: {project.get('owner', 'N/A')}</span>",
                unsafe_allow_html=True
            )
            status_c = "#22c55e" if project["status"] == "active" else "#8b949e"
            badge_cols[3].markdown(
                f"<span style='color:{status_c}'>{project['status'].upper()}</span>",
                unsafe_allow_html=True
            )

            # Phase Navigator
            st.markdown("#### DMAIC Phase Navigator")
            p_nav = st.columns(5)
            phase_complete_fields = {
                "define": "define_complete", "measure": "measure_complete",
                "analyze": "analyze_complete", "improve": "improve_complete",
                "control": "control_complete"
            }
            for i, phase in enumerate(PHASE_ORDER):
                with p_nav[i]:
                    complete = project.get(phase_complete_fields[phase], 0)
                    is_current = project["current_phase"] == phase
                    icon = "✅" if complete else ("🔄" if is_current else "🔒")
                    color = PHASE_COLORS[phase]
                    st.markdown(
                        f"<div style='text-align:center;border:1px solid {'#30363d' if not is_current else color};"
                        f"border-radius:8px;padding:12px;background:{'rgba(0,212,170,0.05)' if is_current else '#161b22'}'>"
                        f"<div style='font-size:18px'>{icon}</div>"
                        f"<div style='color:{color};font-weight:600;font-size:14px'>{phase[0].upper()}</div>"
                        f"<div style='color:#8b949e;font-size:11px'>{phase.capitalize()}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

            current_phase = project["current_phase"]
            st.markdown(f"#### {current_phase.capitalize()} Phase")

            # Phase panels
            if current_phase == "define":
                with st.form("define_form"):
                    st.text_area("Problem Statement", placeholder="Describe the problem clearly...")
                    st.text_area("Scope — What's IN")
                    st.text_area("Scope — What's OUT")
                    st.text_input("Team Members")
                    st.text_input("Target Metric", value=project.get("target_metric", ""))
                    st.number_input("Target Value", value=float(project.get("target_value") or 0))
                    if st.form_submit_button("✅ Mark Define Complete"):
                        update_dmaic_phase(sel_proj_id, "define")
                        st.success("Define phase complete — advancing to Measure.")
                        st.rerun()

            elif current_phase == "measure":
                with st.form("measure_form"):
                    st.number_input("Baseline Value", value=float(project.get("baseline_value") or 0))
                    st.text_area("Data Collection Plan")
                    st.text_area("Current Process Description")
                    st.text_area("Measurement Gaps Identified")
                    if st.form_submit_button("✅ Mark Measure Complete"):
                        update_dmaic_phase(sel_proj_id, "measure")
                        st.success("Measure phase complete — advancing to Analyze.")
                        st.rerun()

            elif current_phase == "analyze":
                with st.form("analyze_form"):
                    st.text_area("Root Causes Identified")
                    st.text_area("Pareto Analysis Summary")
                    st.text_area("Fishbone Diagram Notes (6Ms: Man, Machine, Method, Material, Measurement, Mother Nature)")
                    st.text_area("Key Finding")
                    if st.form_submit_button("✅ Mark Analyze Complete"):
                        update_dmaic_phase(sel_proj_id, "analyze")
                        st.success("Analyze phase complete — advancing to Improve.")
                        st.rerun()

            elif current_phase == "improve":
                with st.form("improve_form"):
                    st.text_area("Solutions Proposed")
                    st.text_area("Pilot Results")
                    st.number_input("Before Value", value=float(project.get("baseline_value") or 0))
                    after_val = st.number_input("After Value (Post-Improvement)",
                                                value=float(project.get("current_value") or 0))
                    if st.form_submit_button("✅ Mark Improve Complete"):
                        update_dmaic_phase(sel_proj_id, "improve")
                        conn = __import__("modules.db", fromlist=["get_connection"]).get_connection()
                        conn.execute("UPDATE dmaic_projects SET current_value=? WHERE id=?",
                                     (after_val, sel_proj_id))
                        conn.commit()
                        conn.close()
                        st.success("Improve phase complete — advancing to Control.")
                        st.rerun()

            elif current_phase == "control":
                with st.form("control_form"):
                    st.text_area("Control Plan Summary")
                    st.text_area("KPI Monitoring Setup")
                    st.checkbox("SOP Updated?")
                    st.checkbox("Training Completed?")
                    st.date_input("Handover Date")
                    if st.form_submit_button("🏁 Close Project"):
                        update_dmaic_phase(sel_proj_id, "control")
                        st.success("Project closed — DMAIC cycle complete!")
                        st.rerun()

    st.divider()

    # ── New Project Form ──────────────────────────────────────────────────────
    with st.expander("➕ New DMAIC Project"):
        with st.form("new_dmaic_form"):
            nc1, nc2 = st.columns(2)
            with nc1:
                proj_name = st.text_input("Project Name")
                module = st.selectbox("Module", MODULES)
                owner = st.text_input("Owner")
            with nc2:
                target_metric = st.text_input("Target Metric")
                baseline = st.number_input("Baseline Value", value=0.0)
                target = st.number_input("Target Value", value=0.0)
            if st.form_submit_button("Create Project"):
                insert_dmaic_project({
                    "project_name": proj_name, "module": module, "owner": owner,
                    "target_metric": target_metric, "baseline_value": baseline,
                    "target_value": target
                })
                st.success(f"Project '{proj_name}' created.")
                st.rerun()

    st.divider()

    # ── DMAIC Timeline Chart ──────────────────────────────────────────────────
    st.markdown("### DMAIC Project Progress Overview")
    if not df.empty:
        fig = go.Figure()
        for _, row in df.iterrows():
            pct = row.get("progress_pct", 0)
            phase = row.get("current_phase", "define")
            color = PHASE_COLORS.get(phase, "#8b949e")
            fig.add_trace(go.Bar(
                x=[pct], y=[row["project_name"]], orientation="h",
                marker_color=color, showlegend=False,
                text=f"{pct}% | {phase.capitalize()}",
                textposition="inside",
                hovertext=f"Module: {row['module']}<br>Owner: {row['owner']}<br>Status: {row['status']}"
            ))
        fig.update_layout(
            **{**{
                "paper_bgcolor": "#161b22", "plot_bgcolor": "#0d1117",
                "font": dict(color="#e6edf3"), "margin": dict(l=20, r=20, t=30, b=20),
            }},
            height=max(200, len(df) * 50 + 80),
            xaxis=dict(range=[0, 100], title="% Complete",
                        gridcolor="#21262d", tickfont=dict(color="#8b949e")),
            yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e")),
            title="DMAIC Projects — Completion Progress"
        )
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
