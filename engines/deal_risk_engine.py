from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from engines.qualification_engine import assess_qualification
from models.deal import (
    Deal,
    DealStage,
    ForecastCategory,
)


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendedAction(str, Enum):
    HOLD = "HOLD"
    FOLLOW_UP = "FOLLOW_UP"
    MULTI_THREAD = "MULTI_THREAD"
    REQUALIFY = "REQUALIFY"
    DEAL_REVIEW = "DEAL_REVIEW"
    FOUNDER_ASSISTED_CLOSE = "FOUNDER_ASSISTED_CLOSE"
    COMMERCIAL_RESET = "COMMERCIAL_RESET"


@dataclass
class DealRiskAssessment:
    deal_id: str

    health_score: float
    risk_level: RiskLevel

    revenue_exposed: float

    primary_risk: str
    risk_reasons: list[str]

    recommended_action: RecommendedAction
    action_reason: str

    owner: str
    sla: str

    qualification_score: float
    adjusted_probability: float


def _days_since(
    earlier: date,
    today: date,
) -> int:
    return max(
        0,
        (today - earlier).days,
    )


def assess_deal_risk(
    deal: Deal,
    today: date,
) -> DealRiskAssessment:

    qualification = assess_qualification(
        deal
    )

    risk_points = 0.0
    risk_reasons: list[str] = []

    inactivity_days = _days_since(
        deal.last_meaningful_activity_date,
        today,
    )

    proposal_age = None

    if deal.proposal_sent_date is not None:
        proposal_age = _days_since(
            deal.proposal_sent_date,
            today,
        )

    # 1. Weak qualification
    if qualification.score < 40:
        risk_points += 25
        risk_reasons.append(
            "Qualification is materially incomplete."
        )

    elif qualification.score < 55:
        risk_points += 18
        risk_reasons.append(
            "Qualification quality is weak."
        )

    elif qualification.score < 70:
        risk_points += 10
        risk_reasons.append(
            "Qualification still has important gaps."
        )

    # 2. Deal inactivity
    if inactivity_days >= 10:
        risk_points += 25
        risk_reasons.append(
            f"No meaningful activity for {inactivity_days} days."
        )

    elif inactivity_days >= 6:
        risk_points += 16
        risk_reasons.append(
            f"Deal has been inactive for {inactivity_days} days."
        )

    elif inactivity_days >= 3:
        risk_points += 7
        risk_reasons.append(
            f"Deal has had no meaningful activity for {inactivity_days} days."
        )

    # 3. Proposal stall
    if (
        deal.stage == DealStage.PROPOSAL
        and proposal_age is not None
    ):
        if proposal_age >= 10:
            risk_points += 22
            risk_reasons.append(
                f"Proposal has been outstanding for {proposal_age} days."
            )

        elif proposal_age >= 6:
            risk_points += 14
            risk_reasons.append(
                f"Proposal has been open for {proposal_age} days."
            )

    # 4. Missing next meeting
    if (
        deal.stage
        in {
            DealStage.DISCOVERY,
            DealStage.SOLUTION,
            DealStage.PROPOSAL,
            DealStage.NEGOTIATION,
            DealStage.CONTRACT,
        }
        and deal.next_meeting_date is None
    ):
        risk_points += 14
        risk_reasons.append(
            "No committed next meeting is scheduled."
        )

    # 5. Excessive stage age
    if deal.days_in_stage >= 20:
        risk_points += 16
        risk_reasons.append(
            f"Deal has remained in stage for {deal.days_in_stage} days."
        )

    elif deal.days_in_stage >= 12:
        risk_points += 9
        risk_reasons.append(
            f"Stage age is elevated at {deal.days_in_stage} days."
        )

    # 6. Commercial objection
    if deal.primary_objection:
        risk_points += 6
        risk_reasons.append(
            f"Open objection: {deal.primary_objection}."
        )

    # 7. High-value deals deserve tighter scrutiny
    if deal.amount_usd >= 60000:
        risk_points += 6
        risk_reasons.append(
            "High-value opportunity requires tighter executive attention."
        )

    # 8. Forecast optimism penalty
    if (
        deal.forecast_category
        in {
            ForecastCategory.COMMIT,
            ForecastCategory.LIKELY,
        }
        and qualification.score < 70
    ):
        risk_points += 10
        risk_reasons.append(
            "Forecast category is aggressive relative to qualification quality."
        )

    health_score = max(
        0.0,
        100.0 - risk_points,
    )

    if risk_points >= 70:
        risk_level = RiskLevel.CRITICAL
    elif risk_points >= 45:
        risk_level = RiskLevel.HIGH
    elif risk_points >= 22:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW

    adjusted_probability = round(
        deal.probability
        * qualification.forecast_multiplier,
        4,
    )

    # Recommended action
    action = RecommendedAction.HOLD
    action_reason = (
        "No material intervention is required."
    )
    sla = "This week"

    if (
        deal.amount_usd >= 60000
        and risk_level
        in {
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        }
    ):
        action = (
            RecommendedAction.FOUNDER_ASSISTED_CLOSE
        )
        action_reason = (
            "High-value opportunity has material stall "
            "or qualification risk and deserves executive intervention."
        )
        sla = "Today"

    elif qualification.score < 40:
        action = RecommendedAction.REQUALIFY
        action_reason = (
            "Pipeline value should not be trusted until "
            "qualification gaps are resolved."
        )
        sla = "Within 24 hours"

    elif (
        deal.next_meeting_date is None
        and inactivity_days >= 4
    ):
        action = RecommendedAction.FOLLOW_UP
        action_reason = (
            "The deal has no committed next step and is beginning to stall."
        )
        sla = "Today"

    elif (
        qualification.score < 70
        and not deal.qualification.economic_buyer_identified
    ):
        action = RecommendedAction.MULTI_THREAD
        action_reason = (
            "Deal lacks economic-buyer coverage and should be multi-threaded."
        )
        sla = "Within 48 hours"

    elif risk_level == RiskLevel.MEDIUM:
        action = RecommendedAction.DEAL_REVIEW
        action_reason = (
            "Deal requires structured review before forecast confidence increases."
        )
        sla = "Within 48 hours"

    primary_risk = (
        risk_reasons[0]
        if risk_reasons
        else "No material risk detected."
    )

    revenue_exposed = (
        deal.amount_usd
        if risk_level
        in {
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        }
        else 0.0
    )

    return DealRiskAssessment(
        deal_id=deal.deal_id,

        health_score=round(
            health_score,
            2,
        ),

        risk_level=risk_level,

        revenue_exposed=round(
            revenue_exposed,
            2,
        ),

        primary_risk=primary_risk,
        risk_reasons=risk_reasons,

        recommended_action=action,
        action_reason=action_reason,

        owner=deal.owner,
        sla=sla,

        qualification_score=(
            qualification.score
        ),

        adjusted_probability=(
            adjusted_probability
        ),
    )
