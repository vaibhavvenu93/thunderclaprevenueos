from datetime import date

import streamlit as st

from data.synthetic_pipeline import load_synthetic_pipeline
from engines.deal_risk_engine import (
    RiskLevel,
    assess_deal_risk,
)
from engines.forecast_engine import build_forecast
from models.deal import DealSource


TODAY = date(2026, 8, 26)
TARGET_REVENUE = 750000


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value:.1f}%"


st.set_page_config(
    page_title="ThunderClap Revenue OS",
    page_icon="⚡",
    layout="wide",
)


# --------------------------------------------------
# DATA
# --------------------------------------------------

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

optimism_gap = max(
    0.0,
    forecast.rep_weighted_forecast
    - forecast.qualification_adjusted_forecast,
)

founder_deals = [
    deal
    for deal in deals
    if deal.founder_involved
    or deal.owner == "Founder"
]

founder_pipeline = sum(
    deal.amount_usd
    for deal in founder_deals
)

founder_share = (
    founder_pipeline / forecast.raw_pipeline * 100
    if forecast.raw_pipeline > 0
    else 0
)

expansion_deals = [
    deal
    for deal in deals
    if deal.source == DealSource.EXISTING_ACCOUNT
]

expansion_pipeline = sum(
    deal.amount_usd
    for deal in expansion_deals
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

st.caption("OUTSIDE-IN REVENUE OPERATING SYSTEM")

st.title("⚡ ThunderClap Revenue Command Center")

st.write(
    "What should management believe, where is revenue exposed, "
    "and what needs action today?"
)

st.info(
    "This is an independent application exercise. "
    "All account, opportunity and operating data is synthetic. "
    "Public ThunderClap figures are used only as directional context."
)


# --------------------------------------------------
# TOP METRICS
# --------------------------------------------------

st.subheader("Revenue Pulse")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Open Pipeline",
    money(forecast.raw_pipeline),
    f"{forecast.open_deals} deals",
)

col2.metric(
    "Rep Forecast",
    money(forecast.rep_weighted_forecast),
)

col3.metric(
    "OS Forecast",
    money(
        forecast.qualification_adjusted_forecast
    ),
    f"-{money(optimism_gap)} vs rep",
)

col4.metric(
    "Revenue at Risk",
    money(forecast.revenue_at_risk),
    f"{forecast.high_risk_deals + forecast.critical_risk_deals} deals",
)

col5.metric(
    "Believable Attainment",
    percent(
        forecast.forecast_attainment_pct
    ),
)


st.divider()


# --------------------------------------------------
# PIPELINE TRUTH
# --------------------------------------------------

st.subheader("Pipeline Truth")

left, right = st.columns([1.2, 1])

with left:
    st.markdown("### Forecast Quality")

    forecast_data = {
        "Rep-weighted forecast": forecast.rep_weighted_forecast,
        "Qualification-adjusted forecast": (
            forecast.qualification_adjusted_forecast
        ),
        "Optimism gap": optimism_gap,
        "Revenue at risk": forecast.revenue_at_risk,
    }

    for label, value in forecast_data.items():
        st.write(
            f"**{label}:** {money(value)}"
        )

    st.write(
        f"**Forecast confidence:** "
        f"{forecast.forecast_confidence:.0%}"
    )

    st.write(
        f"**Pipeline coverage:** "
        f"{forecast.pipeline_coverage:.2f}x"
    )

with right:
    st.markdown("### Forecast Mix")

    st.write(
        f"**Commit:** {money(forecast.commit_pipeline)}"
    )

    st.write(
        f"**Likely:** {money(forecast.likely_pipeline)}"
    )

    st.write(
        f"**Upside:** {money(forecast.upside_pipeline)}"
    )

    st.write(
        f"**Target:** {money(forecast.target_revenue)}"
    )

    st.write(
        f"**Forecast gap:** {money(forecast.forecast_gap)}"
    )


st.divider()


# --------------------------------------------------
# MANAGEMENT INTERVENTIONS
# --------------------------------------------------

st.subheader("Management Attention")

st.write(
    "Deals ranked by revenue exposure, risk and intervention urgency."
)

if not risky:
    st.success(
        "No high-risk or critical opportunities detected."
    )
else:
    for rank, (deal, assessment) in enumerate(
        risky[:7],
        start=1,
    ):
        if assessment.risk_level == RiskLevel.CRITICAL:
            status = "🔴 CRITICAL"
        else:
            status = "🟠 HIGH"

        with st.expander(
            f"#{rank} — {deal.deal_name} | "
            f"{money(deal.amount_usd)} | {status}",
            expanded=(rank <= 3),
        ):
            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Health",
                f"{assessment.health_score:.0f}/100",
            )

            c2.metric(
                "Qualification",
                f"{assessment.qualification_score:.0f}/100",
            )

            c3.metric(
                "Rep Probability",
                f"{deal.probability:.0%}",
            )

            c4.metric(
                "OS Probability",
                f"{assessment.adjusted_probability:.0%}",
            )

            st.markdown(
                f"**Primary risk:** "
                f"{assessment.primary_risk}"
            )

            st.markdown(
                f"**Recommended action:** "
                f"`{assessment.recommended_action.value}`"
            )

            st.write(
                assessment.action_reason
            )

            st.write(
                f"**Owner:** {assessment.owner} "
                f" | **SLA:** {assessment.sla}"
            )

            if assessment.risk_reasons:
                st.markdown("**Signals detected:**")

                for reason in assessment.risk_reasons:
                    st.write(f"- {reason}")


st.divider()


# --------------------------------------------------
# TODAY'S ACTION QUEUE
# --------------------------------------------------

st.subheader("What Should We Do Today?")

for rank, (deal, assessment) in enumerate(
    risky[:5],
    start=1,
):
    st.markdown(
        f"**{rank}. {assessment.recommended_action.value.replace('_', ' ').title()} "
        f"— {deal.deal_name}**"
    )

    st.caption(
        f"{money(deal.amount_usd)} exposed | "
        f"Owner: {assessment.owner} | "
        f"SLA: {assessment.sla}"
    )


st.divider()


# --------------------------------------------------
# FOUNDER DEPENDENCY + EXPANSION
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Founder Dependency")

    st.metric(
        "Founder-owned / involved pipeline",
        money(founder_pipeline),
    )

    st.metric(
        "Founder-involved deals",
        len(founder_deals),
    )

    st.metric(
        "Share of pipeline",
        f"{founder_share:.1f}%",
    )

    st.caption(
        "The goal of the Revenue OS is not to remove founders "
        "from strategic selling. It is to make founder involvement intentional."
    )


with col2:
    st.subheader("Expansion Radar")

    st.metric(
        "Existing-account pipeline",
        money(expansion_pipeline),
    )

    st.metric(
        "Expansion opportunities",
        len(expansion_deals),
    )

    st.caption(
        "Existing-account growth is modeled separately so expansion "
        "does not disappear inside new-logo pipeline reporting."
    )


st.divider()


# --------------------------------------------------
# STRATEGIC QUESTION
# --------------------------------------------------

st.subheader("Revenue Leadership Question")

st.success(
    "Which opportunities deserve intervention, which forecast assumptions "
    "should be challenged, and where should founder time be spent next?"
)

st.caption(
    "Synthetic demonstration of revenue decision architecture. "
    "Not ThunderClap's actual CRM, pipeline or forecast."
)
