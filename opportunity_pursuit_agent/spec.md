# Opportunity Pursuit Agent — Engineering Specification

**Version:** 1.0  
**Date:** June 2026  
**Status:** Ready for Engineering Handoff  
**Prototype location:** `/prototype/`

---

## 1. Overview

The Opportunity Pursuit Agent is an AI-powered bid intelligence tool that ingests RFP documents, reasons over them against a company's internal knowledge base, and produces a structured go/no-go recommendation with gap analysis, SME assignments, win themes, and a submission checklist.

### 1.1 Problem Being Solved

Enterprise proposal teams spend 200–500 person-hours responding to RFPs before knowing whether the opportunity is worth pursuing. Every bad bid wastes real money. This agent compresses the go/no-go decision from days to minutes.

### 1.2 Users

| Role | How they use the agent |
|---|---|
| **Capture Manager / BD Lead** | Uploads RFP, reviews recommendation, makes bid decision |
| **Proposal Manager** | Uses gap action plan and submission checklist to coordinate team |
| **SME / Subject Expert** | Receives escalation notifications when their domain is flagged |
| **Sales Leadership** | Views bid score and rationale for pipeline prioritisation |

### 1.3 Prototype Reference

A working prototype is included in `/prototype/`. It demonstrates:
- The 6-tool agent loop with Claude Sonnet as the reasoning engine
- Parallel tool execution (3 API round trips vs 6 sequential)
- Per-step confidence scoring with automatic human escalation at < 80%
- Streamlit UI with RFP selector, execution trace, gap analysis, and submission checklist

Production build replaces mock data with real integrations (see §4).

---

## 2. Functional Requirements

### FR-1 — RFP Ingestion

| ID | Requirement | Priority |
|---|---|---|
| FR-1.1 | System must accept RFP documents via file upload (PDF, DOCX, PPTX) | P0 |
| FR-1.2 | System must accept RFP text pasted directly into a text field | P0 |
| FR-1.3 | System must accept a URL pointing to a public RFP portal page and scrape its content | P1 |
| FR-1.4 | System must extract and persist raw text, page count, file name, and upload timestamp | P0 |
| FR-1.5 | System must handle scanned PDFs via OCR (AWS Textract or Google Document AI) | P1 |
| FR-1.6 | Maximum accepted file size: 50 MB | P0 |
| FR-1.7 | System must support bulk upload of up to 10 RFPs for batch analysis | P2 |

### FR-2 — Requirements Extraction

| ID | Requirement | Priority |
|---|---|---|
| FR-2.1 | Agent must extract and classify requirements into: Mandatory, Scored, Compliance, Team | P0 |
| FR-2.2 | Each requirement must include its source text, page number, and point weight (if scored) | P0 |
| FR-2.3 | Agent must extract RFP metadata: issuing agency, RFP number, deadline, contract value, geography | P0 |
| FR-2.4 | Agent must identify eliminatory clauses (requirements that disqualify if unmet) | P0 |
| FR-2.5 | Extraction output must be reviewable and editable by the user before analysis proceeds | P1 |

### FR-3 — Capability Matching

| ID | Requirement | Priority |
|---|---|---|
| FR-3.1 | Agent must compare extracted requirements against the company capability knowledge base | P0 |
| FR-3.2 | Each requirement must be tagged: MET / PARTIAL / NOT MET / UNKNOWN | P0 |
| FR-3.3 | For PARTIAL matches, agent must include the specific gap between requirement and capability | P0 |
| FR-3.4 | Capability KB must be updatable by authorised users without a code deployment | P0 |
| FR-3.5 | Matching must use semantic similarity (vector search), not keyword matching only | P1 |

### FR-4 — Win / Loss Retrieval

| ID | Requirement | Priority |
|---|---|---|
| FR-4.1 | Agent must retrieve the top 5 most similar past opportunities from the CRM | P0 |
| FR-4.2 | Each retrieved record must include: outcome, contract value, win themes or loss reason | P0 |
| FR-4.3 | Similarity must be computed on industry, agency type, scope, and requirement overlap | P1 |
| FR-4.4 | System must surface repeated loss patterns (e.g. FedRAMP has caused 3 prior losses) | P1 |

### FR-5 — Gap Identification

| ID | Requirement | Priority |
|---|---|---|
| FR-5.1 | Agent must produce a gap list with severity: BLOCKING / HIGH / MEDIUM / LOW | P0 |
| FR-5.2 | Each gap must include the specific requirement, current company status, and remediation path | P0 |
| FR-5.3 | BLOCKING gaps must be surfaced prominently and must trigger a no-bid recommendation by default | P0 |
| FR-5.4 | Users must be able to override a BLOCKING gap classification with a written justification | P1 |

### FR-6 — SME & Content Assignment

| ID | Requirement | Priority |
|---|---|---|
| FR-6.1 | Agent must assign an internal SME owner to each gap area | P0 |
| FR-6.2 | Agent must identify reusable proposal content blocks from the proposal library for each gap | P0 |
| FR-6.3 | SME owners must receive an automated notification (email or Slack) when assigned | P1 |
| FR-6.4 | Each SME notification must include: the gap description, deadline, and a link to the pursuit | P1 |

### FR-7 — Bid Recommendation

| ID | Requirement | Priority |
|---|---|---|
| FR-7.1 | Agent must produce a bid score from 0–100 with explicit scoring rationale | P0 |
| FR-7.2 | Decision output must be one of: BID / CONDITIONAL BID / NO BID | P0 |
| FR-7.3 | Score thresholds: ≥ 70 = BID, 40–69 = CONDITIONAL BID, < 40 = NO BID | P0 |
| FR-7.4 | Score thresholds must be configurable per organisation without a code change | P1 |
| FR-7.5 | Agent must produce top 3 win themes to emphasise in the proposal | P0 |
| FR-7.6 | Agent must produce a submission checklist with item, owner, and deadline | P0 |
| FR-7.7 | Agent must produce a score breakdown across 5 dimensions: Technical fit, Past performance, Compliance, Team readiness, Strategic fit | P0 |

### FR-8 — Per-Step Confidence Scoring

| ID | Requirement | Priority |
|---|---|---|
| FR-8.1 | Each agent execution step must emit a confidence score (0–100%) | P0 |
| FR-8.2 | Confidence scores must be visible to the user in real time during execution | P0 |
| FR-8.3 | Any step with confidence < 80% must trigger an automatic human review escalation | P0 |
| FR-8.4 | Escalation must display: which step(s) triggered it, the score, and the specific reason | P0 |
| FR-8.5 | Confidence threshold (80%) must be configurable per organisation | P1 |
| FR-8.6 | Users must be able to accept or override the escalation and proceed autonomously | P1 |

### FR-9 — Human-in-the-Loop

| ID | Requirement | Priority |
|---|---|---|
| FR-9.1 | Agent must pause and request human input when any step confidence < configured threshold | P0 |
| FR-9.2 | Human reviewer must be able to approve, reject, or edit any intermediate agent output | P1 |
| FR-9.3 | Human overrides must be logged with reviewer identity and timestamp | P0 |
| FR-9.4 | After human input, agent must continue from the paused step (not restart) | P1 |
| FR-9.5 | If no human responds within a configurable timeout (default 24h), agent must escalate to the next reviewer in the chain | P2 |

### FR-10 — Output & Delivery

| ID | Requirement | Priority |
|---|---|---|
| FR-10.1 | Full recommendation report must be exportable as PDF | P0 |
| FR-10.2 | Submission checklist must be exportable as CSV | P1 |
| FR-10.3 | Results must be pushable to CRM (Salesforce / HubSpot) as an opportunity record | P1 |
| FR-10.4 | Results must be shareable via a read-only link with no login required | P2 |
| FR-10.5 | All results must be persisted and retrievable by pursuit name or RFP number | P0 |

### FR-11 — Pursuit Lifecycle Tracking

| ID | Requirement | Priority |
|---|---|---|
| FR-11.1 | System must track RFP status: Uploaded / Analysing / Under Review / Decision Made / Submitted / Won / Lost | P0 |
| FR-11.2 | System must accept RFP amendment uploads and re-run analysis on changed sections only | P1 |
| FR-11.3 | System must log all agent runs, human overrides, and decision history per pursuit | P0 |

---

## 3. Non-Functional Requirements

### NFR-1 — Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-1.1 | End-to-end agent analysis time (6 tools, parallel execution) | ≤ 30s for RFPs up to 100 pages |
| NFR-1.2 | RFP ingestion and text extraction | ≤ 10s for files up to 50 MB |
| NFR-1.3 | UI time-to-first-meaningful-paint | ≤ 2s |
| NFR-1.4 | Confidence scores must stream to UI as each step completes — no batched end-of-run delivery | Real-time |
| NFR-1.5 | Parallel tool execution must be used for all independent steps (Batch 1 and Batch 2 per spec) | ≤ 3 API round trips for standard analysis |

### NFR-2 — Reliability & Availability

| ID | Requirement | Target |
|---|---|---|
| NFR-2.1 | System uptime SLA | 99.9% |
| NFR-2.2 | Agent must retry failed tool calls up to 3 times with exponential backoff before escalating | Max 3 retries |
| NFR-2.3 | Partial results must be saved after each completed batch so a crash does not lose work | Per batch |
| NFR-2.4 | If the LLM API is unavailable, system must queue the request and notify the user | < 5 min queue notification |
| NFR-2.5 | RTO (Recovery Time Objective) | ≤ 1 hour |
| NFR-2.6 | RPO (Recovery Point Objective) | ≤ 15 minutes |

### NFR-3 — Security

| ID | Requirement | Note |
|---|---|---|
| NFR-3.1 | All RFP documents and analysis results must be encrypted at rest (AES-256) | Required |
| NFR-3.2 | All data in transit must use TLS 1.2 or higher | Required |
| NFR-3.3 | API keys (Anthropic, CRM, Slack) must be stored in a secrets manager (AWS Secrets Manager or HashiCorp Vault) — never in environment variables or code | Required |
| NFR-3.4 | All user actions must be logged in an immutable audit trail with user ID, timestamp, and action | Required |
| NFR-3.5 | RFP documents must never be sent to the LLM in a way that leaks them to other tenants | Multi-tenant isolation required |
| NFR-3.6 | RBAC must enforce: Viewer (read results) / Analyst (run analysis) / Admin (manage KB, users, thresholds) | Required |
| NFR-3.7 | SOC 2 Type II compliance must be maintained for the production system | Required |

### NFR-4 — Scalability

| ID | Requirement | Target |
|---|---|---|
| NFR-4.1 | System must support concurrent analysis of up to 50 RFPs without performance degradation | 50 concurrent |
| NFR-4.2 | Capability KB must support up to 10,000 entries with sub-second retrieval via vector search | 10K entries |
| NFR-4.3 | Win/loss history must support up to 100,000 CRM records with semantic search | 100K records |
| NFR-4.4 | Architecture must support horizontal scaling of the agent worker pool | Kubernetes-ready |

### NFR-5 — Observability

| ID | Requirement | Note |
|---|---|---|
| NFR-5.1 | Every agent run must emit structured logs: tool name, inputs (redacted), outputs summary, latency, confidence score | Required |
| NFR-5.2 | Dashboard must track: mean analysis time, confidence score distribution, escalation rate, bid score distribution, decision outcomes over time | Required |
| NFR-5.3 | Alerting must fire when: error rate > 1%, mean latency > 45s, escalation rate > 40% | Required |
| NFR-5.4 | LLM token usage must be tracked per run and per tenant for cost attribution | Required |
| NFR-5.5 | Traces must be exportable to Datadog, Grafana, or equivalent | Required |

### NFR-6 — Maintainability

| ID | Requirement | Note |
|---|---|---|
| NFR-6.1 | Tool implementations must be independently deployable — adding a new tool must not require changes to the agent loop | Required |
| NFR-6.2 | System prompt and confidence thresholds must be editable via admin UI without a code deployment | Required |
| NFR-6.3 | All integrations (CRM, Slack, SharePoint) must be behind an adapter interface so they can be swapped without touching agent logic | Required |
| NFR-6.4 | Test coverage must be ≥ 80% on tool implementations and agent loop | Required |

### NFR-7 — Compliance & Data Governance

| ID | Requirement | Note |
|---|---|---|
| NFR-7.1 | RFP documents marked confidential must not leave the company's cloud region | Data residency |
| NFR-7.2 | Users must be able to delete all data associated with a pursuit (GDPR right to erasure) | Required |
| NFR-7.3 | Retention policy: raw RFP text retained for 7 years; analysis results retained for 3 years by default | Configurable |
| NFR-7.4 | System must support single sign-on (SSO) via SAML 2.0 or OIDC | Required |

---

## 4. System Architecture

### 4.1 High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend (React)                        │
│  RFP Upload · Selector · Execution Trace · Results Dashboard     │
└─────────────────────┬───────────────────────────────────────────┘
                      │ REST / WebSocket
┌─────────────────────▼───────────────────────────────────────────┐
│                       API Gateway (FastAPI)                      │
│  Auth (RBAC) · Rate Limiting · Request Routing · Audit Logging   │
└──────┬──────────────┬──────────────────────┬────────────────────┘
       │              │                      │
┌──────▼──────┐ ┌─────▼──────────┐ ┌────────▼──────────┐
│  Ingestion  │ │  Agent Worker  │ │  Notification     │
│  Service    │ │  (Python)      │ │  Service          │
│  PDF/DOCX   │ │  Claude API    │ │  Slack / Email    │
│  OCR        │ │  Tool Router   │ │                   │
└──────┬──────┘ └─────┬──────────┘ └───────────────────┘
       │              │
┌──────▼──────────────▼───────────────────────────────────────────┐
│                     Data & Integration Layer                      │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │ Capability  │  │  Win/Loss    │  │  Proposal Library       │ │
│  │ KB          │  │  (CRM)       │  │  (SharePoint / S3)      │ │
│  │ (Postgres + │  │  Salesforce  │  │  Vector Index           │ │
│  │  pgvector)  │  │  HubSpot     │  │  (Pinecone / pgvector)  │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘ │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │  SME        │  │  RFP Store   │  │  Audit Log              │ │
│  │  Directory  │  │  (S3 +       │  │  (append-only,          │ │
│  │  (HRIS/AD)  │  │   Postgres)  │  │   immutable)            │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Agent Execution Model

```
User uploads RFP
      │
      ▼
Ingestion Service → extract text, store in S3, create Pursuit record
      │
      ▼
Agent Worker receives job from queue (SQS / Redis)
      │
      ▼
ROUND 1 (parallel)
  ├── extract_requirements   → LLM call over RFP text
  └── get_win_loss_history   → CRM vector search
      │
      ▼
ROUND 2 (parallel)
  ├── check_capabilities     → KB vector search using Round 1 requirements
  └── get_sme_and_content    → HRIS lookup + proposal library search
      │
      ▼
ROUND 3
  └── identify_gaps          → diff requirements vs capability results
      │
      ▼
ROUND 4
  └── generate_recommendation → LLM synthesis with all evidence
      │
      ▼
Persist results → notify user → push to CRM
```

### 4.3 Technology Stack (Recommended)

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | React + TypeScript | Component reuse, type safety |
| UI components | shadcn/ui + Tailwind CSS | Matches responsive.ai design language |
| API | FastAPI (Python) | Async, fast, native Pydantic validation |
| Agent loop | Python + Anthropic SDK | Direct parity with prototype |
| LLM | Claude Sonnet (claude-sonnet-4-6) | Proven in prototype; upgrade path to Opus for complex RFPs |
| Vector DB | pgvector on Postgres | Single DB for relational + vector; simpler ops than Pinecone at initial scale |
| Document store | AWS S3 | Durability, cost, native encryption |
| Job queue | AWS SQS | Decouples ingestion from analysis; handles backpressure |
| OCR | AWS Textract | Handles scanned PDFs, tables, forms |
| Secrets | AWS Secrets Manager | Rotate without redeployment |
| Auth | Auth0 or Okta (OIDC/SAML) | SSO requirement, RBAC |
| Observability | Datadog | Logs + APM + LLM token tracking |
| CI/CD | GitHub Actions + Docker + ECS or EKS | Horizontal scaling |

---

## 5. Data Models

### 5.1 Pursuit

```python
class Pursuit(BaseModel):
    id:               UUID
    name:             str
    rfp_number:       str
    agency:           str
    contract_value:   Optional[str]
    deadline:         Optional[date]
    status:           Literal["uploaded", "analysing", "under_review",
                              "decision_made", "submitted", "won", "lost"]
    rfp_s3_key:       str            # raw document
    created_by:       UUID           # user ID
    created_at:       datetime
    updated_at:       datetime
```

### 5.2 AgentRun

```python
class AgentRun(BaseModel):
    id:                  UUID
    pursuit_id:          UUID
    status:              Literal["running", "paused_for_review", "complete", "failed"]
    total_turns:         int
    total_elapsed_s:     float
    tool_call_log:       list[ToolCallRecord]
    recommendation:      Optional[Recommendation]
    executive_summary:   Optional[str]
    triggered_by:        UUID           # user ID
    started_at:          datetime
    completed_at:        Optional[datetime]

class ToolCallRecord(BaseModel):
    tool:           str
    batch:          int                # parallel batch number
    input_summary:  str                # redacted for logging
    output_keys:    list[str]
    confidence:     int                # 0-100
    confidence_note: str
    elapsed_s:      float
    escalated:      bool
```

### 5.3 Recommendation

```python
class Recommendation(BaseModel):
    bid_score:          int            # 0-100
    decision:           Literal["BID", "CONDITIONAL BID", "NO BID"]
    confidence:         Literal["HIGH", "MODERATE", "LOW"]
    rationale:          str
    top_win_themes:     list[str]      # max 3
    gap_action_plan:    list[Gap]
    submission_checklist: list[ChecklistItem]
    score_breakdown:    dict[str, int] # dimension → score

class Gap(BaseModel):
    requirement:    str
    severity:       Literal["BLOCKING", "HIGH", "MEDIUM", "LOW"]
    current_status: str
    action:         str
    owner:          Optional[str]
    sme_email:      Optional[str]
    due_date:       Optional[date]

class ChecklistItem(BaseModel):
    item:    str
    owner:   str
    due:     str
```

### 5.4 Capability KB Entry

```python
class Capability(BaseModel):
    id:          UUID
    category:    str              # e.g. "certifications", "technical", "team"
    name:        str              # e.g. "FedRAMP Moderate"
    description: str
    status:      Literal["active", "in_progress", "planned", "deprecated"]
    valid_until: Optional[date]
    evidence:    Optional[str]    # URL to certificate or document
    embedding:   list[float]      # pgvector column
    updated_by:  UUID
    updated_at:  datetime
```

---

## 6. API Contracts

### 6.1 Submit RFP for Analysis

```
POST /api/v1/pursuits

Request:
  Content-Type: multipart/form-data
  Body:
    file:       <PDF or DOCX binary>
    name:       string
    rfp_number: string (optional)

Response 202 Accepted:
  {
    "pursuit_id": "uuid",
    "status": "analysing",
    "websocket_url": "wss://api.example.com/ws/pursuits/{pursuit_id}"
  }
```

### 6.2 WebSocket — Live Execution Stream

```
WS /ws/pursuits/{pursuit_id}

Server → Client messages:
  { "type": "step_start",  "tool": "extract_requirements", "batch": 1 }
  { "type": "step_done",   "tool": "extract_requirements", "confidence": 97,
    "confidence_note": "RFP well-structured", "elapsed_s": 1.2 }
  { "type": "escalation",  "tool": "check_capabilities",  "confidence": 55,
    "reason": "Only 2 of 8 requirements matched" }
  { "type": "complete",    "run_id": "uuid" }
  { "type": "error",       "message": "...", "retrying": true }
```

### 6.3 Get Recommendation

```
GET /api/v1/pursuits/{pursuit_id}/recommendation

Response 200:
  {
    "bid_score": 55,
    "decision": "CONDITIONAL BID",
    "confidence": "LOW",
    "rationale": "...",
    "top_win_themes": [...],
    "gap_action_plan": [...],
    "submission_checklist": [...],
    "score_breakdown": { ... },
    "run_id": "uuid",
    "generated_at": "ISO8601"
  }
```

### 6.4 Human Override

```
POST /api/v1/runs/{run_id}/override

Request:
  {
    "step": "check_capabilities",
    "action": "approve" | "reject" | "edit",
    "justification": "string",
    "edited_output": { ... }    // only when action = "edit"
  }

Response 200:
  { "status": "resumed", "next_step": "identify_gaps" }
```

### 6.5 Update Capability KB

```
POST   /api/v1/kb/capabilities       # create
PUT    /api/v1/kb/capabilities/{id}  # update
DELETE /api/v1/kb/capabilities/{id}  # soft delete
GET    /api/v1/kb/capabilities       # list with filters
```

---

## 7. Integration Specifications

### 7.1 CRM (Salesforce / HubSpot)

| Field | Direction | Notes |
|---|---|---|
| Opportunity name, value, close date | Pull → agent | Used for win/loss retrieval |
| Win/loss outcome, themes, reason | Pull → agent | Grounds the recommendation |
| Bid score, decision, agent run ID | Push → CRM | Written back after analysis |
| SME assignments | Push → CRM | Logged as opportunity activities |

Authentication: OAuth 2.0 client credentials. Refresh token must be rotated via Secrets Manager.

### 7.2 Proposal Library (SharePoint / S3)

- Agent calls `get_sme_and_content` which queries a vector index built nightly from proposal library documents
- Index pipeline: SharePoint / S3 → text extraction → chunking (512 tokens, 50% overlap) → embedding (text-embedding-3-small) → pgvector upsert
- Cache embeddings for 7 days; re-embed on document change

### 7.3 SME Directory (HRIS / Active Directory)

- Read-only API call to resolve gap area → SME name + email
- Fallback: static YAML config maintained by Ops if HRIS API is unavailable

### 7.4 Notifications (Slack + Email)

```
Trigger: SME assigned to a gap
Channel: #pursuit-{rfp_number} (auto-created)
Message:
  "You've been assigned as SME owner for [gap] on pursuit [name].
   Action required: [action]
   Deadline: [due_date]
   View pursuit: [link]"
```

Email fallback if Slack unavailable.

---

## 8. Evaluation & Monitoring Framework

### 8.1 Agent Quality Metrics

| Metric | Definition | Target | Measurement |
|---|---|---|---|
| Recommendation accuracy | % of agent decisions that match human expert decision on same RFP | ≥ 85% | Monthly blind audit of 20 RFPs |
| Gap recall | % of real gaps correctly identified (vs. human review) | ≥ 90% | Quarterly SME audit |
| False positive rate | % of BID recommendations on RFPs later lost | ≤ 20% | CRM outcome tracking |
| Confidence calibration | Correlation between step confidence score and actual accuracy | ≥ 0.75 | Monthly statistical analysis |
| Escalation rate | % of runs triggering human review | 20–40% target range | Weekly dashboard |

### 8.2 System Performance Metrics

| Metric | Target | Alert threshold |
|---|---|---|
| P50 analysis time | ≤ 15s | — |
| P95 analysis time | ≤ 30s | > 45s |
| Error rate | ≤ 0.5% | > 1% |
| LLM token cost per run | ≤ $0.50 | > $1.00 |
| Uptime | 99.9% | < 99.5% |

### 8.3 Business Metrics (tracked in CRM, not in agent)

- Bid volume vs. win rate (before/after agent adoption)
- Proposal hours per bid (target: 40% reduction)
- No-bid rate (target: increase from baseline — catching bad bids early)
- Time-to-decision (target: < 30 min vs. 2–3 days manual)

---

## 9. Phased Rollout Plan

### Phase 1 — Foundation (Weeks 1–6)

- [ ] FastAPI backend with RFP ingestion (PDF/DOCX), text extraction, S3 storage
- [ ] Agent loop with parallel tool execution (parity with prototype)
- [ ] Capability KB: Postgres + pgvector, admin CRUD UI
- [ ] Static win/loss data (CSV import from CRM export)
- [ ] React frontend: RFP upload, execution trace with live confidence scores, results dashboard
- [ ] Auth: SSO via Auth0, three RBAC roles
- [ ] PDF export of recommendation report
- [ ] Audit logging

### Phase 2 — Integrations (Weeks 7–10)

- [ ] Live CRM integration (Salesforce or HubSpot)
- [ ] SharePoint / S3 proposal library with nightly vector index pipeline
- [ ] HRIS / Active Directory SME lookup
- [ ] Slack + email SME notifications
- [ ] Human-in-loop: pause/resume on low-confidence steps
- [ ] WebSocket streaming for live execution updates

### Phase 3 — Intelligence (Weeks 11–16)

- [ ] OCR for scanned PDFs (AWS Textract)
- [ ] RFP amendment detection and partial re-analysis
- [ ] Confidence calibration pipeline (compare predictions to outcomes)
- [ ] Batch analysis (up to 10 RFPs simultaneously)
- [ ] Observability dashboard (Datadog)
- [ ] Configurable thresholds and system prompt via admin UI

---

## 10. Open Questions for Engineering

| # | Question | Owner | Due |
|---|---|---|---|
| 1 | Which CRM is the source of truth — Salesforce or HubSpot? API credentials and sandbox access needed. | BD / Sales Ops | Before Phase 2 |
| 2 | Is SharePoint the proposal library or are proposals stored in S3? Determines indexing pipeline design. | Proposal Team | Before Phase 2 |
| 3 | What is the HRIS system for SME directory? (Workday, BambooHR, Active Directory?) | HR / IT | Before Phase 2 |
| 4 | Multi-tenant from day one or single-tenant MVP? Determines DB schema and auth isolation model. | Engineering Lead | Before Phase 1 |
| 5 | What is the acceptable LLM cost budget per run? Determines whether Sonnet or Haiku is used for extraction steps. | Finance | Before Phase 1 |
| 6 | Should the agent support non-English RFPs in Phase 1? Determines embedding model selection. | Product | Before Phase 1 |

---

## 11. Prototype → Production Delta

The prototype in `/prototype/` demonstrates the full agent reasoning flow. The following are **not** production-ready in the prototype and must be built:

| Prototype | Production replacement |
|---|---|
| `mock_data.py` — hardcoded KB | Postgres + pgvector with admin CRUD UI |
| `demo_result.py` — pre-computed results | Live agent run with persisted results |
| `pdf_parser.py` — pdfplumber only | pdfplumber + AWS Textract for scanned PDFs |
| `rfp_configs.py` — static RFP registry | Database-backed pursuit management |
| Streamlit UI | React + TypeScript frontend |
| No auth | Auth0 SSO + RBAC |
| No persistence | Postgres for all structured data, S3 for documents |
| No notifications | Slack + email via notification service |
| Single-process execution | SQS job queue + worker pool |
| No observability | Datadog logs, APM, LLM cost tracking |

---

*For questions on this spec, contact the PM. For prototype walkthroughs, run `streamlit run prototype/app.py`.*
