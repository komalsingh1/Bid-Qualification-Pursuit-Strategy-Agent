"""
Generates a self-contained HTML eval report from a runner.py report dict.
"""

import json
import os
from runner import run_eval

METRIC_LABELS = {
    "decision_accuracy":     "Decision Accuracy",
    "score_range_accuracy":  "Score Range Accuracy",
    "gap_recall":            "Gap Recall",
    "gap_precision":         "Gap Precision",
    "blocking_gap_recall":   "Blocking Gap Recall",
    "win_theme_relevance":   "Win Theme Relevance",
    "checklist_completeness":"Checklist Completeness",
    "confidence_calibration":"Confidence Calibration",
    "escalation_correctness":"Escalation Correctness",
}

def score_color(score: float) -> str:
    if score >= 0.8: return "#16a34a"
    if score >= 0.5: return "#d97706"
    return "#dc2626"

def score_bg(score: float) -> str:
    if score >= 0.8: return "#dcfce7"
    if score >= 0.5: return "#fef9c3"
    return "#fee2e2"

def pct(score: float) -> str:
    return f"{score:.0%}"

def generate_html(report: dict) -> str:
    s       = report["summary"]
    rfps    = report["rfps"]
    run_at  = report["run_at"]
    mode    = report["mode"].upper()

    mean_c  = s["mean_composite"]
    mc_col  = score_color(mean_c)

    # ── Per-RFP cards ─────────────────────────────────────────────────────────
    rfp_cards_html = ""
    for rfp_name, data in rfps.items():
        comp   = data["composite_score"]
        passed = data["pass"]
        status_bg  = "#dcfce7" if passed else "#fee2e2"
        status_col = "#15803d" if passed else "#b91c1c"
        status_txt = "PASS" if passed else "FAIL"

        rows = ""
        for metric, vals in data["metrics"].items():
            sc    = vals["score"]
            w     = vals["weight"]
            expl  = vals["explanation"].replace("\n", " · ")
            label = METRIC_LABELS.get(metric, metric)
            bar_w = int(sc * 100)
            bar_col = score_color(sc)
            rows += f"""
            <tr>
              <td style="padding:8px 12px;font-size:0.78rem;color:#374151;font-weight:500">{label}</td>
              <td style="padding:8px 12px;width:120px">
                <div style="background:#e5e7eb;border-radius:99px;height:6px;overflow:hidden">
                  <div style="width:{bar_w}%;height:6px;background:{bar_col};border-radius:99px"></div>
                </div>
              </td>
              <td style="padding:8px 12px;font-size:0.78rem;font-weight:700;color:{bar_col}">{pct(sc)}</td>
              <td style="padding:8px 12px;font-size:0.7rem;color:#9ca3af">{int(w*100)}%</td>
              <td style="padding:8px 12px;font-size:0.73rem;color:#6b7280">{expl[:120]}{"…" if len(expl)>120 else ""}</td>
            </tr>"""

        decision_match = "✓" if data["agent_decision"] == data["correct_decision"] else "✗"
        decision_col   = "#16a34a" if data["agent_decision"] == data["correct_decision"] else "#dc2626"

        rfp_cards_html += f"""
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;margin-bottom:20px;overflow:hidden">
          <div style="padding:16px 20px;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;justify-content:space-between">
            <div>
              <div style="font-size:0.95rem;font-weight:700;color:#111827">{rfp_name}</div>
              <div style="margin-top:4px;font-size:0.78rem;color:#6b7280">
                Agent: <strong style="color:{decision_col}">{data['agent_decision']}</strong>
                &nbsp;·&nbsp; Expected: <strong>{data['correct_decision']}</strong>
                &nbsp;·&nbsp; {decision_match} Decision match
                &nbsp;·&nbsp; Bid score: {data['bid_score']}
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:12px">
              <div style="font-size:1.6rem;font-weight:700;color:{score_color(comp)}">{pct(comp)}</div>
              <span style="background:{status_bg};color:{status_col};font-size:0.72rem;font-weight:700;
                           padding:3px 10px;border-radius:20px;text-transform:uppercase">{status_txt}</span>
            </div>
          </div>
          <table style="width:100%;border-collapse:collapse">
            <thead>
              <tr style="background:#f9fafb">
                <th style="padding:8px 12px;text-align:left;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;font-weight:700">Metric</th>
                <th style="padding:8px 12px;text-align:left;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;font-weight:700">Score</th>
                <th style="padding:8px 12px;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;font-weight:700"></th>
                <th style="padding:8px 12px;text-align:left;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;font-weight:700">Weight</th>
                <th style="padding:8px 12px;text-align:left;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;font-weight:700">Explanation</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>"""

    # ── Metric summary radar (as bar chart) ───────────────────────────────────
    metric_bars_html = ""
    for metric, mean_score in sorted(s["metric_means"].items(), key=lambda x: -x[1]):
        label   = METRIC_LABELS.get(metric, metric)
        col     = score_color(mean_score)
        bg      = score_bg(mean_score)
        bar_w   = int(mean_score * 100)
        weight  = METRIC_WEIGHTS_REF.get(metric, 0)
        metric_bars_html += f"""
        <div style="margin-bottom:12px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span style="font-size:0.8rem;font-weight:600;color:#374151">{label}</span>
            <div style="display:flex;align-items:center;gap:8px">
              <span style="font-size:0.68rem;color:#9ca3af">weight {int(weight*100)}%</span>
              <span style="font-size:0.82rem;font-weight:700;color:{col}">{pct(mean_score)}</span>
            </div>
          </div>
          <div style="background:#e5e7eb;border-radius:99px;height:8px;overflow:hidden">
            <div style="width:{bar_w}%;height:8px;background:{col};border-radius:99px;transition:width 0.3s"></div>
          </div>
        </div>"""

    # ── HTML ──────────────────────────────────────────────────────────────────
    pass_rate_pct = int(s["pass_rate"] * 100)
    passed = s["passed"]
    total  = s["total_rfps"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Opportunity Pursuit Agent — Eval Report</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
            background: #f8f9fa; color: #111827; padding: 40px 24px; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    table tr:hover {{ background: #fafafa; }}
  </style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div style="display:flex;align-items:center;justify-content:space-between;
              border-bottom:1px solid #e5e7eb;padding-bottom:20px;margin-bottom:28px">
    <div style="display:flex;align-items:center;gap:12px">
      <div style="width:36px;height:36px;background:#16a34a;border-radius:8px;
                  display:flex;align-items:center;justify-content:center;
                  color:white;font-weight:700;font-size:1rem">O</div>
      <div>
        <div style="font-size:1rem;font-weight:700;color:#111827">Opportunity Pursuit Agent</div>
        <div style="font-size:0.78rem;color:#6b7280">Evaluation Report · {mode} mode · {run_at}</div>
      </div>
    </div>
    <span style="background:#f0fdf4;color:#15803d;font-size:0.72rem;font-weight:700;
                 padding:4px 12px;border-radius:20px">responsive.ai prototype eval</span>
  </div>

  <!-- Summary cards -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px">
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px 20px">
      <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;margin-bottom:8px">Mean Composite</div>
      <div style="font-size:2rem;font-weight:700;color:{mc_col}">{pct(mean_c)}</div>
      <div style="font-size:0.75rem;color:#6b7280;margin-top:4px">weighted across 9 metrics</div>
    </div>
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px 20px">
      <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;margin-bottom:8px">Pass Rate</div>
      <div style="font-size:2rem;font-weight:700;color:{score_color(s['pass_rate'])}">{passed}/{total}</div>
      <div style="font-size:0.75rem;color:#6b7280;margin-top:4px">RFPs scoring ≥ 70%</div>
    </div>
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px 20px">
      <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;margin-bottom:8px">Best Metric</div>
      <div style="font-size:1rem;font-weight:700;color:#16a34a;line-height:1.3">{METRIC_LABELS.get(s['best_metric'], s['best_metric'])}</div>
      <div style="font-size:0.75rem;color:#6b7280;margin-top:4px">{pct(s['metric_means'].get(s['best_metric'],0))}</div>
    </div>
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px 20px">
      <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;margin-bottom:8px">Worst Metric</div>
      <div style="font-size:1rem;font-weight:700;color:#dc2626;line-height:1.3">{METRIC_LABELS.get(s['worst_metric'], s['worst_metric'])}</div>
      <div style="font-size:0.75rem;color:#6b7280;margin-top:4px">{pct(s['metric_means'].get(s['worst_metric'],0))}</div>
    </div>
  </div>

  <!-- Two-column: metric summary + interpretation -->
  <div style="display:grid;grid-template-columns:1.6fr 1fr;gap:20px;margin-bottom:28px">
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:20px 24px">
      <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.9px;
                  color:#6b7280;margin-bottom:16px">Average Score per Metric (across all RFPs)</div>
      {metric_bars_html}
    </div>
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:20px 24px">
      <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.9px;
                  color:#6b7280;margin-bottom:16px">Metric Weights & Rationale</div>
      <div style="font-size:0.78rem;color:#4b5563;line-height:1.8">
        <div><strong>Decision Accuracy (25%)</strong> — The primary output. Wrong call = wasted proposal spend.</div>
        <div style="margin-top:8px"><strong>Blocking Gap Recall (20%)</strong> — A missed blocker causes a disqualifying submission. Zero tolerance.</div>
        <div style="margin-top:8px"><strong>Gap Recall (15%)</strong> — Incomplete gap list leads to unprepared proposals.</div>
        <div style="margin-top:8px"><strong>Gap Precision (10%)</strong> — False gaps waste SME time on non-issues.</div>
        <div style="margin-top:8px"><strong>Score Range (10%)</strong> — Miscalibrated scores mislead leadership on risk.</div>
        <div style="margin-top:8px"><strong>Win Themes (8%)</strong> — Wrong themes produce weak proposal narratives.</div>
        <div style="margin-top:8px"><strong>Checklist (7%)</strong> — Missing actions cause missed deadlines.</div>
        <div style="margin-top:8px"><strong>Calibration + Escalation (5%)</strong> — Trust signals for the human-in-loop.</div>
      </div>
    </div>
  </div>

  <!-- Per-RFP results -->
  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.9px;
              color:#6b7280;margin-bottom:12px">Per-RFP Breakdown</div>
  {rfp_cards_html}

  <!-- Footer -->
  <div style="text-align:center;margin-top:32px;font-size:0.75rem;color:#9ca3af;border-top:1px solid #e5e7eb;padding-top:16px">
    Opportunity Pursuit Agent · Eval generated {run_at} · Pass threshold: 70% composite score
  </div>

</div>
</body>
</html>"""

# Need weights ref for the template
from metrics import METRIC_WEIGHTS as METRIC_WEIGHTS_REF


if __name__ == "__main__":
    print("Running eval...")
    report = run_eval("demo")

    html = generate_html(report)
    out_html = os.path.join(os.path.dirname(__file__), "eval_report.html")
    out_json = os.path.join(os.path.dirname(__file__), "eval_report.json")

    with open(out_html, "w") as f:
        f.write(html)
    with open(out_json, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✓ HTML report : {out_html}")
    print(f"✓ JSON report : {out_json}")

    # Print summary to terminal
    s = report["summary"]
    print(f"\n  Mean composite : {s['mean_composite']:.0%}")
    print(f"  Pass rate      : {s['passed']}/{s['total_rfps']} RFPs")
    print(f"  Best metric    : {s['best_metric']}")
    print(f"  Worst metric   : {s['worst_metric']}")
