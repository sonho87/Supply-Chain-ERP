"""AI Root Cause Assistant Page."""
import streamlit as st
import pandas as pd

from modules.ai_assistant import get_ai_response, extract_root_cause_from_response
from modules.db import insert_root_cause


QUICK_PROMPTS = [
    "Analyze today's GRN error spike and give me the root cause",
    "Why is inventory accuracy dropping? Run a 5-Why analysis",
    "Root cause for picking errors in Zone B — what do I fix first?",
    "Run 5-Why on dispatch delays this week",
    "What's causing the dead stock increase? Suggest liquidation actions",
    "Suggest a DMAIC project for inventory mismatch resolution",
]


def render():
    st.markdown(
        "<div class='module-header'>🤖 AI Root Cause Assistant</div>"
        "<div class='module-subtitle'>Six Sigma Black Belt + 20 years warehouse experience, on demand</div>",
        unsafe_allow_html=True
    )
    st.info(
        "Powered by Anthropic Claude. Add your API key to the `.env` file: `ANTHROPIC_API_KEY=your_key`",
        icon="🔑"
    )

    # ── Quick Prompt Buttons ─────────────────────────────────────────────────
    st.markdown("### Quick Analysis Prompts")
    qp_cols = st.columns(3)
    for i, prompt in enumerate(QUICK_PROMPTS):
        with qp_cols[i % 3]:
            if st.button(prompt[:55] + ("..." if len(prompt) > 55 else ""), key=f"qp_{i}"):
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                st.session_state.pending_prompt = prompt

    st.divider()

    # ── Chat Interface ────────────────────────────────────────────────────────
    st.markdown("### Chat with AI Warehouse Expert")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display conversation history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"<div style='display:flex;justify-content:flex-end;margin:8px 0'>"
                f"<div style='background:#1e3a5f;border:1px solid #3b82f6;border-radius:12px 12px 2px 12px;"
                f"padding:10px 14px;max-width:70%;font-size:13px'>{msg['content']}</div></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='display:flex;justify-content:flex-start;margin:8px 0'>"
                f"<div style='background:#161b22;border:1px solid #30363d;border-radius:12px 12px 12px 2px;"
                f"padding:12px 16px;max-width:80%;font-size:13px'>"
                f"<span style='color:#00d4aa;font-size:11px;font-weight:600'>🤖 AI WAREHOUSE EXPERT</span>"
                f"<div style='margin-top:8px'>{msg['content'].replace(chr(10), '<br>')}</div>"
                f"</div></div>",
                unsafe_allow_html=True
            )
            # Save to root cause log button
            col_save, _ = st.columns([1, 4])
            with col_save:
                if st.button("📝 Save to Root Cause Log", key=f"save_rc_{len(st.session_state.messages)}"):
                    extracted = extract_root_cause_from_response(msg["content"])
                    last_user = next(
                        (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"),
                        "AI Analysis"
                    )
                    insert_root_cause({
                        "module": "ai_assistant",
                        "issue_description": last_user[:200],
                        "root_cause": extracted.get("root_cause", "See AI analysis"),
                        "why_1": "AI analysis", "why_2": "", "why_3": "", "why_4": "", "why_5": "",
                        "corrective_action": extracted.get("corrective_action", "See AI response"),
                        "preventive_action": "",
                        "logged_by": "AI Assistant"
                    })
                    st.success("Saved to Root Cause Log.")

    # Handle pending quick prompt
    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pending_prompt
        del st.session_state.pending_prompt
        with st.spinner("Analyzing warehouse data..."):
            history = [{"role": m["role"], "content": m["content"]}
                       for m in st.session_state.messages]
            response = get_ai_response(prompt, history)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Message input
    st.markdown("")
    input_col, btn_col = st.columns([5, 1])
    with input_col:
        user_input = st.text_area(
            "Ask the AI Warehouse Expert:",
            placeholder="Describe a warehouse problem for root cause analysis...",
            height=80, key="ai_input", label_visibility="collapsed"
        )
    with btn_col:
        st.markdown("<div style='margin-top:8px'>", unsafe_allow_html=True)
        send_clicked = st.button("Send", type="primary", use_container_width=True)
        clear_clicked = st.button("Clear", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if send_clicked and user_input.strip():
        with st.spinner("Analyzing..."):
            history = [{"role": m["role"], "content": m["content"]}
                       for m in st.session_state.messages]
            response = get_ai_response(user_input.strip(), history)
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if clear_clicked:
        st.session_state.messages = []
        st.rerun()
