"""
RFP registry — maps each uploaded PDF to its metadata and pre-computed demo result.

Pre-computed results are used in demo mode (no API key).
They are honest gap analyses of our company profile against each real RFP.

Company profile (from mock_data.py):
  Enterprise cloud platform company. Healthcare/government vertical.
  Capabilities: FHIR, ML, cloud-native AWS/Azure, mobile (React Native),
  real-time analytics, SOC2, HIPAA, WCAG 2.1 AA, US data residency.
  NOT: a creative agency, AR developer, web design shop, or media buyer.
"""

import os

BASE = os.path.join(os.path.dirname(__file__), "..")

RFP_REGISTRY = {
    "Hemisfair AR Project": {
        "file": os.path.join(BASE, "05.25.2021-RFP-Hemisfair-Augmented-Reality-Project.pdf"),
        "agency": "Hemisfair Park Area Redevelopment Corporation",
        "rfp_number": "HPARC-2021-AR",
        "title": "Augmented Reality Tree Donor Recognition App",
        "deadline": "June 2021",
        "value": "$50K – $100K",
        "type": "Mobile / AR Development",
        "demo_result": {
            "tool_call_log": [
                {"tool": "extract_requirements",    "input": {}, "output_keys": ["mandatory_requirements","scored_requirements","team_requirements"]},
                {"tool": "check_capabilities",       "input": {}, "output_keys": ["AR development","iOS & Android","QR/GPS","nonprofit experience"]},
                {"tool": "get_win_loss_history",     "input": {}, "output_keys": "list"},
                {"tool": "identify_gaps",            "input": {}, "output_keys": "list"},
                {"tool": "get_sme_and_content",      "input": {}, "output_keys": ["smes","reusable_content"]},
                {"tool": "generate_recommendation",  "input": {}, "output_keys": ["bid_score","decision"]},
            ],
            "executive_summary": (
                "The Hemisfair AR project is a strong technical concept but a poor strategic fit. "
                "Our company has no AR development capability, no consumer mobile app portfolio, "
                "and no non-profit sector experience. At $50K–$100K the contract value is 200x below "
                "our typical engagement size — overhead alone would eliminate any margin. "
                "Recommendation: No Bid. This opportunity should be declined without further investment."
            ),
            "total_turns": 7,
            "recommendation": {
                "bid_score": 22,
                "decision": "NO BID",
                "confidence": "HIGH",
                "rationale": (
                    "Score of 22/100. 2 blocking gaps, 3 high gaps. "
                    "No AR development capability exists in-house. Contract value ($50K–$100K) is "
                    "below our minimum viable engagement threshold. No prior non-profit or consumer "
                    "app work to reference. Pursuing this would distract from core health/government pipeline."
                ),
                "top_win_themes": [],
                "historical_loss_warnings": [
                    "No comparable AR or consumer mobile projects in win/loss history — zero past performance to cite.",
                ],
                "gap_action_plan": [
                    {
                        "requirement": "Augmented Reality (AR) development capability",
                        "severity": "BLOCKING",
                        "current_status": "No AR development experience. Not a current capability.",
                        "action": "Would require hiring or acquiring an AR specialist team. 6–12 month build time minimum. Not viable for this timeline or contract value.",
                        "owner": "CTO / Engineering",
                        "owner_area": "Engineering",
                    },
                    {
                        "requirement": "Contract value fit ($50K–$100K)",
                        "severity": "BLOCKING",
                        "current_status": "Our minimum viable contract threshold is ~$500K. This is 5–10x below floor.",
                        "action": "No path to profitability at this contract size given our cost structure. Pass.",
                        "owner": "VP Sales / Finance",
                        "owner_area": "Finance",
                    },
                    {
                        "requirement": "Non-profit / public parks sector experience",
                        "severity": "HIGH",
                        "current_status": "All past performance is in state health agencies and federal healthcare. No parks, arts, or non-profit clients.",
                        "action": "Cannot credibly demonstrate relevant past performance. Evaluators will see this gap immediately.",
                        "owner": "Business Development",
                        "owner_area": "BD",
                    },
                    {
                        "requirement": "Consumer mobile app (iOS + Android) with QR/GPS",
                        "severity": "HIGH",
                        "current_status": "Mobile capability exists (React Native) but only for enterprise care manager workflows — not consumer-facing public apps.",
                        "action": "Consumer app UX, App Store submission, public-facing design — all require different skills than our enterprise mobile team.",
                        "owner": "Mobile Engineering",
                        "owner_area": "Mobile",
                    },
                    {
                        "requirement": "Familiarity with Hemisfair branding guidelines",
                        "severity": "MEDIUM",
                        "current_status": "No brand design capability in-house.",
                        "action": "Would require creative/design subcontract — adds cost to an already margin-thin project.",
                        "owner": "Design / Creative",
                        "owner_area": "Creative",
                    },
                ],
                "submission_checklist": [],
                "reusable_content_available": [],
            },
        },
    },

    "DLC Website Redesign": {
        "file": os.path.join(BASE, "DLC_Website-RFP_5-6-20_FINAL.pdf"),
        "agency": "DesignLights Consortium (DLC)",
        "rfp_number": "DLC-2020-WEB",
        "title": "Website Design, Development & CMS Solution",
        "deadline": "May 2020",
        "value": "Not specified",
        "type": "Web Design & CMS",
        "demo_result": {
            "tool_call_log": [
                {"tool": "extract_requirements",    "input": {}, "output_keys": ["mandatory_requirements","scored_requirements","team_requirements"]},
                {"tool": "check_capabilities",       "input": {}, "output_keys": ["Web design","CMS","UX/IA","WCAG 2.1","ADA"]},
                {"tool": "get_win_loss_history",     "input": {}, "output_keys": "list"},
                {"tool": "identify_gaps",            "input": {}, "output_keys": "list"},
                {"tool": "get_sme_and_content",      "input": {}, "output_keys": ["smes","reusable_content"]},
                {"tool": "generate_recommendation",  "input": {}, "output_keys": ["bid_score","decision"]},
            ],
            "executive_summary": (
                "DLC is seeking a web design and CMS agency — not an enterprise platform company. "
                "We have WCAG 2.1 AA compliance experience and strong cloud/security credentials, "
                "but no web design portfolio, no CMS product or implementation experience, and no "
                "UX/information architecture practice. The evaluation will be heavily weighted on "
                "prior website projects we cannot demonstrate. Recommendation: No Bid."
            ),
            "total_turns": 7,
            "recommendation": {
                "bid_score": 31,
                "decision": "NO BID",
                "confidence": "HIGH",
                "rationale": (
                    "Score of 31/100. 1 blocking gap, 2 high gaps, 2 medium. "
                    "Core issue: DLC is buying web design and CMS services — a category we do not operate in. "
                    "We have no prior website projects, no design portfolio, no CMS platform, "
                    "and no content strategy practice. WCAG 2.1 compliance is a plus but insufficient alone."
                ),
                "top_win_themes": [
                    "WCAG 2.1 AA accessibility compliance",
                    "Cloud-native hosting and security posture",
                    "Structured content architecture experience",
                ],
                "historical_loss_warnings": [
                    "No web design or CMS implementations in win/loss history — evaluators will see an empty portfolio section.",
                ],
                "gap_action_plan": [
                    {
                        "requirement": "Website design portfolio (2+ comparable redesigns)",
                        "severity": "BLOCKING",
                        "current_status": "No website redesign projects in past performance library. We build enterprise platforms, not marketing websites.",
                        "action": "Cannot manufacture portfolio. Would need to partner with a web agency and position ourselves as a subcontractor — but RFP is likely looking for a prime agency.",
                        "owner": "Business Development",
                        "owner_area": "BD",
                    },
                    {
                        "requirement": "CMS platform expertise (WordPress, Drupal, or Sitecore)",
                        "severity": "HIGH",
                        "current_status": "No CMS product or implementation practice. Our stack is custom cloud platforms.",
                        "action": "CMS selection, theming, and content migration are core deliverables. We have no bench strength here.",
                        "owner": "Engineering",
                        "owner_area": "Engineering",
                    },
                    {
                        "requirement": "UX / information architecture (IA) practice",
                        "severity": "HIGH",
                        "current_status": "UX capability exists for enterprise product design — not marketing site IA or user journey mapping for public audiences.",
                        "action": "DLC explicitly requires stakeholder interviews, card sorts, and IA deliverables. Our UX team is product-focused.",
                        "owner": "Product Design",
                        "owner_area": "Design",
                    },
                    {
                        "requirement": "WCAG 2.1 AA accessibility compliance",
                        "severity": "LOW",
                        "current_status": "MET — all our products are annually audited for WCAG 2.1 AA.",
                        "action": "Highlight strongly in proposal as a differentiator. Include audit methodology.",
                        "owner": "Product Team",
                        "owner_area": "Product",
                    },
                    {
                        "requirement": "Content strategy and migration",
                        "severity": "MEDIUM",
                        "current_status": "No content strategy practice. We don't do editorial planning or content migration.",
                        "action": "DLC has 39 pages of structured content requirements. This is a significant workstream with no internal ownership.",
                        "owner": "TBD",
                        "owner_area": "Content",
                    },
                ],
                "submission_checklist": [],
                "reusable_content_available": [
                    "Security & Compliance Narrative (SOC2/HIPAA)",
                    "Cloud Architecture (AWS)",
                ],
            },
        },
    },

    "MCCVB Creative Agency": {
        "file": os.path.join(BASE, "MCCVB_AOR_RFP_FINAL_2021_86bccca1-3682-4a3a-aa4f-43831d7b7058.pdf"),
        "agency": "Monterey County Convention & Visitors Bureau (MCCVB)",
        "rfp_number": "MCCVB-2021-AOR",
        "title": "Creative & Media Buying Agency of Record",
        "deadline": "June 25, 2021",
        "value": "~$1M / year (est.)",
        "type": "Creative Agency / Media Buying",
        "demo_result": {
            "tool_call_log": [
                {"tool": "extract_requirements",    "input": {}, "output_keys": ["mandatory_requirements","scored_requirements","team_requirements"]},
                {"tool": "check_capabilities",       "input": {}, "output_keys": ["Creative / brand","Media buying","Tourism marketing","TV/Radio production"]},
                {"tool": "get_win_loss_history",     "input": {}, "output_keys": "list"},
                {"tool": "identify_gaps",            "input": {}, "output_keys": "list"},
                {"tool": "get_sme_and_content",      "input": {}, "output_keys": ["smes","reusable_content"]},
                {"tool": "generate_recommendation",  "input": {}, "output_keys": ["bid_score","decision"]},
            ],
            "executive_summary": (
                "MCCVB is searching for a full-service creative and media buying agency of record — "
                "a fundamentally different business category from enterprise software. "
                "We have no creative production, no media buying capability, no tourism sector experience, "
                "and no brand strategy practice. This is not a borderline case. "
                "Recommendation: No Bid. Zero overlap with our capabilities or strategic direction."
            ),
            "total_turns": 7,
            "recommendation": {
                "bid_score": 8,
                "decision": "NO BID",
                "confidence": "HIGH",
                "rationale": (
                    "Score of 8/100. 3 blocking gaps. "
                    "MCCVB requires a creative agency with TV/radio production, media buying desk, "
                    "brand strategy, and tourism domain expertise. We are an enterprise cloud platform company. "
                    "There is no version of this bid that reflects honest capability."
                ),
                "top_win_themes": [],
                "historical_loss_warnings": [
                    "No creative, marketing, or media buying projects exist in any history — this category is entirely outside our business.",
                ],
                "gap_action_plan": [
                    {
                        "requirement": "Creative & brand strategy capability",
                        "severity": "BLOCKING",
                        "current_status": "We are a technology company. No creative studio, brand strategists, or advertising creatives on staff.",
                        "action": "This is a fundamental business model mismatch. Pass immediately.",
                        "owner": "N/A",
                        "owner_area": "N/A",
                    },
                    {
                        "requirement": "Media buying and planning (TV, CTV, radio, digital)",
                        "severity": "BLOCKING",
                        "current_status": "No media buying desk, no agency trading desk, no media vendor relationships.",
                        "action": "Media buying requires licensed agency infrastructure and vendor contracts we do not have and cannot build quickly.",
                        "owner": "N/A",
                        "owner_area": "N/A",
                    },
                    {
                        "requirement": "Tourism / destination marketing experience",
                        "severity": "BLOCKING",
                        "current_status": "All past performance is in state health IT and federal healthcare. Zero tourism sector experience.",
                        "action": "Evaluators will compare us against purpose-built DMO agencies like 62ABOVE. No competitive path forward.",
                        "owner": "N/A",
                        "owner_area": "N/A",
                    },
                    {
                        "requirement": "Integrated marketing program delivery (Paid/Earned/Owned)",
                        "severity": "HIGH",
                        "current_status": "No marketing services practice.",
                        "action": "MCCVB needs an annual marketing partner, not a technology vendor.",
                        "owner": "N/A",
                        "owner_area": "N/A",
                    },
                ],
                "submission_checklist": [],
                "reusable_content_available": [],
            },
        },
    },
}
