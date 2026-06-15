"""
Expert-annotated ground truth for each RFP.

In production this file is replaced by a human-reviewed annotation store
(a database table where domain experts label each RFP after the bid decision
is known). For the prototype eval we hard-code expert judgments based on
careful reading of each RFP document.

Each entry contains:
  - correct_decision       : what a senior BD expert would decide
  - required_gaps          : every gap a thorough human reviewer would flag
  - required_win_themes    : themes that genuinely differentiate the company
  - required_checklist_items: critical actions that must appear in the checklist
  - expected_score_range   : acceptable bid score band (lo, hi)
  - per_step_expected_conf : rough expected confidence per tool step
  - notes                  : rationale for the expert judgment
"""

GROUND_TRUTH = {

    # ── California CDHS ───────────────────────────────────────────────────────
    "California CDHS (Sample)": {
        "correct_decision": "CONDITIONAL BID",
        "expected_score_range": (45, 65),
        "required_gaps": [
            "FedRAMP Moderate authorization",
            "25% California-certified SBE subcontracting",
            "Multilingual support (Spanish, Chinese, Vietnamese)",
            "On-site Sacramento presence during go-live (3 months)",
            "Clinical Informatics lead — 5+ years Medicaid",
        ],
        "blocking_gaps": [
            "FedRAMP Moderate authorization",
        ],
        "required_win_themes": [
            "FHIR",
            "ML",
            "Medicaid",
        ],
        "required_checklist_items": [
            "FedRAMP",
            "SBE",
            "Sacramento",
            "Clinical",
            "Legal",
        ],
        "per_step_expected_conf": {
            "extract_requirements":    (85, 100),
            "check_capabilities":      (80, 100),
            "get_win_loss_history":    (75, 100),
            "identify_gaps":           (75, 100),
            "get_sme_and_content":     (80, 100),
            "generate_recommendation": (60, 85),
        },
        "notes": (
            "FedRAMP in-progress is the key risk. Legal interpretation of M-1 "
            "is genuinely ambiguous — agent is correct to flag this and recommend "
            "conditional bid rather than auto-proceeding. SBE gap (18% vs 25%) "
            "is closeable in 2 weeks. Score of 50–60 is appropriate."
        ),
    },

    # ── Hemisfair AR Project ──────────────────────────────────────────────────
    "Hemisfair AR Project": {
        "correct_decision": "NO BID",
        "expected_score_range": (0, 35),
        "required_gaps": [
            "Augmented Reality (AR) development capability",
            "Contract value fit ($50K–$100K)",
            "Non-profit / public parks sector experience",
            "Consumer mobile app (iOS + Android) with QR/GPS",
        ],
        "blocking_gaps": [
            "Augmented Reality (AR) development capability",
            "Contract value fit ($50K–$100K)",
        ],
        "required_win_themes": [],   # no genuine win themes — correct answer is no bid
        "required_checklist_items": [],  # no checklist if no bid
        "per_step_expected_conf": {
            "extract_requirements":    (85, 100),
            "check_capabilities":      (40, 70),
            "get_win_loss_history":    (20, 55),
            "identify_gaps":           (85, 100),
            "get_sme_and_content":     (20, 50),
            "generate_recommendation": (85, 100),
        },
        "notes": (
            "Clear no-bid. Company has no AR capability and $50K–$100K is below "
            "minimum viable contract threshold. Agent should reach this conclusion "
            "with high confidence. Low scores on check_capabilities and win/loss "
            "retrieval are expected and correct — the agent should still surface them."
        ),
    },

    # ── DLC Website Redesign ──────────────────────────────────────────────────
    "DLC Website Redesign": {
        "correct_decision": "NO BID",
        "expected_score_range": (20, 45),
        "required_gaps": [
            "Website design portfolio (2+ comparable redesigns)",
            "CMS platform expertise (WordPress, Drupal, or Sitecore)",
            "UX / information architecture (IA) practice",
            "Content strategy and migration",
        ],
        "blocking_gaps": [
            "Website design portfolio (2+ comparable redesigns)",
        ],
        "required_win_themes": [
            "WCAG",
            "accessibility",
        ],
        "required_checklist_items": [],
        "per_step_expected_conf": {
            "extract_requirements":    (85, 100),
            "check_capabilities":      (50, 75),
            "get_win_loss_history":    (35, 65),
            "identify_gaps":           (80, 100),
            "get_sme_and_content":     (35, 60),
            "generate_recommendation": (80, 100),
        },
        "notes": (
            "No-bid — wrong category. Company is an enterprise platform builder, "
            "not a web agency. WCAG compliance is a genuine strength but insufficient "
            "without a web design portfolio. Agent should identify the portfolio "
            "gap as blocking."
        ),
    },

    # ── MCCVB Creative Agency ─────────────────────────────────────────────────
    "MCCVB Creative Agency": {
        "correct_decision": "NO BID",
        "expected_score_range": (0, 20),
        "required_gaps": [
            "Creative & brand strategy capability",
            "Media buying and planning (TV, CTV, radio, digital)",
            "Tourism / destination marketing experience",
            "Integrated marketing program delivery (Paid/Earned/Owned)",
        ],
        "blocking_gaps": [
            "Creative & brand strategy capability",
            "Media buying and planning (TV, CTV, radio, digital)",
            "Tourism / destination marketing experience",
        ],
        "required_win_themes": [],
        "required_checklist_items": [],
        "per_step_expected_conf": {
            "extract_requirements":    (85, 100),
            "check_capabilities":      (10, 35),
            "get_win_loss_history":    (10, 30),
            "identify_gaps":           (85, 100),
            "get_sme_and_content":     (10, 25),
            "generate_recommendation": (90, 100),
        },
        "notes": (
            "Complete mismatch. This is a creative and media buying RFP — "
            "an entirely different industry from enterprise software. "
            "The agent should score this near 0 and reach no-bid with very high confidence. "
            "check_capabilities and win/loss should return very low confidence "
            "because nothing matches."
        ),
    },
}
