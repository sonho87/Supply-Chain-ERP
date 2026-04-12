"""Anthropic API integration for AI Root Cause Assistant."""
import os
from dotenv import load_dotenv

load_dotenv()


def get_warehouse_context():
    """Pull latest KPI data to inject as context."""
    try:
        from modules.db import get_latest_kpi
        kpi = get_latest_kpi()
        if not kpi:
            return "KPI data not available."
        return (
            f"Current warehouse stats: "
            f"Picking Accuracy: {kpi.get('picking_accuracy_pct', 'N/A')}%, "
            f"Inventory Accuracy: {kpi.get('inventory_accuracy_pct', 'N/A')}%, "
            f"GRN Error Rate: {kpi.get('grn_error_pct', 'N/A')}%, "
            f"Dispatch TAT: {kpi.get('dispatch_tat_hours', 'N/A')} hrs, "
            f"Dead Stock Value: ₹{kpi.get('dead_stock_value', 0) / 1e7:.2f} Cr"
        )
    except Exception:
        return "KPI data unavailable."


SYSTEM_PROMPT = """You are an expert Six Sigma Black Belt and Warehouse Operations Consultant \
with 20 years of hands-on experience working at Amazon Fulfillment Centers, DHL Supply Chain India, \
Walmart Distribution Centers, and Flipkart Logistics. You have physically managed warehouse floors, \
resolved GRN crises at 2am, redesigned bin systems, trained picker teams, and built KPI dashboards \
for C-suite reviews. You know every failure mode in a warehouse and its root cause from experience, \
not textbooks.

When analyzing a problem:
1. Always identify the most probable root cause first based on operational experience
2. Walk through the 5-Why chain clearly — each step must logically lead to the next
3. Distinguish between immediate cause and systemic root cause
4. Give corrective actions that are specific and implementable on a warehouse floor
5. Give preventive actions that address the system, not just the symptom
6. Recommend which KPI to watch and what the target should be
7. Suggest which DMAIC phase this problem is in

Be direct, practical, and operational. Speak like a warehouse veteran, not a consultant.

Format your response with clear sections:
**Root Cause Summary:** (1-2 sentences)
**5-Why Chain:**
1. Why...
2. Why...
3. Why...
4. Why...
5. Root Cause: ...

**Corrective Actions:**
1. ...
2. ...

**Preventive Actions:**
1. ...
2. ...

**KPIs to Monitor:** (bullet list with targets)
**DMAIC Phase:** (which phase this problem is in and why)"""


def get_ai_response(user_message: str, conversation_history: list) -> str:
    """Call Anthropic API and return response text."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return (
            "**API Key Not Configured**\n\n"
            "To enable the AI Assistant, add your Anthropic API key to the `.env` file:\n"
            "```\nANTHROPIC_API_KEY=your_actual_key_here\n```\n"
            "Get your key at https://console.anthropic.com"
        )

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        warehouse_context = get_warehouse_context()
        system_with_context = SYSTEM_PROMPT + f"\n\n{warehouse_context}"

        messages = conversation_history.copy()
        messages.append({"role": "user", "content": user_message})

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=system_with_context,
            messages=messages,
        )
        return response.content[0].text

    except ImportError:
        return "Anthropic library not installed. Run: pip install anthropic"
    except Exception as e:
        return f"API Error: {str(e)}"


def extract_root_cause_from_response(ai_text: str) -> dict:
    """Extract key sections from AI response for saving to root_cause_log."""
    lines = ai_text.split("\n")
    root_cause = ""
    corrective = ""
    for i, line in enumerate(lines):
        if "Root Cause Summary:" in line or "Root Cause:" in line:
            root_cause = line.split(":", 1)[-1].strip()
        if "Corrective Action" in line and i + 1 < len(lines):
            corrective = lines[i + 1].strip().lstrip("1234567890. ")
    return {"root_cause": root_cause or "See AI analysis", "corrective_action": corrective}
