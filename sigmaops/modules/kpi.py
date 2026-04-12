"""KPI calculation functions for SigmaOps ERP."""
from modules.db import (
    get_latest_kpi, get_yesterday_kpi, get_kpi_snapshots,
    get_inventory_accuracy, get_picking_stats_today,
    get_grn_stats_today, get_dispatch_stats_today, get_dead_stock_summary,
)


def get_kpi_dashboard_data():
    """Return latest + yesterday KPI data for dashboard display."""
    latest = get_latest_kpi()
    yesterday = get_yesterday_kpi()
    return latest, yesterday


def calc_picking_accuracy_delta(latest, yesterday):
    if not latest or not yesterday:
        return 0
    return round(latest.get("picking_accuracy_pct", 0) - yesterday.get("picking_accuracy_pct", 0), 2)


def calc_inventory_accuracy_delta(latest, yesterday):
    if not latest or not yesterday:
        return 0
    return round(latest.get("inventory_accuracy_pct", 0) - yesterday.get("inventory_accuracy_pct", 0), 2)


def calc_grn_error_delta(latest, yesterday):
    if not latest or not yesterday:
        return 0
    return round(latest.get("grn_error_pct", 0) - yesterday.get("grn_error_pct", 0), 2)


def calc_dispatch_tat_delta(latest, yesterday):
    if not latest or not yesterday:
        return 0
    return round(latest.get("dispatch_tat_hours", 0) - yesterday.get("dispatch_tat_hours", 0), 1)


def calc_dead_stock_delta(latest, yesterday):
    if not latest or not yesterday:
        return 0
    return round(
        (latest.get("dead_stock_value", 0) - yesterday.get("dead_stock_value", 0)) / 1e7, 2
    )


def get_kpi_status(kpi_name, value):
    """Return 'green', 'amber', or 'red' based on target."""
    targets = {
        "picking_accuracy": (">=", 99.5),
        "inventory_accuracy": (">=", 98.0),
        "grn_error": ("<=", 2.0),
        "dispatch_tat": ("<=", 24.0),
    }
    if kpi_name not in targets:
        return "grey"
    op, target = targets[kpi_name]
    if op == ">=":
        if value >= target:
            return "green"
        elif value >= target * 0.97:
            return "amber"
        return "red"
    else:
        if value <= target:
            return "green"
        elif value <= target * 1.15:
            return "amber"
        return "red"


def format_inr_crore(value):
    """Format a number as Indian Crore (₹X.XX Cr)."""
    return f"₹{value / 1e7:.2f} Cr"


def get_kpi_scorecard():
    """Return a list of KPI scorecard rows for the KPI Center page."""
    latest = get_latest_kpi()
    yesterday = get_yesterday_kpi()
    snapshots = get_kpi_snapshots(7)

    scorecard = []

    kpis = [
        ("Picking Accuracy %", "picking_accuracy_pct", "picking_accuracy", ">=", 99.5, "%"),
        ("Inventory Accuracy %", "inventory_accuracy_pct", "inventory_accuracy", ">=", 98.0, "%"),
        ("GRN Error %", "grn_error_pct", "grn_error", "<=", 2.0, "%"),
        ("Dispatch TAT (hrs)", "dispatch_tat_hours", "dispatch_tat", "<=", 24.0, "hrs"),
    ]

    for name, field, key, op, target, unit in kpis:
        current = latest.get(field, 0) if latest else 0
        prev = yesterday.get(field, 0) if yesterday else 0
        delta = round(current - prev, 2)
        status = get_kpi_status(key, current)
        trend_vals = snapshots[field].tolist() if field in snapshots.columns else []

        action = ""
        if status == "red":
            action = "Immediate intervention required"
        elif status == "amber":
            action = "Monitor closely — approaching threshold"

        scorecard.append({
            "kpi": name,
            "target": f"{op} {target}{unit}",
            "current": f"{current}{unit}",
            "status": status,
            "delta": delta,
            "trend": trend_vals,
            "action": action,
        })

    return scorecard


def get_module_fix_progress(module):
    """Return fix progress dict for a module."""
    from modules.db import get_fix_checklists
    df = get_fix_checklists(module)
    if df.empty:
        return {"done": 0, "total": 0, "pct": 0}
    done = int(df["is_done"].sum())
    total = len(df)
    return {"done": done, "total": total, "pct": round(done / total * 100)}
