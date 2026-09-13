"""Reusable UI Components for SIH PS26122 Streamlit Application."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List

ROLE_CONFIGS = {
    "L1_DIRECTOR": {
        "title": "Project Director / Executive (L1-L2)",
        "badge_class": "badge-l1",
        "chat_class": "chat-l1",
        "icon": "👔",
        "default_name": "R. K. Baruah"
    },
    "L3_DISCIPLINE_LEAD": {
        "title": "Discipline Lead / Manager (L3-L4)",
        "badge_class": "badge-l3",
        "chat_class": "chat-l3",
        "icon": "📐",
        "default_name": "Debashis Phukan (Piping Lead)"
    },
    "L5_SITE_SUPERVISOR": {
        "title": "Site Supervisor / Field Engineer (L5-L6)",
        "badge_class": "badge-l5",
        "chat_class": "chat-l5",
        "icon": "👷",
        "default_name": "Pranab Saikia (Rack-3 Supervisor)"
    }
}

def clean_html(html_str: str) -> str:
    """Strips leading/trailing indentation from each line so Markdown never interprets it as a <pre><code> block."""
    return "\n".join(line.strip() for line in html_str.strip().splitlines())

def render_header():
    """Renders top header banner with Oil India brand aesthetics."""
    html = """
    <div class="oil-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div class="oil-badge">🛢️ Oil India Limited • SIH PS26122</div>
                <h1 style="margin: 8px 0 4px 0; font-size: 1.8rem; font-weight: 800; color: #ffffff;">
                    ProjectPulse — Schedule-Linking System
                </h1>
                <p style="margin: 0; color: #94a3b8; font-size: 0.92rem;">
                    Field-to-schedule linking: regex extraction + fuzzy matching + weighted L6→L1 roll-up.
                </p>
            </div>
            <div style="text-align: right;">
                <span class="wbs-badge status-completed" style="font-size: 0.82rem; padding: 6px 14px;">
                    ● System Live (Threshold: 85%)
                </span>
            </div>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)

def render_metric_cards(metrics: Dict[str, Any]):
    """Renders 4 glassmorphic metric cards across the top."""
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        html1 = f"""
        <div class="metric-card">
            <div class="metric-label">Macro Project Progress (L1)</div>
            <div class="metric-val">{metrics['l1_progress']:.1f}%</div>
            <div class="oil-progress-bg">
                <div class="oil-progress-fill" style="width: {metrics['l1_progress']}%;"></div>
            </div>
        </div>
        """
        st.markdown(clean_html(html1), unsafe_allow_html=True)

    with c2:
        html2 = f"""
        <div class="metric-card">
            <div class="metric-label">Total WBS Elements (L1–L6)</div>
            <div class="metric-val">{metrics['total_tasks']}</div>
            <span style="color: #94a3b8; font-size: 0.78rem;">Hierarchically linked</span>
        </div>
        """
        st.markdown(clean_html(html2), unsafe_allow_html=True)

    with c3:
        html3 = f"""
        <div class="metric-card">
            <div class="metric-label">Executable Tasks (L5/L6)</div>
            <div class="metric-val">{metrics['completed_micro']} / {metrics['micro_tasks']}</div>
            <span style="color: #10b981; font-size: 0.78rem;">Completed micro-nodes</span>
        </div>
        """
        st.markdown(clean_html(html3), unsafe_allow_html=True)

    with c4:
        pending_color = "#ef4444" if metrics['pending_reviews'] > 0 else "#10b981"
        html4 = f"""
        <div class="metric-card">
            <div class="metric-label">Review Queue (&lt; 85%)</div>
            <div class="metric-val" style="color: {pending_color};">{metrics['pending_reviews']}</div>
            <span style="color: #f59e0b; font-size: 0.78rem;">Awaiting manager action</span>
        </div>
        """
        st.markdown(clean_html(html4), unsafe_allow_html=True)

def render_chat_bubble(msg: Dict[str, Any]):
    """Renders an individual chat message with role-based formatting and confidence chip."""
    role_key = msg.get("sender_role", "L5_SITE_SUPERVISOR")
    cfg = ROLE_CONFIGS.get(role_key, ROLE_CONFIGS["L5_SITE_SUPERVISOR"])

    is_update = msg.get("is_field_update", 0)
    conf = msg.get("confidence_score")
    linked_task = msg.get("linked_task_id")

    chip_html = ""
    if is_update:
        if conf and conf >= 85.0:
            chip_html = f'<div class="match-chip match-high">⚡ Auto-Linked to <b>{linked_task}</b> • Confidence: {conf:.1f}% (≥ 85% Auto-Approved)</div>'
        elif conf:
            chip_html = f'<div class="match-chip match-low">⚠️ Match Confidence: {conf:.1f}% (&lt; 85%) • Pushed to Manager Review Queue</div>'

    bubble_html = f"""
    <div class="chat-bubble {cfg['chat_class']}">
        <div class="chat-sender">
            <span>{cfg['icon']} <b>{msg.get('sender_name', 'User')}</b> <span class="wbs-badge {cfg['badge_class']}">{role_key}</span></span>
            <span style="color: #64748b; font-size: 0.75rem;">{msg.get('timestamp', '')}</span>
        </div>
        <div style="color: #e2e8f0; font-size: 0.92rem; margin-top: 4px; line-height: 1.4;">
            {msg.get('message_text', '')}
        </div>
        {chip_html}
    </div>
    """
    st.markdown(clean_html(bubble_html), unsafe_allow_html=True)

def render_audit_table(audit_records: List[Dict[str, Any]]):
    """Renders standardized Audit Table per PS26122 specification."""
    if not audit_records:
        st.info("No field updates recorded in the audit trail yet.")
        return

    table_data = []
    for r in audit_records:
        status = r.get("status", "")
        conf = r.get("confidence_score", 0.0)
        prog = r.get("extracted_progress_pct", 0.0)

        table_data.append({
            "ID": f"#{r['id']}",
            "Timestamp": r.get("timestamp", ""),
            "Sender / Role": f"{r.get('sender_name', '')} ({r.get('sender_role', '')})",
            "Extracted Task Text": r.get("extracted_task") or r.get("raw_input", ""),
            "Matched Node": f"{r.get('matched_node_id', '')}: {r.get('matched_node_name', '')}",
            "Confidence": f"{conf:.1f}%",
            "Calculated %": f"{prog:.1f}%",
            "Decision / Status": status,
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
