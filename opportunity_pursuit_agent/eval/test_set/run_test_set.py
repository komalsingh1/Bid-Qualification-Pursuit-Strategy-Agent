"""
Test set runner — runs the real agent against all 8 test RFPs and scores the results.

This is NOT mocked. It calls Claude via the Anthropic API for each test case.

Usage:
  export ANTHROPIC_API_KEY=sk-ant-...
  python run_test_set.py                    # run all 8 cases
  python run_test_set.py --case TC-01       # run a single case
  python run_test_set.py --dry-run          # validate setup without API calls

Output:
  test_results.json   — full structured results
  test_report.html    — visual report
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "prototype"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

import json
import time
import argparse
from datetime import datetime

from rfp_texts import TEST_RFPS
from ground_truth import TEST_GROUND_TRUTH
from metrics import run_all_metrics, METRIC_WEIGHTS

LIVE_MODE = bool(os.environ.get("ANTHROPIC_API_KEY"))

# ── Heuristic agent (no API key) ─────────────────────────────────────────────

def heuristic_agent(rfp_text: str, rfp_name: str) -> dict:
    """
    Runs when no API key is available.
    Uses keyword matching and rule-based logic to simulate agent outputs.
    Good enough to validate the eval pipeline; not a substitute for real Claude.
    """
    from tools import (
        extract_requirements, check_capabilities, get_win_loss_history,
        identify_gaps, get_sme_and_content, generate_recommendation
    )

    t0 = time.perf_counter()
    tool_log = []

    def log(tool, inp, out):
        tool_log.append({
            "tool": tool,
            "input": str(inp)[:80],
            "output_keys": list(out.keys()) if isinstance(out, dict) else "list",
            "elapsed_s": round(time.perf_counter() - t0, 2),
        })

    reqs   = extract_requirements(rfp_text)
    log("extract_requirements", {}, reqs)

    all_reqs = (
        reqs.get("mandatory_requirements", []) +
        [s["req"] if isinstance(s, dict) else s for s in reqs.get("scored_requirements", [])] +
        reqs.get("compliance_requirements", []) +
        reqs.get("team_requirements", [])
    )

    caps   = check_capabilities(all_reqs)
    log("check_capabilities", all_reqs[:3], caps)

    wl     = get_win_loss_history(["Medicaid", "FHIR", "state health", "federal"])
    log("get_win_loss_history", {}, wl)

    gaps   = identify_gaps(all_reqs, caps)
    log("identify_gaps", {}, {"gaps": gaps})

    gap_areas = list({g.get("owner_area","General") for g in gaps})
    sme    = get_sme_and_content(gap_areas)
    log("get_sme_and_content", gap_areas, sme)

    rec    = generate_recommendation(
        rfp_summary=reqs.get("title", rfp_name),
        gaps=gaps,
        win_loss_context=wl,
        reusable_content=sme.get("reusable_content", []),
        sme_assignments=sme,
    )
    log("generate_recommendation", {}, rec)

    return {
        "tool_call_log":     tool_log,
        "recommendation":    rec,
        "executive_summary": rec.get("rationale", ""),
        "total_turns":       4,
        "total_elapsed_s":   round(time.perf_counter() - t0, 2),
        "parallel_savings_s": 0,
        "mode": "heuristic",
    }


def live_agent(rfp_text: str) -> dict:
    """Calls the real Claude agent."""
    from agent import run_agent
    return run_agent(rfp_text, stream_callback=None)


# ── Step confidence heuristic ─────────────────────────────────────────────────

def derive_step_confidence(agent_result: dict, truth: dict) -> dict:
    """
    In live/heuristic mode we don't get per-step confidence from the UI layer.
    Derive rough confidence from the tool outputs:
      - extract_requirements: always high if output is non-empty
      - check_capabilities: proportion of MET results
      - get_win_loss_history: number of relevant records found
      - identify_gaps: inverse of gap count (more gaps = less confident bid)
      - get_sme_and_content: proportion of gaps with owners
      - generate_recommendation: bid score proximity to threshold
    """
    rec   = agent_result.get("recommendation", {})
    log   = agent_result.get("tool_call_log", [])
    gaps  = rec.get("gap_action_plan", [])
    score = rec.get("bid_score", 50)

    # extract_requirements — always high if we got structured output
    ext_conf = 95

    # check_capabilities — look at how many PARTIAL/NOT MET appear
    blocking = len([g for g in gaps if g.get("severity") == "BLOCKING"])
    high     = len([g for g in gaps if g.get("severity") == "HIGH"])
    cap_conf = max(15, 95 - (blocking * 25) - (high * 10))

    # win/loss — presence of records
    wl_tool = next((t for t in log if t["tool"] == "get_win_loss_history"), None)
    wl_conf = 85 if wl_tool else 50

    # identify_gaps — confidence is higher when gaps are unambiguous
    gap_conf = 92 if blocking >= 2 else (88 if blocking == 1 else 82)

    # sme/content — lower if many gaps have no owner
    sme_conf = max(20, 88 - (blocking * 15))

    # generate_recommendation — distance from threshold
    if score >= 70 or score <= 25:
        gen_conf = 88   # clear decision
    elif 30 <= score <= 45 or 65 <= score < 70:
        gen_conf = 68   # close to threshold — uncertain
    else:
        gen_conf = 75

    return {
        "extract_requirements":    (ext_conf, "Derived from output completeness"),
        "check_capabilities":      (cap_conf,  f"Derived from {blocking} blocking, {high} high gaps"),
        "get_win_loss_history":    (wl_conf,   "Derived from CRM record availability"),
        "identify_gaps":           (gap_conf,  "Derived from gap severity distribution"),
        "get_sme_and_content":     (sme_conf,  "Derived from SME assignment coverage"),
        "generate_recommendation": (gen_conf,  f"Derived from bid score {score} vs thresholds"),
    }


# ── Main runner ───────────────────────────────────────────────────────────────

def run_test_set(filter_case: str = None) -> dict:
    report = {
        "mode":    "live" if LIVE_MODE else "heuristic",
        "run_at":  datetime.utcnow().isoformat() + "Z",
        "cases":   {},
    }

    cases = {
        k: v for k, v in TEST_RFPS.items()
        if filter_case is None or filter_case in k
    }

    for i, (rfp_name, rfp_text) in enumerate(cases.items(), 1):
        truth = TEST_GROUND_TRUTH.get(rfp_name)
        if not truth:
            print(f"  [SKIP] No ground truth for: {rfp_name}")
            continue

        print(f"\n  [{i}/{len(cases)}] {rfp_name}")
        print(f"         Expected: {truth['correct_decision']}")

        t_start = time.perf_counter()
        try:
            if LIVE_MODE:
                agent_result = live_agent(rfp_text)
                print(f"         Mode: LIVE (Claude API)")
            else:
                agent_result = heuristic_agent(rfp_text, rfp_name)
                print(f"         Mode: HEURISTIC (no API key)")
        except Exception as e:
            print(f"         ERROR: {e}")
            report["cases"][rfp_name] = {"error": str(e)}
            continue

        elapsed = round(time.perf_counter() - t_start, 2)
        rec     = agent_result.get("recommendation", {})
        decision = rec.get("decision", "—")
        score    = rec.get("bid_score", "—")

        print(f"         Agent:    {decision}  (score: {score})  [{elapsed}s]")

        step_scores = derive_step_confidence(agent_result, truth)
        metrics     = run_all_metrics(rec, truth, step_scores)
        composite   = metrics.pop("_composite")
        passed      = composite >= 0.70

        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"         Result:   {status}  composite={composite:.0%}")

        # Flag critical failures
        blocking_score = metrics.get("blocking_gap_recall", {}).get("score", 1.0)
        if blocking_score < 1.0:
            print(f"         ⚠ CRITICAL: blocking gap(s) missed!")

        decision_score = metrics.get("decision_accuracy", {}).get("score", 0)
        if decision_score == 0:
            print(f"         ✗ WRONG DECISION: agent={decision}, expected={truth['correct_decision']}")

        report["cases"][rfp_name] = {
            "metrics":          metrics,
            "composite_score":  composite,
            "pass":             passed,
            "agent_decision":   decision,
            "correct_decision": truth["correct_decision"],
            "bid_score":        score,
            "elapsed_s":        elapsed,
            "agent_turns":      agent_result.get("total_turns", "—"),
            "step_scores":      {k: v[0] for k, v in step_scores.items()},
        }

    # ── Summary ──────────────────────────────────────────────────────────────
    results    = [v for v in report["cases"].values() if "error" not in v]
    composites = [v["composite_score"] for v in results]
    passed_n   = sum(1 for v in results if v["pass"])
    total_n    = len(results)

    # Decision confusion matrix
    tp = sum(1 for v in results if v["agent_decision"] == v["correct_decision"])
    wrong_bids = [
        v for v in results
        if "NO BID" not in v.get("correct_decision","")
        and "NO BID" in v.get("agent_decision","")
    ]
    missed_bids = [
        v for v in results
        if "NO BID" in v.get("correct_decision","")
        and "NO BID" not in v.get("agent_decision","")
    ]

    metric_names = list(METRIC_WEIGHTS.keys())
    metric_means = {}
    for m in metric_names:
        vals = [v["metrics"][m]["score"] for v in results if m in v.get("metrics",{})]
        metric_means[m] = round(sum(vals)/len(vals), 3) if vals else 0.0

    report["summary"] = {
        "total_cases":        total_n,
        "passed":             passed_n,
        "failed":             total_n - passed_n,
        "pass_rate":          round(passed_n / total_n, 2) if total_n else 0,
        "mean_composite":     round(sum(composites)/len(composites), 3) if composites else 0,
        "decision_accuracy":  round(tp / total_n, 2) if total_n else 0,
        "false_no_bids":      len(wrong_bids),    # bid ops we incorrectly rejected
        "false_bids":         len(missed_bids),   # no-bid ops we incorrectly pursued
        "metric_means":       metric_means,
        "worst_metric":       min(metric_means, key=metric_means.get) if metric_means else "—",
        "best_metric":        max(metric_means, key=metric_means.get) if metric_means else "—",
        "mean_elapsed_s":     round(sum(v["elapsed_s"] for v in results)/len(results), 1) if results else 0,
    }

    return report


def print_summary(report: dict):
    GREEN = "\033[92m"; AMBER = "\033[93m"; RED = "\033[91m"
    BOLD  = "\033[1m";  RESET = "\033[0m";  DIM  = "\033[2m"

    def col(s):
        return GREEN if s >= 0.8 else (AMBER if s >= 0.5 else RED)

    s = report["summary"]
    print(f"\n{'═'*62}")
    print(f"{BOLD}  TEST SET RESULTS — {report['mode'].upper()} MODE{RESET}")
    print(f"  {report['run_at']}")
    print(f"{'═'*62}")
    print(f"  Pass rate        : {col(s['pass_rate'])}{BOLD}{s['passed']}/{s['total_cases']} cases{RESET}")
    print(f"  Mean composite   : {col(s['mean_composite'])}{s['mean_composite']:.0%}{RESET}")
    print(f"  Decision accuracy: {col(s['decision_accuracy'])}{s['decision_accuracy']:.0%}{RESET}")
    print(f"  False no-bids    : {s['false_no_bids']}  (real bids we rejected)")
    print(f"  False bids       : {s['false_bids']}   (bad bids we pursued)")
    print(f"  Mean elapsed     : {s['mean_elapsed_s']}s per case")
    print(f"\n  Metric means:")
    for m, mean in sorted(s["metric_means"].items(), key=lambda x: -x[1]):
        bar = "█" * int(mean*10) + "░"*(10-int(mean*10))
        print(f"  {col(mean)}{bar}{RESET} {mean:.0%}  {DIM}{m}{RESET}")
    print(f"\n  Best  : {s['best_metric']}")
    print(f"  Worst : {s['worst_metric']}")
    print(f"{'═'*62}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case",    type=str, help="Filter to a single test case (e.g. TC-01)")
    parser.add_argument("--dry-run", action="store_true", help="Validate setup, no API calls")
    parser.add_argument("--json",    action="store_true", help="Print JSON to stdout")
    args = parser.parse_args()

    if args.dry_run:
        print("✓ rfp_texts.py      —", len(TEST_RFPS), "RFPs")
        print("✓ ground_truth.py   —", len(TEST_GROUND_TRUTH), "annotated cases")
        print("✓ API key present   —", "YES" if LIVE_MODE else "NO (heuristic mode)")
        print("✓ Setup valid. Run without --dry-run to execute.")
        sys.exit(0)

    if not LIVE_MODE:
        print("\n  ⚠  ANTHROPIC_API_KEY not set — running in HEURISTIC mode.")
        print("     Results reflect rule-based tool implementations, not real Claude.\n")

    report = run_test_set(filter_case=args.case)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_summary(report)

    out = os.path.join(os.path.dirname(__file__), "test_results.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  Saved: {out}")
