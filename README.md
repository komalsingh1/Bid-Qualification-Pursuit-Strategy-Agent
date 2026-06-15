# Opportunity Pursuit Agent


## The Problem

Enterprise proposal teams spend **200–500 person-hours** responding to RFPs before anyone knows whether the opportunity is worth pursuing. The go/no-bid decision happens too late, on gut feel, after real money has already been spent.

At 50 RFPs/year, a 30% win rate, and $150/hr loaded cost — that's **$2.5M annually in wasted effort** on bids you'll lose.

This agent compresses the decision from days to minutes and replaces intuition with evidence.

---

## What It Does

Upload an RFP. The agent runs 6 reasoning steps and returns:

| Output | What it answers |
|---|---|
| **Go / No-Go decision** | Should we bid? |
| **Bid score (0–100)** | How strong is our position? |
| **Gap action plan** | What are we missing, and who owns fixing it? |
| **Win themes** | What should we emphasise in the proposal? |
| **Submission checklist** | What must be done before deadline? |
| **Per-step confidence** | Where should a human review the agent's reasoning? |

---

## Demo

> Live at `http://localhost:8501` after setup.

![Agent execution trace with confidence scores](.github/demo.png)

The agent analyses 4 RFPs out of the box — including 3 real uploaded PDFs:

| RFP | Decision | Score | Key finding |
|---|---|---|---|
| California CDHS — Medicaid Platform | **CONDITIONAL BID** | 55/100 | FedRAMP in-progress is the risk |
| Hemisfair — AR App | **NO BID** | 22/100 | No AR capability; contract too small |
| DLC — Website Redesign | **NO BID** | 31/100 | Not a web design agency |
| MCCVB — Creative Agency | **NO BID** | 8/100 | Complete category mismatch |

---

## Architecture

```
RFP Document
     │
     ▼
┌─────────────────────────────────────────┐
│           Agent Loop (Claude)           │
│                                         │
│  BATCH 1 ── extract_requirements  ──┐  │
│          └── get_win_loss_history  ─┤  │  ← parallel
│                                     │  │
│  BATCH 2 ── check_capabilities  ───┤  │
│          └── get_sme_and_content ──┤  │  ← parallel
│                                     │  │
│  BATCH 3 ── identify_gaps  ─────────┤  │
│                                     │  │
│  BATCH 4 ── generate_recommendation ┘  │
└─────────────────────────────────────────┘
     │
     ▼
Bid Recommendation + Gap Plan + Checklist
```

**6 tools → 3 parallel API round trips → ~50% latency reduction vs sequential.**

Each step emits a confidence score. Any step below **80%** triggers automatic human escalation.

---

## Project Structure

```
opportunity_pursuit_agent/
│
├── prototype/
│   ├── agent.py          # Core agent loop — Claude tool use, parallel execution
│   ├── tools.py          # 6 tool definitions + implementations
│   ├── mock_data.py      # Capability KB, win/loss history, SME directory, proposal library
│   ├── pdf_parser.py     # PDF text extraction (pdfplumber)
│   ├── rfp_configs.py    # Per-RFP metadata and pre-computed demo results
│   ├── demo_result.py    # Pre-computed result for CDHS sample (demo mode)
│   └── app.py            # Streamlit UI
│
├── eval/
│   ├── ground_truth.py   # Expert-annotated correct answers for 4 demo RFPs
│   ├── metrics.py        # 9 eval metrics + weighted composite scorer
│   ├── runner.py         # Eval runner — demo or live mode, CLI output
│   ├── report_generator.py # Generates eval_report.html
│   │
│   └── test_set/
│       ├── rfp_texts.py      # 8 synthetic RFPs (BID / CONDITIONAL / NO BID mix)
│       ├── ground_truth.py   # Expert annotations for all 8 test cases
│       └── run_test_set.py   # Test set runner — heuristic or live Claude
│
├── spec.md               # Full engineering handoff specification
├── workflow_diagram.html # Interactive workflow diagram
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Install dependencies

```bash
pip install anthropic streamlit pdfplumber
```

### 2. Run in demo mode (no API key needed)

```bash
cd prototype
streamlit run app.py
```

Opens at `http://localhost:8501`. Animates the agent execution with pre-computed results.

### 3. Run with live Claude (API key required)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
cd prototype
streamlit run app.py
```

The agent calls Claude Sonnet in real time, reads the actual RFP text, and reasons over it.

---

## Agent Tools

| Tool | What it does | Production replacement |
|---|---|---|
| `extract_requirements` | Parse RFP into mandatory / scored / compliance / team requirements | LLM call over raw document |
| `check_capabilities` | Match requirements against internal KB | Vector search (pgvector) |
| `get_win_loss_history` | Retrieve similar past opportunities | CRM API (Salesforce / HubSpot) |
| `identify_gaps` | Classify gaps by severity: BLOCKING / HIGH / MEDIUM / LOW | Diff engine over KB results |
| `get_sme_and_content` | Assign SME owners + find reusable proposal content | HRIS + SharePoint search |
| `generate_recommendation` | Synthesise all evidence into bid score + action plan | LLM synthesis call |

---

## Evaluation

The eval framework scores agent outputs across 9 metrics with expert-annotated ground truth.

```bash
# Score the demo results
cd eval
python3 runner.py

# Generate HTML report
python3 report_generator.py
# → opens eval/eval_report.html

# Run against the 8-case test set (heuristic mode, no API key)
cd eval/test_set
python3 run_test_set.py

# Run against the 8-case test set (live Claude)
export ANTHROPIC_API_KEY=sk-ant-...
python3 run_test_set.py
```

### Metrics

| Metric | Weight | What it catches |
|---|---|---|
| Decision accuracy | 25% | Wrong go/no-bid call |
| Blocking gap recall | 20% | Missed disqualifying requirements |
| Gap recall | 15% | Incomplete gap identification |
| Gap precision | 10% | Hallucinated gaps |
| Score range accuracy | 10% | Miscalibrated bid scores |
| Win theme relevance | 8% | Wrong proposal emphasis |
| Checklist completeness | 7% | Missing pre-submission actions |
| Confidence calibration | 3% | Poorly calibrated uncertainty |
| Escalation correctness | 2% | Human-in-loop misfires |

### Test set design

8 synthetic RFPs designed to stress different failure modes:

| Case | Expected | Tests |
|---|---|---|
| TC-01 NY Medicaid Analytics | BID | Strong match recognition |
| TC-02 CMS Federal Platform | NO BID | FedRAMP HIGH blocking |
| TC-03 Colorado Care Management | CONDITIONAL BID | Partial gap handling |
| TC-04 Texas Population Health | BID | Incumbent advantage |
| TC-05 Brand & Marketing Agency | NO BID | Category mismatch |
| TC-06 Massachusetts Behavioral Health | CONDITIONAL BID | Domain specialization gap |
| TC-07 Chicago Community Health | BID | Small contract, good fit |
| TC-08 VA Veterans Platform | NO BID | Multiple federal blockers |



---

## Key Design Decisions

**Why agentic, not a simple AI feature?**
A summary of the RFP is not a decision. The agent has to simultaneously reason over the RFP requirements, the company's capability gaps, historical win/loss patterns, and available SMEs — then synthesise all of that into a structured recommendation with owners and deadlines. No single prompt or retrieval step can do this.

**Why parallel tool execution?**
`extract_requirements` and `get_win_loss_history` have no dependency on each other. Running them sequentially wastes time. The agent loop uses `ThreadPoolExecutor` to fan out independent tool calls, reducing round trips from 6 to 3.

**Why per-step confidence scores?**
The hardest problem in agentic AI is knowing when not to trust the agent. Confidence scores make the agent's uncertainty explicit and trigger human review automatically when a step scores below 80%. This is how you get adoption from teams that are sceptical of AI.

**Why a human-in-loop escalation?**
An agent that always gives an answer is dangerous. The escalation path lets the system say *"I found something but I'm not sure — a human should look at this before we commit."* That's not a fallback; it's the feature.

---

## Engineering Handoff

See [`spec.md`](spec.md) for the full production specification including:

- Functional and non-functional requirements (60+ requirements, P0/P1/P2)
- System architecture diagram and component breakdown
- Data models (Pydantic schemas for all entities)
- REST + WebSocket API contracts
- Integration specs (CRM, SharePoint, HRIS, Slack)
- Phased rollout plan (3 phases, 16 weeks)
- Prototype → production delta table

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Claude Sonnet (`claude-sonnet-4-6`) via Anthropic SDK |
| Agent pattern | Tool use with parallel fan-out |
| UI | Streamlit (prototype) → React + TypeScript (production) |
| PDF parsing | pdfplumber + AWS Textract (production) |
| Vector search | pgvector on Postgres (production) |
| Job queue | AWS SQS (production) |
| Auth | Auth0 / Okta OIDC + RBAC (production) |

---

## What's Mocked vs Real

| Prototype component | What it is | Production replacement |
|---|---|---|
| `mock_data.py` | Hardcoded capability KB and win/loss records | Postgres + pgvector, live CRM |
| `demo_result.py` | Pre-computed outputs | Live agent run, persisted to DB |
| `pdf_parser.py` | pdfplumber only | + AWS Textract for scanned PDFs |
| Streamlit UI | Rapid prototype | React + TypeScript |
| No auth | Anyone can access | Auth0 SSO + RBAC |
| No persistence | Results lost on restart | Postgres + S3 |
| No notifications | Silent | Slack + email SME alerts |

---

## Running the Eval

```
eval/
├── ground_truth.py       ← expert annotations (written before running agent)
├── metrics.py            ← 9 scorers + weighted composite
├── runner.py             ← runs eval, prints CLI report
├── report_generator.py   ← generates eval_report.html
└── test_set/
    ├── rfp_texts.py      ← 8 realistic synthetic RFPs
    ├── ground_truth.py   ← independent expert annotations
    └── run_test_set.py   ← test runner (heuristic + live modes)
```


---
