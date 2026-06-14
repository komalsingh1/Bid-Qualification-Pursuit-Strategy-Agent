"""
Mock data layer — stands in for real integrations:
  - Internal capability knowledge base
  - Past win/loss CRM records
  - Proposal content library
  - SME directory

In production each of these would be a retrieval call
(vector search, CRM API, SharePoint, HRIS).
"""

# ── Sample RFP ────────────────────────────────────────────────────────────────

SAMPLE_RFP = """
REQUEST FOR PROPOSAL
Issuing Agency: State of California — Department of Health Services
RFP Number: CDHS-2024-IT-0042
Title: Enterprise Care Coordination Platform
Submission Deadline: 2024-09-30
Estimated Contract Value: $18M over 3 years

1. SCOPE OF WORK
The Department seeks a vendor to design, build, and operate a cloud-based
Care Coordination Platform serving 2.3 million Medicaid beneficiaries.
The platform must integrate with the existing MMIS (Medi-Cal) system,
provide real-time care gap alerts, and support care manager workflows.

2. MANDATORY REQUIREMENTS
M-1: Vendor must hold a current FedRAMP Moderate authorization.
M-2: Vendor must demonstrate HIPAA Business Associate Agreement capability.
M-3: System must achieve 99.9% uptime SLA.
M-4: All data must remain within US borders.
M-5: Vendor must have delivered at least two state Medicaid projects
     in the past five years.

3. SCORED REQUIREMENTS
S-1: Cloud-native architecture (AWS, Azure, or GCP) — 20 pts
S-2: HL7 FHIR R4 integration capability — 25 pts
S-3: Real-time analytics and dashboards — 15 pts
S-4: Mobile application for care managers — 10 pts
S-5: AI/ML-powered care gap prediction — 20 pts
S-6: Multilingual support (Spanish, Chinese, Vietnamese) — 10 pts

4. COMPLIANCE REQUIREMENTS
- SOC 2 Type II certification required
- State accessibility standard WCAG 2.1 AA compliance
- Mandatory subcontracting: 25% to California-certified SBE firms

5. TEAM REQUIREMENTS
- Dedicated Project Manager with PMP certification
- Clinical Informatics lead with 5+ years Medicaid experience
- On-site presence in Sacramento required during go-live (3 months)

6. EVALUATION CRITERIA
Technical approach: 40%
Past performance: 30%
Price: 20%
Small business participation: 10%
"""

# ── Company Capability Knowledge Base ─────────────────────────────────────────

COMPANY_CAPABILITIES = {
    "certifications": [
        "SOC 2 Type II (renewed 2024-01)",
        "HIPAA BAA capability — standard template on file",
        "ISO 27001",
        "WCAG 2.1 AA — all products audited annually",
        # NOTE: FedRAMP Moderate authorization is IN PROGRESS (est. Q1 2025)
    ],
    "technical": [
        "Cloud-native AWS and Azure deployments",
        "HL7 FHIR R4 integration — production deployments at 4 clients",
        "Real-time analytics via embedded Looker dashboards",
        "React Native mobile app framework",
        "Proprietary ML care gap prediction model (v2.1, F1=0.82)",
        "US-only data residency — enforced by contract and architecture",
        "99.95% uptime achieved across last 24 months",
    ],
    "languages_supported": ["English", "Spanish", "Chinese (Simplified)"],
    # Vietnamese is NOT currently supported
    "past_state_medicaid_projects": [
        {
            "state": "Texas",
            "agency": "HHSC",
            "year_delivered": 2022,
            "scope": "Care management platform, 1.8M beneficiaries",
            "outcome": "On time, under budget, 98.7% uptime yr1",
        },
        {
            "state": "Florida",
            "agency": "AHCA",
            "year_delivered": 2023,
            "scope": "FHIR integration layer for Medicaid claims",
            "outcome": "Delivered 6 weeks early",
        },
    ],
    "team": {
        "pmp_certified_pms": 8,
        "clinical_informatics_leads": 2,
        "clinical_informatics_medicaid_experience_years": [7, 4],
        # Lead with 4 years is borderline on the 5yr requirement
        "sacramento_office": False,
        "nearest_office": "San Francisco (90 miles)",
    },
    "subcontracting": {
        "sbe_partners_california": ["DataBridge SBE LLC", "HealthLink Consulting (SBE)"],
        "typical_sbe_percentage": 18,
        # Current SBE % is 18% — requirement is 25%
    },
}

# ── Win / Loss History (CRM records) ─────────────────────────────────────────

WIN_LOSS_HISTORY = [
    {
        "opportunity": "NY DOHMH — Care Coordination RFP 2023",
        "outcome": "WON",
        "contract_value": "$14M",
        "win_themes": ["FHIR expertise", "ML care gap model", "strong past performance"],
        "notes": "FedRAMP was not required. FHIR demo was decisive.",
    },
    {
        "opportunity": "CMS Innovation Center — CMMI Platform 2023",
        "outcome": "LOST",
        "contract_value": "$22M",
        "loss_reason": "Lacked FedRAMP authorization — eliminated at mandatory review.",
        "notes": "FedRAMP gap is recurring loss driver in federal/state work.",
    },
    {
        "opportunity": "Colorado HCPF — Medicaid Analytics 2022",
        "outcome": "WON",
        "contract_value": "$9M",
        "win_themes": ["Real-time dashboards", "multilingual UI", "SBE partnership"],
        "notes": "SBE at 22% — client waived to 20% minimum. Watch CA 25% req.",
    },
    {
        "opportunity": "Michigan DHHS — Care Management 2021",
        "outcome": "WON",
        "contract_value": "$11M",
        "win_themes": ["Mobile app", "on-site implementation team", "PMP-led delivery"],
        "notes": "On-site presence was a differentiator. No Sacramento office needed.",
    },
    {
        "opportunity": "HHS — Federal Health Data Platform 2022",
        "outcome": "LOST",
        "loss_reason": "FedRAMP High required. Not in scope for us.",
        "notes": "Another FedRAMP loss. Authorization is strategic priority.",
    },
]

# ── Proposal Content Library (reusable blocks) ────────────────────────────────

PROPOSAL_LIBRARY = [
    {"section": "FHIR Integration Approach", "last_used": "NY DOHMH 2023", "reuse_score": 0.92},
    {"section": "ML Care Gap Prediction Methodology", "last_used": "Colorado 2022", "reuse_score": 0.88},
    {"section": "Cloud Architecture (AWS)", "last_used": "Florida AHCA 2023", "reuse_score": 0.85},
    {"section": "Security & Compliance Narrative (SOC2/HIPAA)", "last_used": "Michigan 2021", "reuse_score": 0.90},
    {"section": "Mobile App UX — Care Manager Workflows", "last_used": "Michigan 2021", "reuse_score": 0.78},
    {"section": "Past Performance — Texas HHSC", "last_used": "NY DOHMH 2023", "reuse_score": 0.95},
    {"section": "SBE Participation Plan", "last_used": "Colorado 2022", "reuse_score": 0.70},
]

# ── SME Directory ─────────────────────────────────────────────────────────────

SME_DIRECTORY = {
    "FedRAMP": {"owner": "Sarah Chen, VP Security", "email": "s.chen@company.com"},
    "FHIR": {"owner": "Dr. Raj Patel, Clinical Informatics", "email": "r.patel@company.com"},
    "ML / AI": {"owner": "Mia Torres, Head of Data Science", "email": "m.torres@company.com"},
    "Mobile": {"owner": "James Wu, Mobile Engineering Lead", "email": "j.wu@company.com"},
    "SBE / Subcontracting": {"owner": "Linda Park, Partnerships", "email": "l.park@company.com"},
    "On-site Staffing": {"owner": "Tom Nguyen, Delivery Director", "email": "t.nguyen@company.com"},
    "Clinical Staffing": {"owner": "HR / Talent Acquisition", "email": "talent@company.com"},
    "Multilingual": {"owner": "Product Localization Team", "email": "localization@company.com"},
}
