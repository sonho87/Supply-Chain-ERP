import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sigmaops.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS grn_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grn_number TEXT NOT NULL,
        sku TEXT NOT NULL,
        vendor TEXT NOT NULL,
        expected_qty INTEGER,
        received_qty INTEGER,
        discrepancy INTEGER,
        entry_method TEXT,
        verified_step1 INTEGER DEFAULT 0,
        verified_step2 INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS bin_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bin_code TEXT UNIQUE NOT NULL,
        zone TEXT NOT NULL,
        aisle TEXT,
        rack TEXT,
        level TEXT,
        sku TEXT,
        mapped_qty INTEGER DEFAULT 0,
        actual_qty INTEGER DEFAULT 0,
        variance INTEGER,
        abc_class TEXT DEFAULT 'B',
        last_audited TEXT,
        status TEXT DEFAULT 'active'
    );

    CREATE TABLE IF NOT EXISTS picking_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        sku TEXT NOT NULL,
        sku_description TEXT,
        required_qty INTEGER,
        picked_qty INTEGER DEFAULT 0,
        bin_code TEXT,
        picker_id TEXT,
        pick_method TEXT DEFAULT 'manual',
        double_checked INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        error_type TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS dispatch_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        carrier TEXT,
        scheduled_slot TEXT,
        staging_done INTEGER DEFAULT 0,
        docs_ready INTEGER DEFAULT 0,
        truck_arrived TEXT,
        loading_started TEXT,
        dispatched_at TEXT,
        delay_minutes INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending'
    );

    CREATE TABLE IF NOT EXISTS inventory_snapshot (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL,
        description TEXT,
        category TEXT,
        system_qty INTEGER,
        physical_qty INTEGER,
        variance INTEGER,
        variance_pct REAL,
        last_cycle_count TEXT,
        count_frequency TEXT DEFAULT 'weekly',
        status TEXT DEFAULT 'matched',
        root_cause TEXT
    );

    CREATE TABLE IF NOT EXISTS dead_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL,
        description TEXT,
        category TEXT,
        warehouse_location TEXT,
        qty_on_hand INTEGER,
        unit_cost REAL,
        total_value REAL,
        last_movement_date TEXT,
        days_no_movement INTEGER,
        aging_bucket TEXT,
        recommended_action TEXT,
        status TEXT DEFAULT 'active'
    );

    CREATE TABLE IF NOT EXISTS kpi_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_date TEXT DEFAULT CURRENT_DATE,
        picking_accuracy_pct REAL,
        inventory_accuracy_pct REAL,
        grn_error_pct REAL,
        dispatch_tat_hours REAL,
        dead_stock_value REAL,
        orders_processed INTEGER,
        orders_on_time INTEGER,
        grn_entries_total INTEGER,
        grn_errors_total INTEGER
    );

    CREATE TABLE IF NOT EXISTS dmaic_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        module TEXT NOT NULL,
        current_phase TEXT DEFAULT 'define',
        define_complete INTEGER DEFAULT 0,
        measure_complete INTEGER DEFAULT 0,
        analyze_complete INTEGER DEFAULT 0,
        improve_complete INTEGER DEFAULT 0,
        control_complete INTEGER DEFAULT 0,
        owner TEXT,
        target_metric TEXT,
        baseline_value REAL,
        target_value REAL,
        current_value REAL,
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module TEXT NOT NULL,
        severity TEXT DEFAULT 'info',
        title TEXT NOT NULL,
        description TEXT,
        is_read INTEGER DEFAULT 0,
        is_resolved INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS root_cause_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module TEXT NOT NULL,
        issue_description TEXT NOT NULL,
        root_cause TEXT,
        why_1 TEXT,
        why_2 TEXT,
        why_3 TEXT,
        why_4 TEXT,
        why_5 TEXT,
        corrective_action TEXT,
        preventive_action TEXT,
        logged_by TEXT,
        status TEXT DEFAULT 'open',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS fix_checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module TEXT NOT NULL,
        fix_item TEXT NOT NULL,
        is_done INTEGER DEFAULT 0,
        owner TEXT,
        implemented_date TEXT
    );
    """)

    conn.commit()
    conn.close()


# ─── GRN Queries ────────────────────────────────────────────────────────────

def get_all_grn(filters=None):
    conn = get_connection()
    query = "SELECT * FROM grn_entries"
    params = []
    if filters:
        clauses = []
        if filters.get("status"):
            placeholders = ",".join("?" * len(filters["status"]))
            clauses.append(f"status IN ({placeholders})")
            params.extend(filters["status"])
        if filters.get("vendor"):
            clauses.append("vendor = ?")
            params.append(filters["vendor"])
        if filters.get("entry_method"):
            clauses.append("entry_method = ?")
            params.append(filters["entry_method"])
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY ABS(discrepancy) DESC"
    import pandas as pd
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_grn_stats_today():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM grn_entries WHERE DATE(created_at) = DATE('now')")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM grn_entries WHERE DATE(created_at) = DATE('now') AND status='verified'")
    verified = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM grn_entries WHERE DATE(created_at) = DATE('now') AND status='flagged'")
    flagged = c.fetchone()[0]
    conn.close()
    return {"total": total, "verified": verified, "flagged": flagged}


def get_pending_verification():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query(
        "SELECT * FROM grn_entries WHERE status='pending' OR (verified_step1=1 AND verified_step2=0) ORDER BY created_at DESC",
        conn
    )
    conn.close()
    return df


def insert_grn_entry(data: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO grn_entries (grn_number, sku, vendor, expected_qty, received_qty,
            discrepancy, entry_method, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data["grn_number"], data["sku"], data["vendor"], data["expected_qty"],
          data["received_qty"], data["discrepancy"], data["entry_method"], data["status"]))
    conn.commit()
    conn.close()


def update_grn_verification(grn_id, step):
    conn = get_connection()
    c = conn.cursor()
    if step == 1:
        c.execute("UPDATE grn_entries SET verified_step1=1 WHERE id=?", (grn_id,))
    elif step == 2:
        c.execute("UPDATE grn_entries SET verified_step2=1, status='verified' WHERE id=?", (grn_id,))
    conn.commit()
    conn.close()


def update_grn_status(grn_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE grn_entries SET status=? WHERE id=?", (status, grn_id))
    conn.commit()
    conn.close()


def get_grn_error_trend(days=14):
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("""
        SELECT DATE(created_at) as date,
               COUNT(*) as total,
               SUM(CASE WHEN status='flagged' OR status='rejected' THEN 1 ELSE 0 END) as errors
        FROM grn_entries
        WHERE DATE(created_at) >= DATE('now', ?)
        GROUP BY DATE(created_at)
        ORDER BY date
    """, conn, params=(f"-{days} days",))
    conn.close()
    if not df.empty:
        df["error_pct"] = (df["errors"] / df["total"] * 100).round(2)
    return df


# ─── Bin Location Queries ────────────────────────────────────────────────────

def get_all_bins(zone=None):
    conn = get_connection()
    import pandas as pd
    if zone:
        df = pd.read_sql_query("SELECT * FROM bin_locations WHERE zone=? ORDER BY bin_code", conn, params=(zone,))
    else:
        df = pd.read_sql_query("SELECT * FROM bin_locations ORDER BY bin_code", conn)
    conn.close()
    return df


def get_mismatch_bins(zone=None):
    conn = get_connection()
    import pandas as pd
    if zone:
        df = pd.read_sql_query("SELECT * FROM bin_locations WHERE status='mismatch' AND zone=? ORDER BY ABS(variance) DESC", conn, params=(zone,))
    else:
        df = pd.read_sql_query("SELECT * FROM bin_locations WHERE status='mismatch' ORDER BY ABS(variance) DESC", conn)
    conn.close()
    return df


def get_zone_summary():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("""
        SELECT zone,
               COUNT(*) as total_bins,
               SUM(CASE WHEN status='mismatch' THEN 1 ELSE 0 END) as mismatch_count,
               SUM(CASE WHEN status='empty' THEN 1 ELSE 0 END) as empty_count,
               MAX(last_audited) as last_audited
        FROM bin_locations
        GROUP BY zone ORDER BY zone
    """, conn)
    conn.close()
    return df


def update_bin_mapping(bin_id, mapped_qty):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE bin_locations SET mapped_qty=?, variance=actual_qty-? WHERE id=?",
              (mapped_qty, mapped_qty, bin_id))
    conn.commit()
    conn.close()


def update_bin_audited(bin_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE bin_locations SET last_audited=CURRENT_TIMESTAMP WHERE id=?", (bin_id,))
    conn.commit()
    conn.close()


def insert_bin(data: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO bin_locations
        (bin_code, zone, aisle, rack, level, sku, mapped_qty, actual_qty, variance, abc_class, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (data["bin_code"], data["zone"], data.get("aisle"), data.get("rack"), data.get("level"),
          data.get("sku"), data.get("mapped_qty", 0), data.get("actual_qty", 0),
          data.get("actual_qty", 0) - data.get("mapped_qty", 0),
          data.get("abc_class", "B"), data.get("status", "active")))
    conn.commit()
    conn.close()


# ─── Picking Order Queries ───────────────────────────────────────────────────

def get_all_picking_orders(status_filter=None):
    conn = get_connection()
    import pandas as pd
    if status_filter:
        placeholders = ",".join("?" * len(status_filter))
        df = pd.read_sql_query(
            f"SELECT * FROM picking_orders WHERE status IN ({placeholders}) ORDER BY created_at DESC",
            conn, params=status_filter
        )
    else:
        df = pd.read_sql_query("SELECT * FROM picking_orders ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_picking_stats_today():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM picking_orders WHERE DATE(created_at) = DATE('now')")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM picking_orders WHERE DATE(created_at) = DATE('now') AND status='picked'")
    picked = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM picking_orders WHERE DATE(created_at) = DATE('now') AND status='error'")
    errors = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM picking_orders WHERE status='pending'")
    pending = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM picking_orders WHERE status='in_progress'")
    in_progress = c.fetchone()[0]
    conn.close()
    accuracy = round((picked / total * 100), 2) if total > 0 else 0
    return {"total": total, "picked": picked, "errors": errors, "pending": pending,
            "in_progress": in_progress, "accuracy": accuracy}


def update_picking_status(order_id, status, picked_qty=None, error_type=None):
    conn = get_connection()
    c = conn.cursor()
    if status == "picked":
        c.execute("""UPDATE picking_orders SET status=?, picked_qty=?, completed_at=CURRENT_TIMESTAMP
                     WHERE id=?""", (status, picked_qty, order_id))
    elif status == "error":
        c.execute("UPDATE picking_orders SET status=?, error_type=? WHERE id=?",
                  (status, error_type, order_id))
    else:
        c.execute("UPDATE picking_orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()


def get_picker_performance():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("""
        SELECT picker_id,
               COUNT(*) as total_picks,
               SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) as errors,
               ROUND(100.0*(SUM(CASE WHEN status='picked' THEN 1 ELSE 0 END))/COUNT(*),2) as accuracy_pct,
               GROUP_CONCAT(DISTINCT pick_method) as methods
        FROM picking_orders
        GROUP BY picker_id
        ORDER BY accuracy_pct ASC
    """, conn)
    conn.close()
    return df


def get_picking_error_by_sku():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("""
        SELECT sku, sku_description,
               COUNT(*) as error_count
        FROM picking_orders
        WHERE status='error'
        GROUP BY sku ORDER BY error_count DESC LIMIT 10
    """, conn)
    conn.close()
    return df


# ─── Dispatch Order Queries ──────────────────────────────────────────────────

def get_all_dispatch_orders():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("SELECT * FROM dispatch_orders ORDER BY id DESC", conn)
    conn.close()
    return df


def get_dispatch_stats_today():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM dispatch_orders")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM dispatch_orders WHERE status='dispatched'")
    dispatched = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM dispatch_orders WHERE status='delayed' OR delay_minutes > 0")
    delayed = c.fetchone()[0]
    c.execute("SELECT AVG(delay_minutes) FROM dispatch_orders WHERE delay_minutes > 0")
    avg_delay = c.fetchone()[0] or 0
    conn.close()
    return {"total": total, "dispatched": dispatched, "delayed": delayed, "avg_delay": round(avg_delay, 1)}


def update_dispatch_status(order_id, status):
    conn = get_connection()
    c = conn.cursor()
    ts_field = {
        "loading": "loading_started",
        "dispatched": "dispatched_at"
    }.get(status)
    if ts_field:
        c.execute(f"UPDATE dispatch_orders SET status=?, {ts_field}=CURRENT_TIMESTAMP WHERE id=?",
                  (status, order_id))
    else:
        c.execute("UPDATE dispatch_orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()


def get_delay_by_carrier():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("""
        SELECT carrier, AVG(delay_minutes) as avg_delay, COUNT(*) as total_orders,
               SUM(CASE WHEN delay_minutes > 0 THEN 1 ELSE 0 END) as delayed_count
        FROM dispatch_orders
        GROUP BY carrier ORDER BY avg_delay DESC
    """, conn)
    conn.close()
    return df


# ─── Inventory Queries ───────────────────────────────────────────────────────

def get_all_inventory(status_filter=None, category=None):
    conn = get_connection()
    import pandas as pd
    query = "SELECT * FROM inventory_snapshot WHERE 1=1"
    params = []
    if status_filter:
        placeholders = ",".join("?" * len(status_filter))
        query += f" AND status IN ({placeholders})"
        params.extend(status_filter)
    if category and category != "All":
        query += " AND category=?"
        params.append(category)
    query += " ORDER BY ABS(variance_pct) DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_inventory_accuracy():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM inventory_snapshot")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM inventory_snapshot WHERE status='matched'")
    matched = c.fetchone()[0]
    conn.close()
    return round(matched / total * 100, 2) if total > 0 else 0


def get_inventory_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM inventory_snapshot")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM inventory_snapshot WHERE status='matched'")
    matched = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM inventory_snapshot WHERE status='variance_minor'")
    minor = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM inventory_snapshot WHERE status='variance_critical'")
    critical = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM inventory_snapshot WHERE status='unresolved'")
    unresolved = c.fetchone()[0]
    conn.close()
    return {"total": total, "matched": matched, "minor": minor,
            "critical": critical, "unresolved": unresolved}


def update_inventory_count(inv_id, physical_qty, system_qty):
    conn = get_connection()
    c = conn.cursor()
    variance = physical_qty - system_qty
    variance_pct = round(variance / system_qty * 100, 2) if system_qty > 0 else 0
    if abs(variance_pct) > 5:
        status = "variance_critical"
    elif abs(variance_pct) > 0:
        status = "variance_minor"
    else:
        status = "matched"
    c.execute("""UPDATE inventory_snapshot
                 SET physical_qty=?, variance=?, variance_pct=?,
                     status=?, last_cycle_count=CURRENT_TIMESTAMP
                 WHERE id=?""",
              (physical_qty, variance, variance_pct, status, inv_id))
    conn.commit()
    conn.close()
    return status


def get_overdue_cycle_counts():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("""
        SELECT * FROM inventory_snapshot
        WHERE (count_frequency='daily' AND (last_cycle_count IS NULL OR DATE(last_cycle_count) < DATE('now')))
           OR (count_frequency='weekly' AND (last_cycle_count IS NULL OR DATE(last_cycle_count) < DATE('now', '-7 days')))
           OR (count_frequency='monthly' AND (last_cycle_count IS NULL OR DATE(last_cycle_count) < DATE('now', '-30 days')))
        ORDER BY last_cycle_count ASC
    """, conn)
    conn.close()
    return df


# ─── Dead Stock Queries ──────────────────────────────────────────────────────

def get_all_dead_stock(aging_buckets=None, category=None, actions=None):
    conn = get_connection()
    import pandas as pd
    query = "SELECT * FROM dead_stock WHERE 1=1"
    params = []
    if aging_buckets:
        placeholders = ",".join("?" * len(aging_buckets))
        query += f" AND aging_bucket IN ({placeholders})"
        params.extend(aging_buckets)
    if category and category != "All":
        query += " AND category=?"
        params.append(category)
    if actions:
        placeholders = ",".join("?" * len(actions))
        query += f" AND recommended_action IN ({placeholders})"
        params.extend(actions)
    query += " ORDER BY days_no_movement DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_dead_stock_summary():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(total_value) FROM dead_stock")
    row = c.fetchone()
    count, total_val = row[0], row[1] or 0
    c.execute("""SELECT aging_bucket, COUNT(*), SUM(total_value)
                 FROM dead_stock GROUP BY aging_bucket""")
    buckets = {r[0]: {"count": r[1], "value": r[2] or 0} for r in c.fetchall()}
    conn.close()
    return {"count": count, "total_value": total_val, "buckets": buckets}


def update_dead_stock_action(item_id, status, action=None):
    conn = get_connection()
    c = conn.cursor()
    if action:
        c.execute("UPDATE dead_stock SET status=?, recommended_action=? WHERE id=?",
                  (status, action, item_id))
    else:
        c.execute("UPDATE dead_stock SET status=? WHERE id=?", (status, item_id))
    conn.commit()
    conn.close()


# ─── KPI Snapshot Queries ────────────────────────────────────────────────────

def get_kpi_snapshots(days=30):
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query(
        "SELECT * FROM kpi_snapshots ORDER BY snapshot_date DESC LIMIT ?",
        conn, params=(days,)
    )
    conn.close()
    return df.sort_values("snapshot_date") if not df.empty else df


def get_latest_kpi():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM kpi_snapshots ORDER BY snapshot_date DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}


def get_yesterday_kpi():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM kpi_snapshots ORDER BY snapshot_date DESC LIMIT 1 OFFSET 1")
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}


# ─── DMAIC Queries ───────────────────────────────────────────────────────────

def get_all_dmaic_projects():
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query("SELECT * FROM dmaic_projects ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_dmaic_project(project_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM dmaic_projects WHERE id=?", (project_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}


def update_dmaic_phase(project_id, phase, field_updates=None):
    conn = get_connection()
    c = conn.cursor()
    phase_complete_map = {
        "define": ("define_complete", "measure"),
        "measure": ("measure_complete", "analyze"),
        "analyze": ("analyze_complete", "improve"),
        "improve": ("improve_complete", "control"),
        "control": ("control_complete", None),
    }
    complete_field, next_phase = phase_complete_map.get(phase, (None, None))
    if complete_field:
        if next_phase:
            c.execute(f"UPDATE dmaic_projects SET {complete_field}=1, current_phase=? WHERE id=?",
                      (next_phase, project_id))
        else:
            c.execute(f"UPDATE dmaic_projects SET {complete_field}=1, status='closed' WHERE id=?",
                      (project_id,))
    conn.commit()
    conn.close()


def insert_dmaic_project(data: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO dmaic_projects
                 (project_name, module, owner, target_metric, baseline_value, target_value)
                 VALUES (?,?,?,?,?,?)""",
              (data["project_name"], data["module"], data.get("owner"),
               data.get("target_metric"), data.get("baseline_value"), data.get("target_value")))
    conn.commit()
    conn.close()


# ─── Alerts Queries ──────────────────────────────────────────────────────────

def get_alerts(resolved=None, severity=None, limit=20):
    conn = get_connection()
    import pandas as pd
    query = "SELECT * FROM alerts WHERE 1=1"
    params = []
    if resolved is not None:
        query += " AND is_resolved=?"
        params.append(int(resolved))
    if severity:
        query += " AND severity=?"
        params.append(severity)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_critical_alert_count():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM alerts WHERE is_resolved=0 AND severity='critical'")
    count = c.fetchone()[0]
    conn.close()
    return count


def resolve_alert(alert_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE alerts SET is_resolved=1 WHERE id=?", (alert_id,))
    conn.commit()
    conn.close()


def insert_alert(module, severity, title, description=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO alerts (module, severity, title, description) VALUES (?,?,?,?)",
              (module, severity, title, description))
    conn.commit()
    conn.close()


# ─── Root Cause Log Queries ──────────────────────────────────────────────────

def get_root_cause_log(module=None):
    conn = get_connection()
    import pandas as pd
    if module:
        df = pd.read_sql_query(
            "SELECT * FROM root_cause_log WHERE module=? ORDER BY created_at DESC", conn, params=(module,))
    else:
        df = pd.read_sql_query("SELECT * FROM root_cause_log ORDER BY created_at DESC", conn)
    conn.close()
    return df


def insert_root_cause(data: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO root_cause_log
                 (module, issue_description, root_cause, why_1, why_2, why_3, why_4, why_5,
                  corrective_action, preventive_action, logged_by)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (data.get("module"), data.get("issue_description"), data.get("root_cause"),
               data.get("why_1"), data.get("why_2"), data.get("why_3"),
               data.get("why_4"), data.get("why_5"), data.get("corrective_action"),
               data.get("preventive_action"), data.get("logged_by")))
    conn.commit()
    conn.close()


def update_root_cause_status(log_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE root_cause_log SET status=? WHERE id=?", (status, log_id))
    conn.commit()
    conn.close()


# ─── Fix Checklist Queries ───────────────────────────────────────────────────

def get_fix_checklists(module):
    conn = get_connection()
    import pandas as pd
    df = pd.read_sql_query(
        "SELECT * FROM fix_checklists WHERE module=? ORDER BY id", conn, params=(module,))
    conn.close()
    return df


def update_fix_item(item_id, is_done):
    conn = get_connection()
    c = conn.cursor()
    if is_done:
        c.execute("UPDATE fix_checklists SET is_done=1, implemented_date=DATE('now') WHERE id=?", (item_id,))
    else:
        c.execute("UPDATE fix_checklists SET is_done=0, implemented_date=NULL WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
