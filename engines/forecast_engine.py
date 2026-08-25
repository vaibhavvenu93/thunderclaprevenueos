from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from engines.deal_risk_engine import (
    RiskLevel,
    assess_deal_risk,
)
from engines.qualification_engine import (
    adjusted_probability,
)
from models.deal import (
    Deal,
    DealStage,
    ForecastCategory,
)


@dataclass
class ForecastSummary:
    open_deals: int

    raw_pipeline: float
    rep_weighted_forecast: float
    qualification_adjusted_forecast: float

    commit_pipeline: float
    likely_pipeline: float
    upside_pipeline: float

    revenue_at_risk: float
    high_risk_deals: int
    critical_risk_deals: int

    target_revenue: float
    pipeline_coverage: float

    forecast_gap: float
    forecast_attainment_pct: float

    forecast_confidence: float


def _is_open(deal: Deal) -> bool:
    return deal.stage not in {
        DealStage.CLOSED_WON,
        DealStage.CLOSED_LOST,
    }


def build_forecast(
    deals: list[Deal],
    target_revenue: float,
    today: date,
) -> ForecastSummary:
    """
    Build a qualification-adjusted revenue forecast.

    Rep-entered probabilities are preserved for comparison,
    but the Revenue OS independently discounts them based on
    qualification quality.

    Risk exposure is calculated separately so management can
    distinguish pipeline quantity from pipeline quality.
    """

    open_deals = [
        deal
        for deal in deals
        if _is_open(deal)
    ]

    raw_pipeline = 0.0
    rep_weighted_forecast = 0.0
    qualification_adjusted_forecast = 0.0

    commit_pipeline = 0.0
    likely_pipeline = 0.0
    upside_pipeline = 0.0

    revenue_at_risk = 0.0

    high_risk_deals = 0
    critical_risk_deals = 0

    qualification_scores: list[float] = []

    for deal in open_deals:
        raw_pipeline += deal.amount_usd

        rep_weighted_forecast += (
            deal.amount_usd
            * deal.probability
        )

        disciplined_probability = (
            adjusted_probability(deal)
        )

        qualification_adjusted_forecast += (
            deal.amount_usd
            * disciplined_probability
        )

        risk = assess_deal_risk(
            deal,
            today=today,
        )

        qualification_scores.append(
            risk.qualification_score
        )

        if (
            deal.forecast_category
            == ForecastCategory.COMMIT
        ):
            commit_pipeline += deal.amount_usd

        elif (
            deal.forecast_category
            == ForecastCategory.LIKELY
        ):
            likely_pipeline += deal.amount_usd

        elif (
            deal.forecast_category
            == ForecastCategory.UPSIDE
        ):
            upside_pipeline += deal.amount_usd

        if risk.risk_level == RiskLevel.HIGH:
            high_risk_deals += 1
            revenue_at_risk += deal.amount_usd

        elif (
            risk.risk_level
            == RiskLevel.CRITICAL
        ):
            critical_risk_deals += 1
            revenue_at_risk += deal.amount_usd

    if target_revenue > 0:
        pipeline_coverage = (
            raw_pipeline
            / target_revenue
        )

        forecast_attainment_pct = (
            qualification_adjusted_forecast
            / target_revenue
            * 100
        )

    else:
        pipeline_coverage = 0.0
        forecast_attainment_pct = 0.0

    forecast_gap = max(
        0.0,
        target_revenue
        - qualification_adjusted_forecast,
    )

    if qualification_scores:
        average_qualification = (
            sum(qualification_scores)
            / len(qualification_scores)
        )

        forecast_confidence = (
            average_qualification
            / 100
        )

    else:
        forecast_confidence = 0.0

    return ForecastSummary(
        open_deals=len(open_deals),

        raw_pipeline=round(
            raw_pipeline,
            2,
        ),

        rep_weighted_forecast=round(
            rep_weighted_forecast,
            2,
        ),

        qualification_adjusted_forecast=round(
            qualification_adjusted_forecast,
            2,
        ),

        commit_pipeline=round(
            commit_pipeline,
            2,
        ),

        likely_pipeline=round(
            likely_pipeline,
            2,
        ),

        upside_pipeline=round(
            upside_pipeline,
            2,
        ),

        revenue_at_risk=round(
            revenue_at_risk,
            2,
        ),

        high_risk_deals=high_risk_deals,
        critical_risk_deals=critical_risk_deals,

        target_revenue=round(
            target_revenue,
            2,
        ),

        pipeline_coverage=round(
            pipeline_coverage,
            2,
        ),

        forecast_gap=round(
            forecast_gap,
            2,
        ),

        forecast_attainment_pct=round(
            forecast_attainment_pct,
            2,
        ),

        forecast_confidence=round(
            forecast_confidence,
            2,
        ),
    )
