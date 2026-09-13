"""Unit tests for SIH PS26122 Intelligent Schedule-Linking Engine."""

import os
import pytest
from database.db_manager import (
    init_db, get_connection, get_all_tasks, get_task_by_id,
    update_task_progress, recalculate_rollup, get_review_queue,
    process_review_queue_item, get_target_tasks_for_matching,
    get_project_summary_metrics
)
from engine.extractor import parse_field_message, extract_progress_pct
from engine.matcher import match_field_update, CONFIDENCE_THRESHOLD

TEST_DB = "test_oil_india.db"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db(force_reseed=True, db_path=TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_extractor_percentages_and_intent():
    msg = "Spool erected on line 24 at Rack 3, completed 80% welding on Joint W-04"
    res = parse_field_message(msg)
    assert res["is_field_update"] is True
    assert res["extracted_progress_pct"] == 80.0
    assert "Line 24" in res["extracted_task"] or "Joint W-04" in res["extracted_task"]
    assert res["discipline_hint"] == "Piping & Mechanical"

def test_extractor_fraction_progress():
    msg = "Cable pulling ongoing, pulled 3 out of 4 segments"
    pct = extract_progress_pct(msg)
    assert pct == 75.0

def test_high_confidence_auto_approval_matching():
    target_tasks = get_target_tasks_for_matching(db_path=TEST_DB)
    query = "Fit-up & Root Pass TIG Welding on Joint W-04 Line 24"
    match = match_field_update(query, target_tasks, discipline_hint="Piping & Mechanical")

    assert match["matched_node_id"] == "OIL-L6-07"
    assert match["confidence_score"] >= CONFIDENCE_THRESHOLD
    assert match["status"] == "AUTO_APPROVED"

def test_low_confidence_pending_review_matching():
    target_tasks = get_target_tasks_for_matching(db_path=TEST_DB)
    # Ambiguous / generic text
    query = "Worked on some equipment near the station"
    match = match_field_update(query, target_tasks)

    assert match["confidence_score"] < CONFIDENCE_THRESHOLD
    assert match["status"] == "PENDING_REVIEW"

def test_hierarchical_rollup_math():
    # Update L6 task OIL-L6-07 (child of OIL-L5-03)
    update_task_progress("OIL-L6-07", 100.0, db_path=TEST_DB)

    l6_task = get_task_by_id("OIL-L6-07", db_path=TEST_DB)
    assert l6_task["progress_pct"] == 100.0
    assert l6_task["status"] == "COMPLETED"

    # Parent L5-03 has children:
    # OIL-L6-06 (weight 0.25, 100%)
    # OIL-L6-07 (weight 0.35, 100%)
    # OIL-L6-08 (weight 0.25, 0%)
    # OIL-L6-09 (weight 0.15, 0%)
    # Expected weighted L5 = (0.25*100 + 0.35*100) / 1.0 = 60.0%
    l5_task = get_task_by_id("OIL-L5-03", db_path=TEST_DB)
    assert l5_task["progress_pct"] == 60.0
    assert l5_task["status"] == "IN_PROGRESS"

    # L1 progress should be > 0
    metrics = get_project_summary_metrics(db_path=TEST_DB)
    assert metrics["l1_progress"] > 0.0

def test_review_queue_approval_workflow():
    from database.db_manager import add_audit_trail_entry

    audit_id = add_audit_trail_entry(
        raw_input="Done some welding on line 24",
        sender_name="Site Worker",
        sender_role="L5_SITE_SUPERVISOR",
        extracted_task="welding line 24",
        extracted_state="IN_PROGRESS",
        extracted_progress_pct=65.0,
        matched_node_id="OIL-L6-07",
        matched_node_name="Fit-up & Root Pass TIG Welding on Joint W-04 Line 24",
        confidence_score=78.0,
        status="PENDING_REVIEW",
        db_path=TEST_DB
    )

    pending = get_review_queue(db_path=TEST_DB)
    assert any(item["id"] == audit_id for item in pending)

    # Discipline Lead reviews and approves
    success = process_review_queue_item(
        audit_id=audit_id,
        decision="APPROVE",
        matched_node_id="OIL-L6-07",
        override_progress_pct=70.0,
        reviewer_name="Lead Engineer",
        review_notes="Verified on site, approved at 70%",
        db_path=TEST_DB
    )
    assert success is True

    # Check that task was updated
    task = get_task_by_id("OIL-L6-07", db_path=TEST_DB)
    assert task["progress_pct"] == 70.0

    # Review queue should no longer contain this item
    pending_after = get_review_queue(db_path=TEST_DB)
    assert not any(item["id"] == audit_id for item in pending_after)
