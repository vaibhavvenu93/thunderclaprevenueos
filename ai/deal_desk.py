from __future__ import annotations

import os
from typing import List

from openai import OpenAI

from engines.deal_risk_engine import DealRiskAssessment
from models.deal import Deal


MODEL = "gpt-5.6-luna"


def _build_deal_context(
    deal: Deal,
    assessment: DealRiskAssessment,
) -> str:
    risk_reasons = "\n".join(
        f"- {reason}"
        for reason in assessment.risk_reasons
    )

    return f"""
DEAL
Deal ID: {deal.deal_id}
Deal name: {deal.deal_name}
Value: ${deal.amount_usd:,.0f}
Stage: {deal.stage.value}
Owner: {deal.owner}

FORECAST
Rep probability: {deal.probability:.0%}
OS probability: {assessment.adjusted_probability:.0%}
Qualification score: {assessment.qualification_score:.0f}/100
Health score: {assessment.health_score:.0f}/100
Risk level: {assessment.risk_level.value}

OPERATING STATE
Days in stage: {deal.days_in_stage}
Last meaningful activity: {deal.last_meaningful_activity_date}
Next meeting: {deal.next_meeting_date or "Not scheduled"}
Proposal sent: {deal.proposal_sent_date or "Not sent"}
Primary objection: {deal.primary_objection or "None recorded"}
Founder involved: {deal.founder_involved}

RISK SIGNALS
{risk_reasons or "- No material risk signals"}

CURRENT SYSTEM RECOMMENDATION
Action: {assessment.recommended_action.value}
Reason: {assessment.action_reason}
SLA: {assessment.sla}
"""


def analyse_deal(
    deal: Deal,
    assessment: DealRiskAssessment,
) -> str:
    """
    Use an LLM to produce an executive deal diagnosis.

    The deterministic Revenue OS remains the source of truth
    for scoring. AI is used for interpretation and action design.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=api_key,
    )

    context = _build_deal_context(
        deal,
        assessment,
    )

    prompt = f"""
You are the AI Deal Desk inside a B2B agency Revenue Operating System.

Your job is not to repeat CRM data.

Act like an exceptional Head of Sales reviewing a deal with the founder.

Use ONLY the supplied synthetic deal information.
Do not invent customer facts.

Produce a concise management-quality analysis with exactly these sections:

## Executive Diagnosis
2-3 sentences. What is actually happening with this deal?

## Why I Do Not Fully Trust The Forecast
Explain the largest gap between the rep view and evidence.

## What I Would Do Next
Give exactly 3 concrete actions in priority order.

## Founder Involvement
State whether founder involvement is needed and why.

## Questions We Still Need Answered
Give the 3 most important missing pieces of information.

## Recommended Management Forecast
Give one recommended probability percentage and a one-sentence explanation.

DEAL CONTEXT

{context}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    return response.output_text


def build_close_plan(
    deal: Deal,
    assessment: DealRiskAssessment,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=api_key,
    )

    context = _build_deal_context(
        deal,
        assessment,
    )

    prompt = f"""
You are building a practical close plan for a B2B agency opportunity.

Use only the supplied deal information.
Do not fabricate buyer names, meetings or commitments.

Return:

## Close Objective
One sentence.

## Next 48 Hours
Exactly 3 actions.

## Stakeholder Plan
Who needs to be reached or identified based on the known gaps?

## Commercial Risk
What needs resolving commercially?

## Decision Path
What should happen before this deal can genuinely move into Commit?

## Kill Criteria
Give 2 signals that should cause management to reduce probability or remove the deal from forecast.

DEAL CONTEXT

{context}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    return response.output_text


def draft_follow_up(
    deal: Deal,
    assessment: DealRiskAssessment,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=api_key,
    )

    context = _build_deal_context(
        deal,
        assessment,
    )

    prompt = f"""
Draft a short B2B sales follow-up email for this opportunity.

Important:
- Do not invent customer facts.
- Do not pretend a conversation happened if it is not in the context.
- Keep it human.
- No sales clichés.
- No fake urgency.
- Goal is to reopen momentum and secure a concrete next step.
- Maximum 140 words.

Return only:

Subject: ...

Email body

DEAL CONTEXT

{context}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    return response.output_text
