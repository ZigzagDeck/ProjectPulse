"""Fuzzy-Matching Engine for ProjectPulse (SIH PS26122 — Oil India Limited).

Performs fuzzy string matching (Levenshtein, Token Set Ratio, WRatio) using RapidFuzz
to compare extracted worker field updates against official L5/L6 Primavera P6 task strings.

Enforces PS26122 Threshold Logic:
- Confidence >= 85%: Auto-update master schedule database.
- Confidence < 85%: Flag as PENDING_REVIEW and push to manual review queue.
"""

import re
from typing import Dict, Any, List, Optional

try:
    from rapidfuzz import fuzz
except ImportError:
    import difflib

    class _FuzzFallback:
        @staticmethod
        def token_set_ratio(s1: str, s2: str) -> float:
            tokens1 = set(s1.split())
            tokens2 = set(s2.split())
            intersection = " ".join(sorted(tokens1.intersection(tokens2)))
            diff1 = " ".join(sorted(tokens1.difference(tokens2)))
            diff2 = " ".join(sorted(tokens2.difference(tokens1)))
            base1 = f"{intersection} {diff1}".strip()
            base2 = f"{intersection} {diff2}".strip()
            if not base1 and not base2:
                return 100.0
            r1 = difflib.SequenceMatcher(None, intersection, base1).ratio() if base1 else 0.0
            r2 = difflib.SequenceMatcher(None, intersection, base2).ratio() if base2 else 0.0
            r3 = difflib.SequenceMatcher(None, base1, base2).ratio()
            return max(r1, r2, r3) * 100.0

        @staticmethod
        def WRatio(s1: str, s2: str) -> float:
            return difflib.SequenceMatcher(None, s1, s2).ratio() * 100.0

        @staticmethod
        def partial_ratio(s1: str, s2: str) -> float:
            if not s1 or not s2:
                return 0.0
            short, long_ = (s1, s2) if len(s1) <= len(s2) else (s2, s1)
            blocks = difflib.SequenceMatcher(None, short, long_).get_matching_blocks()
            scores = [difflib.SequenceMatcher(None, short, long_[max(0, j-i):max(0, j-i)+len(short)]).ratio() * 100.0 for i, j, n in blocks]
            return max(scores) if scores else 0.0

    fuzz = _FuzzFallback()

CONFIDENCE_THRESHOLD = 85.0

DOMAIN_SYNONYMS = {
    r"\bjnt\b": "joint",
    r"\bweld\b": "welding",
    r"\bwelders\b": "welding",
    r"\bspool\b": "pipe spool",
    r"\brt\b": "radiographic testing",
    r"\bndt\b": "non-destructive testing",
    r"\bconc\b": "concrete",
    r"\bplinth\b": "plinth foundation",
    r"\bhydro\b": "hydrostatic testing",
    r"\btest\b": "testing",
    r"\bc101\b": "c-101",
    r"\bc102\b": "c-102",
    r"\bp101\b": "p-101",
    r"\bw04\b": "w-04",
    r"\bline 24\b": "line 24",
    r"\b11 kv\b": "11kv",
    r"\berct\b": "erect",
}

def normalize_text(text: str) -> str:
    """Normalize and expand domain-specific acronyms and worker jargon."""
    t = text.lower()
    for pattern, replacement in DOMAIN_SYNONYMS.items():
        t = re.sub(pattern, replacement, t, flags=re.IGNORECASE)
    t = re.sub(r"[^\w\s\-\.]", " ", t)
    return " ".join(t.split())

def extract_key_tokens(text: str) -> set:
    """Extract specific equipment tags, joint IDs, or line numbers."""
    tokens = set()
    # Find codes like W-04, C-101, Line 24, SP-24-A, P-101, 11kV
    matches = re.findall(r"\b[A-Za-z]{1,4}-\d{2,4}[A-Za-z]?\b|\bline\s*\d{2}\b|\b11kv\b", text.lower())
    for m in matches:
        tokens.add(m.replace(" ", ""))
    return tokens

def match_field_update(
    extracted_task_text: str,
    target_tasks: List[Dict[str, Any]],
    discipline_hint: Optional[str] = None
) -> Dict[str, Any]:
    """Matches an extracted worker task against official L5/L6 Primavera nodes."""
    if not target_tasks or not extracted_task_text.strip():
        return {
            "matched_node_id": None,
            "matched_node_name": None,
            "confidence_score": 0.0,
            "status": "PENDING_REVIEW",
            "top_candidates": []
        }

    norm_query = normalize_text(extracted_task_text)
    query_tokens = extract_key_tokens(extracted_task_text)

    scored_candidates = []

    for task in target_tasks:
        task_name = task["name"]
        task_code = task.get("code", "")
        task_desc = task.get("description", "")
        task_discipline = task.get("discipline", "")

        norm_task_name = normalize_text(task_name)
        norm_task_combined = normalize_text(f"{task_code} {task_name} {task_desc}")

        # RapidFuzz scores
        score_token_set = fuzz.token_set_ratio(norm_query, norm_task_name)
        score_wratio = fuzz.WRatio(norm_query, norm_task_combined)
        score_partial = fuzz.partial_ratio(norm_query, norm_task_name)

        # Base composite score
        composite_score = (score_token_set * 0.50) + (score_wratio * 0.35) + (score_partial * 0.15)

        # Key token matching bonus (e.g. W-04, Line 24, C-101)
        target_tokens = extract_key_tokens(norm_task_combined)
        token_overlap = query_tokens.intersection(target_tokens)
        if token_overlap:
            # Significant boost if specific hardware / line / joint matches
            composite_score = min(100.0, composite_score + (12.0 * len(token_overlap)))

        # Discipline alignment bonus
        if discipline_hint and task_discipline:
            if discipline_hint.lower() in task_discipline.lower() or task_discipline.lower() in discipline_hint.lower():
                composite_score = min(100.0, composite_score + 5.0)

        composite_score = round(min(100.0, max(0.0, composite_score)), 1)

        scored_candidates.append({
            "task_id": task["id"],
            "code": task_code,
            "level": task["level"],
            "name": task_name,
            "discipline": task_discipline,
            "score": composite_score,
            "current_progress": task.get("progress_pct", 0.0),
        })

    # Sort descending by match score
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    best_candidate = scored_candidates[0] if scored_candidates else None

    confidence = best_candidate["score"] if best_candidate else 0.0
    status = "AUTO_APPROVED" if confidence >= CONFIDENCE_THRESHOLD else "PENDING_REVIEW"

    return {
        "matched_node_id": best_candidate["task_id"] if best_candidate else None,
        "matched_node_name": best_candidate["name"] if best_candidate else None,
        "confidence_score": confidence,
        "status": status,
        "top_candidates": scored_candidates[:5]
    }
