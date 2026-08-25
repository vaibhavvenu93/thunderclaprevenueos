## What I built

Rather than building another CRM dashboard, I approached the problem as a revenue operating system.

The system takes opportunity data and commercial activity, evaluates what management should actually believe about the pipeline, and converts that into actions.

```text
CRM Opportunities
       +
Email / Meetings / Activity
       ↓
Commercial Signals
       ↓
Qualification Engine
       ↓
Deal Risk + Momentum
       ↓
Forecast Intelligence
       ↓
Management Intervention
       ↓
Next Best Action
Product Modules
1. Executive Overview

A management command centre showing:

open pipeline;
believable forecast;
revenue exposed;
forecast optimism gap;
pipeline coverage;
highest-priority interventions;
founder-dependent revenue.

The goal is not simply to report what is in the CRM.

It is to answer:

What requires management attention right now?

2. Action Queue

Deals are ranked using signals such as:

deal value;
qualification quality;
inactivity;
stage ageing;
missing next steps;
forecast disagreement;
commercial risk.

Instead of asking management to inspect every opportunity, the system surfaces the deals where intervention matters most.

3. Pipeline Truth

Rep-entered probabilities are compared with qualification-adjusted probabilities.

This creates two views of the forecast:

Rep Forecast

What the CRM currently says.

OS Forecast

What the operating system believes after considering qualification and deal evidence.

The difference becomes the Optimism Gap.

This is designed to help management challenge forecast assumptions before committing to a revenue number.

4. Deal Room

Each opportunity gets a management-level view containing:

deal value;
health;
momentum;
qualification;
rep probability;
OS probability;
risk signals;
stage ageing;
objections;
next meeting status;
recommended next action.

The objective is to move from:

"What happened with this deal?"

to:

"Why is this deal at risk and what should we do next?"

5. Inbox Intelligence

Customer email conversations become revenue signals.

The prototype demonstrates how an inbox layer could detect:

buying signals;
unanswered conversations;
stakeholder engagement;
objections;
next-step confirmation;
existing-account momentum.

Those signals can then influence deal state and the management action queue.

6. Meeting Intelligence

Meeting transcripts or notes are converted into structured commercial evidence.

The system can represent signals such as:

business need;
budget resistance;
decision criteria;
stakeholder involvement;
objections;
next steps.

This creates the architecture for:

Meeting
   ↓
Transcript
   ↓
Commercial Signals
   ↓
Qualification Update
   ↓
Deal State
   ↓
Next Best Action
7. Activity Feed

Email, meetings, CRM events and machine-generated interventions are represented in one operating timeline.

This provides a single view of:

What happened → what changed → what the system recommends.

8. Automation Layer

The prototype also models the workflows that could sit behind the sales team, including:

deal stall monitoring;
follow-up SLAs;
qualification guards;
forecast challenges;
meeting follow-up;
management escalation.

The principle is simple:

Revenue operations should not depend on someone remembering every follow-up, stalled deal or forecast review.

9. Revenue Digital Twin

The Revenue Plan allows management to model combinations of:

average contract value;
qualified win rate;
qualified opportunities;
AE capacity;
opportunities per AE;
expansion contribution.

The model then estimates whether the operating system can support the stated revenue ambition.

This turns the revenue target into an operating model rather than just a number.

System Architecture

The current prototype separates the system into several layers:

┌──────────────────────────────────────┐
│           DATA SOURCES               │
│ CRM • Gmail • Calendar • Meetings    │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│          ACTIVITY LAYER              │
│ Email • Calls • Meetings • CRM       │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│        COMMERCIAL SIGNALS            │
│ Intent • Risk • Objections • Next    │
│ Steps • Stakeholders • Momentum      │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│       REVENUE INTELLIGENCE           │
│ Qualification • Risk • Forecast      │
│ Momentum • Deal Health               │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│        MANAGEMENT SYSTEM             │
│ Action Queue • Deal Room • Pipeline  │
│ Truth • Revenue Brief                │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│          ACTION LAYER                │
│ Follow-up • Escalation • CRM Update  │
│ Coaching • Automation                │
└──────────────────────────────────────┘
Repository Structure
thunderclaprevenueos/
│
├── app/
│   └── command_center.py
│
├── ai/
│   └── intelligence layer
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
├── requirements.txt
├── revenue_report.py
└── README.md

The architecture intentionally separates:

data → models → intelligence engines → application

so individual pieces can evolve without turning the application into one large script.

Engineering Approach

I deliberately kept the first version deterministic.

Qualification, risk and forecast calculations are implemented as explicit business logic rather than hiding the entire system behind an LLM.

This makes the underlying reasoning:

testable;
explainable;
inspectable;
easier to change.

An AI layer can then sit above those foundations for tasks where language models add genuine value:

transcript interpretation;
email classification;
objection extraction;
call summarisation;
follow-up drafting;
management briefs;
coaching recommendations.

This creates a hybrid architecture:

Deterministic Revenue Logic
            +
AI Interpretation
            +
Workflow Automation

rather than treating an LLM as the entire product.

Integration Architecture

The prototype includes an integration layer showing how the Revenue OS could connect to the tools a sales organisation already uses.

Gmail
Gmail
  ↓
Inbox Intelligence
  ↓
Commercial Signals
  ↓
Deal State
  ↓
Action Queue
Google Calendar
Calendar
  ↓
Meeting Detection
  ↓
Momentum / Next-Step Evidence
Meeting Transcripts
Transcript
  ↓
Meeting Intelligence
  ↓
Qualification + Objections + Stakeholders
  ↓
CRM Update
CRM

A production implementation could use HubSpot, Salesforce or another CRM as the system of record while the Revenue OS acts as the intelligence and orchestration layer above it.

These connectors are architecture-ready concepts in the current prototype and are not authenticated to ThunderClap systems.

Synthetic Data

All opportunity, account, contact, email, meeting and activity data in this repository is synthetic.

The synthetic dataset exists to demonstrate the operating logic without accessing private company systems.

The current simulation contains:

35 opportunities;
pipeline stages;
qualification evidence;
rep probabilities;
synthetic commercial activity;
email signals;
meeting transcripts;
objections;
stakeholder information;
automation events.
Tests

The revenue engines include automated tests covering core behaviour such as:

deal model validation;
qualification scoring;
risk detection;
stalled opportunities;
forecast adjustment;
revenue-at-risk calculations;
optimistic probability detection.

Run the test suite with:

python3 -m pytest -v
Running Locally

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app/command_center.py
Current Prototype vs Production System
Built in this prototype
synthetic CRM dataset;
canonical deal model;
qualification engine;
deal-risk engine;
forecast engine;
management action queue;
pipeline truth view;
deal intelligence;
synthetic inbox intelligence;
synthetic meeting intelligence;
unified activity feed;
automation concepts;
Revenue Digital Twin;
integration architecture;
automated tests;
deployed Streamlit application.
Production evolution

A production implementation would add:

authenticated CRM integration;
Gmail / Microsoft 365 ingestion;
Calendar integration;
meeting transcription ingestion;
persistent database;
background jobs;
event-driven workflows;
user authentication;
role-based permissions;
audit logs;
AI model integration;
approval gates before external actions;
production monitoring.
Design Principle

The system is intentionally designed around one management loop:

Observe
   ↓
Understand
   ↓
Challenge
   ↓
Prioritise
   ↓
Act
   ↓
Learn

The CRM remains the system of record.

The Revenue OS becomes the system that asks:

What should we believe?

What changed?

What needs attention?

What should happen next?

Why I Built This

I wanted the application itself to demonstrate how I think about the Head of Sales role.

Not simply:

sell more.

But build the operating system that makes selling more repeatable.

The hypothesis behind this project is that ThunderClap's next stage does not require more dashboards.

It requires a tighter connection between:

demand → qualification → execution → management intervention → forecast → revenue.

This prototype is my attempt to show what that system could begin to look like.

Disclaimer

This is an independent application exercise built from publicly available information and synthetic data.

It is not an official ThunderClap product and does not contain confidential ThunderClap information.
