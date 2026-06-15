"""
Synthetic test RFPs — realistic full-text documents.

8 test cases designed to stress different parts of the agent:
  TC-01  Strong match → BID               (NY Medicaid Analytics)
  TC-02  FedRAMP High required → NO BID   (CMS Federal Platform)
  TC-03  SBE + cert gap → CONDITIONAL     (Colorado Care Management)
  TC-04  Near-perfect match → BID         (Texas Population Health)
  TC-05  Wrong domain entirely → NO BID   (Marketing Agency RFP)
  TC-06  Team gap + geography → CONDITIONAL (Massachusetts Behavioral Health)
  TC-07  Small gov, good fit → BID        (Chicago Community Health)
  TC-08  Multiple blockers → NO BID       (VA Veterans Platform)

Each is realistic enough that a real agent can extract requirements from it.
"""

TEST_RFPS = {

    # ── TC-01 ─────────────────────────────────────────────────────────────────
    "TC-01: NY Medicaid Analytics": """
REQUEST FOR PROPOSAL
New York State Department of Health (NYSDOH)
RFP Number: DOH-2024-MA-0089
Title: Statewide Medicaid Analytics and Population Health Platform
Submission Deadline: October 15, 2024
Estimated Contract Value: $12M over 3 years

1. SCOPE OF WORK
NYSDOH seeks a vendor to deliver a cloud-based analytics platform supporting
3.1 million Medicaid beneficiaries. The platform must provide real-time population
health dashboards, care gap identification, and integration with the eMedNY claims system
via HL7 FHIR R4 APIs.

2. MANDATORY REQUIREMENTS
M-1: Vendor must hold SOC 2 Type II certification (current, renewed within 24 months).
M-2: Vendor must demonstrate HIPAA Business Associate Agreement execution capability.
M-3: All data must be hosted within the continental United States.
M-4: System must achieve 99.9% uptime SLA with documented maintenance windows.
M-5: Vendor must have delivered at least one state Medicaid analytics platform in the past 5 years.

3. SCORED REQUIREMENTS (100 points total)
S-1: HL7 FHIR R4 integration with existing state systems — 30 pts
S-2: Real-time population health dashboards — 20 pts
S-3: AI/ML care gap prediction model — 25 pts
S-4: Cloud-native architecture (AWS or Azure) — 15 pts
S-5: Role-based access control and audit logging — 10 pts

4. COMPLIANCE
- WCAG 2.1 AA accessibility compliance required
- Annual third-party penetration testing required
- Data retention policy: 7 years minimum

5. TEAM REQUIREMENTS
- Project Manager with PMP certification
- Clinical Data Analyst with Medicaid claims experience
- Cloud Security Architect

6. EVALUATION WEIGHTS
Technical approach: 45% | Past performance: 30% | Price: 25%
""",

    # ── TC-02 ─────────────────────────────────────────────────────────────────
    "TC-02: CMS Federal Health Platform": """
REQUEST FOR PROPOSAL
Centers for Medicare & Medicaid Services (CMS)
RFP Number: CMS-2024-FHP-0017
Title: Federal Health Innovation Data Platform
Submission Deadline: November 30, 2024
Estimated Contract Value: $45M over 5 years

1. SCOPE OF WORK
CMS seeks a vendor to build and operate a federal-grade health innovation data platform
processing claims data for 140 million Medicare and Medicaid beneficiaries. The platform
will support CMS Innovation Center (CMMI) pilots and require integration with CMS
enterprise systems including the Integrated Data Repository (IDR).

2. MANDATORY REQUIREMENTS
M-1: Vendor must hold a current FedRAMP HIGH authorization (not Moderate, not In Progress).
M-2: Vendor must hold a current FISMA High system ATO.
M-3: Vendor must have a cleared facility and personnel with Secret clearance for select roles.
M-4: Vendor must demonstrate prior federal civilian agency contract performance at $20M+.
M-5: All data processing must occur within FedRAMP-authorized GovCloud environments.
M-6: HIPAA BAA with Federal addendum required.

3. SCORED REQUIREMENTS
S-1: FHIR R4 and SMART on FHIR implementation — 25 pts
S-2: Real-time streaming analytics (sub-100ms latency) — 20 pts
S-3: Zero-trust network architecture — 20 pts
S-4: ML anomaly detection for fraud, waste, and abuse — 20 pts
S-5: Compliance dashboard (FISMA, NIST 800-53) — 15 pts

4. EVALUATION
Technical: 40% | Past performance: 35% | Price: 25%
""",

    # ── TC-03 ─────────────────────────────────────────────────────────────────
    "TC-03: Colorado Care Management": """
REQUEST FOR PROPOSAL
Colorado Department of Health Care Policy and Financing (HCPF)
RFP Number: HCPF-2024-CM-0031
Title: Medicaid Care Management Platform
Submission Deadline: August 20, 2024
Estimated Contract Value: $9M over 3 years

1. SCOPE OF WORK
Colorado HCPF seeks a vendor to implement a care management platform for 620,000
Medicaid members, with a focus on complex case management, care coordinator workflows,
and integration with Colorado's BIDM (Business Intelligence and Data Management) system.

2. MANDATORY REQUIREMENTS
M-1: SOC 2 Type II certification required.
M-2: HIPAA BAA capability required.
M-3: System uptime: 99.5% minimum.
M-4: All PII must remain within US borders.
M-5: Vendor must hold or be actively pursuing FedRAMP Moderate authorization.
     (In-Progress status accepted with PMO letter confirming active assessment.)

3. SCORED REQUIREMENTS
S-1: FHIR R4 integration — 25 pts
S-2: Care coordinator mobile application — 20 pts
S-3: ML-driven risk stratification — 20 pts
S-4: Real-time alerts and dashboards — 15 pts
S-5: Multilingual UI (Spanish required; additional languages a plus) — 10 pts
S-6: API-first architecture — 10 pts

4. COMPLIANCE
- WCAG 2.1 AA required
- Colorado SB 21-234 data privacy compliance required
- Small Business subcontracting: 20% minimum to Colorado-certified SBE firms

5. TEAM
- PMP-certified Project Manager
- Colorado on-site presence during implementation (Denver office or travel)
- Clinical informatics lead

6. EVALUATION
Technical: 40% | Past performance: 25% | Price: 25% | SBE participation: 10%
""",

    # ── TC-04 ─────────────────────────────────────────────────────────────────
    "TC-04: Texas Population Health": """
REQUEST FOR PROPOSAL
Texas Health and Human Services Commission (HHSC)
RFP Number: HHSC-2024-PH-0055
Title: Medicaid Population Health Intelligence Platform
Submission Deadline: September 5, 2024
Estimated Contract Value: $14M over 3 years

1. SCOPE OF WORK
Texas HHSC seeks to expand its population health analytics capabilities for 4.8 million
Medicaid beneficiaries. The system must integrate with the Texas Medicaid MMIS (TMHP),
deliver predictive care gap analytics, and support a statewide care management workforce.

2. MANDATORY REQUIREMENTS
M-1: SOC 2 Type II certification required.
M-2: HIPAA Business Associate Agreement capability.
M-3: US-only data residency, enforced by contract and technical controls.
M-4: 99.9% uptime SLA with penalty provisions.
M-5: Vendor must have successfully delivered a state Medicaid platform in Texas or
     at least two other US states within the past 5 years.

3. SCORED REQUIREMENTS
S-1: FHIR R4 integration (TMHP-compatible) — 25 pts
S-2: Predictive ML care gap model with documented accuracy metrics — 25 pts
S-3: Cloud-native deployment (AWS preferred) — 20 pts
S-4: Real-time dashboards and KPI reporting — 15 pts
S-5: Mobile application for care managers — 10 pts
S-6: WCAG 2.1 AA accessibility — 5 pts

4. TEAM
- PMP-certified Project Manager
- Clinical Informatics lead (Medicaid experience required)
- AWS-certified Solutions Architect

5. EVALUATION
Technical: 40% | Past performance: 35% | Price: 25%
Note: Prior Texas HHSC work will be weighted heavily in past performance scoring.
""",

    # ── TC-05 ─────────────────────────────────────────────────────────────────
    "TC-05: Brand & Digital Marketing Agency": """
REQUEST FOR PROPOSAL
Pacific Northwest Tourism Alliance (PNTA)
RFP Number: PNTA-2024-MKT-0008
Title: Brand Strategy and Digital Marketing Agency of Record
Submission Deadline: July 31, 2024
Estimated Contract Value: $2.4M over 2 years

1. SCOPE OF WORK
PNTA seeks a full-service brand and digital marketing agency to serve as Agency of Record.
Scope includes brand refresh, paid digital media (search, social, programmatic), content
creation, influencer partnerships, and quarterly campaign reporting.

2. MANDATORY REQUIREMENTS
M-1: Agency must have a minimum of 5 years operating as a full-service marketing agency.
M-2: Agency must demonstrate experience managing media budgets of $500K+ annually.
M-3: Agency must provide a dedicated creative team (art director, copywriter, strategist).
M-4: Agency must have prior tourism, hospitality, or destination marketing experience.

3. DELIVERABLES
- Brand audit and strategic brief (Month 1)
- Refreshed brand identity system (Month 3)
- Annual media plan and buying across digital channels
- Monthly performance reports (impressions, CTR, ROAS)
- Quarterly campaign creative (video, static, OOH)
- Influencer campaign management (4 campaigns/year)

4. EVALUATION
Creative portfolio: 35% | Strategic approach: 30% | Media capabilities: 20% | Price: 15%
""",

    # ── TC-06 ─────────────────────────────────────────────────────────────────
    "TC-06: Massachusetts Behavioral Health": """
REQUEST FOR PROPOSAL
Massachusetts Executive Office of Health and Human Services (EOHHS)
RFP Number: EOHHS-2024-BH-0042
Title: Behavioral Health Care Coordination Platform
Submission Deadline: October 1, 2024
Estimated Contract Value: $7.5M over 3 years

1. SCOPE OF WORK
Massachusetts EOHHS seeks a behavioral health-specific care coordination platform
for 280,000 MassHealth members receiving behavioral health services. The platform
must support complex SUD (Substance Use Disorder) case management workflows and
integrate with the Commonwealth's HIE (Health Information Exchange).

2. MANDATORY REQUIREMENTS
M-1: SOC 2 Type II certification.
M-2: HIPAA BAA with 42 CFR Part 2 (substance use disorder data) compliance capability.
M-3: US-only data residency.
M-4: 99.9% uptime SLA.
M-5: Vendor must have a Massachusetts office OR commit to opening one within 90 days of contract award.
M-6: Vendor must have delivered a behavioral health or SUD-specific platform, not general care management.

3. SCORED REQUIREMENTS
S-1: FHIR R4 integration — 20 pts
S-2: 42 CFR Part 2 compliant data segmentation — 25 pts
S-3: SUD-specific care pathway templates — 20 pts
S-4: Real-time crisis alert escalation — 15 pts
S-5: Peer support specialist mobile workflow — 10 pts
S-6: ML relapse risk prediction — 10 pts

4. TEAM
- PMP-certified Project Manager
- Behavioral Health Clinical Lead (licensed LCSW or equivalent, SUD experience)
- Massachusetts-based implementation support staff

5. EVALUATION
Technical: 40% | Domain expertise: 25% | Past performance: 20% | Price: 15%
""",

    # ── TC-07 ─────────────────────────────────────────────────────────────────
    "TC-07: Chicago Community Health Platform": """
REQUEST FOR PROPOSAL
Chicago Department of Public Health (CDPH)
RFP Number: CDPH-2024-CH-0019
Title: Community Health Intelligence and Care Coordination System
Submission Deadline: August 30, 2024
Estimated Contract Value: $4.2M over 2 years

1. SCOPE OF WORK
CDPH seeks a cloud-based community health platform to support care coordination
for 180,000 Chicago residents enrolled in city-run health programs. The system
must integrate with Illinois' CHIRP immunization registry and support multilingual
outreach workflows.

2. MANDATORY REQUIREMENTS
M-1: SOC 2 Type II or equivalent security certification.
M-2: HIPAA BAA capability.
M-3: US-only data hosting.
M-4: System uptime: 99.5% minimum.

3. SCORED REQUIREMENTS
S-1: HL7 FHIR R4 or equivalent integration capability — 25 pts
S-2: Multilingual UI (English, Spanish, Polish, Mandarin) — 20 pts
S-3: Real-time dashboards and population reporting — 20 pts
S-4: Mobile-friendly care manager interface — 15 pts
S-5: Cloud-native architecture — 10 pts
S-6: AI-assisted outreach prioritization — 10 pts

4. COMPLIANCE
- WCAG 2.1 AA accessibility
- Illinois PIPA data privacy compliance
- City of Chicago MBE/WBE participation: 25% of contract value

5. TEAM
- Project Manager (PMP preferred)
- Chicago-area support team for go-live assistance (travel acceptable)

6. EVALUATION
Technical: 40% | Price: 30% | Past performance: 20% | MBE/WBE: 10%
""",

    # ── TC-08 ─────────────────────────────────────────────────────────────────
    "TC-08: VA Veterans Health Platform": """
REQUEST FOR PROPOSAL
U.S. Department of Veterans Affairs (VA)
RFP Number: VA-2024-VHP-0003
Title: Veterans Integrated Health and Analytics Platform
Submission Deadline: December 15, 2024
Estimated Contract Value: $38M over 5 years

1. SCOPE OF WORK
The VA seeks a vendor to design, implement, and operate an integrated health analytics
platform supporting 9 million enrolled Veterans across 170 VA Medical Centers. The
platform must integrate with the VA's VistA EHR system and support transition to
Oracle Health (Cerner) via FHIR APIs.

2. MANDATORY REQUIREMENTS
M-1: Vendor must hold FedRAMP HIGH authorization (not Moderate).
M-2: Vendor must hold a current VA Authority to Operate (ATO).
M-3: Key personnel must hold active Secret or Top Secret clearance.
M-4: Vendor must have prior VA or DoD contract performance at $10M+ within 5 years.
M-5: Vendor must have a CMMI Level 3 or higher software development maturity rating.
M-6: System must be Section 508 compliant (Federal accessibility standard).
M-7: All infrastructure must run on VA-approved cloud environments (VA EARC approved).

3. SCORED REQUIREMENTS
S-1: VistA / Oracle Health FHIR integration — 30 pts
S-2: Real-time clinical decision support — 25 pts
S-3: ML predictive analytics (suicide risk, readmission) — 20 pts
S-4: Zero-trust security architecture — 15 pts
S-5: Veteran-facing mobile application — 10 pts

4. EVALUATION
Technical: 40% | Past performance: 35% | Price: 15% | Small Business: 10%
""",
}
