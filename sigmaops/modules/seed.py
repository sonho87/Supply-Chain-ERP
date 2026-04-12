import sqlite3
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("en_IN")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sigmaops.db")

VENDORS = [
    "Reliance Retail", "Tata CLiQ", "Metro Cash and Carry",
    "Walmart India", "D-Mart", "Big Bazaar Wholesale"
]
CARRIERS = ["DHL", "Bluedart", "Delhivery", "DTDC", "Amazon Logistics", "Ecom Express"]
SLOTS = ["06:00-08:00", "08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]
CATEGORIES = ["Electronics", "FMCG", "Apparel", "Pharma", "Auto Parts"]
SKU_PREFIXES = ["SKU-ELEC", "SKU-FMCG", "SKU-APRL", "SKU-PHRM", "SKU-AUTO"]
CAT_MAP = {
    "SKU-ELEC": "Electronics",
    "SKU-FMCG": "FMCG",
    "SKU-APRL": "Apparel",
    "SKU-PHRM": "Pharma",
    "SKU-AUTO": "Auto Parts",
}
ZONES = ["A", "B", "C", "D"]
PICKERS = [f"PKR-{i:03d}" for i in range(1, 16)]

INDIAN_NAMES = [
    "Rajesh Kumar", "Priya Sharma", "Amit Singh", "Sunita Patel",
    "Rahul Verma", "Deepika Nair", "Vikram Reddy", "Anjali Mishra",
    "Suresh Gupta", "Kavitha Rao"
]


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def table_is_empty(conn, table):
    c = conn.cursor()
    c.execute(f"SELECT COUNT(*) FROM {table}")
    return c.fetchone()[0] == 0


def rand_date(days_back=60):
    return (datetime.now() - timedelta(days=random.randint(0, days_back))).strftime("%Y-%m-%d %H:%M:%S")


def rand_date_only(days_back=90):
    return (datetime.now() - timedelta(days=random.randint(0, days_back))).strftime("%Y-%m-%d")


def seed_grn(conn):
    if not table_is_empty(conn, "grn_entries"):
        return
    c = conn.cursor()
    statuses = (["verified"] * 84 + ["flagged"] * 18 + ["pending"] * 12 + ["rejected"] * 6)
    random.shuffle(statuses)
    for i in range(120):
        grn_num = f"GRN-2024-{1000 + i}"
        prefix = random.choice(SKU_PREFIXES)
        sku = f"{prefix}-{random.randint(1, 99):04d}"
        vendor = random.choice(VENDORS)
        expected = random.randint(50, 500)
        status = statuses[i]
        if status in ("flagged", "rejected"):
            discrepancy = random.choice([-1, 1]) * random.randint(5, 50)
        elif status == "pending":
            discrepancy = random.choice([0, random.randint(-3, 3)])
        else:
            discrepancy = 0
        received = expected + discrepancy
        method = "barcode" if random.random() < 0.8 else "manual"
        v1 = 1 if status == "verified" else (1 if random.random() < 0.5 else 0)
        v2 = 1 if status == "verified" else 0
        created = rand_date(60)
        c.execute("""INSERT INTO grn_entries
                     (grn_number, sku, vendor, expected_qty, received_qty, discrepancy,
                      entry_method, verified_step1, verified_step2, status, created_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                  (grn_num, sku, vendor, expected, received, discrepancy,
                   method, v1, v2, status, created))
    conn.commit()


def seed_bin_locations(conn):
    if not table_is_empty(conn, "bin_locations"):
        return
    c = conn.cursor()
    statuses_pool = ["active"] * 72 + ["mismatch"] * 30 + ["empty"] * 12 + ["locked"] * 6
    abc_pool = ["A"] * 36 + ["B"] * 60 + ["C"] * 24
    random.shuffle(statuses_pool)
    random.shuffle(abc_pool)
    idx = 0
    for zone in ZONES:
        for j in range(30):
            aisle = f"{random.randint(1, 10):02d}"
            rack = f"R{random.randint(1, 5)}"
            level = f"L{random.randint(1, 4)}"
            bin_code = f"{zone}-{aisle}-{rack}-{level}"
            status = statuses_pool[idx]
            abc = abc_pool[idx]
            idx += 1
            prefix = random.choice(SKU_PREFIXES)
            sku = f"{prefix}-{random.randint(1, 99):04d}" if status != "empty" else None
            mapped_qty = random.randint(10, 300) if status != "empty" else 0
            if status == "mismatch":
                diff = random.choice([-1, 1]) * random.randint(5, 50)
                actual_qty = mapped_qty + diff
            else:
                actual_qty = mapped_qty
            variance = actual_qty - mapped_qty
            last_audited = rand_date_only(14) if random.random() > 0.2 else None
            c.execute("""INSERT OR IGNORE INTO bin_locations
                         (bin_code, zone, aisle, rack, level, sku, mapped_qty, actual_qty,
                          variance, abc_class, last_audited, status)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (bin_code, zone, aisle, rack, level, sku, mapped_qty, actual_qty,
                       variance, abc, last_audited, status))
    conn.commit()


def seed_picking_orders(conn):
    if not table_is_empty(conn, "picking_orders"):
        return
    c = conn.cursor()
    statuses = (["picked"] * 50 + ["in_progress"] * 20 + ["error"] * 15 +
                ["pending"] * 10 + ["cancelled"] * 5)
    random.shuffle(statuses)
    error_types = ["wrong_item"] * 40 + ["wrong_qty"] * 35 + ["wrong_bin"] * 25
    error_idx = 0
    for i in range(100):
        order_id = f"ORD-2024-{3000 + i}"
        prefix = random.choice(SKU_PREFIXES)
        sku = f"{prefix}-{random.randint(1, 99):04d}"
        desc = f"{CAT_MAP[prefix]} Product {random.randint(100, 999)}"
        required = random.randint(1, 50)
        status = statuses[i]
        picked = required if status == "picked" else (random.randint(0, required) if status in ("in_progress", "error") else 0)
        zone = random.choice(ZONES)
        bin_code = f"{zone}-{random.randint(1, 10):02d}-R{random.randint(1, 5)}-L{random.randint(1, 4)}"
        picker = random.choice(PICKERS)
        method = "barcode_scan" if random.random() < 0.6 else "manual"
        double_checked = 1 if status == "picked" and random.random() < 0.7 else 0
        error_type = None
        if status == "error":
            error_type = error_types[error_idx % len(error_types)]
            error_idx += 1
        created = rand_date(30)
        completed = rand_date(10) if status == "picked" else None
        c.execute("""INSERT INTO picking_orders
                     (order_id, sku, sku_description, required_qty, picked_qty, bin_code,
                      picker_id, pick_method, double_checked, status, error_type, created_at, completed_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (order_id, sku, desc, required, picked, bin_code, picker,
                   method, double_checked, status, error_type, created, completed))
    conn.commit()


def seed_dispatch_orders(conn):
    if not table_is_empty(conn, "dispatch_orders"):
        return
    c = conn.cursor()
    statuses = (["dispatched"] * 24 + ["staged"] * 15 + ["loading"] * 12 +
                ["pending"] * 6 + ["delayed"] * 3)
    random.shuffle(statuses)
    for i in range(60):
        order_id = f"DORD-2024-{5000 + i}"
        carrier = random.choice(CARRIERS)
        slot = random.choice(SLOTS)
        status = statuses[i]
        staging = 1 if status in ("staged", "loading", "dispatched") else 0
        docs = 1 if status in ("loading", "dispatched") else (1 if random.random() < 0.5 else 0)
        truck = rand_date(5) if status not in ("pending",) else None
        loading_started = rand_date(3) if status in ("loading", "dispatched") else None
        dispatched_at = rand_date(2) if status == "dispatched" else None
        delay = random.randint(30, 180) if status == "delayed" else (
            random.randint(0, 45) if status == "dispatched" and random.random() < 0.2 else 0)
        c.execute("""INSERT INTO dispatch_orders
                     (order_id, carrier, scheduled_slot, staging_done, docs_ready,
                      truck_arrived, loading_started, dispatched_at, delay_minutes, status)
                     VALUES (?,?,?,?,?,?,?,?,?,?)""",
                  (order_id, carrier, slot, staging, docs, truck, loading_started,
                   dispatched_at, delay, status))
    conn.commit()


def seed_inventory(conn):
    if not table_is_empty(conn, "inventory_snapshot"):
        return
    c = conn.cursor()
    statuses = (["matched"] * 90 + ["variance_minor"] * 30 + ["variance_critical"] * 22 +
                ["unresolved"] * 8)
    random.shuffle(statuses)
    cat_pool = (["Electronics"] * 45 + ["FMCG"] * 38 + ["Apparel"] * 30 +
                ["Pharma"] * 22 + ["Auto Parts"] * 15)
    random.shuffle(cat_pool)
    root_causes_pool = [
        "GRN entry error", "Picking discrepancy", "Returns not logged",
        "Transfer not updated", "Damage write-off pending", None
    ]
    freq_pool = ["daily", "weekly", "monthly"]
    for i in range(150):
        prefix = random.choice(SKU_PREFIXES)
        sku = f"{prefix}-{i + 1:04d}"
        cat = cat_pool[i] if i < len(cat_pool) else random.choice(CATEGORIES)
        desc = f"{cat} SKU {i + 1}"
        sys_qty = random.randint(50, 5000)
        status = statuses[i]
        if status == "variance_critical":
            pct = random.uniform(5.1, 20.0)
            variance = int(sys_qty * pct / 100) * random.choice([-1, 1])
        elif status == "variance_minor":
            pct = random.uniform(0.5, 4.9)
            variance = int(sys_qty * pct / 100) * random.choice([-1, 1])
        else:
            variance = 0
            pct = 0.0
        phys_qty = sys_qty + variance
        last_count = rand_date_only(30) if random.random() > 0.1 else None
        freq = random.choice(freq_pool)
        root_cause = random.choice(root_causes_pool) if status != "matched" else None
        c.execute("""INSERT INTO inventory_snapshot
                     (sku, description, category, system_qty, physical_qty, variance,
                      variance_pct, last_cycle_count, count_frequency, status, root_cause)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                  (sku, desc, cat, sys_qty, phys_qty, variance, round(pct, 2),
                   last_count, freq, status, root_cause))
    conn.commit()


def seed_dead_stock(conn):
    if not table_is_empty(conn, "dead_stock"):
        return
    c = conn.cursor()
    aging_pool = (["30_days"] * 24 + ["60_days"] * 24 + ["90_days"] * 20 + ["90_plus"] * 12)
    random.shuffle(aging_pool)
    action_map = {
        "30_days": "monitor",
        "60_days": random.choice(["discount", "return_vendor"]),
        "90_days": "liquidate",
        "90_plus": "write_off",
    }
    for i in range(80):
        prefix = random.choice(SKU_PREFIXES)
        sku = f"{prefix}-DS-{i + 1:03d}"
        cat = CAT_MAP[prefix]
        desc = f"Dead Stock {cat} Item {i + 1}"
        aging = aging_pool[i]
        if aging == "30_days":
            days = random.randint(31, 60)
        elif aging == "60_days":
            days = random.randint(61, 90)
        elif aging == "90_days":
            days = random.randint(91, 180)
        else:
            days = random.randint(181, 365)
        last_move = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        zone = random.choice(ZONES)
        loc = f"{zone}-{random.randint(1, 10):02d}-R{random.randint(1, 5)}-L{random.randint(1, 4)}"
        qty = random.randint(10, 500)
        cost = round(random.uniform(50, 15000), 2)
        total = round(qty * cost, 2)
        action = action_map.get(aging, "monitor")
        if aging == "60_days":
            action = random.choice(["discount", "return_vendor"])
        c.execute("""INSERT INTO dead_stock
                     (sku, description, category, warehouse_location, qty_on_hand, unit_cost,
                      total_value, last_movement_date, days_no_movement, aging_bucket,
                      recommended_action, status)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (sku, desc, cat, loc, qty, cost, total, last_move, days, aging, action, "active"))
    conn.commit()


def seed_kpi_snapshots(conn):
    if not table_is_empty(conn, "kpi_snapshots"):
        return
    c = conn.cursor()
    for d in range(30):
        date = (datetime.now() - timedelta(days=29 - d)).strftime("%Y-%m-%d")
        t = d / 29.0
        pick_acc = 96.5 + t * 2.6 + random.uniform(-0.4, 0.4)
        inv_acc = 93.2 + t * 4.2 + random.uniform(-0.5, 0.5)
        grn_err = 8.5 - t * 6.4 + random.uniform(-0.3, 0.3)
        tat = 31 - t * 9 + random.uniform(-1, 1)
        ds_value = 42000000 - t * 14000000 + random.uniform(-500000, 500000)
        orders = random.randint(200, 450)
        on_time = int(orders * random.uniform(0.88, 0.97))
        grn_total = random.randint(30, 80)
        grn_err_count = max(0, int(grn_total * grn_err / 100))
        c.execute("""INSERT INTO kpi_snapshots
                     (snapshot_date, picking_accuracy_pct, inventory_accuracy_pct,
                      grn_error_pct, dispatch_tat_hours, dead_stock_value,
                      orders_processed, orders_on_time, grn_entries_total, grn_errors_total)
                     VALUES (?,?,?,?,?,?,?,?,?,?)""",
                  (date, round(pick_acc, 2), round(inv_acc, 2), round(max(0.5, grn_err), 2),
                   round(max(18, tat), 1), round(ds_value, 0), orders, on_time,
                   grn_total, grn_err_count))
    conn.commit()


def seed_dmaic_projects(conn):
    if not table_is_empty(conn, "dmaic_projects"):
        return
    c = conn.cursor()
    projects = [
        ("GRN Accuracy Improvement", "grn", "measure", 1, 0, 0, 0, 0,
         "Rajesh Kumar", "GRN Error %", 8.5, 2.0, 4.2),
        ("Bin Location Audit System", "bin", "analyze", 1, 1, 0, 0, 0,
         "Priya Sharma", "Mismatch Bin %", 25.0, 5.0, 18.0),
        ("Picking Accuracy Optimisation", "picking", "improve", 1, 1, 1, 0, 0,
         "Vikram Reddy", "Picking Accuracy %", 96.5, 99.5, 98.2),
        ("Dispatch TAT Reduction", "dispatch", "control", 1, 1, 1, 1, 0,
         "Anjali Mishra", "Dispatch TAT (hrs)", 31.0, 24.0, 25.5),
        ("Inventory Reconciliation", "inventory", "define", 0, 0, 0, 0, 0,
         "Suresh Gupta", "Inventory Accuracy %", 93.2, 98.0, 93.2),
    ]
    for p in projects:
        c.execute("""INSERT INTO dmaic_projects
                     (project_name, module, current_phase, define_complete, measure_complete,
                      analyze_complete, improve_complete, control_complete, owner,
                      target_metric, baseline_value, target_value, current_value)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", p)
    conn.commit()


def seed_alerts(conn):
    if not table_is_empty(conn, "alerts"):
        return
    c = conn.cursor()
    alerts_data = [
        ("grn", "critical", "GRN Error Rate spiked to 7.2% today",
         "18 flagged entries in last 6 hours. Manual entry errors detected across 3 vendors.", 0, 0),
        ("bin", "critical", "Zone C has 18 mismatch bins unresolved",
         "Last audit was 9 days ago. ABC-A class bins overdue for daily check.", 0, 0),
        ("picking", "critical", "Picking accuracy dropped to 96.8% this shift",
         "12 error picks in last 2 hours. PKR-007 and PKR-012 account for 60% of errors.", 0, 0),
        ("dispatch", "critical", "3 shipments missed cut-off window",
         "Bluedart slot 14:00-16:00 missed. Docs not ready was cited as root cause.", 0, 0),
        ("inventory", "critical", "SKU-ELEC-0021 variance critical at -18%",
         "Physical count shows 182 units vs system 222. Investigation required.", 0, 0),
        ("grn", "warning", "Vendor Walmart India — 3 consecutive GRN mismatches",
         "Pattern detected. Recommend vendor audit and reconciliation meeting.", 0, 0),
        ("bin", "warning", "Zone B — 8 bins not audited in 5+ days",
         "A-class bins in Zone B overdue. Picker errors likely in affected aisles.", 0, 0),
        ("picking", "warning", "SKU-ELEC-0034 and SKU-ELEC-0035 confusion — 4 errors this week",
         "Similar SKU codes causing mis-picks. Color coding fix not yet implemented.", 0, 0),
        ("dispatch", "warning", "DHL average delay now 47 mins over 7 days",
         "Trending up from 28 mins last week. Escalate to carrier account manager.", 0, 0),
        ("deadstock", "warning", "Dead stock value exceeded ₹3.5 Cr threshold",
         "60-day bucket grew by ₹18L this week. Monthly review meeting overdue.", 0, 0),
        ("inventory", "info", "Cycle count completed for 42 A-class SKUs",
         "All within tolerance. No critical variances found in today's count.", 0, 1),
        ("grn", "info", "Barcode adoption increased to 84% this week",
         "Target is 90%. Remaining 16% manual entries are high-risk.", 0, 1),
        ("dispatch", "info", "Ecom Express TAT improved by 2.3 hrs this month",
         "Pre-staging checklist implementation showing measurable results.", 0, 1),
        ("picking", "info", "Double-check compliance at 72% this week",
         "Up from 61% last week. Target is 95%. Continue training push.", 0, 1),
        ("bin", "warning", "Zone A audit compliance at 68% this week",
         "Below target of 85%. Assign dedicated audit resource for Zone A.", 0, 0),
    ]
    for a in alerts_data:
        c.execute("""INSERT INTO alerts (module, severity, title, description, is_read, is_resolved)
                     VALUES (?,?,?,?,?,?)""", a)
    conn.commit()


def seed_root_cause_log(conn):
    if not table_is_empty(conn, "root_cause_log"):
        return
    c = conn.cursor()
    entries = [
        ("grn", "GRN discrepancy of -23 units on SKU-FMCG-0045 from D-Mart",
         "2-step verification not mandatory in system",
         "GRN showed -23 unit shortfall on delivery",
         "Receiving team accepted vendor count without physical verification",
         "No mandatory physical count procedure at dock",
         "GRN SOP allows manual entry without system prompt for verification",
         "No 2-step verification enforced for orders above threshold",
         "Implement system-enforced 2-step verification for all GRNs",
         "Update GRN SOP; add automatic flag when discrepancy > 2%",
         "Rajesh Kumar", "closed"),
        ("bin", "Zone C bin C-05-R3-L2 showing -35 variance consistently",
         "SOP gap — inter-zone transfer logging not mandated",
         "Physical count shows 45 units, system shows 80",
         "Stock was moved but transfer not logged in WMS",
         "Transfer team assumed store team would log the movement",
         "No ownership defined for inter-zone transfer logging",
         "Transfer SOP does not specify real-time WMS update requirement",
         "Add WMS inter-zone transfer log step to transfer SOP",
         "Create bin audit alert when variance > 10 units for 48 hours",
         "Priya Sharma", "in_progress"),
        ("picking", "PKR-007 picked SKU-ELEC-0034 instead of SKU-ELEC-0035 — 3 times",
         "Color coding SOP not enforced for new bin assignments",
         "3 mis-picks on similar SKUs within same shift",
         "SKU-ELEC-0034 and SKU-ELEC-0035 look identical to human eye",
         "Bins C-03-R2-L1 and C-03-R2-L2 are physically adjacent",
         "No color coding or visual differentiation on adjacent similar SKUs",
         "Color coding implementation paused due to manpower allocation",
         "Implement color coding on all A-class adjacent similar SKUs immediately",
         "Add similar SKU check to putaway SOP; flag adjacent similar codes",
         "Vikram Reddy", "in_progress"),
        ("dispatch", "Bluedart slot missed — 47 min delay on DORD-2024-5012",
         "No T-24hr carrier confirmation protocol in place",
         "Dispatch delayed 47 minutes on Bluedart slot",
         "Loading could not start — LR/AWB not ready at truck arrival",
         "LR number request sent to Bluedart only 20 mins before slot",
         "No standard lead time for LR request in dispatch SOP",
         "Dispatch team assumes same-day LR request is sufficient",
         "Implement T-24hr LR request protocol for all carrier slots",
         "Add LR readiness check to pre-staging checklist; set reminder alert",
         "Anjali Mishra", "closed"),
        ("inventory", "SKU-ELEC-0021 shows -18% variance after cycle count",
         "UI design flaw — one-tap completion allows incorrect quantity",
         "Physical count: 182 units, WMS: 222 units — 40 unit gap",
         "WMS shows higher qty than physical due to incomplete pick logging",
         "Pickers completing partial picks but logging as full picks",
         "WMS pick completion screen does not force actual quantity entry",
         "Default behavior logs required_qty as picked_qty if picker taps OK",
         "Fix WMS pick completion to require explicit quantity confirmation",
         "Add daily variance alert for A-class SKUs with >3% gap",
         "Suresh Gupta", "open"),
        ("deadstock", "Dead stock value in Electronics grew by 22L this month",
         "Procurement SOP gap — velocity check not linked to forecast data",
         "Electronics dead stock increased 22L in 30 days",
         "PO raised for 800 units of SKU-ELEC-0078 based on Q4 2023 velocity",
         "Q4 2024 demand dropped 40% due to new model launch",
         "Procurement team did not consult demand forecast before PO",
         "No mandatory forecast review step before raising POs above 5L",
         "Freeze POs for SKU-ELEC-0078; initiate vendor return negotiation",
         "Add forecast review gate to procurement SOP for POs above 2L",
         "Kavitha Rao", "in_progress"),
    ]
    for entry in entries:
        c.execute("""INSERT INTO root_cause_log
                     (module, issue_description, root_cause, why_1, why_2, why_3, why_4, why_5,
                      corrective_action, preventive_action, logged_by, status)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", entry)
    conn.commit()


def seed_fix_checklists(conn):
    if not table_is_empty(conn, "fix_checklists"):
        return
    c = conn.cursor()
    items = [
        # GRN fixes
        ("grn", "Implement mandatory 2-step verification for all GRN entries", 1, "Rajesh Kumar", "2024-03-15"),
        ("grn", "Enforce barcode scan for all inward entries — disable manual override", 1, "Rajesh Kumar", "2024-03-20"),
        ("grn", "Install real-time discrepancy alert: flag if variance > 2%", 1, "Priya Sharma", "2024-04-01"),
        ("grn", "Vendor scorecard: track GRN error rate per vendor monthly", 0, "Rajesh Kumar", None),
        # Bin Location fixes
        ("bin", "Implement fixed bin system — one SKU per bin, labelled", 1, "Priya Sharma", "2024-02-28"),
        ("bin", "Daily ABC audit: A-class bins every day, B-class weekly", 1, "Vikram Reddy", "2024-03-05"),
        ("bin", "Real-time bin update SOP: update WMS within 15 mins of movement", 0, "Priya Sharma", None),
        ("bin", "Install bin-level RF scanner — eliminate manual bin updates", 0, "Suresh Gupta", None),
        # Picking fixes
        ("picking", "Color code adjacent similar SKUs — different rack labels", 1, "Vikram Reddy", "2024-03-10"),
        ("picking", "Enforce barcode scan verification before every pick completion", 1, "Vikram Reddy", "2024-03-18"),
        ("picking", "Implement double-check protocol: second scan before packing", 0, "Anjali Mishra", None),
        ("picking", "Rearrange bin layout: separate similar SKUs to different zones", 0, "Priya Sharma", None),
        # Dispatch fixes
        ("dispatch", "Implement T-24hr carrier slot confirmation protocol", 1, "Anjali Mishra", "2024-04-02"),
        ("dispatch", "Pre-staging checklist: all SKUs staged by T-2hr before slot", 1, "Rajesh Kumar", "2024-03-25"),
        ("dispatch", "Documents ready protocol: invoice + LR + AWB by T-1hr", 1, "Anjali Mishra", "2024-04-05"),
        ("dispatch", "Dedicated loading bay allocation: confirm 30 mins before truck", 0, "Suresh Gupta", None),
        # Inventory fixes
        ("inventory", "Implement daily A-class SKU cycle count with WMS update", 1, "Suresh Gupta", "2024-03-08"),
        ("inventory", "Mandatory root cause for all variances > 2% before closure", 0, "Kavitha Rao", None),
        ("inventory", "WMS pick completion: force actual quantity confirmation entry", 0, "Suresh Gupta", None),
        ("inventory", "Monthly full physical count for all critical variance SKUs", 0, "Rajesh Kumar", None),
        # Dead stock fixes
        ("deadstock", "Implement monthly dead stock aging review — mandatory meeting", 1, "Kavitha Rao", "2024-02-15"),
        ("deadstock", "Velocity-based reorder: no PO raised without demand forecast check", 0, "Kavitha Rao", None),
        ("deadstock", "60-day aging triggers automatic discount/liquidation workflow", 0, "Rajesh Kumar", None),
        ("deadstock", "Dead stock vendor return SOP: initiate within 90 days of last movement", 0, "Priya Sharma", None),
    ]
    for item in items:
        c.execute("""INSERT INTO fix_checklists (module, fix_item, is_done, owner, implemented_date)
                     VALUES (?,?,?,?,?)""", item)
    conn.commit()


def run_seed():
    conn = get_conn()
    seed_grn(conn)
    seed_bin_locations(conn)
    seed_picking_orders(conn)
    seed_dispatch_orders(conn)
    seed_inventory(conn)
    seed_dead_stock(conn)
    seed_kpi_snapshots(conn)
    seed_dmaic_projects(conn)
    seed_alerts(conn)
    seed_root_cause_log(conn)
    seed_fix_checklists(conn)
    conn.close()


if __name__ == "__main__":
    from modules.db import init_db
    init_db()
    run_seed()
    print("Seed completed successfully.")
