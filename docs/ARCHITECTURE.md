# ThunderClap Revenue OS — System Architecture

## 1. Purpose

ThunderClap Revenue OS is an outside-in prototype of a revenue intelligence and orchestration layer for a founder-led B2B sales organisation.

The system is designed around four management questions:

1. What should we believe about the pipeline?
2. What changed?
3. What requires attention?
4. What should happen next?

The CRM remains the system of record.

The Revenue OS sits above operational systems to become a **system of intelligence and action**.

---

## 2. Architecture Principles

The prototype follows five principles.

### Explainable before intelligent

Qualification, risk and forecast logic should be inspectable.

An operator should be able to understand why the system changed a probability or surfaced an opportunity.

### Signals before dashboards

The objective is not to create more reporting.

The system converts commercial activity into signals that affect decisions.

### Human-in-the-loop execution

AI can analyse, classify and draft.

External actions such as customer communication should remain human-approved.

### Canonical data model

CRM, email, meeting and activity data should ultimately map into a common representation of the opportunity.

This prevents business logic from becoming dependent on a specific CRM.

### Modular intelligence

Qualification, risk, forecasting, communication intelligence and automation should remain separate modules.

This makes the system easier to test and evolve.

---

## 3. High-Level Architecture

```text
┌─────────────────────────────────────────────┐
│                 DATA SOURCES                │
│                                             │
│ CRM     Gmail     Calendar     Meetings     │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│               INGESTION LAYER               │
│                                             │
│ Deals • Emails • Meetings • Activities      │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│              CANONICAL MODELS               │
│                                             │
│ Deal • Activity • Commercial Evidence       │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│             INTELLIGENCE ENGINES            │
│                                             │
│ Qualification                               │
│ Deal Risk                                   │
│ Forecast                                    │
│ Momentum                                    │
│ Communication Signals                       │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│            ORCHESTRATION LAYER              │
│                                             │
│ Prioritise • Recommend • Escalate • Route   │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│            MANAGEMENT EXPERIENCE            │
│                                             │
│ Overview                                    │
│ Action Queue                                │
│ Pipeline Truth                              │
│ Deal Room                                   │
│ Inbox Intelligence                          │
│ Meeting Intelligence                        │
│ Activity Feed                               │
│ Revenue Digital Twin                        │
└─────────────────────────────────────────────┘
```

---

## 4. Repository Architecture

```text
thunderclaprevenueos/
│
├── app/
│   └── command_center.py
│
├── ai/
│   ├── __init__.py
│   └── deal_desk.py
│
├── data/
│   ├── synthetic_pipeline.py
│   └── synthetic_activity.py
│
├── engines/
│   ├── qualification_engine.py
│   ├── deal_risk_engine.py
│   └── forecast_engine.py
│
├── models/
│   └── deal.py
│
├── tests/
│
├── docs/
│   └── ARCHITECTURE.md
│
├── requirements.txt
├── revenue_report.py
└── README.md
```

The important separation is:

```text
DATA
  ↓
MODELS
  ↓
ENGINES
  ↓
ORCHESTRATION
  ↓
APPLICATION
```

The UI does not need to own the underlying revenue logic.

---

## 5. Canonical Deal Model

The deal model provides a common representation of an opportunity.

It contains commercial attributes such as:

- account;
- deal value;
- stage;
- owner;
- probability;
- source;
- qualification evidence;
- activity dates;
- next meeting;
- objections;
- proposal status;
- founder involvement.

The long-term objective is for upstream systems to map into this canonical representation.

For example:

```text
HubSpot Deal ──────┐
                   │
Salesforce Opp ────┼──→ Canonical Deal → Revenue Engines
                   │
Other CRM ─────────┘
```

This allows the intelligence layer to remain CRM-agnostic.

---

## 6. Activity Model

Revenue does not move because a CRM field changes.

It moves because something happened.

The activity layer therefore represents events such as:

```text
EMAIL_INBOUND
EMAIL_OUTBOUND
MEETING
CRM_UPDATE
AUTOMATION
```

Each event can contain:

- opportunity association;
- timestamp;
- summary;
- signal type;
- extracted commercial signals;
- recommended action;
- transcript;
- sender / recipient;
- automation source.

This creates an event stream around each opportunity.

---

## 7. Qualification Engine

The qualification engine converts evidence into an explicit qualification score.

Instead of trusting stage or rep probability alone, the system evaluates whether sufficient commercial evidence exists.

Conceptually:

```text
Need
+
Budget
+
Authority
+
Timeline
+
Decision Process
+
Next Step
        ↓
Qualification Score
```

The purpose is not to enforce one specific sales methodology.

The purpose is to distinguish:

**CRM confidence**

from:

**evidence-backed confidence.**

---

## 8. Deal Risk Engine

The Deal Risk Engine evaluates whether an opportunity requires intervention.

Signals can include:

- poor qualification;
- excessive stage ageing;
- inactivity;
- missing next meeting;
- unresolved objection;
- forecast optimism;
- missing decision evidence;
- high-value exposure.

The engine produces outputs such as:

```text
Risk Level
Health Score
Adjusted Probability
Primary Risk
Recommended Action
Action Owner
SLA
```

This converts opportunity data into management intervention.

---

## 9. Forecast Engine

The forecast engine separates two concepts.

### Rep-weighted forecast

```text
Deal Value × Rep Probability
```

### Qualification-adjusted forecast

```text
Deal Value × Evidence-adjusted Probability
```

The difference becomes:

```text
OPTIMISM GAP
=
REP FORECAST
-
OS FORECAST
```

This creates a mechanism for management to challenge forecast assumptions systematically.

The goal is not to prove that the rep is wrong.

The goal is to expose where the forecast requires discussion.

---

## 10. Action Orchestration

Revenue intelligence becomes useful only when it creates action.

The system therefore converts risk and commercial signals into an operating queue.

Conceptually:

```text
Signal
  ↓
Evaluate
  ↓
Prioritise
  ↓
Assign Owner
  ↓
Set SLA
  ↓
Execute
  ↓
Observe New Signal
```

Examples:

```text
No next meeting
        ↓
Follow-up SLA Guard
        ↓
AE action within 24 hours
```

```text
High-value + critical risk
        ↓
Founder Escalation Engine
        ↓
Executive intervention
```

```text
Existing customer expresses new need
        ↓
Expansion Radar
        ↓
Expansion opportunity
```

---

## 11. Inbox Intelligence Architecture

In a production system, customer communication becomes another source of commercial evidence.

```text
Gmail / Microsoft 365
          ↓
    Email Ingestion
          ↓
 Thread / Deal Matching
          ↓
 Signal Classification
          ↓
┌───────────────────────────┐
│ Buying Intent             │
│ Objection                 │
│ Budget                    │
│ Delay                     │
│ Stakeholder Engagement    │
│ Procurement               │
│ Next Step                 │
└───────────────────────────┘
          ↓
      Deal State
          ↓
 Revenue Engines Re-run
          ↓
     Action Queue
```

The current prototype demonstrates this flow with synthetic email activity.

No live mailbox is connected.

---

## 12. Meeting Intelligence Architecture

Meetings contain information that CRM fields often fail to capture.

The proposed workflow is:

```text
Calendar
   ↓
Meeting
   ↓
Transcript / Notes
   ↓
Signal Extraction
   ↓
┌───────────────────────────┐
│ Need                      │
│ Budget                    │
│ Authority                 │
│ Timeline                  │
│ Objections                │
│ Competitors               │
│ Decision Process          │
│ Next Steps                │
└───────────────────────────┘
   ↓
Qualification Update
   ↓
Risk Recalculation
   ↓
Forecast Recalculation
   ↓
Recommended Action
```

The current prototype uses synthetic meeting transcripts to demonstrate this operating model.

---

## 13. AI Layer

The architecture deliberately does not make an LLM responsible for the entire Revenue OS.

Deterministic business logic remains responsible for core scoring.

AI is best used where interpretation of unstructured information adds value.

Examples include:

- meeting summarisation;
- commercial signal extraction;
- email classification;
- objection extraction;
- close-plan generation;
- follow-up drafting;
- management briefs;
- coaching recommendations.

The intended architecture is:

```text
STRUCTURED DATA
      ↓
DETERMINISTIC ENGINES
      ↓
REVENUE STATE
      +
UNSTRUCTURED CONTEXT
      ↓
AI INTERPRETATION
      ↓
RECOMMENDATION
      ↓
HUMAN APPROVAL
```

The repository contains the beginning of an AI Deal Desk layer, while live model connectivity is intentionally deferred in the current deployed prototype.

---

## 14. Integration Layer

A production system could connect to:

### CRM

Examples:

- HubSpot;
- Salesforce;
- another CRM through an adapter.

Purpose:

```text
Read deal state
      ↓
Run intelligence
      ↓
Write approved updates
```

### Gmail / Microsoft 365

Purpose:

- ingest deal-related communication;
- identify response gaps;
- classify commercial signals;
- generate follow-up drafts.

### Google Calendar / Microsoft Calendar

Purpose:

- detect meetings;
- associate meetings with opportunities;
- validate next-step commitments;
- calculate momentum.

### Meeting Platforms / Transcript Providers

Purpose:

- ingest transcripts;
- extract qualification evidence;
- detect objections and stakeholders;
- generate follow-up actions.

### Slack / Teams

Purpose:

- management alerts;
- founder escalation;
- daily revenue briefs;
- urgent deal notifications.

---

## 15. Automation Architecture

The automation layer follows an event-driven model.

```text
EVENT
  ↓
RULE / SIGNAL
  ↓
CONDITION
  ↓
ACTION
```

Examples:

### Deal Stall Monitor

```text
No meaningful activity
+
Stage ageing threshold exceeded
        ↓
Create intervention
```

### Forecast Truth Engine

```text
High rep probability
+
Weak qualification
        ↓
Challenge forecast
```

### Founder Escalation

```text
Large opportunity
+
Critical risk
        ↓
Route to founder
```

### Expansion Radar

```text
Existing customer
+
New commercial intent
        ↓
Create expansion action
```

---

## 16. Human Approval Layer

A production implementation should not automatically send every generated action externally.

For high-impact actions:

```text
AI / Automation
      ↓
Draft
      ↓
Human Review
      ↓
Approve / Edit / Reject
      ↓
Execute
```

This is particularly important for:

- customer email;
- pricing changes;
- CRM stage movement;
- forecast overrides;
- executive escalation.

---

## 17. Revenue Digital Twin

The Revenue Digital Twin models how operating assumptions translate into revenue.

Inputs include:

```text
Average Contract Value
Qualified Opportunity Volume
Win Rate
AE Count
AE Capacity
Expansion Contribution
```

Outputs include:

```text
Modeled Revenue
Required Wins
Required Opportunities
Capacity Requirement
Revenue Shortfall / Surplus
```

This allows management to test questions such as:

> Can the current sales organisation support the revenue target?

> Does the business need more pipeline or better conversion?

> What happens if ACV increases?

> How much does expansion matter?

---

## 18. Testing Strategy

Core revenue logic is tested independently of the Streamlit interface.

This matters because UI behaviour should not determine whether revenue calculations are correct.

Tests cover areas such as:

- deal validation;
- qualification behaviour;
- risk classification;
- probability adjustment;
- stalled opportunity detection;
- forecast calculations;
- revenue exposure.

The current suite can be executed with:

```bash
python3 -m pytest -v
```

---

## 19. Current Prototype Boundary

### Implemented

The current repository includes:

- canonical deal models;
- synthetic pipeline data;
- synthetic revenue activity;
- qualification logic;
- deal-risk logic;
- forecast logic;
- action prioritisation;
- pipeline truth;
- deal intelligence;
- inbox intelligence simulation;
- meeting intelligence simulation;
- activity feed;
- automation architecture;
- Revenue Digital Twin;
- integration architecture;
- automated tests;
- deployed Streamlit application.

### Not represented as live production integrations

The current prototype does **not** claim live connectivity to:

- ThunderClap CRM;
- ThunderClap Gmail;
- customer mailboxes;
- Google Calendar;
- Google Meet;
- Salesforce;
- HubSpot;
- Slack;
- live meeting recordings.

These are represented as architectural extension points.

---

## 20. Production Evolution

A production version would introduce several additional layers.

```text
Authentication
      ↓
Persistent Database
      ↓
Integration Workers
      ↓
Event Queue
      ↓
Revenue Engines
      ↓
LLM Services
      ↓
Workflow Orchestrator
      ↓
Approval Layer
      ↓
CRM / Email / Slack Actions
      ↓
Audit Log
```

Likely infrastructure would include:

- relational database;
- encrypted credential storage;
- OAuth integrations;
- background workers;
- job queues;
- webhook ingestion;
- API layer;
- observability;
- audit logging;
- role-based access control;
- retry and failure handling.

---

## 21. Design Trade-Offs

### Why synthetic data?

The application demonstrates operating logic without requiring access to private company systems.

### Why deterministic scoring first?

It makes management reasoning inspectable and testable.

### Why Streamlit?

The objective of this prototype is to test the operating concept quickly rather than optimise frontend infrastructure.

### Why separate models and engines?

It creates a foundation that could later sit behind another frontend or API.

### Why not connect every integration immediately?

The highest-value question at this stage is whether the operating model itself is useful.

Production authentication and integration work can follow once that is established.

---

## 22. Core Operating Loop

The architecture ultimately exists to support one loop:

```text
OBSERVE
   ↓
UNDERSTAND
   ↓
CHALLENGE
   ↓
PRIORITISE
   ↓
ACT
   ↓
LEARN
   └────────────→ OBSERVE
```

Or, in revenue terms:

```text
Something happened.
        ↓
What does it mean?
        ↓
Did our view of the deal change?
        ↓
Does the forecast change?
        ↓
Who needs to do what?
        ↓
Did it work?
```

That is the core architecture of ThunderClap Revenue OS.

---

## Disclaimer

ThunderClap Revenue OS is an independent application prototype.

The architecture is based on publicly available information, synthetic commercial data and my interpretation of the operating problem.

It does not contain confidential ThunderClap information and is not an official ThunderClap product.
