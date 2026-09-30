"""Reusable, safe UI components for ProjectPulse."""

from html import escape
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


ROLE_CONFIGS = {
    "L1_DIRECTOR": {
        "title": "Project Director",
        "scope": "Portfolio oversight · L1–L2",
        "badge_class": "badge-l1",
        "chat_class": "chat-l1",
        "icon": "◆",
        "default_name": "R. K. Baruah",
        "permissions": {"review", "import", "reset", "direct_update"},
    },
    "L3_DISCIPLINE_LEAD": {
        "title": "Discipline Lead",
        "scope": "Package control · L3–L4",
        "badge_class": "badge-l3",
        "chat_class": "chat-l3",
        "icon": "◇",
        "default_name": "Debashis Phukan",
        "permissions": {"review", "import", "direct_update"},
    },
    "L5_SITE_SUPERVISOR": {
        "title": "Site Supervisor",
        "scope": "Field reporting · L5–L6",
        "badge_class": "badge-l5",
        "chat_class": "chat-l5",
        "icon": "●",
        "default_name": "Pranab Saikia",
        "permissions": {"direct_update"},
    },
}


def role_can(role_key: str, permission: str) -> bool:
    """Return whether the selected application role can perform an action."""
    return permission in ROLE_CONFIGS.get(role_key, {}).get("permissions", set())


def clean_html(html_str: str) -> str:
    """Remove indentation so Markdown never interprets HTML as a code block."""
    return "\n".join(line.strip() for line in html_str.strip().splitlines())


def render_header():
    """Render the product hero and live-system state."""
    html = """
    <div class="oil-header">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:18px;position:relative;z-index:1;">
            <div>
                <div class="oil-badge"><span class="live-dot" style="width:6px;height:6px;box-shadow:none;"></span> Live project intelligence</div>
                <div class="hero-title">ProjectPulse Control Room</div>
                <p class="hero-copy">One operational view from field evidence to Primavera-aligned progress, review decisions, and portfolio risk.</p>
            </div>
            <div class="hero-status">
                <span class="live-dot"></span>
                <span><b>Matching engine online</b><br><span style="color:#8297ae;">85% auto-approval gate</span></span>
            </div>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)


def _metric_card(label: str, value: str, foot: str, icon: str, progress: Optional[float] = None) -> str:
    progress_html = ""
    if progress is not None:
        width = max(0.0, min(100.0, float(progress)))
        progress_html = f'<div class="oil-progress-bg"><div class="oil-progress-fill" style="width:{width:.1f}%"></div></div>'
    return clean_html(
        f"""
        <div class="metric-card">
            <div class="metric-top"><span class="metric-label">{escape(label)}</span><span class="metric-icon">{escape(icon)}</span></div>
            <div class="metric-val">{escape(value)}</div>
            {progress_html}
            <div class="metric-foot">{foot}</div>
        </div>
        """
    )


def render_metric_cards(metrics: Dict[str, Any]):
    """Render the top portfolio KPI strip."""
    completion_ratio = (
        metrics["completed_micro"] / metrics["micro_tasks"] * 100
        if metrics["micro_tasks"]
        else 0
    )
    auto_rate = metrics.get("auto_approval_rate", 0.0)
    cards = [
        ("Portfolio progress", f"{metrics['l1_progress']:.1f}%", "Weighted roll-up from <strong>L6 → L1</strong>", "↗", metrics["l1_progress"]),
        ("Field work closed", f"{metrics['completed_micro']} / {metrics['micro_tasks']}", f"<strong>{completion_ratio:.0f}%</strong> of executable nodes", "✓", completion_ratio),
        ("Verification queue", str(metrics["pending_reviews"]), "Items below the confidence gate", "!", None),
        ("Auto-link rate", f"{auto_rate:.0f}%", f"Across <strong>{metrics['total_audits']}</strong> audited updates", "⌁", auto_rate),
    ]
    for col, card in zip(st.columns(4), cards):
        with col:
            st.markdown(_metric_card(*card), unsafe_allow_html=True)


def render_chat_bubble(msg: Dict[str, Any]):
    """Render a chat message while escaping all database/user supplied strings."""
    role_key = msg.get("sender_role", "L5_SITE_SUPERVISOR")
    cfg = ROLE_CONFIGS.get(role_key, ROLE_CONFIGS["L5_SITE_SUPERVISOR"])
    is_update = bool(msg.get("is_field_update", 0))
    confidence = msg.get("confidence_score")
    linked_task = escape(str(msg.get("linked_task_id") or "Unresolved"))

    chip_html = ""
    if is_update and confidence is not None:
        if confidence >= 85.0:
            chip_html = f'<div class="match-chip match-high">✓ Linked to <b>{linked_task}</b> · {float(confidence):.1f}% confidence</div>'
        else:
            chip_html = f'<div class="match-chip match-low">! Review required · {float(confidence):.1f}% confidence</div>'

    bubble_html = f"""
    <div class="chat-bubble {cfg['chat_class']}">
        <div class="chat-sender">
            <span>{cfg['icon']} <b>{escape(str(msg.get('sender_name', 'User')))}</b> <span class="wbs-badge {cfg['badge_class']}">{escape(cfg['title'])}</span></span>
            <span style="color:#71869e;">{escape(str(msg.get('timestamp', '')))}</span>
        </div>
        <div style="color:#dbe7f3;font-size:.9rem;margin-top:7px;line-height:1.5;">{escape(str(msg.get('message_text', '')))}</div>
        {chip_html}
    </div>
    """
    st.markdown(clean_html(bubble_html), unsafe_allow_html=True)


def render_audit_table(audit_records: List[Dict[str, Any]]):
    """Render a compact audit table with consistent labels."""
    if not audit_records:
        st.markdown('<div class="empty-state">No audit records match this filter.</div>', unsafe_allow_html=True)
        return

    rows = []
    for record in audit_records:
        rows.append(
            {
                "ID": f"#{record['id']}",
                "Recorded": record.get("timestamp", ""),
                "Submitted by": record.get("sender_name", ""),
                "Extracted work": record.get("extracted_task") or record.get("raw_input", ""),
                "WBS node": record.get("matched_node_id") or "—",
                "Confidence": f"{float(record.get('confidence_score') or 0):.1f}%",
                "Progress": f"{float(record.get('extracted_progress_pct') or 0):.1f}%",
                "Decision": record.get("status", ""),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
