from datetime import date
from typing import Optional

from engines.deal_risk_engine import (
    RecommendedAction,
    RiskLevel,
    assess_deal_risk,
)
from models.deal import (
    Deal,
    DealSource,
    DealStage,
    ForecastCategory,
    ServiceLine,
)
from models.qualification import Qualification


TODAY = date(2026, 8, 25)


def build_deal(
    *,
    amount_usd: float = 45000,
    probability: float = 0.60,
    stage: DealStage = DealStage.PROPOSAL,
    forecast_category: ForecastCategory = ForecastCategory.UPSIDE,
    last_activity: date = date(2026, 8, 23),
    proposal_sent: Optional[date] = date(2026, 8, 22),
    next_meeting: Optional[date] = date(2026, 8, 28),
    days_in_stage: int = 5,
    founder_involved: bool = False,
    primary_objection: Optional[str] = None,
    qualification: Optional[Qualification] = None,
) -> Deal:
    if qualification is None:
        qualification = Qualification(
            budget_confirmed=True,
            authority_confirmed=True,
            economic_buyer_identified=True,
            business_need_confirmed=True,
            quantified_problem=True,
            timeline_confirmed=True,
            decision_process_known=True,
            procurement_process_known=True,
            champion_identified=True,
            success_criteria_defined=True,
        )

    return Deal(
        deal_id="TC-RISK-001",
        account_id="ACC-RISK-001",
        deal_name="Synthetic Revenue Transformation",

        stage=stage,
        forecast_category=forecast_category,

        service_line=ServiceLine.WEBSITE_AND_BRAND,
        source=DealSource.INBOUND,

        amount_usd=amount_usd,
        probability=probability,

        owner="AE-01",

        created_date=date(2026, 7, 1),
        expected_close_date=date(2026, 9, 30),
        last_meaningful_activity_date=last_activity,

        next_meeting_date=next_meeting,
        proposal_sent_date=proposal_sent,

        days_in_stage=days_in_stage,

        founder_involved=founder_involved,

        qualification=qualification,

        primary_objection=primary_objection,
    )


def test_healthy_deal_is_low_risk():
    deal = build_deal()

    assessment = assess_deal_risk(
        deal,
        today=TODAY,
    )

    assert assessment.risk_level == RiskLevel.LOW
    assert assessment.revenue_exposed == 0
    assert (
        assessment.recommended_action
        == RecommendedAction.HOLD
    )


def test_stalled_high_value_proposal_gets_executive_action():
    deal = build_deal(
        amount_usd=72000,
        last_activity=date(2026, 8, 14),
        proposal_sent=date(2026, 8, 12),
        next_meeting=None,
        days_in_stage=15,
        primary_objection="Internal stakeholder alignment",
    )

    assessment = assess_deal_risk(
        deal,
        today=TODAY,
    )

    assert assessment.risk_level in {
        RiskLevel.HIGH,
        RiskLevel.CRITICAL,
    }

    assert assessment.revenue_exposed == 72000

    assert (
        assessment.recommended_action
        == RecommendedAction.FOUNDER_ASSISTED_CLOSE
    )

    assert assessment.sla == "Today"


def test_weakly_qualified_deal_is_requalified():
    qualification = Qualification(
        business_need_confirmed=True,
        champion_identified=True,
    )

    deal = build_deal(
        stage=DealStage.DISCOVERY,
        proposal_sent=None,
        qualification=qualification,
    )

    assessment = assess_deal_risk(
        deal,
        today=TODAY,
    )

    assert assessment.qualification_score < 40

    assert (
        assessment.recommended_action
        == RecommendedAction.REQUALIFY
    )


def test_missing_economic_buyer_can_trigger_multithreading():
    qualification = Qualification(
        budget_confirmed=True,
        authority_confirmed=True,
        business_need_confirmed=True,
        quantified_problem=True,
        timeline_confirmed=True,
        decision_process_known=False,
        procurement_process_known=False,
        champion_identified=True,
        success_criteria_defined=True,
    )

    deal = build_deal(
        stage=DealStage.DISCOVERY,
        proposal_sent=None,
        last_activity=date(2026, 8, 24),
        next_meeting=date(2026, 8, 29),
        qualification=qualification,
    )

    assessment = assess_deal_risk(
        deal,
        today=TODAY,
    )

    assert (
        assessment.recommended_action
        == RecommendedAction.MULTI_THREAD
    )


def test_adjusted_probability_reflects_qualification():
    qualification = Qualification(
        business_need_confirmed=True,
        champion_identified=True,
    )

    deal = build_deal(
        probability=0.80,
        stage=DealStage.DISCOVERY,
        proposal_sent=None,
        qualification=qualification,
    )

    assessment = assess_deal_risk(
        deal,
        today=TODAY,
    )

    assert assessment.adjusted_probability < 0.80
