"""SIH PS26122: Intelligent Data Capture & Schedule-Linking Layer for Infrastructure.

Client: Oil India Limited
Streamlit Application Entry Point.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_manager import (
    init_db, get_all_tasks, get_tasks_by_level, get_task_by_id,
    update_task_progress, add_chat_message, get_chat_messages,
    add_audit_trail_entry, get_audit_trail, get_review_queue,
    process_review_queue_item, get_target_tasks_for_matching,
    get_project_summary_metrics
)
from engine.extractor import parse_field_message
from engine.matcher import match_field_update, CONFIDENCE_THRESHOLD
from ui.styles import inject_styles
from ui.components import (
    render_header, render_metric_cards, render_chat_bubble,
    render_audit_table, ROLE_CONFIGS, clean_html
)
from ui.analytics import (
    plot_planned_vs_actual, plot_discipline_progress,
    plot_status_distribution, plot_wbs_sunburst
)

# Set page configuration
st.set_page_config(
    page_title="Oil India Limited • Schedule-Linking Layer",
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
    st.markdown("### 🛢️ Oil India Limited")
    st.markdown("<span style='font-size: 0.8rem; color: #94a3b8;'>PS26122 • Infrastructure AI Layer</span>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("#### 👤 Active User Identity")
    selected_role_key = st.selectbox(
        "Select your Role / Level:",
        options=list(ROLE_CONFIGS.keys()),
        format_func=lambda k: f"{ROLE_CONFIGS[k]['icon']} {ROLE_CONFIGS[k]['title']}",
        index=2  # Default to Site Supervisor
    )
    current_role_cfg = ROLE_CONFIGS[selected_role_key]

    user_name = st.text_input("User Name:", value=current_role_cfg["default_name"])

    st.markdown("---")
    st.markdown("#### ⚙️ System Controls")
    st.markdown(f"**Confidence Threshold**: `{CONFIDENCE_THRESHOLD}%`")
    st.caption(r"Matches $\ge 85\%$ auto-update master P6 schedule. Matches $< 85\%$ enter the Review Queue.")

    if st.button("🔄 Reset / Re-seed Schedule DB", use_container_width=True):
        init_db(force_reseed=True)
        st.success("Database re-seeded with Primavera P6 master schedule!")
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.75rem; color: #64748b; line-height: 1.4;">
            <b>WBS Hierarchy:</b><br>
            • L1: Project Level<br>
            • L2: Facility / Plant<br>
            • L3: Discipline Package<br>
            • L4: Area Work Package<br>
            • L5: Work Activity<br>
            • L6: Executable Daily Task
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- TOP METRICS & BANNER -----------------
render_header()
summary_metrics = get_project_summary_metrics()
render_metric_cards(summary_metrics)

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# ----------------- MAIN TABS -----------------
tab_chat, tab_wbs, tab_audit, tab_review, tab_analytics, tab_master = st.tabs([
    "💬 Time Agent & Field Chat",
    "🏗️ WBS Schedule Hierarchy (L1–L6)",
    "📋 Live Audit Trail",
    f"⚖️ Review Queue ({summary_metrics['pending_reviews']})",
    "📊 Analytics & Bottlenecks",
    "📁 Master Schedule & Ingestion"
])

# ================= TAB 1: TIME AGENT & COLLABORATIVE CHAT =================
with tab_chat:
    c_chat, c_info = st.columns([7, 5])

    with c_chat:
        st.markdown(f"### 💬 Field Collaboration Stream & Time Agent")
        st.caption(f"Currently chatting as: **{user_name}** ({current_role_cfg['title']})")

        # Chat history container
        messages = get_chat_messages(limit=60)
        chat_container = st.container(height=420)
        with chat_container:
            if not messages:
                st.write("No messages yet. Send a progress update or inquiry below.")
            for m in messages:
                render_chat_bubble(m)

        # Quick simulated voice/text buttons
        st.markdown("<span style='font-size: 0.78rem; color: #94a3b8; font-weight: 600;'>⚡ QUICK SIMULATED VOICE / FIELD REPORTS:</span>", unsafe_allow_html=True)
        q1, q2, q3 = st.columns(3)
        quick_text = None
        if q1.button("🗣️ 'Line 24 spool welding 80%'"):
            quick_text = "Erected Line 24 spool at bay 1, completed 80% welding on Joint W-04"
        if q2.button("🗣️ 'C-101 plinth curing 100%'"):
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
            c_sub, c_mic = st.columns([8, 2])
            with c_sub:
                submitted = st.form_submit_button("🚀 Send to Time Agent", use_container_width=True)
            with c_mic:
                st.caption("🎙️ Voice Ready")

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
            <h4 style="margin: 0 0 8px 0; color: #f59e0b; font-size: 0.95rem;">How Time Agent Works:</h4>
            <ol style="color: #cbd5e1; font-size: 0.82rem; margin: 0; padding-left: 18px; line-height: 1.6;">
                <li><b>Entity Extraction:</b> NLP parses task intent, equipment codes, and completion % from informal text.</li>
                <li><b>Fuzzy String Matching:</b> RapidFuzz calculates composite Levenshtein & token similarity against L5/L6 schedule strings.</li>
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
        st.markdown("#### 🎯 Quick Task Progress Updater")
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
    st.markdown("### 🏗️ Work Breakdown Structure (L1 to L6 Hierarchy)")
    st.caption("Hierarchical schedule tracking with real-time weighted progress roll-up from L6 daily tasks up to L1 project macro level.")

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
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #94a3b8; margin-left: 6px;">{t['code']} ({t['id']})</span>
                        <span class="wbs-badge {status_class}" style="margin-left: 8px;">{t['status']}</span>
                        <h4 style="margin: 6px 0 2px 0; color: #ffffff; font-size: 1.05rem;">{t['name']}</h4>
                        <p style="margin: 0; color: #94a3b8; font-size: 0.82rem;">{t.get('description', '')}</p>
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
                    <span>Discipline: <b>{t['discipline']}</b></span>
                    <span>Planned: {t['planned_duration']}d | Actual: {t['actual_duration']}d</span>
                </div>
            </div>
            """
            st.markdown(clean_html(wbs_card_html), unsafe_allow_html=True)

# ================= TAB 3: LIVE AUDIT TRAIL =================
with tab_audit:
    st.markdown("### 📋 Live Audit Trail (PS26122 Standardized Table)")
    st.caption("Displays auto-linked and manually verified tasks with exact timestamp, confidence score, extracted metrics, and audit history.")

    col_f1, col_f2 = st.columns([3, 7])
    with col_f1:
        status_filter = st.selectbox("Filter Audit Records by Status:", ["All", "AUTO_APPROVED", "PENDING_REVIEW", "MANUALLY_APPROVED", "REJECTED"])
    filter_val = None if status_filter == "All" else status_filter

    audit_records = get_audit_trail(limit=100, status_filter=filter_val)
    render_audit_table(audit_records)

# ================= TAB 4: MANAGER REVIEW QUEUE =================
with tab_review:
    st.markdown("### ⚖️ Manager Review Queue (Confidence < 85%)")
    st.caption("Human-in-the-loop review for ambiguous worker slang or borderline matches. Human managers can approve, remap to a different node, adjust percentage, or reject.")

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
                        <span class="wbs-badge badge-l4">Item #{audit_id} • Status: PENDING_REVIEW</span>
                        <span style="color: #64748b; font-size: 0.75rem;">Submitted: {item['timestamp']}</span>
                    </div>
                    <div style="font-size: 0.95rem; color: #ffffff; margin-bottom: 6px;">
                        <b>Worker Raw Input:</b> <i>"{item['raw_input']}"</i>
                    </div>
                    <div style="font-size: 0.82rem; color: #94a3b8;">
                        Sender: <b>{item['sender_name']}</b> ({item['sender_role']}) | Extracted Task: <code>{item['extracted_task']}</code>
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="match-chip match-low">
                            AI Top Match: <b>{item['matched_node_id']}</b> ({item['matched_node_name']}) • Confidence: <b>{item['confidence_score']:.1f}%</b> (&lt; 85%)
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
                        if st.button(f"✅ Approve & Update Master Schedule", key=f"app_{audit_id}", use_container_width=True):
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
                        if st.button(f"❌ Reject Update", key=f"rej_{audit_id}", use_container_width=True):
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
    st.markdown("### 📊 Infrastructure Project Analytics & Bottlenecks")
    st.caption("Visual tracking of planned vs. actual durations and discipline progress to isolate operational bottlenecks across Civil, Piping, and Electrical works.")

    all_tasks = get_all_tasks()

    an_row1_c1, an_row1_c2 = st.columns(2)
    with an_row1_c1:
        fig_dur = plot_planned_vs_actual(all_tasks)
        if fig_dur:
            st.plotly_chart(fig_dur, use_container_width=True)
        else:
            st.info("Planned vs Actual chart available with Plotly.")
    with an_row1_c2:
        fig_disc = plot_discipline_progress(all_tasks)
        if fig_disc:
            st.plotly_chart(fig_disc, use_container_width=True)
        else:
            st.info("Discipline progress chart available with Plotly.")

    an_row2_c1, an_row2_c2 = st.columns(2)
    with an_row2_c1:
        fig_stat = plot_status_distribution(all_tasks)
        if fig_stat:
            st.plotly_chart(fig_stat, use_container_width=True)
        else:
            st.info("Status distribution chart available with Plotly.")
    with an_row2_c2:
        fig_sun = plot_wbs_sunburst(all_tasks)
        if fig_sun:
            st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("WBS Sunburst chart available with Plotly.")

# ================= TAB 6: MASTER SCHEDULE & INGESTION =================
with tab_master:
    st.markdown("### 📁 Master Schedule & Synthetic Ingestion Layer")
    st.caption("Inspect raw Primavera P6 database records or upload synthetic daily reports / discipline CSVs.")

    all_tasks_df = pd.DataFrame(get_all_tasks())
    if not all_tasks_df.empty:
        csv_data = all_tasks_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Live Primavera Master Schedule (CSV)",
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
    st.markdown("#### 📤 Upload Synthetic CSV / Daily Report")
    uploaded_file = st.file_uploader("Upload CSV file matching Primavera export format:", type=["csv"])
    if uploaded_file is not None:
        try:
            up_df = pd.read_csv(uploaded_file)
            st.write(f"Uploaded file contains **{len(up_df)}** records:")
            st.dataframe(up_df.head(5), use_container_width=True)
            st.info("Synthetic format recognized. Tasks can be merged into master schedule.")
        except Exception as e:
            st.error(f"Error parsing file: {e}")
