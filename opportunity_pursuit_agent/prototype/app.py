"""
Streamlit UI — Opportunity Pursuit Agent
Design: responsive.ai-style B2B SaaS, light theme, green accents.

Run with:  streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import time
import json
from mock_data import SAMPLE_RFP
from agent import run_agent
from demo_result import DEMO_RESULT
from rfp_configs import RFP_REGISTRY
from pdf_parser import extract_pdf_text

LIVE_MODE = bool(os.environ.get("ANTHROPIC_API_KEY"))

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Opportunity Pursuit Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
  html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
  }
  .main { background-color: #f8f9fa; }
  .block-container { padding: 2rem 2.5rem 3rem; max-width: 1280px; }
  section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e5e7eb; }

  .topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 20px 0; border-bottom: 1px solid #e5e7eb; margin-bottom: 24px;
  }
  .topbar-left { display: flex; align-items: center; gap: 12px; }
  .topbar-logo {
    width: 36px; height: 36px; background: #16a34a; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 1rem;
  }
  .topbar-title { font-size: 1.05rem; font-weight: 600; color: #111827; }
  .topbar-sub   { font-size: 0.8rem; color: #6b7280; margin-top: 1px; }
  .live-badge   { font-size: 0.72rem; font-weight: 600; padding: 3px 10px;
                  border-radius: 20px; letter-spacing: 0.3px; }
  .live-on  { background: #dcfce7; color: #15803d; }
  .live-off { background: #fef9c3; color: #854d0e; }

  /* RFP selector cards */
  .rfp-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
  .rfp-card {
    background: #ffffff; border: 1.5px solid #e5e7eb; border-radius: 10px;
    padding: 14px 16px; cursor: pointer; transition: border-color 0.15s;
  }
  .rfp-card.active { border-color: #16a34a; background: #f0fdf4; }
  .rfp-card-label  { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
                     letter-spacing: 0.8px; color: #9ca3af; margin-bottom: 4px; }
  .rfp-card-title  { font-size: 0.83rem; font-weight: 600; color: #111827;
                     line-height: 1.3; margin-bottom: 6px; }
  .rfp-card-meta   { font-size: 0.72rem; color: #6b7280; }
  .rfp-card-value  { font-size: 0.75rem; font-weight: 600; color: #374151; margin-top: 4px; }

  /* RFP strip */
  .rfp-strip {
    background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px;
    padding: 14px 22px; display: flex; gap: 36px; align-items: center;
    margin-bottom: 20px; flex-wrap: wrap;
  }
  .rfp-meta-label { font-size: 0.68rem; text-transform: uppercase;
                    letter-spacing: 0.8px; color: #9ca3af; font-weight: 600; }
  .rfp-meta-value { font-size: 0.85rem; font-weight: 600; color: #111827; margin-top: 2px; }

  /* Score cards */
  .score-card {
    background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 18px 22px; height: 100%;
  }
  .score-card-label { font-size: 0.68rem; text-transform: uppercase;
                      letter-spacing: 0.8px; color: #6b7280; font-weight: 600; margin-bottom: 8px; }
  .score-card-value { font-size: 1.85rem; font-weight: 700; line-height: 1.1; color: #111827; }
  .score-card-sub   { font-size: 0.75rem; color: #6b7280; margin-top: 4px; }
  .decision-bid     { color: #16a34a; }
  .decision-cond    { color: #d97706; }
  .decision-nobid   { color: #dc2626; }
  .score-green { color: #16a34a; }
  .score-amber { color: #d97706; }
  .score-red   { color: #dc2626; }

  /* Score bars */
  .trace-row { margin-bottom: 14px; }
  .trace-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
  .trace-dim  { font-size: 0.8rem; font-weight: 600; color: #374151; }
  .trace-pts  { font-size: 0.8rem; font-weight: 700; color: #16a34a; }
  .trace-bar-bg   { height: 6px; background: #e5e7eb; border-radius: 99px; overflow: hidden; }
  .trace-bar-fill { height: 6px; border-radius: 99px; background: #16a34a; }
  .trace-bar-fill.amber { background: #f59e0b; }
  .trace-bar-fill.red   { background: #ef4444; }
  .trace-desc { font-size: 0.71rem; color: #9ca3af; margin-top: 2px; }

  /* Agent steps */
  .agent-step {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 14px; border-radius: 8px; margin-bottom: 6px;
    background: #f9fafb; border: 1px solid #e5e7eb;
  }
  .agent-step.active  { background: #f0fdf4; border-color: #bbf7d0; }
  .agent-step.done    { background: #ffffff; border-color: #e5e7eb; }
  .agent-step.escalate{ background: #fff7ed; border-color: #fb923c; border-left: 3px solid #ea580c; }
  .step-icon  { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
  .step-name  { font-size: 0.82rem; font-weight: 600; color: #111827; }
  .step-desc  { font-size: 0.73rem; color: #6b7280; margin-top: 1px; }
  .step-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; align-self: center; }
  .step-check { color: #16a34a; font-size: 0.9rem; }

  /* Confidence pill on each step */
  .conf-pill {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.72rem; font-weight: 700; padding: 2px 9px;
    border-radius: 20px; white-space: nowrap;
  }
  .conf-high  { background: #dcfce7; color: #15803d; }
  .conf-mid   { background: #fef9c3; color: #92400e; }
  .conf-low   { background: #fee2e2; color: #b91c1c; }

  /* Escalation banner */
  .escalate-banner {
    background: #fff7ed; border: 1px solid #fb923c;
    border-left: 4px solid #ea580c; border-radius: 8px;
    padding: 14px 18px; margin: 12px 0 4px;
    display: flex; align-items: flex-start; gap: 12px;
  }
  .escalate-icon  { font-size: 1.3rem; flex-shrink: 0; }
  .escalate-title { font-size: 0.88rem; font-weight: 700; color: #9a3412; margin-bottom: 3px; }
  .escalate-body  { font-size: 0.79rem; color: #c2410c; line-height: 1.55; }

  /* Section headers */
  .section-header {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.9px; color: #6b7280; margin: 22px 0 10px;
  }

  /* Gap cards */
  .gap-card {
    background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px;
    padding: 14px 16px; margin-bottom: 10px;
  }
  .gap-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
  .gap-title  { font-size: 0.86rem; font-weight: 600; color: #111827; line-height: 1.3; }
  .gap-action { font-size: 0.79rem; color: #4b5563; line-height: 1.55; }
  .gap-owner  { font-size: 0.73rem; color: #9ca3af; margin-top: 6px; }
  .gap-owner span { color: #374151; font-weight: 600; }

  .badge { display: inline-flex; align-items: center; padding: 2px 9px;
           border-radius: 20px; font-size: 0.67rem; font-weight: 700;
           text-transform: uppercase; letter-spacing: 0.4px; flex-shrink: 0; }
  .badge-blocking { background: #fee2e2; color: #b91c1c; }
  .badge-high     { background: #ffedd5; color: #c2410c; }
  .badge-medium   { background: #fef9c3; color: #92400e; }
  .badge-low      { background: #e0f2fe; color: #0369a1; }

  /* Performance strip */
  .perf-strip {
    background: #f8faff; border: 1px solid #dbeafe; border-radius: 8px;
    padding: 10px 18px; display: flex; gap: 32px; align-items: center;
    margin-bottom: 16px; flex-wrap: wrap;
  }
  .perf-item-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
                     letter-spacing: 0.8px; color: #6b7280; }
  .perf-item-value { font-size: 0.85rem; font-weight: 700; color: #1d4ed8; margin-top: 2px; }
  .perf-item-sub   { font-size: 0.7rem; color: #9ca3af; }
  .saving-badge    { background: #dcfce7; color: #15803d; font-size: 0.72rem;
                     font-weight: 700; padding: 3px 10px; border-radius: 20px; }

  /* Checklist */
  .checklist-wrap { background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:4px 16px; }
  .checklist-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0; border-bottom: 1px solid #f3f4f6; gap: 12px;
  }
  .checklist-row:last-child { border-bottom: none; }
  .checklist-left { display: flex; align-items: flex-start; gap: 10px; flex: 1; }
  .check-box { width: 15px; height: 15px; border: 1.5px solid #d1d5db;
               border-radius: 4px; flex-shrink: 0; margin-top: 2px; }
  .checklist-item-text { font-size: 0.81rem; color: #374151; font-weight: 500; line-height: 1.4; }
  .checklist-owner { font-size: 0.71rem; color: #9ca3af; margin-top: 2px; }
  .checklist-due { font-size: 0.71rem; font-weight: 600; color: #6b7280;
                   background: #f3f4f6; padding: 2px 8px; border-radius: 4px;
                   white-space: nowrap; flex-shrink: 0; }

  .theme-pill {
    display: flex; align-items: center; gap: 8px;
    background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px;
    padding: 9px 14px; margin-bottom: 8px;
    font-size: 0.83rem; font-weight: 500; color: #15803d;
  }
  .warn-card {
    background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px;
    padding: 10px 14px; margin-bottom: 8px;
    font-size: 0.8rem; color: #9a3412; line-height: 1.5;
  }
  .summary-box {
    background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a;
    border-radius: 8px; padding: 14px 18px;
    font-size: 0.85rem; color: #14532d; line-height: 1.65; margin-bottom: 22px;
  }
  .content-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: #f8f9fa; border: 1px solid #e5e7eb; border-radius: 6px;
    padding: 5px 10px; margin: 3px 3px 3px 0; font-size: 0.74rem; color: #374151;
  }
  .no-bid-banner {
    background: #fef2f2; border: 1px solid #fecaca; border-left: 4px solid #dc2626;
    border-radius: 8px; padding: 16px 20px; margin-bottom: 20px;
    font-size: 0.88rem; color: #7f1d1d; font-weight: 500;
  }
  .empty-state { text-align:center; padding: 80px 40px; color: #9ca3af; }
  .empty-icon  { font-size: 2.5rem; margin-bottom: 12px; }
  .empty-title { font-size: 1rem; font-weight: 600; color: #374151; margin-bottom: 6px; }
  .empty-sub   { font-size: 0.85rem; }

  #MainMenu, footer, header { visibility: hidden; }
  div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Tool metadata ─────────────────────────────────────────────────────────────

TOOL_META = {
    "extract_requirements":    ("📋", "Extracting RFP requirements",       "Parsing mandatory, scored, compliance & team requirements"),
    "check_capabilities":      ("🔍", "Checking capabilities",             "Matching requirements against internal knowledge base"),
    "get_win_loss_history":    ("📊", "Retrieving win / loss history",     "Searching CRM for similar past opportunities"),
    "identify_gaps":           ("⚠️",  "Identifying gaps",                  "Classifying gaps by severity: Blocking, High, Medium, Low"),
    "get_sme_and_content":     ("👥", "Assigning SME owners",              "Looking up owners and reusable proposal content"),
    "generate_recommendation": ("🎯", "Generating recommendation",         "Synthesising evidence into bid score and action plan"),
}

# ── Session state ─────────────────────────────────────────────────────────────

if "result" not in st.session_state:
    st.session_state.result = None
if "selected_rfp" not in st.session_state:
    st.session_state.selected_rfp = "California CDHS (Sample)"
if "step_scores" not in st.session_state:
    st.session_state.step_scores = {}

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 16px">
      <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:1px;color:#9ca3af;margin-bottom:12px">Navigation</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**Analysis tools**")
    st.markdown("""
    <div style="font-size:0.79rem;color:#6b7280;line-height:2.3;">
      📋 Requirements Extraction<br>
      🔍 Capability Matching<br>
      📊 Win / Loss Retrieval<br>
      ⚠️ Gap Identification<br>
      👥 SME Assignment<br>
      🎯 Bid Recommendation
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("**Model**")
    st.markdown("`claude-sonnet-4-6`")
    mode_label = "🟢 Live (API key present)" if LIVE_MODE else "🟡 Demo mode"
    st.markdown(mode_label)

# ── Topbar ────────────────────────────────────────────────────────────────────

badge_cls = "live-on" if LIVE_MODE else "live-off"
badge_txt = "● Live" if LIVE_MODE else "● Demo"
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-logo">O</div>
    <div>
      <div class="topbar-title">Opportunity Pursuit Agent</div>
      <div class="topbar-sub">Bid intelligence powered by AI · responsive.ai</div>
    </div>
  </div>
  <span class="live-badge {badge_cls}">{badge_txt}</span>
</div>
""", unsafe_allow_html=True)

# ── RFP Selector ──────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">Select an RFP to analyse</div>', unsafe_allow_html=True)

# Build registry including the built-in sample
ALL_RFPS = {
    "California CDHS (Sample)": {
        "agency": "California Dept. of Health Services",
        "rfp_number": "CDHS-2024-IT-0042",
        "title": "Enterprise Care Coordination Platform",
        "deadline": "Sep 30, 2024",
        "value": "$18M / 3 years",
        "type": "State Medicaid Platform",
        "demo_result": DEMO_RESULT,
        "file": None,
    },
    **{k: v for k, v in RFP_REGISTRY.items()},
}

rfp_names = list(ALL_RFPS.keys())
cols = st.columns(len(rfp_names))

for i, (name, meta) in enumerate(ALL_RFPS.items()):
    with cols[i]:
        is_active = st.session_state.selected_rfp == name
        active_cls = "active" if is_active else ""
        # Show card as HTML for styling, use button for click
        st.markdown(f"""
        <div class="rfp-card {active_cls}">
          <div class="rfp-card-label">{meta['type']}</div>
          <div class="rfp-card-title">{meta['title']}</div>
          <div class="rfp-card-meta">{meta['agency']}</div>
          <div class="rfp-card-value">{meta['value']}</div>
        </div>
        """, unsafe_allow_html=True)
        btn_label = "✓ Selected" if is_active else "Select"
        if st.button(btn_label, key=f"sel_{i}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.selected_rfp = name
            st.session_state.result = None
            st.rerun()

# ── Active RFP metadata strip ─────────────────────────────────────────────────

active = ALL_RFPS[st.session_state.selected_rfp]
st.markdown(f"""
<div class="rfp-strip">
  <div>
    <div class="rfp-meta-label">RFP Number</div>
    <div class="rfp-meta-value">{active['rfp_number']}</div>
  </div>
  <div>
    <div class="rfp-meta-label">Issuing Agency</div>
    <div class="rfp-meta-value">{active['agency']}</div>
  </div>
  <div>
    <div class="rfp-meta-label">Contract Value</div>
    <div class="rfp-meta-value">{active['value']}</div>
  </div>
  <div>
    <div class="rfp-meta-label">Deadline</div>
    <div class="rfp-meta-value">{active['deadline']}</div>
  </div>
  <div>
    <div class="rfp-meta-label">Type</div>
    <div class="rfp-meta-value">{active['type']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Run button ────────────────────────────────────────────────────────────────

col_btn, _ = st.columns([1, 4])
with col_btn:
    run_clicked = st.button("Run Analysis", type="primary", use_container_width=True)

# ── Per-RFP step confidence scores ───────────────────────────────────────────
# Each value is (confidence_pct, one-line rationale)
# Scores below 80 trigger human-in-loop escalation.

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
        "identify_gaps":           (92, "Gaps are unambiguous — AR and budget mismatches are clear"),
        "get_sme_and_content":     (35, "No SME owners or reusable content available for this domain"),
        "generate_recommendation": (96, "No-bid is unambiguous given capability and budget mismatch"),
    },
    "DLC Website Redesign": {
        "extract_requirements":    (93, "39-page RFP parsed; requirements well-defined"),
        "check_capabilities":      (62, "WCAG met; web design, CMS, UX all unmatched"),
        "get_win_loss_history":    (48, "No web agency projects in CRM history"),
        "identify_gaps":           (88, "Gaps clearly identified — no design portfolio is blocking"),
        "get_sme_and_content":     (44, "No CMS or web design SMEs on staff"),
        "generate_recommendation": (91, "No-bid confidence high; partial matches insufficient"),
    },
    "MCCVB Creative Agency": {
        "extract_requirements":    (94, "Scope of work clearly defined across 14 pages"),
        "check_capabilities":      (20, "0 of 6 core requirements matched — entirely different business"),
        "get_win_loss_history":    (18, "No creative or media buying projects in any history"),
        "identify_gaps":           (95, "3 blocking gaps — no viable remediation path"),
        "get_sme_and_content":     (15, "No owners, no reusable content for this category"),
        "generate_recommendation": (98, "No-bid is certain — complete capability mismatch"),
    },
}

ESCALATION_THRESHOLD = 80

def get_step_scores(rfp_name: str) -> dict:
    return STEP_CONFIDENCE.get(rfp_name, {})

def conf_pill(pct: int) -> str:
    if pct >= 80:
        cls, icon = "conf-high", "●"
    elif pct >= 60:
        cls, icon = "conf-mid",  "●"
    else:
        cls, icon = "conf-low",  "●"
    return f'<span class="conf-pill {cls}">{icon} {pct}%</span>'

# ── Helpers ───────────────────────────────────────────────────────────────────

# Parallel batch groupings — shown as section labels in the trace
PARALLEL_BATCHES = [
    ("Batch 1 — parallel", ["extract_requirements", "get_win_loss_history"]),
    ("Batch 2 — parallel", ["check_capabilities",   "get_sme_and_content"]),
    ("Batch 3",            ["identify_gaps"]),
    ("Batch 4",            ["generate_recommendation"]),
]

def render_trace(completed: list, active_tool: str = None, scores: dict = None):
    scores = scores or {}
    html = ""
    tool_to_batch = {t: label for label, tools in PARALLEL_BATCHES for t in tools}
    rendered_batches = set()

    for tool_name, (icon, name, desc) in TOOL_META.items():
        step_score, step_note = scores.get(tool_name, (None, ""))
        if tool_name in completed:
            needs_escalation = step_score is not None and step_score < ESCALATION_THRESHOLD
            cls = "escalate" if needs_escalation else "done"
            pill = conf_pill(step_score) if step_score is not None else ""
            check = "⚠ Review" if needs_escalation else "✓"
            check_color = "#ea580c" if needs_escalation else "#16a34a"
            note_html = f'<div style="font-size:0.7rem;color:#9a3412;margin-top:3px">{step_note}</div>' if needs_escalation else ""
            right = f"""
              <div class="step-right">
                {pill}
                <span style="color:{check_color};font-size:0.82rem;font-weight:600">{check}</span>
              </div>"""
            desc_extra = note_html
        elif tool_name == active_tool:
            cls = "active"
            right = '<div class="step-right"><span style="color:#16a34a;font-size:0.74rem">Running…</span></div>'
            desc_extra = ""
        else:
            cls = ""
            right = '<div class="step-right"><span style="color:#d1d5db;font-size:0.8rem">—</span></div>'
            desc_extra = ""

        # Insert batch label before first tool in each batch
        batch_label = tool_to_batch.get(tool_name, "")
        if batch_label and batch_label not in rendered_batches:
            rendered_batches.add(batch_label)
            is_parallel = "parallel" in batch_label
            badge = '<span style="background:#dbeafe;color:#1d4ed8;font-size:0.65rem;font-weight:700;padding:1px 7px;border-radius:10px;margin-left:6px">⚡ parallel</span>' if is_parallel else ""
            html += f'<div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#9ca3af;margin:12px 0 5px 2px">{batch_label}{badge}</div>'

        html += f"""
        <div class="agent-step {cls}">
          <span class="step-icon">{icon}</span>
          <div class="step-body" style="flex:1">
            <div class="step-name">{name}</div>
            <div class="step-desc">{desc}</div>
            {desc_extra}
          </div>
          {right}
        </div>"""
    return html

def escalation_banner(rfp_name: str, scores: dict) -> str:
    """Return HTML escalation banner if any completed step is below threshold."""
    low_steps = [
        (TOOL_META[t][1], pct, note)
        for t, (pct, note) in scores.items()
        if pct < ESCALATION_THRESHOLD
    ]
    if not low_steps:
        return ""
    items = "".join([
        f'<div style="margin-top:4px">· <strong>{name}</strong> — {pct}% confidence: {note}</div>'
        for name, pct, note in low_steps
    ])
    return f"""
    <div class="escalate-banner">
      <div class="escalate-icon">🧑‍💼</div>
      <div>
        <div class="escalate-title">Human Review Required</div>
        <div class="escalate-body">
          {len(low_steps)} step(s) fell below the {ESCALATION_THRESHOLD}% confidence threshold.
          A human reviewer should validate these findings before the bid decision is finalised.
          {items}
        </div>
      </div>
    </div>"""

# ── Execution ─────────────────────────────────────────────────────────────────

if run_clicked:
    st.session_state.result = None
    st.markdown('<div class="section-header">Agent Execution</div>', unsafe_allow_html=True)
    trace_ph   = st.empty()
    escalate_ph = st.empty()
    scores = get_step_scores(st.session_state.selected_rfp)
    trace_ph.markdown(render_trace([], scores=scores), unsafe_allow_html=True)

    if LIVE_MODE:
        rfp_text = SAMPLE_RFP if active["file"] is None else extract_pdf_text(active["file"])
        completed = []
        state = {"cur": None}

        def cb(event_type, data):
            if event_type == "tool_call":
                state["cur"] = data["name"]
                trace_ph.markdown(render_trace(completed, state["cur"], scores), unsafe_allow_html=True)
            elif event_type == "tool_result":
                if state["cur"] and state["cur"] not in completed:
                    completed.append(state["cur"])
                state["cur"] = None
                trace_ph.markdown(render_trace(completed, scores=scores), unsafe_allow_html=True)
                # Show escalation banner as steps complete
                done_scores = {t: scores[t] for t in completed if t in scores}
                banner = escalation_banner(st.session_state.selected_rfp, done_scores)
                if banner:
                    escalate_ph.markdown(banner, unsafe_allow_html=True)

        result = run_agent(rfp_text, stream_callback=cb)
        trace_ph.markdown(render_trace(list(TOOL_META.keys()), scores=scores), unsafe_allow_html=True)
    else:
        completed = []
        for tool_name in TOOL_META:
            trace_ph.markdown(render_trace(completed, tool_name, scores), unsafe_allow_html=True)
            time.sleep(0.65)
            completed.append(tool_name)
            trace_ph.markdown(render_trace(completed, scores=scores), unsafe_allow_html=True)
            # Show escalation banner live as steps complete
            done_scores = {t: scores[t] for t in completed if t in scores}
            banner = escalation_banner(st.session_state.selected_rfp, done_scores)
            if banner:
                escalate_ph.markdown(banner, unsafe_allow_html=True)
        result = active["demo_result"]

    st.session_state.result = result
    st.session_state.step_scores = scores
    st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────

if st.session_state.result:
    result = st.session_state.result
    rec    = result.get("recommendation", {})
    gaps   = rec.get("gap_action_plan", [])
    checklist = rec.get("submission_checklist", [])
    score  = rec.get("bid_score", 0)
    decision = rec.get("decision", "—")
    log    = result.get("tool_call_log", [])

    score_cls = "score-green" if score >= 70 else ("score-amber" if score >= 40 else "score-red")
    dec_cls   = ("decision-bid" if ("BID" in decision and "CONDITIONAL" not in decision and "NO" not in decision)
                 else ("decision-cond" if "CONDITIONAL" in decision else "decision-nobid"))

    blocking = len([g for g in gaps if g["severity"] == "BLOCKING"])
    high     = len([g for g in gaps if g["severity"] == "HIGH"])

    # No-bid banner
    if "NO BID" in decision:
        st.markdown(f"""
        <div class="no-bid-banner">
          🚫 <strong>No Bid Recommended</strong> — Agent identified {blocking} blocking gap(s)
          with no viable path to compliance. Pursuing this opportunity is not advised.
        </div>""", unsafe_allow_html=True)

    # Escalation banner (persistent after rerun)
    saved_scores = st.session_state.get("step_scores", {})
    if saved_scores:
        banner = escalation_banner(st.session_state.selected_rfp, saved_scores)
        if banner:
            st.markdown(banner, unsafe_allow_html=True)

    # Performance strip (live mode only — demo shows estimated values)
    elapsed  = result.get("total_elapsed_s")
    savings  = result.get("parallel_savings_s")
    turns    = result.get("total_turns", "—")
    n_tools  = len(result.get("tool_call_log", []))
    if elapsed is None:
        # Demo mode: show illustrative estimates
        elapsed, savings, turns = "~6s", "~8s", 3
    saving_html = f'<span class="saving-badge">⚡ ~{savings}s saved vs sequential</span>' if savings else ""
    st.markdown(f"""
    <div class="perf-strip">
      <div>
        <div class="perf-item-label">Wall time</div>
        <div class="perf-item-value">{elapsed}</div>
        <div class="perf-item-sub">end-to-end</div>
      </div>
      <div>
        <div class="perf-item-label">API turns</div>
        <div class="perf-item-value">{turns}</div>
        <div class="perf-item-sub">vs 6 sequential</div>
      </div>
      <div>
        <div class="perf-item-label">Tools executed</div>
        <div class="perf-item-value">{n_tools}</div>
        <div class="perf-item-sub">across {turns} batches</div>
      </div>
      {saving_html}
    </div>""", unsafe_allow_html=True)

    # Executive summary
    summary = result.get("executive_summary", rec.get("rationale", ""))
    if summary:
        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

    # ── Score cards ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">Bid Assessment</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="score-card">
          <div class="score-card-label">Recommendation</div>
          <div class="score-card-value {dec_cls}" style="font-size:1.3rem">{decision}</div>
          <div class="score-card-sub">Confidence: {rec.get('confidence','—')}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="score-card">
          <div class="score-card-label">Bid Score</div>
          <div class="score-card-value {score_cls}">{score}<span style="font-size:1rem;color:#9ca3af;font-weight:400"> /100</span></div>
          <div class="score-card-sub">Based on gap analysis</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="score-card">
          <div class="score-card-label">Gaps Identified</div>
          <div class="score-card-value" style="font-size:1.6rem">{len(gaps)}</div>
          <div class="score-card-sub" style="color:#b91c1c">{blocking} blocking · {high} high</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="score-card">
          <div class="score-card-label">Action Items</div>
          <div class="score-card-value" style="font-size:1.6rem">{len(checklist)}</div>
          <div class="score-card-sub">Before submission</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Columns ───────────────────────────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="section-header">Gap Analysis & Action Plan</div>', unsafe_allow_html=True)
        badge_map = {"BLOCKING":"badge-blocking","HIGH":"badge-high","MEDIUM":"badge-medium","LOW":"badge-low"}
        for gap in gaps:
            sev = gap.get("severity", "LOW")
            owner = gap.get("owner", "")
            owner_html = f'<div class="gap-owner">Owner: <span>{owner}</span></div>' if owner and owner != "N/A" else ""
            st.markdown(f"""
            <div class="gap-card">
              <div class="gap-header">
                <span class="badge {badge_map.get(sev,'badge-low')}">{sev}</span>
                <span class="gap-title">{gap['requirement']}</span>
              </div>
              <div class="gap-action">{gap['action']}</div>
              {owner_html}
            </div>""", unsafe_allow_html=True)

        warnings = rec.get("historical_loss_warnings", [])
        if warnings:
            st.markdown('<div class="section-header">Historical Loss Warnings</div>', unsafe_allow_html=True)
            for w in warnings:
                st.markdown(f'<div class="warn-card">⚠️ &nbsp;{w}</div>', unsafe_allow_html=True)

        with st.expander(f"Agent execution trace  ·  {result.get('total_turns','?')} turns"):
            for step in log:
                icon, name, desc = TOOL_META.get(step["tool"], ("🔧", step["tool"], ""))
                st.markdown(f"""
                <div class="agent-step done" style="margin-bottom:5px">
                  <span class="step-icon">{icon}</span>
                  <div class="step-body">
                    <div class="step-name">{name}</div>
                    <div class="step-desc">{desc}</div>
                  </div>
                  <span class="step-check">✓</span>
                </div>""", unsafe_allow_html=True)

    with right:
        themes = rec.get("top_win_themes", [])
        if themes:
            st.markdown('<div class="section-header">Win Themes to Emphasise</div>', unsafe_allow_html=True)
            for theme in themes:
                st.markdown(f'<div class="theme-pill">✦ &nbsp;{theme}</div>', unsafe_allow_html=True)

        # Score breakdown (dynamic based on gaps)
        st.markdown('<div class="section-header" style="margin-top:20px">Score Breakdown</div>', unsafe_allow_html=True)

        has_blocking = blocking > 0
        score_dims = [
            ("Technical fit",       max(10, score + 30) if not has_blocking else score + 15,
             "Core platform capabilities" if score > 40 else "Capability mismatch with RFP scope",
             "green" if score > 50 else "red"),
            ("Past performance",    max(5, score + 20),
             "Relevant prior work available" if score > 50 else "No comparable past projects",
             "green" if score > 50 else "amber"),
            ("Compliance & certs",  85 if score > 50 else 40,
             "SOC2, HIPAA, WCAG 2.1 AA met" if score > 50 else "Certification gaps present",
             "green" if score > 50 else "amber"),
            ("Team readiness",      70 if score > 30 else 30,
             "Named leads identified" if score > 50 else "No qualified team available",
             "green" if score > 40 else "red"),
            ("Strategic fit",       min(90, score + 10) if score > 40 else score,
             "Aligns with company vertical" if score > 40 else "Outside core market",
             "green" if score > 40 else "red"),
        ]
        for dim, pts, note, colour in score_dims:
            pts = max(0, min(100, pts))
            st.markdown(f"""
            <div class="trace-row">
              <div class="trace-header">
                <span class="trace-dim">{dim}</span>
                <span class="trace-pts" style="color:{'#16a34a' if colour=='green' else ('#f59e0b' if colour=='amber' else '#ef4444')}">{pts}</span>
              </div>
              <div class="trace-bar-bg">
                <div class="trace-bar-fill {'' if colour=='green' else colour}" style="width:{pts}%"></div>
              </div>
              <div class="trace-desc">{note}</div>
            </div>""", unsafe_allow_html=True)

        if checklist:
            st.markdown('<div class="section-header" style="margin-top:22px">Submission Checklist</div>', unsafe_allow_html=True)
            rows = "".join([f"""
            <div class="checklist-row">
              <div class="checklist-left">
                <div class="check-box"></div>
                <div>
                  <div class="checklist-item-text">{item['item']}</div>
                  <div class="checklist-owner">{item['owner']}</div>
                </div>
              </div>
              <span class="checklist-due">{item['due']}</span>
            </div>""" for item in checklist])
            st.markdown(f'<div class="checklist-wrap">{rows}</div>', unsafe_allow_html=True)

        reusable = rec.get("reusable_content_available", [])
        if reusable:
            st.markdown('<div class="section-header" style="margin-top:22px">Reusable Proposal Content</div>', unsafe_allow_html=True)
            chips = "".join([f'<span class="content-chip">📄 {b}</span>' for b in reusable])
            st.markdown(f'<div style="line-height:2.4">{chips}</div>', unsafe_allow_html=True)

else:
    if not run_clicked:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">🎯</div>
          <div class="empty-title">Select an RFP and click Run Analysis</div>
          <div class="empty-sub">The agent will execute 6 reasoning steps and return a bid recommendation with gap analysis and action plan.</div>
        </div>
        """, unsafe_allow_html=True)
