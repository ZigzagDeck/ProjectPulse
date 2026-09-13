"""Rule-Based Entity Extraction Engine for ProjectPulse (SIH PS26122).

Ingests free-text field updates from site supervisors and extracts:
1. Whether the message contains a progress update (keyword scan)
2. Core task entity string (after stripping conversational filler)
3. State (e.g., STARTED, IN_PROGRESS, COMPLETED)
4. Calculated/extracted progress percentage (0.0 to 100.0)
5. Discipline hints (Piping, Civil, Electrical, Quality)
"""

import re
from typing import Dict, Any, Optional

UPDATE_KEYWORDS = [
    "weld", "welding", "welded", "spool", "erect", "erected", "erection",
    "pour", "poured", "pouring", "concrete", "rebar", "plinth", "curing",
    "cured", "hydrotest", "tested", "pressure", "fit-up", "fitup", "flange",
    "cable", "pulled", "pulling", "tray", "grout", "grouting", "shim",
    "shimming", "ndt", "rt", "inspection", "torque", "torquing", "progress",
    "completed", "finished", "done", "%", "percent", "started"
]

DISCIPLINE_PATTERNS = {
    "Piping & Mechanical": [r"spool", r"pipe", r"weld", r"flange", r"valve", r"fitting", r"rigging", r"butt", r"rack"],
    "Civil & Structural": [r"concrete", r"rebar", r"plinth", r"pour", r"curing", r"grout", r"foundation", r"formwork", r"substructure"],
    "Electrical & Instrumentation": [r"cable", r"tray", r"11kv", r"pull", r"substation", r"megger", r"hi-pot", r"termination", r"motor"],
    "Quality & Testing": [r"hydrotest", r"ndt", r"rt", r"radiograph", r"pressure test", r"inspection", r"45 bar", r"blind"],
}

STATE_MAPPINGS = {
    "COMPLETED": [r"\bcompleted\b", r"\bfinished\b", r"\bdone\b", r"\bpassed\b", r"\berected\b", r"\bpoured\b", r"\bcapped\b"],
    "STARTED": [r"\bstarted\b", r"\binitiated\b", r"\bkicked off\b", r"\bbegun\b"],
    "IN_PROGRESS": [r"\bin progress\b", r"\bongoing\b", r"\bunderway\b", r"\bworking on\b", r"\bfit-up\b", r"\broot pass\b"],
}

def is_field_progress_update(text: str) -> bool:
    """Detect if a chat message contains actionable field progress update."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in UPDATE_KEYWORDS)

def extract_progress_pct(text: str) -> Optional[float]:
    """Extract progress percentage from text patterns like '80%', 'completed 75 percent', '3/4 done'."""
    text_lower = text.lower()

    # Match explicit percentage: "80%", "80 %", "80 percent"
    pct_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*(?:%|percent)", text_lower)
    if pct_match:
        try:
            val = float(pct_match.group(1))
            return min(100.0, max(0.0, val))
        except ValueError:
            pass

    # Match fraction/ratio: "3 out of 4", "12 of 16"
    ratio_match = re.search(r"(\d+)\s*(?:out of|/|of)\s*(\d+)", text_lower)
    if ratio_match:
        try:
            num = float(ratio_match.group(1))
            denom = float(ratio_match.group(2))
            if denom > 0:
                return round(min(100.0, max(0.0, (num / denom) * 100.0)), 2)
        except ValueError:
            pass

    # Infer from strong state keywords
    if any(re.search(pat, text_lower) for pat in [r"\b100%\b", r"\bfully completed\b", r"\bcompleted\b", r"\bfinished\b", r"\bpassed\b"]):
        return 100.0
    if any(re.search(pat, text_lower) for pat in [r"\bhalfway\b", r"\bhalf done\b", r"\bmidway\b"]):
        return 50.0
    if any(re.search(pat, text_lower) for pat in [r"\broot pass done\b", r"\bfit-up done\b", r"\bfit-up completed\b"]):
        return 50.0
    if any(re.search(pat, text_lower) for pat in [r"\bstarted\b", r"\bcommenced\b"]):
        return 20.0

    return None

def extract_state(text: str, progress_pct: Optional[float] = None) -> str:
    """Extract operational state."""
    text_lower = text.lower()
    if progress_pct is not None:
        if progress_pct >= 100.0:
            return "COMPLETED"
        elif progress_pct > 0.0:
            return "IN_PROGRESS"

    for state, patterns in STATE_MAPPINGS.items():
        if any(re.search(p, text_lower) for p in patterns):
            return state

    return "IN_PROGRESS"

def infer_discipline(text: str) -> Optional[str]:
    """Infers discipline from terminology."""
    text_lower = text.lower()
    scores = {}
    for disc, patterns in DISCIPLINE_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, text_lower))
        if score > 0:
            scores[disc] = score

    if scores:
        return max(scores, key=scores.get)
    return None

def extract_task_entity(text: str) -> str:
    """Cleans up conversational filler to return core task/action intent string."""
    cleaned = text
    fillers = [
        r"hello\s*,?", r"hi\s*team\s*,?", r"team\s*,?", r"good\s*(morning|afternoon|evening)\s*,?",
        r"please\s*note\s*(that)?", r"update\s*from\s*site\s*:?", r"daily\s*report\s*:?",
        r"supervisor\s*report\s*:?", r"today\s*we\s*(have)?", r"we\s*(have)?",
        r"reporting\s*that", r"fyi\s*,?", r"kindly\s*update"
    ]
    for filler in fillers:
        cleaned = re.sub(filler, "", cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.strip()
    return cleaned if cleaned else text

def parse_field_message(raw_text: str) -> Dict[str, Any]:
    """Full extraction pipeline on an incoming worker message."""
    is_update = is_field_progress_update(raw_text)
    extracted_pct = extract_progress_pct(raw_text)
    state = extract_state(raw_text, extracted_pct)
    task_entity = extract_task_entity(raw_text)
    disc_hint = infer_discipline(raw_text)

    return {
        "is_field_update": is_update,
        "extracted_task": task_entity,
        "extracted_state": state,
        "extracted_progress_pct": extracted_pct if extracted_pct is not None else 0.0,
        "discipline_hint": disc_hint,
    }
