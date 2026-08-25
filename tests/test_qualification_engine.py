from datetime import date

from engines.qualification_engine import (
    adjusted_probability,
    assess_qualification,
)
from models.deal import (
    Deal,
    DealSource,
    DealStage,
    ForecastCategory,
    ServiceLine,
)
from models.qualification import Qualification


def build_deal(
    qualification: Qualification,
    probability: float = 0.70,
) -> Deal:
    return Deal(
        deal_id="TC-QUAL-001",
        account_id="ACC-001",
        deal_name="Synthetic Enterprise Website Deal",
        stage=DealStage.PROPOSAL,
        forecast_category=ForecastCategory.UPSIDE,
        service_line=ServiceLine.WEBSITE_AND_BRAND,
        source=DealSource.INBOUND,
        amount_usd=72000,
        probability=probability,
        owner="AE-01",
        created_date=date(2026, 7, 1),
        expected_close_date=date(2026, 9, 30),
        last_meaningful_activity_date=date(2026, 8, 20),
        proposal_sent_date=date(2026, 8, 18),
        days_in_stage=7,
        founder_involved=False,
        qualification=qualification,
    )


def test_strong_qualification_scores_high():
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

    assessment = assess_qualification(
        build_deal(qualification)
    )

    assert assessment.score == 100
    assert assessment.grade == "A"
    assert assessment.forecast_multiplier == 1.0
    assert assessment.missing_signals == []


def test_weak_qualification_scores_low():
    qualification = Qualification(
        business_need_confirmed=True,
        champion_identified=True,
    )

    assessment = assess_qualification(
        build_deal(qualification)
    )

    assert assessment.score < 40
    assert assessment.grade == "F"
    assert assessment.forecast_multiplier == 0.35
    assert len(assessment.missing_signals) == 8


def test_missing_economic_buyer_is_visible():
    qualification = Qualification(
        budget_confirmed=True,
        authority_confirmed=True,
        business_need_confirmed=True,
        quantified_problem=True,
        timeline_confirmed=True,
        decision_process_known=True,
        procurement_process_known=True,
        champion_identified=True,
        success_criteria_defined=True,
    )

    assessment = assess_qualification(
        build_deal(qualification)
    )

    assert "Economic buyer identified" in assessment.missing_signals


def test_qualification_reduces_optimistic_probability():
    qualification = Qualification(
        business_need_confirmed=True,
        champion_identified=True,
    )

    deal = build_deal(
        qualification,
        probability=0.70,
    )

    probability = adjusted_probability(
        deal
    )

    assert probability < deal.probability
    assert probability == 0.245


def test_fully_qualified_deal_preserves_probability():
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

    deal = build_deal(
        qualification,
        probability=0.70,
    )

    assert adjusted_probability(deal) == 0.70
