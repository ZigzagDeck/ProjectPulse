"""Modern Industrial UI Design System & CSS Styles for SIH PS26122 (Oil India Limited)."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-primary: #0b0f19;
    --bg-secondary: #111827;
    --card-bg: rgba(17, 24, 39, 0.75);
    --card-border: rgba(255, 255, 255, 0.08);
    --oil-gold: #f59e0b;
    --oil-gold-light: #fbbf24;
    --oil-blue: #38bdf8;
    --oil-navy: #1e293b;
    --accent-green: #10b981;
    --accent-red: #ef4444;
    --accent-purple: #8b5cf6;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
}

/* App Header Banner */
.oil-header {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.90) 50%, rgba(245, 158, 11, 0.15) 100%);
    border: 1px solid rgba(245, 158, 11, 0.25);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 20px -5px rgba(245, 158, 11, 0.15);
    backdrop-filter: blur(12px);
}

.oil-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.4);
    border-radius: 9999px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.metric-card {
    background: rgba(17, 24, 39, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 18px 20px;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    backdrop-filter: blur(8px);
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: rgba(245, 158, 11, 0.4);
    box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4);
}

.metric-val {
    font-size: 1.85rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 4px 0;
}

.metric-label {
    font-size: 0.8rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}

/* WBS Level Badges */
.badge-l1 { background: rgba(139, 92, 246, 0.2); color: #c4b5fd; border: 1px solid rgba(139, 92, 246, 0.4); }
.badge-l2 { background: rgba(56, 189, 248, 0.2); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.4); }
.badge-l3 { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }
.badge-l4 { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.4); }
.badge-l5 { background: rgba(249, 115, 22, 0.2); color: #fdba74; border: 1px solid rgba(249, 115, 22, 0.4); }
.badge-l6 { background: rgba(236, 72, 153, 0.2); color: #f9a8d4; border: 1px solid rgba(236, 72, 153, 0.4); }

.wbs-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

/* Status Badges */
.status-completed { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.status-inprogress { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
.status-notstarted { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }
.status-delayed { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

/* Chat speech bubbles */
.chat-bubble {
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(6px);
}
.chat-l1 { background: rgba(139, 92, 246, 0.12); border-left: 4px solid #8b5cf6; }
.chat-l3 { background: rgba(56, 189, 248, 0.12); border-left: 4px solid #38bdf8; }
.chat-l5 { background: rgba(245, 158, 11, 0.12); border-left: 4px solid #f59e0b; }

.chat-sender {
    font-size: 0.78rem;
    font-weight: 700;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.match-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 6px;
}
.match-high { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
.match-low { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }

/* Progress bar container */
.oil-progress-bg {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 9999px;
    height: 8px;
    overflow: hidden;
    margin: 6px 0;
}
.oil-progress-fill {
    height: 100%;
    border-radius: 9999px;
    background: linear-gradient(90deg, #f59e0b 0%, #10b981 100%);
    transition: width 0.4s ease;
}

/* Review Card */
.review-card {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 16px;
}
</style>
"""

def inject_styles():
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
