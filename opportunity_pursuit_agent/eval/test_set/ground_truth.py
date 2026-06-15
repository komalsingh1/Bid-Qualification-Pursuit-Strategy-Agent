"""
Expert-annotated ground truth for the 8 test-set RFPs.

Each entry was annotated independently based on:
  1. Careful reading of the RFP text (rfp_texts.py)
  2. The company's capability profile (mock_data.py)
  3. Win/loss history patterns (mock_data.py)

Annotations represent what a senior BD expert with full knowledge
of the company profile would decide — NOT what the agent decides.
These are written before running the agent so there is no leakage.

Company profile summary (for annotation reference):
  ✓ SOC 2 Type II, HIPAA BAA, WCAG 2.1 AA, US data residency
  ✓ FHIR R4 (4 production clients), ML care gap model (F1=0.82)
  ✓ AWS + Azure cloud-native, React Native mobile, Looker dashboards
  ✓ Texas HHSC (2022) + Florida AHCA (2023) state Medicaid past perf
  ✗ FedRAMP: IN PROGRESS (not yet authorized — Moderate target)
  ✗ No FedRAMP HIGH, no FISMA, no clearances, no CMMI rating
  ✗ SBE subcontracting: ~18% typical (some RFPs require 20–25%)
  ✗ No Massachusetts or Colorado office
  ✗ No behavioral health / SUD specialization
  ✗ No creative/marketing/brand capabilities
"""

TEST_GROUND_TRUTH = {

    # ── TC-01: NY Medicaid Analytics ──────────────────────────────────────────
    "TC-01: NY Medicaid Analytics": {
        "correct_decision": "BID",
        "expected_score_range": (72, 88),
        "required_gaps": [
            # No mandatory gaps — all M-requirements met
            # Minor scored gap: no specific RBAC audit logging product mentioned
        ],
        "blocking_gaps": [],
        "required_win_themes": [
            "FHIR",
            "ML",
            "Medicaid",
            "SOC 2",
        ],
        "required_checklist_items": [
            "SOC 2",
            "FHIR",
            "past performance",
        ],
        "per_step_expected_conf": {
            "extract_requirements":    (88, 100),
            "check_capabilities":      (88, 100),
            "get_win_loss_history":    (82, 100),
            "identify_gaps":           (85, 100),
            "get_sme_and_content":     (82, 100),
            "generate_recommendation": (80, 100),
        },
        "notes": (
            "Strong match across all mandatory requirements. FHIR R4, ML care gap, "
            "cloud-native, SOC2, HIPAA, WCAG all met. Past performance in NY DOH "
            "(win in 2023) and two state Medicaid projects meet M-5. "
            "No blocking gaps. Agent should recommend BID with high confidence."
        ),
    },

    # ── TC-02: CMS Federal Platform ──────────────────────────────────────────
    "TC-02: CMS Federal Health Platform": {
        "correct_decision": "NO BID",
        "expected_score_range": (0, 25),
        "required_gaps": [
            "FedRAMP HIGH authorization",
            "FISMA High ATO",
            "Personnel security clearances (Secret)",
            "Federal civilian agency contract at $20M+",
            "FedRAMP GovCloud infrastructure",
        ],
        "blocking_gaps": [
            "FedRAMP HIGH authorization",
            "FISMA High ATO",
            "Personnel security clearances (Secret)",
        ],
        "required_win_themes": [],
        "required_checklist_items": [],
        "per_step_expected_conf": {
            "extract_requirements":    (88, 100),
            "check_capabilities":      (15, 40),
            "get_win_loss_history":    (20, 45),
            "identify_gaps":           (90, 100),
            "get_sme_and_content":     (10, 35),
            "generate_recommendation": (92, 100),
        },
        "notes": (
            "Hard no-bid. M-1 requires FedRAMP HIGH (we have FedRAMP Moderate in progress). "
            "M-2 requires FISMA High ATO. M-3 requires Secret clearances. "
            "Three blocking disqualifiers. History shows we lost CMS CMMI 2023 for FedRAMP. "
            "Agent should reach no-bid with high confidence and very fast."
        ),
    },

    # ── TC-03: Colorado Care Management ──────────────────────────────────────
    "TC-03: Colorado Care Management": {
        "correct_decision": "CONDITIONAL BID",
        "expected_score_range": (52, 68),
        "required_gaps": [
            "20% Colorado-certified SBE subcontracting",
            "Multilingual support (Spanish required)",
            "Colorado on-site presence",
            "FedRAMP Moderate in-progress confirmation",
        ],
        "blocking_gaps": [],
        "required_win_themes": [
            "FHIR",
            "ML",
            "care management",
        ],
        "required_checklist_items": [
            "SBE",
            "Spanish",
            "FedRAMP",
            "on-site",
        ],
        "per_step_expected_conf": {
            "extract_requirements":    (88, 100),
            "check_capabilities":      (75, 92),
            "get_win_loss_history":    (72, 90),
            "identify_gaps":           (82, 100),
            "get_sme_and_content":     (70, 90),
            "generate_recommendation": (68, 88),
        },
        "notes": (
            "Good technical fit — FHIR, ML, cloud, SOC2 all met. FedRAMP in-progress "
            "accepted by M-5 wording (letter from PMO needed). SBE at 18% vs 20% "
            "required — smaller gap than California (7pp vs 7pp). Spanish is met. "
            "Colorado on-site is manageable via travel. Conditional bid is right call."
        ),
    },

    # ── TC-04: Texas Population Health ──────────────────────────────────────
    "TC-04: Texas Population Health": {
        "correct_decision": "BID",
        "expected_score_range": (78, 92),
        "required_gaps": [],
        "blocking_gaps": [],
        "required_win_themes": [
            "FHIR",
            "ML",
            "Texas",
            "past performance",
        ],
        "required_checklist_items": [
            "SOC 2",
            "FHIR",
            "Texas HHSC",
            "AWS",
        ],
        "per_step_expected_conf": {
            "extract_requirements":    (90, 100),
            "check_capabilities":      (92, 100),
            "get_win_loss_history":    (92, 100),
            "identify_gaps":           (90, 100),
            "get_sme_and_content":     (88, 100),
            "generate_recommendation": (88, 100),
        },
        "notes": (
            "Near-perfect match. Texas HHSC is existing past performance (2022 win). "
            "M-5 satisfied by Texas HHSC + Florida AHCA. All scored requirements met "
            "(FHIR, ML, AWS, dashboards, mobile, WCAG). No gaps. "
            "Evaluation note: prior Texas HHSC work is weighted heavily — this is a "
            "strong incumbent advantage. Agent should recommend BID with high confidence."
        ),
    },

    # ── TC-05: Brand & Digital Marketing ─────────────────────────────────────
    "TC-05: Brand & Digital Marketing Agency": {
        "correct_decision": "NO BID",
        "expected_score_range": (0, 15),
        "required_gaps": [
            "Full-service marketing agency experience (5+ years)",
            "Media buying capability ($500K+ budget management)",
            "Dedicated creative team (art director, copywriter)",
            "Tourism / destination marketing experience",
        ],
        "blocking_gaps": [
            "Full-service marketing agency experience (5+ years)",
            "Media buying capability ($500K+ budget management)",
            "Dedicated creative team (art director, copywriter)",
        ],
        "required_win_themes": [],
        "required_checklist_items": [],
        "per_step_expected_conf": {
            "extract_requirements":    (88, 100),
            "check_capabilities":      (5, 25),
            "get_win_loss_history":    (5, 20),
            "identify_gaps":           (90, 100),
            "get_sme_and_content":     (5, 20),
            "generate_recommendation": (92, 100),
        },
        "notes": (
            "Complete category mismatch — identical pattern to MCCVB RFP in the demo set. "
            "We are a technology company, not a marketing agency. "
            "No creative team, no media buying desk, no tourism experience. "
            "Agent should reach no-bid quickly with near-zero bid score."
        ),
    },

    # ── TC-06: Massachusetts Behavioral Health ────────────────────────────────
    "TC-06: Massachusetts Behavioral Health": {
        "correct_decision": "CONDITIONAL BID",
        "expected_score_range": (38, 58),
        "required_gaps": [
            "Massachusetts office requirement (M-5)",
            "Behavioral health / SUD platform specialization (M-6)",
            "42 CFR Part 2 substance use disorder data compliance",
            "Behavioral health clinical lead (licensed LCSW)",
            "SUD-specific care pathway templates",
        ],
        "blocking_gaps": [
            "Behavioral health / SUD platform specialization (M-6)",
        ],
        "required_win_themes": [
            "FHIR",
            "ML",
            "care coordination",
        ],
        "required_checklist_items": [
            "SUD",
            "Massachusetts",
            "LCSW",
            "42 CFR",
        ],
        "per_step_expected_conf": {
            "extract_requirements":    (88, 100),
            "check_capabilities":      (52, 72),
            "get_win_loss_history":    (45, 68),
            "identify_gaps":           (82, 100),
            "get_sme_and_content":     (40, 65),
            "generate_recommendation": (60, 82),
        },
        "notes": (
            "Tricky case. Strong technical fit (FHIR, ML, cloud, SOC2) but M-6 requires "
            "behavioral health / SUD specialization — our platform is general care management. "
            "We would need to argue that our platform is configurable to BH workflows. "
            "Massachusetts office commitment is achievable (travel or temporary). "
            "42 CFR Part 2 compliance is a real gap — requires data segmentation we haven't built. "
            "Conditional bid: legal must assess whether M-6 disqualifies us, and product "
            "must confirm 42 CFR Part 2 scope."
        ),
    },

    # ── TC-07: Chicago Community Health ──────────────────────────────────────
    "TC-07: Chicago Community Health Platform": {
        "correct_decision": "BID",
        "expected_score_range": (65, 80),
        "required_gaps": [
            "25% MBE/WBE subcontracting (current ~18%)",
            "Multilingual support (Polish not currently available)",
        ],
        "blocking_gaps": [],
        "required_win_themes": [
            "FHIR",
            "multilingual",
            "cloud",
            "ML",
        ],
        "required_checklist_items": [
            "MBE",
            "Polish",
            "SOC 2",
        ],
        "per_step_expected_conf": {
            "extract_requirements":    (88, 100),
            "check_capabilities":      (78, 95),
            "get_win_loss_history":    (70, 88),
            "identify_gaps":           (82, 100),
            "get_sme_and_content":     (72, 90),
            "generate_recommendation": (75, 92),
        },
        "notes": (
            "Good fit at a smaller contract size ($4.2M). All mandatory requirements met. "
            "MBE/WBE at 25% is same gap as SBE (we're at ~18%) — closeable. "
            "Polish localization is a scored gap (20pts for multilingual) but not mandatory. "
            "English + Spanish + Mandarin are met — Polish is the only missing language. "
            "Evaluate whether partial multilingual credit is available. BID recommended."
        ),
    },

    # ── TC-08: VA Veterans Platform ──────────────────────────────────────────
    "TC-08: VA Veterans Health Platform": {
        "correct_decision": "NO BID",
        "expected_score_range": (0, 20),
        "required_gaps": [
            "FedRAMP HIGH authorization",
            "VA Authority to Operate (ATO)",
            "Personnel security clearances",
            "Prior VA or DoD contract performance",
            "CMMI Level 3 software maturity rating",
            "VA EARC-approved cloud infrastructure",
        ],
        "blocking_gaps": [
            "FedRAMP HIGH authorization",
            "VA Authority to Operate (ATO)",
            "Personnel security clearances",
            "CMMI Level 3 software maturity rating",
        ],
        "required_win_themes": [],
        "required_checklist_items": [],
        "per_step_expected_conf": {
            "extract_requirements":    (88, 100),
            "check_capabilities":      (10, 30),
            "get_win_loss_history":    (15, 35),
            "identify_gaps":           (90, 100),
            "get_sme_and_content":     (8, 25),
            "generate_recommendation": (92, 100),
        },
        "notes": (
            "Hard no-bid — similar to CMS federal platform (TC-02) but with additional "
            "VA-specific barriers. FedRAMP HIGH, VA ATO, Secret clearances, and CMMI Level 3 "
            "are all blocking. VA work requires years of relationship-building and federal "
            "certifications we don't have. No path to compliance before the deadline. "
            "History: lost HHS Federal Health Data Platform 2022 for FedRAMP. Same pattern."
        ),
    },
}
