from datetime import date

from engines.forecast_engine import build_forecast
from models.deal import (
    Deal,
    DealSource,
    DealStage,
    ForecastCategory,
    ServiceLine,
)
from models.qualification import Qualification


TODAY = date(2026, 8, 26)


def strong_qualification() -> Qualification:
    return Qualification(
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


def weak_qualification() -> Qualification:
    return Qualification(
        business_need_confirmed=True,
        champion_identified=True,
    )


def build_deal(
    deal_id: str,
    amount_usd: float,
    probability: float,
    forecast_category: ForecastCategory,
    qualification: Qualification,
    stage: DealStage = DealStage.PROPOSAL,
    last_activity: date = date(2026, 8, 24),
    proposal_sent: date = date(2026, 8, 22),
    next_meeting: date = date(2026, 8, 29),
    days_in_stage: int = 5,
) -> Deal:
    return Deal(
        deal_id=deal_id,
        account_id=f"ACC-{deal_id}",
        deal_name=f"Synthetic Deal {deal_id}",
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
        founder_involved=False,
        qualification=qualification,
    )


def test_forecast_counts_open_pipeline():
    deals = [
        build_deal(
            "TC-001",
            50000,
            0.70,
            ForecastCategory.COMMIT,
            strong_qualification(),
        ),
        build_deal(
            "TC-002",
            40000,
            0.50,
            ForecastCategory.UPSIDE,
            strong_qualification(),
        ),
    ]

    summary = build_forecast(
        deals,
        target_revenue=100000,
        today=TODAY,
    )

    assert summary.open_deals == 2
    assert summary.raw_pipeline == 90000


def test_qualification_adjusted_forecast_can_be_lower_than_rep_forecast():
    deals = [
        build_deal(
            "TC-003",
            100000,
            0.80,
            ForecastCategory.LIKELY,
            weak_qualification(),
            stage=DealStage.DISCOVERY,
            proposal_sent=None,
        )
    ]

    summary = build_forecast(
        deals,
        target_revenue=100000,
        today=TODAY,
    )

    assert (
        summary.qualification_adjusted_forecast
        < summary.rep_weighted_forecast
    )


def test_forecast_buckets_are_calculated():
    deals = [
        build_deal(
            "TC-004",
            60000,
            0.80,
            ForecastCategory.COMMIT,
            strong_qualification(),
        ),
        build_deal(
            "TC-005",
            50000,
            0.65,
            ForecastCategory.LIKELY,
            strong_qualification(),
        ),
        build_deal(
            "TC-006",
            40000,
            0.45,
            ForecastCategory.UPSIDE,
            strong_qualification(),
        ),
    ]

    summary = build_forecast(
        deals,
        target_revenue=150000,
        today=TODAY,
    )

    assert summary.commit_pipeline == 60000
    assert summary.likely_pipeline == 50000
    assert summary.upside_pipeline == 40000


def test_high_risk_deal_creates_revenue_at_risk():
    deals = [
        build_deal(
            "TC-007",
            75000,
            0.70,
            ForecastCategory.LIKELY,
            weak_qualification(),
            last_activity=date(2026, 8, 10),
            proposal_sent=date(2026, 8, 8),
            next_meeting=None,
            days_in_stage=20,
        )
    ]

    summary = build_forecast(
        deals,
        target_revenue=100000,
        today=TODAY,
    )

    assert summary.revenue_at_risk == 75000
    assert (
        summary.high_risk_deals
        + summary.critical_risk_deals
        >= 1
    )


def test_forecast_gap_is_calculated():
    deals = [
        build_deal(
            "TC-008",
            50000,
            0.50,
            ForecastCategory.UPSIDE,
            strong_qualification(),
        )
    ]

    summary = build_forecast(
        deals,
        target_revenue=100000,
        today=TODAY,
    )

    assert summary.forecast_gap > 0
    assert summary.forecast_attainment_pct < 100
