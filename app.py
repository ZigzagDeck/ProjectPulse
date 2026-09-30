"""ProjectPulse — Field Update & Schedule-Linking System for Infrastructure."""

import streamlit as st
import pandas as pd
from datetime import datetime
from html import escape
from database.db_manager import (
    init_db, get_all_tasks, get_tasks_by_level, get_task_by_id,
    update_task_progress, add_chat_message, get_chat_messages,
    add_audit_trail_entry, get_audit_trail, get_review_queue,
    process_review_queue_item, get_target_tasks_for_matching,
    get_project_summary_metrics, get_dashboard_insights, import_schedule_tasks
)
from engine.extractor import parse_field_message
from engine.matcher import match_field_update, CONFIDENCE_THRESHOLD
from ui.styles import inject_styles
from ui.components import (
    render_header, render_metric_cards, render_chat_bubble,
    render_audit_table, ROLE_CONFIGS, clean_html, role_can
)
from ui.analytics import (
    plot_planned_vs_actual, plot_discipline_progress,
    plot_status_distribution, plot_wbs_sunburst, plot_level_progress, CHART_CONFIG
)

# Set page configuration
st.set_page_config(
    page_title="ProjectPulse • Project Control Room",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db(force_reseed=False)

# Inject custom modern CSS
inject_styles()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-mark"><span>PP</span></div>
            <div class="sidebar-brand-copy"><b>ProjectPulse</b><span>PROJECT CONTROL</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("<div class='eyebrow'>Active workspace</div>", unsafe_allow_html=True)
    selected_role_key = st.selectbox(
        "Operating role",
        options=list(ROLE_CONFIGS.keys()),
        format_func=lambda k: f"{ROLE_CONFIGS[k]['icon']} {ROLE_CONFIGS[k]['title']}",
        index=2  # Default to Site Supervisor
    )
    current_role_cfg = ROLE_CONFIGS[selected_role_key]

    user_name = st.text_input("Signed in as", value=current_role_cfg["default_name"])
    st.caption(current_role_cfg["scope"])

    st.markdown("---")
    st.markdown("<div class='eyebrow'>Governance</div>", unsafe_allow_html=True)
    st.markdown(f"**{CONFIDENCE_THRESHOLD:.0f}%** confidence gate")
    st.caption("High-confidence matches update P6 instantly. Everything else stays in the verification queue.")

    if role_can(selected_role_key, "reset"):
        with st.expander("Advanced controls"):
            if st.button("Reset demonstration data", use_container_width=True):
                init_db(force_reseed=True)
                st.success("Schedule data restored.")
                st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:.72rem;color:#70849b;line-height:1.55;">
            <b style="color:#9fb0c6;">Live data chain</b><br>
            Field report → entity extraction → confidence gate → WBS roll-up → audit record
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- TOP METRICS & BANNER -----------------
render_header()
summary_metrics = get_project_summary_metrics()
render_metric_cards(summary_metrics)
all_tasks = get_all_tasks()
dashboard_insights = get_dashboard_insights()

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# ----------------- MAIN TABS -----------------
tab_overview, tab_chat, tab_wbs, tab_review, tab_analytics, tab_audit, tab_master = st.tabs([
    "Overview",
    "Field updates",
    "WBS schedule",
    f"Review queue · {summary_metrics['pending_reviews']}",
    "Analytics",
    "Audit trail",
    "Schedule data",
])

# ================= TAB 1: EXECUTIVE OVERVIEW =================
with tab_overview:
    st.markdown(
        """
        <div class="section-heading"><div><span class="eyebrow">Command center</span><h3>Project health at a glance</h3><p>Progress, risk, and verification signals distilled for the current shift.</p></div></div>
        """,
        unsafe_allow_html=True,
    )
    overview_chart, overview_focus = st.columns([7, 4], gap="large")
    with overview_chart:
        fig_levels = plot_level_progress(all_tasks)
        if fig_levels:
            st.plotly_chart(fig_levels, use_container_width=True, config=CHART_CONFIG)

    with overview_focus:
        st.markdown("#### Focus now")
        pending = summary_metrics["pending_reviews"]
        if pending:
            st.markdown(
                f'<div class="insight-card attention"><div class="insight-title">{pending} update(s) need verification</div><div class="insight-copy">Resolve low-confidence field evidence before the next schedule cut.</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="insight-card good"><div class="insight-title">Verification queue is clear</div><div class="insight-copy">No ambiguous updates are waiting for a decision.</div></div>', unsafe_allow_html=True)

        risks = dashboard_insights["at_risk"]
        if risks:
            for risk in risks[:2]:
                st.markdown(
                    clean_html(
                        f"""
                        <div class="insight-card critical">
                            <div class="insight-title">{escape(risk['code'])} · low progress against duration</div>
                            <div class="insight-copy">{escape(risk['name'])}<br>{risk['progress_pct']:.0f}% complete · {risk['burn_ratio']:.0f}% of planned duration consumed</div>
                        </div>
                        """
                    ),
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="insight-card good"><div class="insight-title">No duration-pressure flags</div><div class="insight-copy">Active work packages remain inside the configured risk heuristic.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-heading"><div><span class="eyebrow">Portfolio</span><h3>Workfront snapshot</h3></div></div>', unsafe_allow_html=True)
    workfront_cols = st.columns(max(1, len(dashboard_insights["l2_workfronts"])))
    for col, workfront in zip(workfront_cols, dashboard_insights["l2_workfronts"]):
        with col:
            st.markdown(
                clean_html(
                    f"""
                    <div class="panel">
                        <span class="wbs-badge badge-l2">{escape(workfront['code'])}</span>
                        <div style="color:#f4f8fd;font-weight:700;font-size:.9rem;margin:10px 0 3px;min-height:42px;">{escape(workfront['name'])}</div>
                        <div style="font-size:1.45rem;font-weight:700;color:#fff;">{workfront['progress_pct']:.1f}%</div>
                        <div class="oil-progress-bg"><div class="oil-progress-fill" style="width:{workfront['progress_pct']}%;"></div></div>
                        <div style="color:#7890a9;font-size:.71rem;margin-top:8px;">{escape(workfront['discipline'])}</div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    recent_col, signal_col = st.columns([7, 4], gap="large")
    with recent_col:
        st.markdown("#### Recent control activity")
        recent = dashboard_insights["recent_activity"]
        if recent:
            render_audit_table(recent[:5])
        else:
            st.markdown('<div class="empty-state">Field decisions will appear here as updates arrive.</div>', unsafe_allow_html=True)
    with signal_col:
        st.markdown("#### Data quality")
        st.markdown(
            clean_html(
                f"""
                <div class="mini-grid">
                    <div class="mini-stat"><span>Recent match confidence</span><strong>{dashboard_insights['recent_avg_confidence']:.0f}%</strong></div>
                    <div class="mini-stat"><span>Audited updates</span><strong>{summary_metrics['total_audits']}</strong></div>
                    <div class="mini-stat"><span>WBS nodes</span><strong>{summary_metrics['total_tasks']}</strong></div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

# ================= TAB 2: FIELD UPDATES & CHAT =================
with tab_chat:
    c_chat, c_info = st.columns([7, 5])

    with c_chat:
        st.markdown("### Field evidence inbox")
        st.caption(f"Submitting as **{user_name}** · {current_role_cfg['title']}")

        # Chat history container
        messages = get_chat_messages(limit=60)
        chat_container = st.container(height=420)
        with chat_container:
            if not messages:
                st.write("No messages yet. Send a progress update or inquiry below.")
            for m in messages:
                render_chat_bubble(m)

        # Quick sample message buttons
        st.markdown("<span style='font-size: 0.78rem; color: #94a3b8; font-weight: 600;'>⚡ QUICK-TEST SAMPLE MESSAGES:</span>", unsafe_allow_html=True)
        q1, q2, q3 = st.columns(3)
        quick_text = None
        if q1.button("📋 'Line 24 spool welding 80%'"):
            quick_text = "Erected Line 24 spool at bay 1, completed 80% welding on Joint W-04"
        if q2.button("📋 'C-101 plinth curing 100%'"):
            quick_text = "Curing with wet hessian cloth 100% completed on plinth P-101, ready for shimming"
        if q3.button("⚠️ 'Worked on some piping' (<85%)"):
            quick_text = "Did some preliminary fitting work somewhere on the pipe rack"

        # Chat input form
        with st.form("chat_input_form", clear_on_submit=True):
            input_text = st.text_input(
                "Enter field update, supervisor log, or message:",
                value=quick_text if quick_text else "",
                placeholder="e.g. Line 24 spool erected at Rack 3, completed 75% welding on Joint W-04"
            )
            c_sub, _ = st.columns([10, 1])
            with c_sub:
                submitted = st.form_submit_button("🚀 Submit Field Update", use_container_width=True)

        if submitted and input_text.strip():
            # 1. Extraction step
            extracted = parse_field_message(input_text)
            is_update = 1 if extracted["is_field_update"] else 0

            matched_id = None
            matched_name = None
            conf_score = None

            if is_update:
                target_tasks = get_target_tasks_for_matching()
                match_res = match_field_update(
                    extracted["extracted_task"],
                    target_tasks,
                    discipline_hint=extracted["discipline_hint"]
                )
                matched_id = match_res["matched_node_id"]
                matched_name = match_res["matched_node_name"]
                conf_score = match_res["confidence_score"]
                status = match_res["status"]

                # 2. Add chat message
                msg_id = add_chat_message(
                    sender_name=user_name,
                    sender_role=selected_role_key,
                    message_text=input_text,
                    channel="field-updates",
                    is_field_update=is_update,
                    linked_task_id=matched_id,
                    confidence_score=conf_score
                )

                # 3. Add to audit trail
                audit_id = add_audit_trail_entry(
                    raw_input=input_text,
                    sender_name=user_name,
                    sender_role=selected_role_key,
                    extracted_task=extracted["extracted_task"],
                    extracted_state=extracted["extracted_state"],
                    extracted_progress_pct=extracted["extracted_progress_pct"],
                    matched_node_id=matched_id,
                    matched_node_name=matched_name,
                    confidence_score=conf_score,
                    status=status,
                    message_id=msg_id
                )

                # 4. Threshold logic: Auto-update if >= 85%
                if conf_score >= CONFIDENCE_THRESHOLD and matched_id:
                    update_task_progress(matched_id, extracted["extracted_progress_pct"])
                    st.toast(f"✅ Auto-Updated {matched_id} to {extracted['extracted_progress_pct']}% (Confidence: {conf_score}%)", icon="⚡")
                else:
                    st.toast(f"⚠️ Confidence {conf_score}% < 85%. Update sent to Manager Review Queue.", icon="⏳")

            else:
                # Regular message
                add_chat_message(
                    sender_name=user_name,
                    sender_role=selected_role_key,
                    message_text=input_text,
                    channel="general",
                    is_field_update=0
                )
                st.toast("Message sent to channel.", icon="💬")

            st.rerun()

    with c_info:
        info_html = """
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px;">
            <h4 style="margin: 0 0 8px 0; color: #f59e0b; font-size: 0.95rem;">How Field Updates Are Processed:</h4>
            <ol style="color: #cbd5e1; font-size: 0.82rem; margin: 0; padding-left: 18px; line-height: 1.6;">
                <li><b>Entity Extraction:</b> Rule-based regex parser pulls task codes, equipment tags, completion %, and discipline hints from free-text messages.</li>
                <li><b>Fuzzy String Matching:</b> RapidFuzz calculates composite Levenshtein &amp; token similarity against L5/L6 schedule strings.</li>
                <li><b>85% Confidence Gate:</b>
                    <ul>
                        <li><span style="color: #10b981;">≥ 85%</span>: Instantly writes progress to DB and recalculates L6 → L1 rollups.</li>
                        <li><span style="color: #f59e0b;">&lt; 85%</span>: Enters Review Queue for Lead verification without dropping data.</li>
                    </ul>
                </li>
            </ol>
        </div>
        """
        st.markdown(clean_html(info_html), unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("#### Direct task update")
        target_tasks = get_target_tasks_for_matching()
        task_options = {t["id"]: f"[{t['level']}] {t['code']} - {t['name']} ({t['progress_pct']}%)" for t in target_tasks}

        selected_direct_id = st.selectbox("Select Target L5/L6 Task directly:", options=list(task_options.keys()), format_func=lambda k: task_options[k])
        direct_task = get_task_by_id(selected_direct_id)

        if direct_task:
            new_pct = st.slider(f"Adjust progress for {direct_task['code']}:", min_value=0.0, max_value=100.0, value=float(direct_task["progress_pct"]), step=5.0)
            if st.button(f"💾 Update {direct_task['code']} to {new_pct}%", use_container_width=True):
                update_task_progress(selected_direct_id, new_pct)
                add_audit_trail_entry(
                    raw_input=f"Manual direct slider update by {user_name} to {new_pct}%",
                    sender_name=user_name,
                    sender_role=selected_role_key,
                    extracted_task=direct_task["name"],
                    extracted_state="IN_PROGRESS" if new_pct < 100 else "COMPLETED",
                    extracted_progress_pct=new_pct,
                    matched_node_id=selected_direct_id,
                    matched_node_name=direct_task["name"],
                    confidence_score=100.0,
                    status="MANUALLY_APPROVED",
                    reviewed_by=user_name,
                    review_notes="Direct dashboard adjustment"
                )
                st.success(f"Updated {direct_task['code']} and recalculated L1–L6 roll-up!")
                st.rerun()

# ================= TAB 2: WBS SCHEDULE HIERARCHY (L1 TO L6) =================
with tab_wbs:
    st.markdown("### Work breakdown structure")
    st.caption("Search and inspect the live L1–L6 hierarchy. Progress rolls up from executable field tasks.")

    all_tasks = get_all_tasks()

    # Filter controls
    f_col1, f_col2, f_col3 = st.columns([3, 3, 4])
    with f_col1:
        lvl_filter = st.selectbox("Filter by WBS Level:", ["All Levels", "L1 (Project)", "L2 (Plant)", "L3 (Discipline)", "L4 (Work Package)", "L5 (Work Activity)", "L6 (Micro-Task)"])
    with f_col2:
        disciplines = ["All Disciplines"] + sorted(list(set(t["discipline"] for t in all_tasks if t.get("discipline"))))
        disc_filter = st.selectbox("Filter by Discipline:", disciplines)
    with f_col3:
        search_query = st.text_input("🔍 Search task by code, joint, or keyword:", "")

    # Apply filters
    filtered_tasks = all_tasks
    if lvl_filter != "All Levels":
        lvl_code = lvl_filter.split()[0]
        filtered_tasks = [t for t in filtered_tasks if t["level"] == lvl_code]
    if disc_filter != "All Disciplines":
        filtered_tasks = [t for t in filtered_tasks if t["discipline"] == disc_filter]
    if search_query.strip():
        q = search_query.lower()
        filtered_tasks = [t for t in filtered_tasks if q in t["name"].lower() or q in t["code"].lower() or q in t["id"].lower()]

    st.markdown(f"**Showing {len(filtered_tasks)} matching tasks:**")

    for t in filtered_tasks:
        lvl = t["level"]
        badge_class = f"badge-{lvl.lower()}"
        status_class = f"status-{t['status'].lower().replace('_', '')}"

        with st.container():
            wbs_card_html = f"""
            <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span class="wbs-badge {badge_class}">{lvl}</span>
                        <span style="font-family:'IBM Plex Mono',monospace;font-size:.78rem;color:#8fa4bb;margin-left:6px;">{escape(t['code'])} · {escape(t['id'])}</span>
                        <span class="wbs-badge {status_class}" style="margin-left:8px;">{escape(t['status'].replace('_', ' '))}</span>
                        <h4 style="margin:7px 0 3px;color:#fff;font-size:1rem;">{escape(t['name'])}</h4>
                        <p style="margin:0;color:#8fa4bb;font-size:.8rem;">{escape(t.get('description', '') or '')}</p>
                    </div>
                    <div style="text-align: right; min-width: 140px;">
                        <div style="font-size: 1.4rem; font-weight: 800; color: #f59e0b;">{t['progress_pct']:.1f}%</div>
                        <div style="font-size: 0.75rem; color: #64748b;">Weight: {t['weight']} • Parent: {t.get('parent_id') or 'ROOT'}</div>
                    </div>
                </div>
                <div class="oil-progress-bg" style="margin-top: 10px;">
                    <div class="oil-progress-fill" style="width: {t['progress_pct']}%;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b; margin-top: 4px;">
                    <span>Discipline: <b>{escape(t['discipline'])}</b></span>
                    <span>Planned: {t['planned_duration']}d | Actual: {t['actual_duration']}d</span>
                </div>
            </div>
            """
            st.markdown(clean_html(wbs_card_html), unsafe_allow_html=True)

# ================= TAB 3: LIVE AUDIT TRAIL =================
with tab_audit:
    st.markdown("### Live audit trail")
    st.caption("Displays auto-linked and manually verified tasks with exact timestamp, confidence score, extracted metrics, and audit history.")

    col_f1, col_f2 = st.columns([3, 7])
    with col_f1:
        status_filter = st.selectbox("Filter Audit Records by Status:", ["All", "AUTO_APPROVED", "PENDING_REVIEW", "MANUALLY_APPROVED", "REJECTED"])
    filter_val = None if status_filter == "All" else status_filter

    audit_records = get_audit_trail(limit=100, status_filter=filter_val)
    render_audit_table(audit_records)

# ================= TAB 4: MANAGER REVIEW QUEUE =================
with tab_review:
    st.markdown("### Verification queue")
    st.caption("Resolve ambiguous field evidence, remap it to the right WBS node, and preserve every decision in the audit trail.")
    can_review = role_can(selected_role_key, "review")
    if not can_review:
        st.markdown('<div class="permission-note">Read-only for Site Supervisors. Switch to a Discipline Lead or Project Director role to approve or reject evidence.</div>', unsafe_allow_html=True)

    pending_items = get_review_queue()

    if not pending_items:
        st.success("🎉 Review Queue is clear! All recent field updates either exceeded the 85% confidence threshold or have already been reviewed.")
    else:
        st.warning(f"There are **{len(pending_items)} pending updates** requiring verification:")
        target_tasks = get_target_tasks_for_matching()
        task_dict = {t["id"]: f"[{t['level']}] {t['code']} - {t['name']}" for t in target_tasks}

        for item in pending_items:
            audit_id = item["id"]
            with st.container():
                review_card_html = f"""
                <div class="review-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span class="wbs-badge badge-l4">Item #{audit_id} · Pending review</span>
                        <span style="color:#71869e;font-size:.75rem;">{escape(item['timestamp'])}</span>
                    </div>
                    <div style="font-size: 0.95rem; color: #ffffff; margin-bottom: 6px;">
                        <b>Field evidence:</b> “{escape(item['raw_input'])}”
                    </div>
                    <div style="font-size: 0.82rem; color: #94a3b8;">
                        Submitted by <b>{escape(item['sender_name'])}</b> · Extracted work: <code>{escape(item['extracted_task'] or '')}</code>
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="match-chip match-low">
                            Suggested match: <b>{escape(item['matched_node_id'] or 'Unresolved')}</b> · Confidence <b>{item['confidence_score']:.1f}%</b>
                        </span>
                    </div>
                </div>
                """
                st.markdown(clean_html(review_card_html), unsafe_allow_html=True)

                # Review actions form
                with st.expander(f"⚙️ Take Action on Item #{audit_id}", expanded=True):
                    ra1, ra2 = st.columns([6, 6])
                    with ra1:
                        # Remap option if the AI match was slightly off
                        default_node_id = item["matched_node_id"] if item["matched_node_id"] in task_dict else list(task_dict.keys())[0]
                        selected_node = st.selectbox(
                            "Confirm or Remap to Task:",
                            options=list(task_dict.keys()),
                            index=list(task_dict.keys()).index(default_node_id) if default_node_id in task_dict else 0,
                            format_func=lambda k: task_dict[k],
                            key=f"remap_{audit_id}"
                        )
                    with ra2:
                        adjusted_pct = st.number_input(
                            "Verified Progress Percentage (%):",
                            min_value=0.0,
                            max_value=100.0,
                            value=float(item.get("extracted_progress_pct") or 50.0),
                            step=5.0,
                            key=f"pct_{audit_id}"
                        )

                    review_notes = st.text_input("Reviewer Notes / Justification:", value="Verified with site supervisor", key=f"notes_{audit_id}")

                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if st.button("Approve & update schedule", key=f"app_{audit_id}", use_container_width=True, disabled=not can_review):
                            process_review_queue_item(
                                audit_id=audit_id,
                                decision="APPROVE",
                                matched_node_id=selected_node,
                                override_progress_pct=adjusted_pct,
                                reviewer_name=user_name,
                                review_notes=review_notes
                            )
                            st.success(f"Item #{audit_id} approved and applied to {selected_node}!")
                            st.rerun()

                    with btn_c2:
                        if st.button("Reject evidence", key=f"rej_{audit_id}", use_container_width=True, disabled=not can_review):
                            process_review_queue_item(
                                audit_id=audit_id,
                                decision="REJECT",
                                reviewer_name=user_name,
                                review_notes=review_notes
                            )
                            st.warning(f"Item #{audit_id} marked as REJECTED.")
                            st.rerun()

# ================= TAB 5: ANALYTICS & BOTTLENECK DASHBOARD =================
with tab_analytics:
    st.markdown("### Performance analytics")
    st.caption("Compare duration burn, discipline progress, schedule status, and WBS roll-up in one analytical workspace.")

    all_tasks = get_all_tasks()

    an_row1_c1, an_row1_c2 = st.columns(2)
    with an_row1_c1:
        fig_dur = plot_planned_vs_actual(all_tasks)
        if fig_dur:
            st.plotly_chart(fig_dur, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("Planned vs Actual chart available with Plotly.")
    with an_row1_c2:
        fig_disc = plot_discipline_progress(all_tasks)
        if fig_disc:
            st.plotly_chart(fig_disc, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("Discipline progress chart available with Plotly.")

    an_row2_c1, an_row2_c2 = st.columns(2)
    with an_row2_c1:
        fig_stat = plot_status_distribution(all_tasks)
        if fig_stat:
            st.plotly_chart(fig_stat, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("Status distribution chart available with Plotly.")
    with an_row2_c2:
        fig_sun = plot_wbs_sunburst(all_tasks)
        if fig_sun:
            st.plotly_chart(fig_sun, use_container_width=True, config=CHART_CONFIG)
        else:
            st.info("WBS Sunburst chart available with Plotly.")

# ================= TAB 6: MASTER SCHEDULE & INGESTION =================
with tab_master:
    st.markdown("### Schedule data workspace")
    st.caption("Inspect, export, and safely upsert Primavera-style CSV records into the live hierarchy.")

    all_tasks_df = pd.DataFrame(get_all_tasks())
    if not all_tasks_df.empty:
        csv_data = all_tasks_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export live schedule · CSV",
            data=csv_data,
            file_name=f"oil_india_p6_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        st.dataframe(
            all_tasks_df[["id", "code", "level", "parent_id", "name", "discipline", "weight", "progress_pct", "status", "planned_duration", "actual_duration"]],
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.markdown("#### Import schedule changes")
    st.caption("Required columns: id, code, level, name, discipline. Existing IDs are updated; new IDs are inserted after parent validation.")
    can_import = role_can(selected_role_key, "import")
    if not can_import:
        st.markdown('<div class="permission-note">Schedule import is available to Discipline Leads and Project Directors. You can still inspect and export the live schedule.</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a Primavera-style CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            up_df = pd.read_csv(uploaded_file)
            st.write(f"**{len(up_df)} rows ready for validation**")
            st.dataframe(up_df.head(8), use_container_width=True, hide_index=True)
            if st.button("Validate & import schedule", type="primary", disabled=not can_import, use_container_width=True):
                result = import_schedule_tasks(up_df.to_dict(orient="records"))
                st.success(f"Import complete: {result['inserted']} inserted, {result['updated']} updated.")
                st.rerun()
        except Exception as e:
            st.error(f"Import could not be completed: {e}")
