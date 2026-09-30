"""Database Manager for ProjectPulse (SIH PS26122 — Oil India Limited)."""

import sqlite3
import os
import math
from datetime import datetime
from typing import List, Dict, Any, Optional
from database.schema import SCHEMA_SQL
from database.seed_data import SEED_TASKS, INITIAL_CHAT_MESSAGES

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "oil_india_p6.db")

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(force_reseed: bool = False, db_path: str = DB_PATH):
    """Initialize database tables and seed with Primavera P6 synthetic dataset."""
    conn = get_connection(db_path)
    with conn:
        conn.executescript(SCHEMA_SQL)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0 or force_reseed:
        with conn:
            conn.execute("DELETE FROM audit_trail")
            conn.execute("DELETE FROM chat_messages")
            conn.execute("DELETE FROM tasks")

            for t in SEED_TASKS:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute(
                    """
                    INSERT INTO tasks (
                        id, code, level, parent_id, name, description,
                        discipline, weight, planned_duration, actual_duration,
                        planned_start, planned_end, progress_pct, status, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        t["id"], t["code"], t["level"], t["parent_id"], t["name"],
                        t["description"], t["discipline"], t["weight"],
                        t["planned_duration"], t["actual_duration"],
                        t["planned_start"], t["planned_end"], t["progress_pct"],
                        t["status"], now_str
                    )
                )

            for m in INITIAL_CHAT_MESSAGES:
                conn.execute(
                    """
                    INSERT INTO chat_messages (
                        channel, sender_name, sender_role, message_text,
                        is_field_update, linked_task_id, confidence_score, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        m["channel"], m["sender_name"], m["sender_role"],
                        m["message_text"], m["is_field_update"], m["linked_task_id"],
                        m["confidence_score"], m["timestamp"]
                    )
                )

        conn.close()
        recalculate_rollup(db_path=db_path)
    else:
        conn.close()

def recalculate_rollup(db_path: str = DB_PATH):
    """Hierarchically calculate weighted progress from L6 up through L5, L4, L3, L2, L1."""
    conn = get_connection(db_path)
    levels = ['L6', 'L5', 'L4', 'L3', 'L2', 'L1']
    child_levels = ['L6', 'L5', 'L4', 'L3', 'L2']

    with conn:
        for parent_level, child_level in zip(['L5', 'L4', 'L3', 'L2', 'L1'], child_levels):
            # Fetch parents at parent_level
            cur = conn.cursor()
            cur.execute("SELECT id FROM tasks WHERE level = ?", (parent_level,))
            parents = cur.fetchall()

            for p in parents:
                parent_id = p["id"]
                # Fetch children
                cur.execute(
                    "SELECT progress_pct, weight FROM tasks WHERE parent_id = ? AND level = ?",
                    (parent_id, child_level)
                )
                children = cur.fetchall()

                if children:
                    total_weight = sum(c["weight"] for c in children if c["weight"] is not None) or 1.0
                    weighted_progress = sum(
                        (c["progress_pct"] or 0.0) * (c["weight"] or 1.0) for c in children
                    ) / total_weight
                    weighted_progress = round(min(100.0, max(0.0, weighted_progress)), 2)

                    # Determine status based on progress
                    if weighted_progress >= 100.0:
                        status = "COMPLETED"
                    elif weighted_progress > 0.0:
                        status = "IN_PROGRESS"
                    else:
                        status = "NOT_STARTED"

                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    conn.execute(
                        """
                        UPDATE tasks
                        SET progress_pct = ?, status = ?, last_updated = ?
                        WHERE id = ?
                        """,
                        (weighted_progress, status, now_str, parent_id)
                    )
    conn.close()

def update_task_progress(
    task_id: str,
    new_progress_pct: float,
    status: Optional[str] = None,
    actual_duration: Optional[int] = None,
    db_path: str = DB_PATH
) -> bool:
    """Updates an individual L5/L6 task's progress and recalculates rollup up to L1."""
    conn = get_connection(db_path)
    new_progress_pct = round(min(100.0, max(0.0, float(new_progress_pct))), 2)

    if not status:
        if new_progress_pct >= 100.0:
            status = "COMPLETED"
        elif new_progress_pct > 0.0:
            status = "IN_PROGRESS"
        else:
            status = "NOT_STARTED"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn:
        if actual_duration is not None:
            conn.execute(
                """
                UPDATE tasks
                SET progress_pct = ?, status = ?, actual_duration = ?, last_updated = ?
                WHERE id = ?
                """,
                (new_progress_pct, status, actual_duration, now_str, task_id)
            )
        else:
            conn.execute(
                """
                UPDATE tasks
                SET progress_pct = ?, status = ?, last_updated = ?
                WHERE id = ?
                """,
                (new_progress_pct, status, now_str, task_id)
            )
    conn.close()

    # Recalculate full hierarchy roll-up
    recalculate_rollup(db_path=db_path)
    return True

def get_all_tasks(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY level, id")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_tasks_by_level(level: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE level = ? ORDER BY id", (level,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_task_by_id(task_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_target_tasks_for_matching(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Returns all L5 and L6 nodes to serve as the target matching index."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, code, level, parent_id, name, description, discipline, progress_pct, status
        FROM tasks
        WHERE level IN ('L5', 'L6')
        ORDER BY level DESC, id
        """
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def add_chat_message(
    sender_name: str,
    sender_role: str,
    message_text: str,
    channel: str = "general",
    is_field_update: int = 0,
    linked_task_id: Optional[str] = None,
    confidence_score: Optional[float] = None,
    timestamp: Optional[str] = None,
    db_path: str = DB_PATH
) -> int:
    conn = get_connection(db_path)
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO chat_messages (
                channel, sender_name, sender_role, message_text,
                is_field_update, linked_task_id, confidence_score, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                channel, sender_name, sender_role, message_text,
                is_field_update, linked_task_id, confidence_score, timestamp
            )
        )
        msg_id = cur.lastrowid
    conn.close()
    return msg_id

def get_chat_messages(limit: int = 100, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM chat_messages ORDER BY id ASC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def add_audit_trail_entry(
    raw_input: str,
    sender_name: str,
    sender_role: str,
    extracted_task: str,
    extracted_state: str,
    extracted_progress_pct: float,
    matched_node_id: Optional[str],
    matched_node_name: Optional[str],
    confidence_score: float,
    status: str,
    message_id: Optional[int] = None,
    reviewed_by: Optional[str] = None,
    review_notes: Optional[str] = None,
    timestamp: Optional[str] = None,
    db_path: str = DB_PATH
) -> int:
    conn = get_connection(db_path)
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO audit_trail (
                message_id, raw_input, sender_name, sender_role,
                extracted_task, extracted_state, extracted_progress_pct,
                matched_node_id, matched_node_name, confidence_score,
                status, reviewed_by, review_notes, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message_id, raw_input, sender_name, sender_role,
                extracted_task, extracted_state, extracted_progress_pct,
                matched_node_id, matched_node_name, confidence_score,
                status, reviewed_by, review_notes, timestamp
            )
        )
        audit_id = cur.lastrowid
    conn.close()
    return audit_id

def get_audit_trail(limit: int = 100, status_filter: Optional[str] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    if status_filter:
        cur.execute("SELECT * FROM audit_trail WHERE status = ? ORDER BY id DESC LIMIT ?", (status_filter, limit))
    else:
        cur.execute("SELECT * FROM audit_trail ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_review_queue(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    return get_audit_trail(limit=100, status_filter="PENDING_REVIEW", db_path=db_path)

def process_review_queue_item(
    audit_id: int,
    decision: str,  # 'APPROVE' or 'REJECT'
    matched_node_id: Optional[str] = None,
    override_progress_pct: Optional[float] = None,
    reviewer_name: str = "Discipline Lead",
    review_notes: str = "",
    db_path: str = DB_PATH
) -> bool:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_trail WHERE id = ?", (audit_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False

    item = dict(row)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with conn:
        if decision == "APPROVE":
            target_node_id = matched_node_id or item["matched_node_id"]
            progress_pct = override_progress_pct if override_progress_pct is not None else item["extracted_progress_pct"]

            cur.execute("SELECT name FROM tasks WHERE id = ?", (target_node_id,))
            target_task = cur.fetchone()
            node_name = target_task["name"] if target_task else item["matched_node_name"]

            conn.execute(
                """
                UPDATE audit_trail
                SET status = 'MANUALLY_APPROVED', matched_node_id = ?, matched_node_name = ?,
                    extracted_progress_pct = ?, reviewed_by = ?, review_notes = ?, timestamp = ?
                WHERE id = ?
                """,
                (target_node_id, node_name, progress_pct, reviewer_name, review_notes, now_str, audit_id)
            )
            success = True

        elif decision == "REJECT":
            conn.execute(
                """
                UPDATE audit_trail
                SET status = 'REJECTED', reviewed_by = ?, review_notes = ?, timestamp = ?
                WHERE id = ?
                """,
                (reviewer_name, review_notes, now_str, audit_id)
            )
            success = True
        else:
            success = False

    conn.close()

    if success and decision == "APPROVE" and target_node_id:
        update_task_progress(target_node_id, progress_pct, db_path=db_path)

    return success

def get_project_summary_metrics(db_path: str = DB_PATH) -> Dict[str, Any]:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cur.fetchone()[0]

    cur.execute("SELECT progress_pct FROM tasks WHERE level = 'L1'")
    row_l1 = cur.fetchone()
    l1_progress = row_l1[0] if row_l1 else 0.0

    cur.execute("SELECT COUNT(*) FROM tasks WHERE level IN ('L5', 'L6')")
    micro_tasks = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tasks WHERE level IN ('L5', 'L6') AND status = 'COMPLETED'")
    completed_micro = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_trail WHERE status = 'PENDING_REVIEW'")
    pending_reviews = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_trail")
    total_audits = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_trail WHERE status = 'AUTO_APPROVED'")
    auto_approved = cur.fetchone()[0]

    auto_approval_rate = round((auto_approved / total_audits) * 100.0, 1) if total_audits else 0.0

    conn.close()
    return {
        "total_tasks": total_tasks,
        "l1_progress": l1_progress,
        "micro_tasks": micro_tasks,
        "completed_micro": completed_micro,
        "pending_reviews": pending_reviews,
        "total_audits": total_audits,
        "auto_approved": auto_approved,
        "auto_approval_rate": auto_approval_rate,
    }


def get_dashboard_insights(db_path: str = DB_PATH) -> Dict[str, Any]:
    """Return compact operational insights for the executive dashboard."""
    tasks = get_all_tasks(db_path=db_path)
    execution_tasks = [task for task in tasks if task["level"] in ("L4", "L5", "L6")]
    at_risk = []
    for task in execution_tasks:
        planned = float(task.get("planned_duration") or 0)
        actual = float(task.get("actual_duration") or 0)
        progress = float(task.get("progress_pct") or 0)
        burn_ratio = actual / planned if planned > 0 else 0.0
        if progress < 100 and (task.get("status") == "DELAYED" or (burn_ratio >= 0.72 and progress < 70)):
            enriched = dict(task)
            enriched["burn_ratio"] = round(burn_ratio * 100, 1)
            at_risk.append(enriched)

    at_risk.sort(key=lambda item: (item["burn_ratio"] - float(item.get("progress_pct") or 0)), reverse=True)
    l2_workfronts = [task for task in tasks if task["level"] == "L2"]
    audit_records = get_audit_trail(limit=8, db_path=db_path)
    confidence_values = [float(item["confidence_score"]) for item in audit_records if item.get("confidence_score") is not None]

    return {
        "at_risk": at_risk[:5],
        "at_risk_count": len(at_risk),
        "l2_workfronts": l2_workfronts,
        "recent_activity": audit_records,
        "recent_avg_confidence": round(sum(confidence_values) / len(confidence_values), 1) if confidence_values else 0.0,
    }


def _clean_import_value(value: Any) -> Any:
    """Normalize spreadsheet nulls without importing pandas in the data layer."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def import_schedule_tasks(records: List[Dict[str, Any]], db_path: str = DB_PATH) -> Dict[str, int]:
    """Validate and upsert Primavera-style schedule rows in one transaction.

    Existing tasks are updated and new tasks are inserted. Parents may be either
    already present in the database or included in the same upload.
    """
    if not records:
        raise ValueError("The upload does not contain any schedule rows.")

    required = {"id", "code", "level", "name", "discipline"}
    valid_levels = {"L1", "L2", "L3", "L4", "L5", "L6"}
    valid_statuses = {"NOT_STARTED", "IN_PROGRESS", "COMPLETED", "DELAYED"}
    normalized = []
    seen_ids = set()

    for index, raw in enumerate(records, start=2):
        row = {key: _clean_import_value(value) for key, value in raw.items()}
        missing = sorted(key for key in required if not row.get(key))
        if missing:
            raise ValueError(f"Row {index}: missing required field(s): {', '.join(missing)}")

        row["id"] = str(row["id"])
        if row["id"] in seen_ids:
            raise ValueError(f"Row {index}: duplicate task id '{row['id']}'.")
        seen_ids.add(row["id"])

        row["level"] = str(row["level"]).upper()
        if row["level"] not in valid_levels:
            raise ValueError(f"Row {index}: level must be L1 through L6.")

        row["status"] = str(row.get("status") or "NOT_STARTED").upper()
        if row["status"] not in valid_statuses:
            raise ValueError(f"Row {index}: invalid status '{row['status']}'.")

        try:
            row["weight"] = float(row.get("weight") if row.get("weight") is not None else 1.0)
            row["progress_pct"] = min(100.0, max(0.0, float(row.get("progress_pct") or 0.0)))
            row["planned_duration"] = max(0, int(float(row.get("planned_duration") or 0)))
            row["actual_duration"] = max(0, int(float(row.get("actual_duration") or 0)))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Row {index}: invalid numeric value ({exc}).") from exc

        normalized.append(row)

    conn = get_connection(db_path)
    try:
        existing_ids = {item[0] for item in conn.execute("SELECT id FROM tasks").fetchall()}
        available_ids = existing_ids | seen_ids
        for index, row in enumerate(normalized, start=2):
            parent_id = row.get("parent_id")
            if row["level"] != "L1" and not parent_id:
                raise ValueError(f"Row {index}: {row['level']} task '{row['id']}' requires a parent_id.")
            if parent_id and parent_id not in available_ids:
                raise ValueError(f"Row {index}: parent_id '{parent_id}' was not found.")

        inserted = 0
        updated = 0
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with conn:
            for row in sorted(normalized, key=lambda item: int(item["level"][1:])):
                exists = row["id"] in existing_ids
                conn.execute(
                    """
                    INSERT INTO tasks (
                        id, code, level, parent_id, name, description, discipline,
                        weight, planned_duration, actual_duration, planned_start,
                        planned_end, progress_pct, status, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        code=excluded.code, level=excluded.level, parent_id=excluded.parent_id,
                        name=excluded.name, description=excluded.description,
                        discipline=excluded.discipline, weight=excluded.weight,
                        planned_duration=excluded.planned_duration,
                        actual_duration=excluded.actual_duration,
                        planned_start=excluded.planned_start, planned_end=excluded.planned_end,
                        progress_pct=excluded.progress_pct, status=excluded.status,
                        last_updated=excluded.last_updated
                    """,
                    (
                        row["id"], row["code"], row["level"], row.get("parent_id"),
                        row["name"], row.get("description"), row["discipline"],
                        row["weight"], row["planned_duration"], row["actual_duration"],
                        row.get("planned_start"), row.get("planned_end"),
                        row["progress_pct"], row["status"], now_str,
                    ),
                )
                updated += int(exists)
                inserted += int(not exists)
    finally:
        conn.close()

    recalculate_rollup(db_path=db_path)
    return {"inserted": inserted, "updated": updated, "total": len(normalized)}
