from datetime import date

from data.synthetic_pipeline import load_synthetic_pipeline
from engines.deal_risk_engine import (
    RiskLevel,
    assess_deal_risk,
)
from engines.forecast_engine import build_forecast
from models.deal import DealSource


TODAY = date(2026, 8, 26)

# Illustrative management target for the synthetic scenario.
TARGET_REVENUE = 750000


def money(value: float) -> str:
    return f"${value:,.0f}"


def divider(character: str = "-", width: int = 72) -> None:
    print(character * width)


def main() -> None:
    deals = load_synthetic_pipeline()

    forecast = build_forecast(
        deals,
        target_revenue=TARGET_REVENUE,
        today=TODAY,
    )

    assessments = [
        (
            deal,
            assess_deal_risk(
                deal,
                today=TODAY,
            ),
        )
        for deal in deals
    ]

    # --------------------------------------------------
    # MANAGEMENT METRICS
    # --------------------------------------------------

    optimism_gap = max(
        0.0,
        forecast.rep_weighted_forecast
        - forecast.qualification_adjusted_forecast,
    )

    founder_pipeline = sum(
        deal.amount_usd
        for deal in deals
        if deal.founder_involved
        or deal.owner == "Founder"
    )

    founder_deals = sum(
        1
        for deal in deals
        if deal.founder_involved
        or deal.owner == "Founder"
    )

    expansion_pipeline = sum(
        deal.amount_usd
        for deal in deals
        if deal.source == DealSource.EXISTING_ACCOUNT
    )

    expansion_deals = sum(
        1
        for deal in deals
        if deal.source == DealSource.EXISTING_ACCOUNT
    )

    risky = [
        (deal, assessment)
        for deal, assessment in assessments
        if assessment.risk_level
        in {
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        }
    ]

    risky.sort(
        key=lambda item: (
            item[1].risk_level == RiskLevel.CRITICAL,
            item[0].amount_usd,
        ),
        reverse=True,
    )

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    print()
    print("THUNDERCLAP — SYNTHETIC REVENUE INTELLIGENCE")
    divider("=")

    print(
        "Question: What should management believe, "
        "where is revenue at risk, and what needs action?"
    )

    # --------------------------------------------------
    # PIPELINE
    # --------------------------------------------------

    print()
    print("PIPELINE")
    divider()

    print(
        f"Open opportunities:                  "
        f"{forecast.open_deals}"
    )

    print(
        f"Raw pipeline:                        "
        f"{money(forecast.raw_pipeline)}"
    )

    print(
        f"Rep-weighted forecast:               "
        f"{money(forecast.rep_weighted_forecast)}"
    )

    print(
        f"Qualification-adjusted forecast:     "
        f"{money(forecast.qualification_adjusted_forecast)}"
    )

    print(
        f"Forecast optimism gap:               "
        f"{money(optimism_gap)}"
    )

    # --------------------------------------------------
    # TARGET
    # --------------------------------------------------

    print()
    print("TARGET & COVERAGE")
    divider()

    print(
        f"Illustrative revenue target:         "
        f"{money(forecast.target_revenue)}"
    )

    print(
        f"Raw pipeline coverage:               "
        f"{forecast.pipeline_coverage:.2f}x"
    )

    print(
        f"Believable forecast attainment:      "
        f"{forecast.forecast_attainment_pct:.1f}%"
    )

    print(
        f"Forecast gap:                        "
        f"{money(forecast.forecast_gap)}"
    )

    print(
        f"Forecast confidence:                 "
        f"{forecast.forecast_confidence:.0%}"
    )

    # --------------------------------------------------
    # FORECAST CATEGORIES
    # --------------------------------------------------

    print()
    print("FORECAST MIX")
    divider()

    print(
        f"Commit pipeline:                     "
        f"{money(forecast.commit_pipeline)}"
    )

    print(
        f"Likely pipeline:                     "
        f"{money(forecast.likely_pipeline)}"
    )

    print(
        f"Upside pipeline:                     "
        f"{money(forecast.upside_pipeline)}"
    )

    # --------------------------------------------------
    # RISK
    # --------------------------------------------------

    print()
    print("REVENUE RISK")
    divider()

    print(
        f"Revenue at risk:                     "
        f"{money(forecast.revenue_at_risk)}"
    )

    print(
        f"High-risk opportunities:             "
        f"{forecast.high_risk_deals}"
    )

    print(
        f"Critical opportunities:              "
        f"{forecast.critical_risk_deals}"
    )

    # --------------------------------------------------
    # MANAGEMENT INTERVENTIONS
    # --------------------------------------------------

    print()
    print("TOP MANAGEMENT INTERVENTIONS")
    divider()

    if not risky:
        print("No high or critical interventions detected.")

    else:
        for rank, (deal, assessment) in enumerate(
            risky[:7],
            start=1,
        ):
            print()
            print(
                f"#{rank} — {deal.deal_name}"
            )

            print(
                f"Deal: {deal.deal_id} | "
                f"Value: {money(deal.amount_usd)} | "
                f"Risk: {assessment.risk_level.value}"
            )

            print(
                f"Health score: "
                f"{assessment.health_score:.0f}/100"
            )

            print(
                f"Qualification score: "
                f"{assessment.qualification_score:.0f}/100"
            )

            print(
                f"Rep probability: "
                f"{deal.probability:.0%}"
            )

            print(
                f"Adjusted probability: "
                f"{assessment.adjusted_probability:.0%}"
            )

            print(
                f"Primary risk: "
                f"{assessment.primary_risk}"
            )

            print(
                f"Recommended action: "
                f"{assessment.recommended_action.value}"
            )

            print(
                f"Why: {assessment.action_reason}"
            )

            print(
                f"Owner: {assessment.owner} | "
                f"SLA: {assessment.sla}"
            )

    # --------------------------------------------------
    # FOUNDER DEPENDENCY
    # --------------------------------------------------

    print()
    print("FOUNDER DEPENDENCY")
    divider()

    print(
        f"Founder-owned / involved deals:      "
        f"{founder_deals}"
    )

    print(
        f"Founder-dependent pipeline:          "
        f"{money(founder_pipeline)}"
    )

    if forecast.raw_pipeline > 0:
        founder_share = (
            founder_pipeline
            / forecast.raw_pipeline
            * 100
        )
    else:
        founder_share = 0.0

    print(
        f"Share of open pipeline:              "
        f"{founder_share:.1f}%"
    )

    # --------------------------------------------------
    # EXPANSION
    # --------------------------------------------------

    print()
    print("EXISTING-ACCOUNT EXPANSION")
    divider()

    print(
        f"Expansion opportunities:             "
        f"{expansion_deals}"
    )

    print(
        f"Expansion pipeline:                  "
        f"{money(expansion_pipeline)}"
    )

    # --------------------------------------------------
    # MANAGEMENT QUESTION
    # --------------------------------------------------

    print()
    print("MANAGEMENT QUESTION")
    divider()

    print(
        "Which deals should we rescue, which forecast "
        "assumptions should we challenge, and where should "
        "the founders spend their next hour?"
    )

    print()
    print(
        "NOTE: All companies, opportunities, pipeline values "
        "and operating assumptions are synthetic."
    )
    print(
        "This project demonstrates revenue decision "
        "architecture, not ThunderClap's actual CRM data."
    )
    print()


if __name__ == "__main__":
    main()
