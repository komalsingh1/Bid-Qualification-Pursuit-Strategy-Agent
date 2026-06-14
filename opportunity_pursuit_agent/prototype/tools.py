"""
Agent tools — each function maps to a tool the LLM can call.

In production:
  - extract_requirements     → LLM pass over raw RFP text
  - check_capabilities       → vector search over internal KB
  - get_win_loss_history      → CRM API (Salesforce / HubSpot)
  - identify_gaps            → diff between requirements and capabilities
  - get_sme_for_gap          → HRIS / directory lookup
  - get_reusable_content     → SharePoint / proposal management system
  - generate_recommendation  → final LLM synthesis step
"""

import json
from mock_data import (
    COMPANY_CAPABILITIES,
    WIN_LOSS_HISTORY,
    PROPOSAL_LIBRARY,
    SME_DIRECTORY,
)

# ── Tool Definitions (passed to Claude as tools=[...]) ────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "extract_requirements",
        "description": (
            "Parse an RFP document and return structured lists of mandatory requirements, "
            "scored requirements, compliance requirements, and team requirements."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "rfp_text": {"type": "string", "description": "Full RFP document text"}
            },
            "required": ["rfp_text"],
        },
    },
    {
        "name": "check_capabilities",
        "description": (
            "Check the company's internal capability knowledge base against a list of requirements. "
            "Returns matched capabilities and flags any that are missing or partially met."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of requirement strings to check",
                }
            },
            "required": ["requirements"],
        },
    },
    {
        "name": "get_win_loss_history",
        "description": (
            "Retrieve past opportunities similar to the current RFP. "
            "Returns outcomes, win themes, and loss reasons."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords to match against past opportunities (e.g. 'Medicaid', 'FHIR', 'state health')",
                }
            },
            "required": ["keywords"],
        },
    },
    {
        "name": "identify_gaps",
        "description": (
            "Given a list of requirements and the capability check results, "
            "return a structured list of gaps with severity (BLOCKING, HIGH, MEDIUM, LOW) "
            "and suggested remediation paths."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "All RFP requirements",
                },
                "capability_check": {
                    "type": "object",
                    "description": "Output from check_capabilities",
                },
            },
            "required": ["requirements", "capability_check"],
        },
    },
    {
        "name": "get_sme_and_content",
        "description": (
            "For each identified gap, look up the internal SME owner and any reusable "
            "proposal content that can be adapted."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "gap_areas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of gap area labels (e.g. 'FedRAMP', 'SBE', 'Multilingual')",
                }
            },
            "required": ["gap_areas"],
        },
    },
    {
        "name": "generate_recommendation",
        "description": (
            "Synthesize all gathered evidence into a final bid recommendation. "
            "Returns a bid score (0-100), go/no-go decision, top win themes, "
            "gap action plan, and submission checklist."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "rfp_summary": {"type": "string"},
                "gaps": {"type": "array", "items": {"type": "object"}},
                "win_loss_context": {"type": "array", "items": {"type": "object"}},
                "reusable_content": {"type": "array", "items": {"type": "object"}},
                "sme_assignments": {"type": "object"},
            },
            "required": ["rfp_summary", "gaps", "win_loss_context"],
        },
    },
]

# ── Tool Implementations ───────────────────────────────────────────────────────

def extract_requirements(rfp_text: str) -> dict:
    """Structured extraction — in prod this is an LLM call over the raw text."""
    return {
        "agency": "California CDHS",
        "rfp_number": "CDHS-2024-IT-0042",
        "title": "Enterprise Care Coordination Platform",
        "deadline": "2024-09-30",
        "contract_value": "$18M over 3 years",
        "mandatory_requirements": [
            "FedRAMP Moderate authorization",
            "HIPAA BAA capability",
            "99.9% uptime SLA",
            "US-only data residency",
            "Two state Medicaid projects in past 5 years",
        ],
        "scored_requirements": [
            {"req": "Cloud-native architecture", "points": 20},
            {"req": "HL7 FHIR R4 integration", "points": 25},
            {"req": "Real-time analytics and dashboards", "points": 15},
            {"req": "Mobile application for care managers", "points": 10},
            {"req": "AI/ML care gap prediction", "points": 20},
            {"req": "Multilingual support (Spanish, Chinese, Vietnamese)", "points": 10},
        ],
        "compliance_requirements": [
            "SOC 2 Type II",
            "WCAG 2.1 AA",
            "25% California-certified SBE subcontracting",
        ],
        "team_requirements": [
            "PMP-certified Project Manager",
            "Clinical Informatics lead — 5+ years Medicaid",
            "On-site Sacramento presence during go-live (3 months)",
        ],
    }


def check_capabilities(requirements: list) -> dict:
    """Cross-reference requirements against internal KB."""
    caps = COMPANY_CAPABILITIES
    results = {}

    mapping = {
        "FedRAMP Moderate authorization": {
            "status": "PARTIAL",
            "note": "Authorization IN PROGRESS — estimated Q1 2025. Not yet achieved.",
        },
        "HIPAA BAA capability": {"status": "MET", "note": "Standard BAA template on file."},
        "99.9% uptime SLA": {"status": "MET", "note": "99.95% achieved over 24 months."},
        "US-only data residency": {"status": "MET", "note": "Enforced by architecture and contract."},
        "Two state Medicaid projects in past 5 years": {
            "status": "MET",
            "note": "Texas HHSC (2022) and Florida AHCA (2023).",
        },
        "Cloud-native architecture": {"status": "MET", "note": "AWS and Azure production deployments."},
        "HL7 FHIR R4 integration": {"status": "MET", "note": "4 production clients on FHIR R4."},
        "Real-time analytics and dashboards": {"status": "MET", "note": "Looker embedded dashboards."},
        "Mobile application for care managers": {"status": "MET", "note": "React Native framework."},
        "AI/ML care gap prediction": {"status": "MET", "note": "Proprietary model v2.1, F1=0.82."},
        "Multilingual support (Spanish, Chinese, Vietnamese)": {
            "status": "PARTIAL",
            "note": "Spanish and Chinese supported. Vietnamese NOT available.",
        },
        "SOC 2 Type II": {"status": "MET", "note": "Renewed Jan 2024."},
        "WCAG 2.1 AA": {"status": "MET", "note": "Annual audit — all products compliant."},
        "25% California-certified SBE subcontracting": {
            "status": "PARTIAL",
            "note": "Current SBE partners cover ~18%. Gap of 7 percentage points.",
        },
        "PMP-certified Project Manager": {"status": "MET", "note": "8 PMP-certified PMs available."},
        "Clinical Informatics lead — 5+ years Medicaid": {
            "status": "PARTIAL",
            "note": "One lead has 7 yrs (MET), one has 4 yrs (borderline). Assign 7-yr lead.",
        },
        "On-site Sacramento presence during go-live (3 months)": {
            "status": "PARTIAL",
            "note": "No Sacramento office. SF office is 90 miles. Temporary relocation required.",
        },
    }

    for req in requirements:
        results[req] = mapping.get(req, {"status": "UNKNOWN", "note": "Not found in KB."})

    return results


def get_win_loss_history(keywords: list) -> list:
    """Keyword-filtered win/loss records — in prod this is a CRM vector search."""
    keywords_lower = [k.lower() for k in keywords]
    relevant = []
    for record in WIN_LOSS_HISTORY:
        text = json.dumps(record).lower()
        if any(kw in text for kw in keywords_lower):
            relevant.append(record)
    return relevant


def identify_gaps(requirements: list, capability_check: dict) -> list:
    """Classify gaps by severity and suggest remediation."""
    gaps = []
    severity_map = {
        "FedRAMP Moderate authorization": {
            "severity": "BLOCKING",
            "remediation": "Authorization in progress (Q1 2025). If deadline is Sept 2024, submit with in-progress status and letter from FedRAMP PMO. Legal must confirm if this satisfies M-1.",
            "owner_area": "FedRAMP",
        },
        "Multilingual support (Spanish, Chinese, Vietnamese)": {
            "severity": "MEDIUM",
            "remediation": "Vietnamese not supported. Engage localization team for effort/cost estimate. Partner or build by go-live. This is scored (10 pts) — partial credit possible.",
            "owner_area": "Multilingual",
        },
        "25% California-certified SBE subcontracting": {
            "severity": "HIGH",
            "remediation": "Current SBE coverage is ~18%. Identify additional CA-certified SBE partners to reach 25%. Linda Park (Partnerships) to source within 2 weeks.",
            "owner_area": "SBE / Subcontracting",
        },
        "On-site Sacramento presence during go-live (3 months)": {
            "severity": "MEDIUM",
            "remediation": "No permanent office. Plan for 3-month temporary relocation of 2-3 staff. Cost estimate needed. Tom Nguyen to confirm staffing availability.",
            "owner_area": "On-site Staffing",
        },
        "Clinical Informatics lead — 5+ years Medicaid": {
            "severity": "LOW",
            "remediation": "Assign Dr. Raj Patel (7 yrs experience) as named lead. Do not name the 4-yr candidate.",
            "owner_area": "Clinical Staffing",
        },
    }

    for req, check in capability_check.items():
        if check["status"] in ("PARTIAL", "UNKNOWN"):
            gap = {
                "requirement": req,
                "current_status": check["note"],
                **severity_map.get(req, {"severity": "LOW", "remediation": "Review manually.", "owner_area": "General"}),
            }
            gaps.append(gap)

    # Sort by severity
    order = {"BLOCKING": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    gaps.sort(key=lambda g: order.get(g["severity"], 9))
    return gaps


def get_sme_and_content(gap_areas: list) -> dict:
    """Look up SME owners and reusable proposal content for each gap area."""
    result = {"smes": {}, "reusable_content": []}

    for area in gap_areas:
        if area in SME_DIRECTORY:
            result["smes"][area] = SME_DIRECTORY[area]

    for block in PROPOSAL_LIBRARY:
        for area in gap_areas:
            if area.split("/")[0].strip().lower() in block["section"].lower():
                result["reusable_content"].append(block)
                break

    # Always include high-value reusable blocks
    always_include = ["Past Performance", "Security & Compliance", "FHIR"]
    for block in PROPOSAL_LIBRARY:
        if any(k in block["section"] for k in always_include):
            if block not in result["reusable_content"]:
                result["reusable_content"].append(block)

    return result


def generate_recommendation(
    rfp_summary: str,
    gaps: list,
    win_loss_context: list,
    reusable_content: list = None,
    sme_assignments: dict = None,
) -> dict:
    """
    Final synthesis — in prod this is a structured LLM call with all evidence.
    Here we compute deterministically from gap severity to demonstrate the logic.
    """
    blocking = [g for g in gaps if g["severity"] == "BLOCKING"]
    high = [g for g in gaps if g["severity"] == "HIGH"]
    medium = [g for g in gaps if g["severity"] == "MEDIUM"]
    low = [g for g in gaps if g["severity"] == "LOW"]

    # Score deduction logic
    base_score = 85
    score = base_score
    score -= len(blocking) * 25
    score -= len(high) * 10
    score -= len(medium) * 5
    score -= len(low) * 2
    score = max(0, min(100, score))

    if score >= 70:
        decision = "BID"
        confidence = "HIGH" if score >= 80 else "MODERATE"
    elif score >= 40:
        decision = "CONDITIONAL BID"
        confidence = "LOW"
    else:
        decision = "NO BID"
        confidence = "HIGH"

    wins = [r for r in win_loss_context if r.get("outcome") == "WON"]
    win_themes = []
    for w in wins:
        win_themes.extend(w.get("win_themes", []))
    # Deduplicate and take top 3
    seen = set()
    unique_themes = []
    for t in win_themes:
        if t not in seen:
            seen.add(t)
            unique_themes.append(t)
    top_themes = unique_themes[:3] if unique_themes else ["FHIR expertise", "ML care gap model", "proven Medicaid delivery"]

    action_plan = []
    for gap in gaps:
        action_plan.append({
            "gap": gap["requirement"],
            "severity": gap["severity"],
            "action": gap["remediation"],
            "owner": (sme_assignments or {}).get("smes", {}).get(gap.get("owner_area", ""), {}).get("owner", "TBD"),
        })

    submission_checklist = [
        {"item": "FedRAMP in-progress letter from PMO", "owner": "Sarah Chen", "due": "T-21 days"},
        {"item": "Legal sign-off on FedRAMP M-1 interpretation", "owner": "Legal", "due": "T-21 days"},
        {"item": "Additional SBE partner agreements (7% gap)", "owner": "Linda Park", "due": "T-14 days"},
        {"item": "Vietnamese localization cost/timeline estimate", "owner": "Localization Team", "due": "T-14 days"},
        {"item": "Sacramento go-live staffing plan + cost", "owner": "Tom Nguyen", "due": "T-10 days"},
        {"item": "Name Dr. Raj Patel as Clinical Informatics lead", "owner": "Delivery Director", "due": "T-7 days"},
        {"item": "Finalize technical volumes (FHIR, ML, Cloud)", "owner": "Proposal Team", "due": "T-5 days"},
        {"item": "Pricing review and sign-off", "owner": "Finance + Legal", "due": "T-3 days"},
        {"item": "Executive approval to submit", "owner": "VP Sales", "due": "T-1 day"},
    ]

    loss_warnings = [r.get("loss_reason", "") for r in win_loss_context if r.get("outcome") == "LOST"]

    return {
        "bid_score": score,
        "decision": decision,
        "confidence": confidence,
        "rationale": (
            f"Score of {score}/100. "
            f"{len(blocking)} blocking gap(s), {len(high)} high, {len(medium)} medium, {len(low)} low. "
            "FedRAMP is the primary risk — in-progress status may satisfy M-1 with legal confirmation. "
            "Technical fit is strong across all scored requirements. SBE gap is closeable."
        ),
        "top_win_themes": top_themes,
        "historical_loss_warnings": [w for w in loss_warnings if w],
        "gap_action_plan": action_plan,
        "submission_checklist": submission_checklist,
        "reusable_content_available": [b["section"] for b in (reusable_content or [])],
    }


# ── Tool Dispatcher ────────────────────────────────────────────────────────────

def dispatch_tool(tool_name: str, tool_input: dict) -> dict:
    """Route tool calls from the LLM to the correct implementation."""
    if tool_name == "extract_requirements":
        return extract_requirements(**tool_input)
    elif tool_name == "check_capabilities":
        return check_capabilities(**tool_input)
    elif tool_name == "get_win_loss_history":
        return get_win_loss_history(**tool_input)
    elif tool_name == "identify_gaps":
        return identify_gaps(**tool_input)
    elif tool_name == "get_sme_and_content":
        return get_sme_and_content(**tool_input)
    elif tool_name == "generate_recommendation":
        return generate_recommendation(**tool_input)
    else:
        return {"error": f"Unknown tool: {tool_name}"}
