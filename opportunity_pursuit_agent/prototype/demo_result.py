"""
Pre-computed demo result — used when ANTHROPIC_API_KEY is not set.
Identical structure to what the live agent returns.
Lets the prototype run without credentials during a presentation.
"""

DEMO_RESULT = {
    "tool_call_log": [
        {"tool": "extract_requirements",    "input": {"rfp_text": "..."}, "output_keys": ["agency","mandatory_requirements","scored_requirements","team_requirements"]},
        {"tool": "check_capabilities",       "input": {"requirements": ["..."]}, "output_keys": ["FedRAMP Moderate authorization","HL7 FHIR R4 integration","..."]},
        {"tool": "get_win_loss_history",     "input": {"keywords": ["Medicaid","FHIR","state health"]}, "output_keys": "list"},
        {"tool": "identify_gaps",            "input": {"requirements": ["..."], "capability_check": {}}, "output_keys": "list"},
        {"tool": "get_sme_and_content",      "input": {"gap_areas": ["FedRAMP","SBE / Subcontracting","Multilingual","On-site Staffing","Clinical Staffing"]}, "output_keys": ["smes","reusable_content"]},
        {"tool": "generate_recommendation",  "input": {"rfp_summary": "..."}, "output_keys": ["bid_score","decision","gap_action_plan","submission_checklist"]},
    ],
    "executive_summary": (
        "The California CDHS Care Coordination Platform RFP presents a strong technical fit — "
        "FHIR R4, cloud-native architecture, ML care gap prediction, and mobile all align with our capabilities. "
        "The primary risk is FedRAMP Moderate authorization, which is in-progress but not yet achieved; "
        "legal must confirm whether an in-progress status satisfies M-1 before we commit. "
        "If FedRAMP is resolved, this is a winnable bid at a 55/100 score. "
        "Key actions: close the SBE gap from 18% to 25%, assess Vietnamese localization effort, and plan Sacramento go-live staffing."
    ),
    "total_turns": 7,
    "recommendation": {
        "bid_score": 55,
        "decision": "CONDITIONAL BID",
        "confidence": "LOW",
        "rationale": (
            "Score of 55/100. 1 blocking gap (FedRAMP), 1 high (SBE subcontracting), "
            "2 medium (multilingual, on-site staffing), 1 low (clinical lead assignment). "
            "FedRAMP is the primary risk — in-progress status may satisfy M-1 with legal confirmation. "
            "Technical fit is strong across all scored requirements. SBE gap is closeable."
        ),
        "top_win_themes": [
            "FHIR expertise",
            "ML care gap model",
            "proven Medicaid delivery",
        ],
        "historical_loss_warnings": [
            "Lacked FedRAMP authorization — eliminated at mandatory review. (CMS 2023)",
            "FedRAMP High required. Not in scope for us. (HHS 2022)",
        ],
        "gap_action_plan": [
            {
                "requirement": "FedRAMP Moderate authorization",
                "severity": "BLOCKING",
                "current_status": "Authorization IN PROGRESS — estimated Q1 2025. Not yet achieved.",
                "action": "Authorization in progress (Q1 2025). If deadline is Sept 2024, submit with in-progress status and letter from FedRAMP PMO. Legal must confirm if this satisfies M-1.",
                "owner": "Sarah Chen, VP Security",
                "owner_area": "FedRAMP",
            },
            {
                "requirement": "25% California-certified SBE subcontracting",
                "severity": "HIGH",
                "current_status": "Current SBE partners cover ~18%. Gap of 7 percentage points.",
                "action": "Current SBE coverage is ~18%. Identify additional CA-certified SBE partners to reach 25%. Linda Park (Partnerships) to source within 2 weeks.",
                "owner": "Linda Park, Partnerships",
                "owner_area": "SBE / Subcontracting",
            },
            {
                "requirement": "Multilingual support (Spanish, Chinese, Vietnamese)",
                "severity": "MEDIUM",
                "current_status": "Spanish and Chinese supported. Vietnamese NOT available.",
                "action": "Vietnamese not supported. Engage localization team for effort/cost estimate. Partner or build by go-live. This is scored (10 pts) — partial credit possible.",
                "owner": "Product Localization Team",
                "owner_area": "Multilingual",
            },
            {
                "requirement": "On-site Sacramento presence during go-live (3 months)",
                "severity": "MEDIUM",
                "current_status": "No Sacramento office. SF office is 90 miles. Temporary relocation required.",
                "action": "No permanent office. Plan for 3-month temporary relocation of 2-3 staff. Cost estimate needed. Tom Nguyen to confirm staffing availability.",
                "owner": "Tom Nguyen, Delivery Director",
                "owner_area": "On-site Staffing",
            },
            {
                "requirement": "Clinical Informatics lead — 5+ years Medicaid",
                "severity": "LOW",
                "current_status": "One lead has 7 yrs (MET), one has 4 yrs (borderline). Assign 7-yr lead.",
                "action": "Assign Dr. Raj Patel (7 yrs experience) as named lead. Do not name the 4-yr candidate.",
                "owner": "HR / Talent Acquisition",
                "owner_area": "Clinical Staffing",
            },
        ],
        "submission_checklist": [
            {"item": "FedRAMP in-progress letter from PMO", "owner": "Sarah Chen", "due": "T-21 days"},
            {"item": "Legal sign-off on FedRAMP M-1 interpretation", "owner": "Legal", "due": "T-21 days"},
            {"item": "Additional SBE partner agreements (7% gap)", "owner": "Linda Park", "due": "T-14 days"},
            {"item": "Vietnamese localization cost/timeline estimate", "owner": "Localization Team", "due": "T-14 days"},
            {"item": "Sacramento go-live staffing plan + cost", "owner": "Tom Nguyen", "due": "T-10 days"},
            {"item": "Name Dr. Raj Patel as Clinical Informatics lead", "owner": "Delivery Director", "due": "T-7 days"},
            {"item": "Finalize technical volumes (FHIR, ML, Cloud)", "owner": "Proposal Team", "due": "T-5 days"},
            {"item": "Pricing review and sign-off", "owner": "Finance + Legal", "due": "T-3 days"},
            {"item": "Executive approval to submit", "owner": "VP Sales", "due": "T-1 day"},
        ],
        "reusable_content_available": [
            "SBE Participation Plan",
            "Past Performance — Texas HHSC",
            "Security & Compliance Narrative (SOC2/HIPAA)",
            "FHIR Integration Approach",
        ],
    },
}
