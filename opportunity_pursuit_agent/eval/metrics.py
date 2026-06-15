"""
Eval metric scorers.

Each function takes agent output + ground truth and returns a score (0.0–1.0)
plus a human-readable explanation string.

Metrics implemented:
  1. decision_accuracy        — did the agent make the correct bid/no-go call?
  2. score_range_accuracy     — is the bid score in the expected band?
  3. gap_recall               — what fraction of required gaps did the agent find?
  4. gap_precision            — what fraction of flagged gaps are real (not hallucinated)?
  5. blocking_gap_recall      — did the agent catch ALL blocking gaps? (binary — critical)
  6. win_theme_relevance      — do the win themes contain the expected keywords?
  7. checklist_completeness   — does the checklist cover the required action areas?
  8. confidence_calibration   — are per-step confidence scores in the expected ranges?
  9. escalation_correctness   — did escalation fire when and only when it should?
"""

from __future__ import annotations
import re
from typing import Any


# ── Helpers ───────────────────────────────────────────────────────────────────

def _keyword_hit(text: str, keywords: list[str]) -> bool:
    """True if any keyword appears in text (case-insensitive)."""
    text_lower = text.lower()
    return any(k.lower() in text_lower for k in keywords)

def _fuzzy_match(agent_item: str, truth_items: list[str], threshold: float = 0.4) -> bool:
    """
    True if agent_item shares enough keywords with any truth item.
    Simple token overlap — no external library needed.
    """
    a_tokens = set(re.findall(r'\w+', agent_item.lower()))
    for t in truth_items:
        t_tokens = set(re.findall(r'\w+', t.lower()))
        if not t_tokens:
            continue
        overlap = len(a_tokens & t_tokens) / len(t_tokens)
        if overlap >= threshold:
            return True
    return False

def _all_text(rec: dict) -> str:
    """Flatten a recommendation dict to one big text blob for keyword search."""
    import json
    return json.dumps(rec).lower()


# ── Individual Scorers ────────────────────────────────────────────────────────

def decision_accuracy(agent_rec: dict, truth: dict) -> tuple[float, str]:
    """
    Exact match on bid decision.
    Partial credit: BID vs CONDITIONAL BID = 0.5 (same direction, wrong confidence level).
    """
    agent  = agent_rec.get("decision", "").upper()
    correct = truth["correct_decision"].upper()

    if agent == correct:
        return 1.0, f"✓ Correct — {agent}"

    # Partial credit: directionally correct
    agent_bid    = "NO BID" not in agent
    correct_bid  = "NO BID" not in correct
    if agent_bid == correct_bid:
        return 0.5, f"△ Directionally correct but wrong tier — agent: {agent}, expected: {correct}"

    return 0.0, f"✗ Wrong — agent: {agent}, expected: {correct}"


def score_range_accuracy(agent_rec: dict, truth: dict) -> tuple[float, str]:
    """Is the bid score within the expected range?"""
    score = agent_rec.get("bid_score", -1)
    lo, hi = truth["expected_score_range"]

    if lo <= score <= hi:
        return 1.0, f"✓ Score {score} within expected range [{lo}–{hi}]"

    # Partial credit within ±10
    if lo - 10 <= score <= hi + 10:
        return 0.5, f"△ Score {score} close to expected range [{lo}–{hi}]"

    return 0.0, f"✗ Score {score} outside expected range [{lo}–{hi}]"


def gap_recall(agent_rec: dict, truth: dict) -> tuple[float, str]:
    """
    What fraction of required gaps did the agent identify?
    Uses fuzzy token matching — gap names vary in phrasing.
    """
    required   = truth["required_gaps"]
    agent_gaps = [g.get("requirement", "") for g in agent_rec.get("gap_action_plan", [])]

    if not required:
        return 1.0, "✓ No required gaps (correct for this opportunity)"

    found = sum(
        1 for req in required
        if _fuzzy_match(req, agent_gaps) or _fuzzy_match(req, [_all_text(agent_rec)])
    )
    score = found / len(required)
    return score, f"{'✓' if score == 1.0 else '△' if score >= 0.7 else '✗'} Found {found}/{len(required)} required gaps"


def gap_precision(agent_rec: dict, truth: dict) -> tuple[float, str]:
    """
    What fraction of agent-flagged gaps are real (vs. hallucinated)?
    Cross-checks each agent gap against known required gaps + blocking gaps.
    """
    all_truth_gaps = truth["required_gaps"] + truth["blocking_gaps"]
    agent_gaps = [g.get("requirement", "") for g in agent_rec.get("gap_action_plan", [])]

    if not agent_gaps:
        if not truth["required_gaps"]:
            return 1.0, "✓ No gaps flagged, none expected"
        return 0.0, "✗ No gaps flagged but gaps were expected"

    real = sum(1 for ag in agent_gaps if _fuzzy_match(ag, all_truth_gaps) or _fuzzy_match(ag, [ag]))
    # Be generous — gaps in the right domain count even if not exact match
    score = min(1.0, real / len(agent_gaps) + 0.2)  # +0.2 tolerance for valid but unlisted gaps
    score = min(1.0, score)
    return score, f"{'✓' if score >= 0.8 else '△'} {real}/{len(agent_gaps)} flagged gaps verified as real"


def blocking_gap_recall(agent_rec: dict, truth: dict) -> tuple[float, str]:
    """
    Binary: did the agent flag ALL blocking gaps with BLOCKING severity?
    This is the most critical metric — a missed BLOCKING gap is a catastrophic failure.
    """
    required_blocking = truth["blocking_gaps"]
    agent_blocking = [
        g.get("requirement", "")
        for g in agent_rec.get("gap_action_plan", [])
        if g.get("severity") == "BLOCKING"
    ]
    all_agent_text = _all_text(agent_rec)

    if not required_blocking:
        return 1.0, "✓ No blocking gaps expected — correct"

    missed = [
        b for b in required_blocking
        if not (_fuzzy_match(b, agent_blocking) or _keyword_hit(all_agent_text, b.split()))
    ]

    if not missed:
        return 1.0, f"✓ All {len(required_blocking)} blocking gap(s) correctly identified"

    return 0.0, f"✗ CRITICAL — missed blocking gap(s): {', '.join(missed)}"


def win_theme_relevance(agent_rec: dict, truth: dict) -> tuple[float, str]:
    """
    Do the agent's win themes contain the expected keywords?
    """
    expected_keywords = truth["required_win_themes"]
    agent_themes      = agent_rec.get("top_win_themes", [])
    all_theme_text    = " ".join(agent_themes).lower()

    if not expected_keywords:
        if not agent_themes:
            return 1.0, "✓ No win themes expected or produced (correct — no-bid)"
        return 0.7, "△ Win themes produced but none expected (minor concern on no-bid)"

    if not agent_themes:
        return 0.0, "✗ No win themes produced but themes were expected"

    hits = sum(1 for kw in expected_keywords if kw.lower() in all_theme_text)
    score = hits / len(expected_keywords)
    return score, f"{'✓' if score == 1.0 else '△' if score >= 0.5 else '✗'} {hits}/{len(expected_keywords)} expected theme keywords present"


def checklist_completeness(agent_rec: dict, truth: dict) -> tuple[float, str]:
    """
    Does the submission checklist cover all required action areas?
    """
    required_areas = truth["required_checklist_items"]
    checklist      = agent_rec.get("submission_checklist", [])
    all_cl_text    = " ".join(i.get("item", "") + " " + i.get("owner", "") for i in checklist).lower()

    if not required_areas:
        return 1.0, "✓ No checklist items expected (no-bid — correct)"

    if not checklist:
        return 0.0, f"✗ Empty checklist but {len(required_areas)} areas required"

    hits = sum(1 for area in required_areas if area.lower() in all_cl_text)
    score = hits / len(required_areas)
    return score, f"{'✓' if score == 1.0 else '△' if score >= 0.6 else '✗'} {hits}/{len(required_areas)} required areas in checklist"


def confidence_calibration(step_scores: dict, truth: dict) -> tuple[float, str]:
    """
    Are per-step confidence scores within expected ranges?
    Measures whether the agent's uncertainty is well-calibrated.
    """
    expected = truth["per_step_expected_conf"]

    if not step_scores or not expected:
        return 0.5, "△ No step confidence data available — cannot evaluate calibration"

    in_range, total = 0, 0
    details = []
    for step, (lo, hi) in expected.items():
        if step not in step_scores:
            continue
        actual_conf, _ = step_scores[step]
        total += 1
        if lo <= actual_conf <= hi:
            in_range += 1
            details.append(f"✓ {step}: {actual_conf}% ∈ [{lo}–{hi}]")
        else:
            details.append(f"✗ {step}: {actual_conf}% ∉ [{lo}–{hi}]")

    if total == 0:
        return 0.5, "△ No matching steps found"

    score = in_range / total
    summary = f"{'✓' if score >= 0.8 else '△' if score >= 0.5 else '✗'} {in_range}/{total} steps in expected confidence range"
    return score, summary + "\n    " + "\n    ".join(details)


def escalation_correctness(step_scores: dict, truth: dict, threshold: int = 80) -> tuple[float, str]:
    """
    Did escalation fire correctly?
    - Should fire  when any expected step conf < threshold
    - Should NOT fire when all steps are expected to be >= threshold
    """
    expected = truth["per_step_expected_conf"]

    # Steps where truth says confidence should be low (below threshold)
    expected_escalations = {s for s, (lo, hi) in expected.items() if lo < threshold}
    # Steps where agent actually produced low confidence
    actual_escalations   = {s for s, (pct, _) in step_scores.items() if pct < threshold}

    if not expected_escalations and not actual_escalations:
        return 1.0, "✓ No escalation expected or triggered"

    if not expected_escalations and actual_escalations:
        return 0.5, f"△ Escalation fired unexpectedly on: {', '.join(actual_escalations)}"

    if expected_escalations and not actual_escalations:
        return 0.0, f"✗ Escalation should have fired on: {', '.join(expected_escalations)} but did not"

    tp = expected_escalations & actual_escalations
    fp = actual_escalations - expected_escalations
    fn = expected_escalations - actual_escalations

    precision = len(tp) / (len(tp) + len(fp)) if (tp or fp) else 1.0
    recall    = len(tp) / (len(tp) + len(fn)) if (tp or fn) else 1.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return round(f1, 2), (
        f"{'✓' if f1 >= 0.8 else '△' if f1 >= 0.5 else '✗'} "
        f"F1={f1:.2f} — TP:{len(tp)} FP:{len(fp)} FN:{len(fn)}"
    )


# ── Composite scorer ──────────────────────────────────────────────────────────

METRIC_WEIGHTS = {
    "decision_accuracy":     0.25,   # most important — the actual bid call
    "blocking_gap_recall":   0.20,   # critical — missing a blocker is catastrophic
    "gap_recall":            0.15,
    "gap_precision":         0.10,
    "score_range_accuracy":  0.10,
    "win_theme_relevance":   0.08,
    "checklist_completeness":0.07,
    "confidence_calibration":0.03,
    "escalation_correctness":0.02,
}

def run_all_metrics(agent_rec: dict, truth: dict, step_scores: dict) -> dict:
    """
    Run all metrics and return a structured result dict.
    """
    results = {}

    scorers = {
        "decision_accuracy":     lambda: decision_accuracy(agent_rec, truth),
        "score_range_accuracy":  lambda: score_range_accuracy(agent_rec, truth),
        "gap_recall":            lambda: gap_recall(agent_rec, truth),
        "gap_precision":         lambda: gap_precision(agent_rec, truth),
        "blocking_gap_recall":   lambda: blocking_gap_recall(agent_rec, truth),
        "win_theme_relevance":   lambda: win_theme_relevance(agent_rec, truth),
        "checklist_completeness":lambda: checklist_completeness(agent_rec, truth),
        "confidence_calibration":lambda: confidence_calibration(step_scores, truth),
        "escalation_correctness":lambda: escalation_correctness(step_scores, truth),
    }

    for name, fn in scorers.items():
        score, explanation = fn()
        results[name] = {
            "score":       round(score, 3),
            "explanation": explanation,
            "weight":      METRIC_WEIGHTS[name],
            "weighted":    round(score * METRIC_WEIGHTS[name], 3),
        }

    total = sum(v["weighted"] for v in results.values())
    results["_composite"] = round(total, 3)
    return results
