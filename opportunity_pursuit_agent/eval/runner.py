"""
Eval runner — executes all metrics across all RFPs and returns a full report dict.

Two modes:
  demo  — uses pre-computed agent outputs from demo_result.py and rfp_configs.py
  live  — calls the real agent (requires ANTHROPIC_API_KEY)

Usage:
  python runner.py            # demo mode
  python runner.py --live     # live mode (requires API key)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..","prototype"))

import json
import time
import argparse
from datetime import datetime

from ground_truth import GROUND_TRUTH
from metrics import run_all_metrics, METRIC_WEIGHTS

# ── Import agent outputs ───────────────────────────────────────────────────────

from demo_result import DEMO_RESULT
from rfp_configs import RFP_REGISTRY

# Step confidence data (from app.py STEP_CONFIDENCE)
STEP_CONFIDENCE = {
    "California CDHS (Sample)": {
        "extract_requirements":    (97, "RFP is well-structured — all sections parsed cleanly"),
        "check_capabilities":      (91, "Strong KB match on 12 of 15 requirements"),
        "get_win_loss_history":    (88, "3 highly similar past opportunities retrieved"),
        "identify_gaps":           (85, "FedRAMP gap is clear; SBE gap measurable"),
        "get_sme_and_content":     (90, "All gap owners resolved; 6 reusable blocks found"),
        "generate_recommendation": (72, "FedRAMP legal interpretation introduces uncertainty"),
    },
    "Hemisfair AR Project": {
        "extract_requirements":    (95, "Short RFP — requirements extracted with high clarity"),
        "check_capabilities":      (55, "Only 2 of 8 requirements matched in KB"),
        "get_win_loss_history":    (40, "No comparable past projects found in CRM"),
        "identify_gaps":           (92, "Gaps are unambiguous"),
        "get_sme_and_content":     (35, "No SME owners or reusable content available"),
        "generate_recommendation": (96, "No-bid is unambiguous"),
    },
    "DLC Website Redesign": {
        "extract_requirements":    (93, "39-page RFP parsed cleanly"),
        "check_capabilities":      (62, "WCAG met; web design/CMS/UX unmatched"),
        "get_win_loss_history":    (48, "No web agency projects in history"),
        "identify_gaps":           (88, "Gaps clearly identified"),
        "get_sme_and_content":     (44, "No CMS or web design SMEs on staff"),
        "generate_recommendation": (91, "No-bid confidence high"),
    },
    "MCCVB Creative Agency": {
        "extract_requirements":    (94, "Scope of work clearly defined"),
        "check_capabilities":      (20, "0 of 6 core requirements matched"),
        "get_win_loss_history":    (18, "No creative or media buying projects in any history"),
        "identify_gaps":           (95, "3 blocking gaps — no viable remediation"),
        "get_sme_and_content":     (15, "No owners, no reusable content"),
        "generate_recommendation": (98, "No-bid is certain"),
    },
}

ALL_RESULTS = {
    "California CDHS (Sample)": DEMO_RESULT,
    **{k: v["demo_result"] for k, v in RFP_REGISTRY.items()},
}


# ── Runner ────────────────────────────────────────────────────────────────────

def run_eval(mode: str = "demo") -> dict:
    """
    Run all metrics across all RFPs.

    Returns:
        {
          "mode": "demo" | "live",
          "run_at": ISO timestamp,
          "rfps": {
              rfp_name: {
                  "metrics": { metric_name: {score, explanation, weight, weighted} },
                  "composite_score": float,
                  "pass": bool,
              }
          },
          "summary": {
              "mean_composite": float,
              "pass_rate": float,
              "metric_means": { metric_name: float },
              "worst_metric": str,
              "best_metric": str,
          }
        }
    """
    report = {
        "mode":   mode,
        "run_at": datetime.utcnow().isoformat() + "Z",
        "rfps":   {},
    }

    for rfp_name, truth in GROUND_TRUTH.items():
        agent_result = ALL_RESULTS.get(rfp_name)
        if not agent_result:
            print(f"  [SKIP] No agent result for: {rfp_name}")
            continue

        agent_rec   = agent_result.get("recommendation", {})
        step_scores = STEP_CONFIDENCE.get(rfp_name, {})

        if mode == "live":
            agent_result, step_scores = _run_live(rfp_name)
            agent_rec = agent_result.get("recommendation", {})

        metrics = run_all_metrics(agent_rec, truth, step_scores)
        composite = metrics.pop("_composite")

        report["rfps"][rfp_name] = {
            "metrics":        metrics,
            "composite_score": composite,
            "pass":           composite >= 0.70,
            "agent_decision": agent_rec.get("decision", "—"),
            "correct_decision": truth["correct_decision"],
            "bid_score":      agent_rec.get("bid_score", "—"),
        }

    # ── Summary ──────────────────────────────────────────────────────
    composites    = [v["composite_score"] for v in report["rfps"].values()]
    pass_count    = sum(1 for v in report["rfps"].values() if v["pass"])
    metric_names  = list(METRIC_WEIGHTS.keys())
    metric_means  = {}
    for m in metric_names:
        vals = [v["metrics"][m]["score"] for v in report["rfps"].values() if m in v["metrics"]]
        metric_means[m] = round(sum(vals) / len(vals), 3) if vals else 0.0

    report["summary"] = {
        "mean_composite": round(sum(composites) / len(composites), 3) if composites else 0,
        "pass_rate":      round(pass_count / len(report["rfps"]), 2) if report["rfps"] else 0,
        "metric_means":   metric_means,
        "worst_metric":   min(metric_means, key=metric_means.get) if metric_means else "—",
        "best_metric":    max(metric_means, key=metric_means.get) if metric_means else "—",
        "total_rfps":     len(report["rfps"]),
        "passed":         pass_count,
        "failed":         len(report["rfps"]) - pass_count,
    }

    return report


def _run_live(rfp_name: str):
    """Run the real agent for a given RFP. Used in live eval mode."""
    from agent import run_agent
    from rfp_configs import RFP_REGISTRY
    from mock_data import SAMPLE_RFP
    from pdf_parser import extract_pdf_text

    if rfp_name == "California CDHS (Sample)":
        rfp_text = SAMPLE_RFP
    elif rfp_name in RFP_REGISTRY:
        rfp_text = extract_pdf_text(RFP_REGISTRY[rfp_name]["file"])
    else:
        raise ValueError(f"Unknown RFP: {rfp_name}")

    step_scores_live = {}

    def cb(event_type, data):
        pass  # live mode — no streaming needed for eval

    result = run_agent(rfp_text, stream_callback=cb)
    # Live mode can't auto-populate step_scores (they come from UI layer)
    # Return empty step_scores and let calibration metric return 0.5
    return result, step_scores_live


# ── CLI ───────────────────────────────────────────────────────────────────────

def print_report(report: dict):
    BOLD  = "\033[1m"
    GREEN = "\033[92m"
    AMBER = "\033[93m"
    RED   = "\033[91m"
    RESET = "\033[0m"
    DIM   = "\033[2m"

    def colour(score):
        if score >= 0.8: return GREEN
        if score >= 0.5: return AMBER
        return RED

    s = report["summary"]
    print(f"\n{'═'*62}")
    print(f"{BOLD}  OPPORTUNITY PURSUIT AGENT — EVAL REPORT{RESET}")
    print(f"  Mode: {report['mode'].upper()}  ·  Run: {report['run_at']}")
    print(f"{'═'*62}")
    print(f"\n  Mean composite score : {colour(s['mean_composite'])}{BOLD}{s['mean_composite']:.0%}{RESET}")
    print(f"  Pass rate (≥70%)     : {colour(s['pass_rate'])}{s['passed']}/{s['total_rfps']} RFPs{RESET}")
    print(f"  Best metric          : {s['best_metric']}")
    print(f"  Worst metric         : {s['worst_metric']}\n")

    for rfp_name, data in report["rfps"].items():
        status = f"{GREEN}PASS{RESET}" if data["pass"] else f"{RED}FAIL{RESET}"
        c = colour(data["composite_score"])
        print(f"  {'─'*58}")
        print(f"  {BOLD}{rfp_name}{RESET}  [{status}]")
        print(f"  Composite: {c}{data['composite_score']:.0%}{RESET}  |  "
              f"Agent: {data['agent_decision']}  |  "
              f"Expected: {data['correct_decision']}  |  "
              f"Score: {data['bid_score']}")
        print()
        for metric, vals in data["metrics"].items():
            sc   = vals["score"]
            expl = vals["explanation"].split("\n")[0]   # first line only
            bar  = "█" * int(sc * 10) + "░" * (10 - int(sc * 10))
            print(f"  {colour(sc)}{bar}{RESET} {sc:.0%}  {DIM}{metric:28}{RESET}  {expl}")
        print()

    print(f"{'═'*62}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run against live agent")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    mode = "live" if args.live else "demo"
    print(f"\nRunning eval in {mode.upper()} mode...")
    report = run_eval(mode)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
        # Always save JSON alongside
        out = os.path.join(os.path.dirname(__file__), "eval_report.json")
        with open(out, "w") as f:
            json.dump(report, f, indent=2)
        print(f"  JSON saved to: {out}\n")
