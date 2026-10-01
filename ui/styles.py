"""Visual design system for the ProjectPulse Streamlit application."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root {
    --ink-950: #07111f;
    --ink-900: #0b1728;
    --ink-850: #102035;
    --ink-800: #17283d;
    --line: rgba(148, 163, 184, 0.16);
    --line-strong: rgba(148, 163, 184, 0.28);
    --orange: #f59e0b;
    --orange-soft: #fbbf24;
    --cyan: #22d3ee;
    --emerald: #34d399;
    --red: #fb7185;
    --violet: #a78bfa;
    --text: #f8fafc;
    --muted: #9fb0c6;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Preserve Streamlit's ligature icon font. A broad font override turns these
   controls into visible strings such as "keyboard_double_arrow_left". */
[data-testid="stIconMaterial"], .material-symbols-rounded, .material-symbols-outlined {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
    font-weight: normal !important;
    font-style: normal !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-feature-settings: 'liga' !important;
    -webkit-font-smoothing: antialiased !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 82% 2%, rgba(34, 211, 238, 0.08), transparent 26rem),
        radial-gradient(circle at 18% 0%, rgba(245, 158, 11, 0.07), transparent 22rem),
        var(--ink-950);
    color: var(--text);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], [data-testid="stStatusWidget"], [data-testid="stDecoration"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1480px; padding: 1.35rem 2rem 3rem; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c1829 0%, #091321 100%);
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem; }
[data-testid="stSidebar"] hr { border-color: var(--line); margin: 1rem 0; }

.sidebar-brand { display: flex; align-items: center; gap: 11px; margin: 2px 0 19px; }
.sidebar-brand-mark {
    position: relative; display: grid; place-items: center; width: 40px; height: 40px;
    border-radius: 13px; overflow: hidden;
    background: linear-gradient(145deg, #fbbf24 0%, #f59e0b 58%, #d97706 100%);
    color: #07111f; font-family: 'IBM Plex Mono', monospace; font-size: .78rem; font-weight: 700;
    box-shadow: 0 8px 24px rgba(245, 158, 11, .2), inset 0 1px 0 rgba(255,255,255,.35);
}
.sidebar-brand-mark::after {
    content: ''; position: absolute; width: 24px; height: 2px; right: -9px; bottom: 8px;
    background: rgba(255,255,255,.65); transform: rotate(-38deg);
}
.sidebar-brand-copy { display: flex; flex-direction: column; gap: 2px; }
.sidebar-brand-copy b { color: #f8fafc; font-size: 1rem; letter-spacing: -.02em; }
.sidebar-brand-copy span {
    color: #7f94aa; font-family: 'IBM Plex Mono', monospace; font-size: .61rem;
    font-weight: 600; letter-spacing: .12em;
}

h1, h2, h3, h4 { color: var(--text); letter-spacing: -0.025em; }
p, label, [data-testid="stCaptionContainer"] { color: var(--muted); }

.oil-header {
    position: relative;
    overflow: hidden;
    background: linear-gradient(120deg, rgba(17, 36, 57, 0.96), rgba(11, 26, 43, 0.96));
    border: 1px solid rgba(245, 158, 11, 0.24);
    border-radius: 22px;
    padding: 25px 28px;
    margin-bottom: 18px;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.24);
}
.oil-header::after {
    content: '';
    position: absolute;
    width: 280px;
    height: 280px;
    right: -110px;
    top: -150px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(245, 158, 11, 0.22), transparent 66%);
}
.oil-badge, .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    color: var(--orange-soft);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.live-dot {
    width: 8px; height: 8px; display: inline-block; border-radius: 50%;
    background: var(--emerald); box-shadow: 0 0 0 5px rgba(52, 211, 153, 0.12);
}
.hero-title { margin: 8px 0 5px; font-size: clamp(1.65rem, 3vw, 2.35rem); font-weight: 700; }
.hero-copy { max-width: 720px; margin: 0; color: #aec0d4; font-size: 0.94rem; }
.hero-status {
    display: flex; gap: 16px; align-items: center; color: #d7e3ef; font-size: 0.78rem;
    background: rgba(7, 17, 31, 0.48); border: 1px solid var(--line); border-radius: 12px;
    padding: 10px 13px;
}

.metric-card {
    min-height: 128px;
    background: linear-gradient(145deg, rgba(20, 39, 62, 0.94), rgba(12, 26, 43, 0.94));
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 17px 18px;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.16);
    transition: transform .18s ease, border-color .18s ease;
}
.metric-card:hover { transform: translateY(-2px); border-color: rgba(245, 158, 11, 0.32); }
.metric-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.metric-icon {
    display: grid; place-items: center; width: 32px; height: 32px; border-radius: 10px;
    background: rgba(245, 158, 11, 0.12); color: var(--orange-soft); font-size: 0.9rem;
}
.metric-val { color: #fff; font-size: 1.72rem; font-weight: 700; margin: 10px 0 2px; line-height: 1; }
.metric-label { color: var(--muted); font-size: 0.71rem; letter-spacing: .075em; text-transform: uppercase; font-weight: 700; }
.metric-foot { color: #8194aa; font-size: 0.74rem; margin-top: 8px; }
.metric-foot strong { color: #dbe8f4; }

.oil-progress-bg { background: rgba(148, 163, 184, 0.13); border-radius: 999px; height: 7px; overflow: hidden; margin: 9px 0 0; }
.oil-progress-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--orange), var(--emerald)); }

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 5px; padding: 5px; border-radius: 14px; background: rgba(12, 27, 45, 0.8); border: 1px solid var(--line);
    overflow-x: auto;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    height: 42px; border-radius: 10px; padding: 0 15px; color: #92a6bd; font-size: .82rem; font-weight: 600;
}
[data-testid="stTabs"] [aria-selected="true"] { background: #1b314a; color: #fff; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none; }

.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
    border-radius: 11px; min-height: 40px; border: 1px solid var(--line-strong);
    background: #172b43; color: #eff6ff; font-weight: 600; transition: all .16s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
    border-color: rgba(245, 158, 11, .65); color: #fff; transform: translateY(-1px);
}
[data-testid="stTextInputRootElement"], [data-baseweb="select"] > div, [data-testid="stNumberInputContainer"] {
    background: rgba(14, 29, 48, .9); border-color: var(--line-strong); border-radius: 11px;
}
[data-testid="stFileUploaderDropzone"] { background: rgba(14, 29, 48, .68); border-color: var(--line-strong); border-radius: 14px; }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }

.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 18px; margin: 12px 0 14px; }
.section-heading h3 { margin: 4px 0 0; font-size: 1.18rem; }
.section-heading p { margin: 4px 0 0; font-size: .82rem; }
.panel, .insight-card, .wbs-card, .review-card {
    background: linear-gradient(145deg, rgba(17, 35, 56, .9), rgba(11, 25, 42, .92));
    border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px;
}
.insight-card { margin-bottom: 10px; }
.insight-card.attention { border-left: 3px solid var(--orange); }
.insight-card.critical { border-left: 3px solid var(--red); }
.insight-card.good { border-left: 3px solid var(--emerald); }
.insight-title { color: #f5f9ff; font-size: .88rem; font-weight: 700; margin-bottom: 4px; }
.insight-copy { color: var(--muted); font-size: .78rem; line-height: 1.45; }
.mini-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin: 10px 0 20px; }
.mini-stat { background: rgba(13, 29, 48, .78); border: 1px solid var(--line); border-radius: 14px; padding: 14px; }
.mini-stat strong { display: block; color: #fff; font-size: 1.18rem; margin-top: 4px; }
.mini-stat span { color: #8fa4bb; font-size: .72rem; }

.wbs-badge, .status-pill {
    display: inline-flex; align-items: center; padding: 3px 8px; border-radius: 7px;
    font-size: .68rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace;
}
.badge-l1 { background: rgba(167,139,250,.14); color: #c4b5fd; border: 1px solid rgba(167,139,250,.3); }
.badge-l2 { background: rgba(34,211,238,.12); color: #67e8f9; border: 1px solid rgba(34,211,238,.28); }
.badge-l3 { background: rgba(52,211,153,.12); color: #6ee7b7; border: 1px solid rgba(52,211,153,.28); }
.badge-l4 { background: rgba(245,158,11,.12); color: #fbbf24; border: 1px solid rgba(245,158,11,.28); }
.badge-l5 { background: rgba(251,113,133,.12); color: #fda4af; border: 1px solid rgba(251,113,133,.28); }
.badge-l6 { background: rgba(96,165,250,.12); color: #93c5fd; border: 1px solid rgba(96,165,250,.28); }
.status-completed { background: rgba(52,211,153,.12); color: #6ee7b7; border: 1px solid rgba(52,211,153,.25); }
.status-inprogress { background: rgba(34,211,238,.11); color: #67e8f9; border: 1px solid rgba(34,211,238,.24); }
.status-notstarted { background: rgba(148,163,184,.11); color: #b6c3d2; border: 1px solid rgba(148,163,184,.22); }
.status-delayed { background: rgba(251,113,133,.12); color: #fda4af; border: 1px solid rgba(251,113,133,.25); }

.chat-bubble { border-radius: 14px; padding: 13px 15px; margin-bottom: 10px; border: 1px solid var(--line); background: rgba(14, 29, 48, .72); }
.chat-l1 { border-left: 3px solid var(--violet); }
.chat-l3 { border-left: 3px solid var(--cyan); }
.chat-l5 { border-left: 3px solid var(--orange); }
.chat-sender { display: flex; justify-content: space-between; gap: 10px; color: #dce8f5; font-size: .76rem; }
.match-chip { display: inline-flex; align-items: center; gap: 5px; padding: 5px 9px; border-radius: 8px; font-size: .71rem; font-weight: 600; margin-top: 8px; }
.match-high { background: rgba(52,211,153,.1); color: #6ee7b7; border: 1px solid rgba(52,211,153,.25); }
.match-low { background: rgba(245,158,11,.1); color: #fbbf24; border: 1px solid rgba(245,158,11,.25); }

.wbs-card { margin-bottom: 9px; padding: 14px 16px; }
.review-card { margin-bottom: 10px; border-color: rgba(245, 158, 11, .3); }
.empty-state { text-align: center; padding: 38px 20px; color: var(--muted); border: 1px dashed var(--line-strong); border-radius: 16px; background: rgba(14,29,48,.4); }
.permission-note { color: #fbbf24; background: rgba(245,158,11,.08); border: 1px solid rgba(245,158,11,.22); border-radius: 11px; padding: 10px 12px; font-size: .78rem; }

[data-testid="stPlotlyChart"] { background: rgba(10, 24, 41, .54); border: 1px solid var(--line); border-radius: 17px; padding: 5px; }
[data-testid="stAlert"] { border-radius: 12px; }

@media (max-width: 900px) {
    .block-container { padding: 1rem; }
    .oil-header { padding: 20px; }
    .mini-grid { grid-template-columns: 1fr; }
    [data-testid="column"] { min-width: 100% !important; }
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
}
</style>
"""


def inject_styles():
    import streamlit as st

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
