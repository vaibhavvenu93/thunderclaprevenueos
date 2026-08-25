from __future__ import annotations

from datetime import date
from textwrap import dedent
from typing import Dict

import streamlit as st

from data.synthetic_pipeline import load_synthetic_pipeline
from engines.deal_risk_engine import (
    RiskLevel,
    assess_deal_risk,
)
from engines.forecast_engine import build_forecast
from models.deal import Deal, DealSource


TODAY = date(2026, 8, 26)
TARGET_REVENUE = 750000


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="ThunderClap Revenue OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# DESIGN SYSTEM
# ==========================================================

st.markdown(
    dedent(
        """
        <style>

        .stApp {
            background:
                radial-gradient(
                    circle at 82% -10%,
                    rgba(216,255,56,0.10),
                    transparent 28%
                ),
                #F7F7F2;
            color: #171717;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            max-width: 1450px;
        }

        section[data-testid="stSidebar"] {
            background: #111111;
            border-right: 1px solid #282828;
        }

        section[data-testid="stSidebar"] * {
            color: #F6F6EF;
        }

        section[data-testid="stSidebar"]
        div[role="radiogroup"] > label {
            border-radius: 8px;
            padding: 8px 10px;
            margin-bottom: 4px;
        }

        h1 {
            font-size: 3rem !important;
            line-height: 1.02 !important;
            letter-spacing: -0.045em !important;
            font-weight: 800 !important;
            color: #171717 !important;
        }

        h2 {
            letter-spacing: -0.03em !important;
            font-weight: 760 !important;
        }

        h3 {
            letter-spacing: -0.02em !important;
        }

        .eyebrow {
            font-size: 0.72rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            font-weight: 700;
            color: #70706A;
            margin-bottom: 0.55rem;
        }

        .hero-copy {
            font-size: 1.06rem;
            line-height: 1.6;
            color: #5E5E58;
            max-width: 900px;
            margin-top: -0.4rem;
            margin-bottom: 1.4rem;
        }

        .metric-card {
            background: rgba(255,255,255,0.82);
            border: 1px solid #E1E1D9;
            border-radius: 16px;
            padding: 20px 20px 18px 20px;
            min-height: 140px;
            box-shadow:
                0 1px 2px rgba(0,0,0,0.02),
                0 8px 24px rgba(0,0,0,0.025);
        }

        .metric-label {
            color: #77776F;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 750;
            margin-bottom: 12px;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 820;
            letter-spacing: -0.04em;
            color: #171717;
            line-height: 1;
        }

        .metric-note {
            color: #6D6D66;
            font-size: 0.84rem;
            margin-top: 12px;
            line-height: 1.4;
        }

        .metric-negative {
            color: #B42318;
        }

        .metric-positive {
            color: #147A42;
        }

        .pill {
            display: inline-block;
            border-radius: 999px;
            padding: 5px 9px;
            font-size: 0.68rem;
            font-weight: 820;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .critical {
            background: #FFE5E5;
            color: #A51212;
        }

        .high {
            background: #FFF0D2;
            color: #8D5200;
        }

        .healthy {
            background: #DDF7E8;
            color: #147A42;
        }

        .active {
            background: #D9FF38;
            color: #141414;
        }

        .ready {
            background: #EBEBE6;
            color: #55554F;
        }

        .action-card {
            background: #FFFFFF;
            border: 1px solid #E0E0D9;
            border-radius: 15px;
            padding: 18px 20px;
            margin-bottom: 12px;
        }

        .action-rank {
            color: #8B8B84;
            font-size: 0.72rem;
            font-weight: 820;
            letter-spacing: 0.10em;
        }

        .action-title {
            font-size: 1.08rem;
            font-weight: 760;
            margin-top: 5px;
            color: #1B1B1B;
        }

        .action-detail {
            color: #666660;
            font-size: 0.88rem;
            margin-top: 8px;
            line-height: 1.5;
        }

        .dark-card {
            background: #171717;
            color: #F5F5ED;
            border-radius: 18px;
            padding: 24px;
        }

        .dark-card .label {
            color: #B8B8B0;
            font-size: 0.70rem;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            font-weight: 700;
        }

        .dark-card .big {
            font-size: 2.25rem;
            font-weight: 820;
            letter-spacing: -0.04em;
            margin-top: 8px;
            margin-bottom: 8px;
        }

        .dark-card .accent {
            color: #D9FF38;
        }

        .automation-card {
            background: #FFFFFF;
            border: 1px solid #E0E0D9;
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 12px;
        }

        .automation-title {
            font-weight: 760;
            font-size: 1rem;
            color: #171717;
        }

        .automation-copy {
            color: #686861;
            font-size: 0.88rem;
            margin-top: 6px;
            line-height: 1.5;
        }

        .score-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-top: 10px;
        }

        .score-box {
            background: #FFFFFF;
            border: 1px solid #E0E0D9;
            border-radius: 14px;
            padding: 16px;
        }

        .score-label {
            font-size: 0.72rem;
            color: #77776F;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 700;
        }

        .score-value {
            font-size: 1.55rem;
            font-weight: 800;
            margin-top: 5px;
        }

        .stButton > button {
            border-radius: 10px;
            font-weight: 700;
            min-height: 42px;
            border: 1px solid #1B1B1B;
        }

        .stButton > button[kind="primary"] {
            background: #171717;
            color: #D9FF38;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        </style>
        """
    ),
    unsafe_allow_html=True,
)


# ==========================================================
# HELPERS
# ==========================================================

def money(value: float) -> str:
    return f"${value:,.0f}"


def clean_action(value: str) -> str:
    return value.replace("_", " ").title()


def risk_pill(risk: RiskLevel) -> str:
    if risk == RiskLevel.CRITICAL:
        return '<span class="pill critical">Critical</span>'

    if risk == RiskLevel.HIGH:
        return '<span class="pill high">High</span>'

    return '<span class="pill healthy">Healthy</span>'


def metric_card(
    label: str,
    value: str,
    note: str,
    note_class: str = "",
) -> None:
    html = dedent(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note {note_class}">
                {note}
            </div>
        </div>
        """
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def momentum_score(
    days_in_stage: int,
    next_meeting_exists: bool,
    risk_reasons_count: int,
) -> int:
    score = 100

    if days_in_stage >= 20:
        score -= 35
    elif days_in_stage >= 12:
        score -= 20
    elif days_in_stage >= 7:
        score -= 10

    if not next_meeting_exists:
        score -= 25

    score -= min(
        30,
        risk_reasons_count * 4,
    )

    return max(
        0,
        score,
    )


# ==========================================================
# LOAD INTELLIGENCE
# ==========================================================

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

assessment_by_id = {
    deal.deal_id: assessment
    for deal, assessment in assessments
}

optimism_gap = max(
    0.0,
    forecast.rep_weighted_forecast
    - forecast.qualification_adjusted_forecast,
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
    founder_pipeline
    / forecast.raw_pipeline
    * 100
    if forecast.raw_pipeline
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


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.markdown("## ⚡ THUNDERCLAP")
    st.caption("REVENUE OS // APPLICATION BUILD")

    st.write("")

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Action Queue",
            "Pipeline Truth",
            "Deal Room",
            "Automations",
            "Revenue Plan",
        ],
        label_visibility="collapsed",
    )

    st.write("")
    st.write("")
    st.caption("SYSTEM STATUS")

    st.markdown(
        '<span class="pill active">● Intelligence Active</span>',
        unsafe_allow_html=True,
    )

    st.write("")
    st.caption("Synthetic dataset")
    st.write(
        f"**{len(deals)} opportunities**"
    )

    st.caption("Last simulated refresh")
    st.write("**26 Aug • 00:15 IST**")

    st.write("")
    st.caption(
        "Independent application exercise. "
        "No confidential ThunderClap information."
    )


# ==========================================================
# OVERVIEW
# ==========================================================

if page == "Overview":

    st.markdown(
        '<div class="eyebrow">Executive Overview</div>',
        unsafe_allow_html=True,
    )

    st.title("Good morning. Revenue needs attention.")

    st.markdown(
        dedent(
            f"""
            <div class="hero-copy">
                {len(risky)} opportunities require intervention.
                <strong>{money(forecast.revenue_at_risk)}</strong>
                of synthetic pipeline is currently exposed.
                The system is challenging
                <strong>{money(optimism_gap)}</strong>
                of rep forecast optimism.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    top_action, top_note = st.columns(
        [1, 4]
    )

    with top_action:
        st.button(
            "⚡ Run Revenue Brief",
            type="primary",
            use_container_width=True,
        )

    with top_note:
        st.caption(
            "Simulates a management refresh across qualification, "
            "forecast quality, deal risk and intervention priority."
        )

    st.write("")

    cols = st.columns(5)

    with cols[0]:
        metric_card(
            "Open Pipeline",
            money(forecast.raw_pipeline),
            f"{forecast.open_deals} active opportunities",
        )

    with cols[1]:
        metric_card(
            "Believable Forecast",
            money(
                forecast.qualification_adjusted_forecast
            ),
            (
                f"{forecast.forecast_attainment_pct:.1f}% "
                "of illustrative target"
            ),
            "metric-positive",
        )

    with cols[2]:
        metric_card(
            "Revenue Exposed",
            money(forecast.revenue_at_risk),
            (
                f"{forecast.high_risk_deals + forecast.critical_risk_deals} "
                "high / critical deals"
            ),
            "metric-negative",
        )

    with cols[3]:
        metric_card(
            "Optimism Gap",
            money(optimism_gap),
            "Rep forecast less OS-adjusted forecast",
            "metric-negative",
        )

    with cols[4]:
        metric_card(
            "Coverage",
            f"{forecast.pipeline_coverage:.2f}x",
            f"{forecast.forecast_confidence:.0%} forecast confidence",
        )

    st.write("")
    st.divider()

    left, right = st.columns(
        [1.45, 0.8]
    )

    with left:
        st.subheader("Priority Queue")

        st.caption(
            "The highest-value actions management should inspect first."
        )

        for rank, (deal, assessment) in enumerate(
            risky[:5],
            start=1,
        ):
            priority_html = dedent(
                f"""
                <div class="action-card">
                    <div class="action-rank">
                        PRIORITY {rank:02d}
                    </div>

                    <div class="action-title">
                        {deal.deal_name}
                        &nbsp;
                        {risk_pill(assessment.risk_level)}
                    </div>

                    <div class="action-detail">
                        <strong>{money(deal.amount_usd)}</strong>
                        &nbsp;•&nbsp;
                        Rep {deal.probability:.0%}
                        &nbsp;→&nbsp;
                        OS {assessment.adjusted_probability:.0%}
                        &nbsp;•&nbsp;
                        {clean_action(
                            assessment.recommended_action.value
                        )}
                        &nbsp;•&nbsp;
                        SLA {assessment.sla}
                    </div>
                </div>
                """
            )

            st.markdown(
                priority_html,
                unsafe_allow_html=True,
            )

    with right:
        revenue_truth_html = dedent(
            f"""
            <div class="dark-card">
                <div class="label">
                    Today's Revenue Truth
                </div>

                <div class="big">
                    {money(optimism_gap)}
                </div>

                <p>
                    of rep-weighted forecast is being challenged
                    by qualification quality.
                </p>

                <hr style="
                    border:none;
                    border-top:1px solid #3A3A3A;
                ">

                <div class="label">
                    Founder Dependency
                </div>

                <div class="big accent">
                    {founder_share:.1f}%
                </div>

                <p>
                    of open pipeline currently has
                    founder ownership or involvement.
                </p>
            </div>
            """
        )

        st.markdown(
            revenue_truth_html,
            unsafe_allow_html=True,
        )

        st.write("")

        st.subheader("Expansion Radar")

        st.metric(
            "Existing-account pipeline",
            money(expansion_pipeline),
        )

        st.caption(
            f"{len(expansion_deals)} synthetic expansion "
            "opportunities identified."
        )


# ==========================================================
# ACTION QUEUE
# ==========================================================

elif page == "Action Queue":

    st.markdown(
        '<div class="eyebrow">Revenue Execution</div>',
        unsafe_allow_html=True,
    )

    st.title("Action Queue")

    st.markdown(
        dedent(
            """
            <div class="hero-copy">
                A ranked operating queue generated from deal value,
                inactivity, qualification gaps, stage ageing and
                forecast risk.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    filter_option = st.selectbox(
        "Show",
        [
            "All urgent actions",
            "Critical only",
            "Founder actions",
            "AE-01",
            "AE-02",
        ],
    )

    display_items = risky

    if filter_option == "Critical only":
        display_items = [
            item
            for item in risky
            if item[1].risk_level
            == RiskLevel.CRITICAL
        ]

    elif filter_option == "Founder actions":
        display_items = [
            item
            for item in risky
            if (
                item[0].founder_involved
                or item[0].owner == "Founder"
            )
        ]

    elif filter_option in {
        "AE-01",
        "AE-02",
    }:
        display_items = [
            item
            for item in risky
            if item[0].owner
            == filter_option
        ]

    for rank, (
        deal,
        assessment,
    ) in enumerate(
        display_items,
        start=1,
    ):

        with st.container(
            border=True
        ):
            top1, top2, top3 = st.columns(
                [3.2, 1, 1]
            )

            with top1:
                st.markdown(
                    f"### {rank:02d}. "
                    f"{deal.deal_name}"
                )

                st.markdown(
                    risk_pill(
                        assessment.risk_level
                    ),
                    unsafe_allow_html=True,
                )

            with top2:
                st.metric(
                    "Value",
                    money(deal.amount_usd),
                )

            with top3:
                st.metric(
                    "Health",
                    f"{assessment.health_score:.0f}/100",
                )

            st.write("")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Qualification",
                f"{assessment.qualification_score:.0f}",
            )

            c2.metric(
                "Rep Probability",
                f"{deal.probability:.0%}",
            )

            c3.metric(
                "OS Probability",
                f"{assessment.adjusted_probability:.0%}",
            )

            c4.metric(
                "SLA",
                assessment.sla,
            )

            st.write(
                f"**Why now:** "
                f"{assessment.primary_risk}"
            )

            st.write(
                f"**Next best action:** "
                f"{clean_action(assessment.recommended_action.value)}"
            )

            b1, b2, b3 = st.columns(3)

            b1.button(
                "Open Deal Room",
                key=f"open_{deal.deal_id}",
                use_container_width=True,
            )

            b2.button(
                "Draft Rescue",
                key=f"rescue_{deal.deal_id}",
                use_container_width=True,
            )

            b3.button(
                "Escalate",
                key=f"escalate_{deal.deal_id}",
                use_container_width=True,
            )


# ==========================================================
# PIPELINE TRUTH
# ==========================================================

elif page == "Pipeline Truth":

    st.markdown(
        '<div class="eyebrow">Forecast Intelligence</div>',
        unsafe_allow_html=True,
    )

    st.title(
        "What can we actually believe?"
    )

    st.markdown(
        dedent(
            """
            <div class="hero-copy">
                Separate pipeline quantity from pipeline quality.
                Rep-entered probabilities are compared with
                qualification-adjusted probabilities before
                management commits to a forecast.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Rep Forecast",
            money(
                forecast.rep_weighted_forecast
            ),
            "CRM probability × deal value",
        )

    with c2:
        metric_card(
            "OS Forecast",
            money(
                forecast.qualification_adjusted_forecast
            ),
            "Qualification-adjusted management view",
            "metric-positive",
        )

    with c3:
        metric_card(
            "Optimism Gap",
            money(optimism_gap),
            "Forecast management should challenge",
            "metric-negative",
        )

    st.write("")

    st.subheader("Forecast Mix")

    mix1, mix2, mix3, mix4 = st.columns(4)

    mix1.metric(
        "Commit",
        money(
            forecast.commit_pipeline
        ),
    )

    mix2.metric(
        "Likely",
        money(
            forecast.likely_pipeline
        ),
    )

    mix3.metric(
        "Upside",
        money(
            forecast.upside_pipeline
        ),
    )

    mix4.metric(
        "Pipeline Coverage",
        f"{forecast.pipeline_coverage:.2f}x",
    )

    st.divider()

    st.subheader(
        "Largest Forecast Disagreements"
    )

    disagreement_rows = sorted(
        assessments,
        key=lambda item: (
            item[0].amount_usd
            * (
                item[0].probability
                - item[1].adjusted_probability
            )
        ),
        reverse=True,
    )

    for deal, assessment in disagreement_rows[:8]:

        value_gap = (
            deal.amount_usd
            * (
                deal.probability
                - assessment.adjusted_probability
            )
        )

        with st.container(
            border=True
        ):
            c1, c2, c3, c4 = st.columns(
                [2.5, 1, 1, 1]
            )

            c1.markdown(
                f"**{deal.deal_name}**"
            )

            c2.metric(
                "Rep",
                f"{deal.probability:.0%}",
            )

            c3.metric(
                "OS",
                f"{assessment.adjusted_probability:.0%}",
            )

            c4.metric(
                "Forecast Gap",
                money(value_gap),
            )


# ==========================================================
# DEAL ROOM
# ==========================================================

elif page == "Deal Room":

    st.markdown(
        '<div class="eyebrow">Deal Intelligence</div>',
        unsafe_allow_html=True,
    )

    st.title("Deal Room")

    deal_lookup: Dict[str, Deal] = {
        (
            f"{deal.deal_id} — "
            f"{deal.deal_name} — "
            f"{money(deal.amount_usd)}"
        ): deal
        for deal in deals
    }

    selected_label = st.selectbox(
        "Select an opportunity",
        list(
            deal_lookup.keys()
        ),
    )

    selected = deal_lookup[
        selected_label
    ]

    assessment = assessment_by_id[
        selected.deal_id
    ]

    momentum = momentum_score(
        selected.days_in_stage,
        selected.next_meeting_date
        is not None,
        len(
            assessment.risk_reasons
        ),
    )

    forecast_confidence = int(
        assessment.adjusted_probability
        * 100
    )

    st.write("")

    title1, title2 = st.columns(
        [4, 1]
    )

    with title1:
        st.subheader(
            selected.deal_name
        )

        st.markdown(
            risk_pill(
                assessment.risk_level
            ),
            unsafe_allow_html=True,
        )

    with title2:
        st.metric(
            "Deal Value",
            money(
                selected.amount_usd
            ),
        )

    score_html = dedent(
        f"""
        <div class="score-row">
            <div class="score-box">
                <div class="score-label">
                    Health
                </div>
                <div class="score-value">
                    {assessment.health_score:.0f}
                </div>
            </div>

            <div class="score-box">
                <div class="score-label">
                    Momentum
                </div>
                <div class="score-value">
                    {momentum}
                </div>
            </div>

            <div class="score-box">
                <div class="score-label">
                    Qualification
                </div>
                <div class="score-value">
                    {assessment.qualification_score:.0f}
                </div>
            </div>

            <div class="score-box">
                <div class="score-label">
                    Forecast Confidence
                </div>
                <div class="score-value">
                    {forecast_confidence}
                </div>
            </div>
        </div>
        """
    )

    st.markdown(
        score_html,
        unsafe_allow_html=True,
    )

    st.divider()

    left, right = st.columns(
        [1.2, 1]
    )

    with left:
        st.subheader(
            "Why the system is concerned"
        )

        if assessment.risk_reasons:
            for reason in assessment.risk_reasons:
                st.write(
                    f"● {reason}"
                )
        else:
            st.success(
                "No material risk signals detected."
            )

        st.write("")

        st.subheader(
            "Current Deal State"
        )

        st.write(
            f"**Stage:** "
            f"{selected.stage.value.title()}"
        )

        st.write(
            f"**Owner:** "
            f"{selected.owner}"
        )

        st.write(
            f"**Days in stage:** "
            f"{selected.days_in_stage}"
        )

        st.write(
            f"**Next meeting:** "
            f"{selected.next_meeting_date or 'Not scheduled'}"
        )

        st.write(
            f"**Primary objection:** "
            f"{selected.primary_objection or 'None recorded'}"
        )

        st.write(
            f"**Rep probability:** "
            f"{selected.probability:.0%}"
        )

        st.write(
            f"**OS probability:** "
            f"{assessment.adjusted_probability:.0%}"
        )

    with right:
        next_action_html = dedent(
            f"""
            <div class="dark-card">
                <div class="label">
                    Next Best Action
                </div>

                <div
                    class="big accent"
                    style="font-size:1.7rem;"
                >
                    {
                        clean_action(
                            assessment.recommended_action.value
                        )
                    }
                </div>

                <p>
                    {assessment.action_reason}
                </p>

                <hr style="
                    border:none;
                    border-top:1px solid #3A3A3A;
                ">

                <div class="label">
                    Owner
                </div>

                <p>
                    {assessment.owner}
                    &nbsp; • &nbsp;
                    SLA {assessment.sla}
                </p>
            </div>
            """
        )

        st.markdown(
            next_action_html,
            unsafe_allow_html=True,
        )

        st.write("")

        a1, a2 = st.columns(2)

        a1.button(
            "✨ Analyse with AI",
            type="primary",
            use_container_width=True,
        )

        a2.button(
            "Build Close Plan",
            use_container_width=True,
        )

        a3, a4 = st.columns(2)

        a3.button(
            "Draft Follow-up",
            use_container_width=True,
        )

        a4.button(
            "Escalate",
            use_container_width=True,
        )


# ==========================================================
# AUTOMATIONS
# ==========================================================

elif page == "Automations":

    st.markdown(
        '<div class="eyebrow">Revenue Automation</div>',
        unsafe_allow_html=True,
    )

    st.title(
        "The machine behind the sales team"
    )

    st.markdown(
        dedent(
            """
            <div class="hero-copy">
                Revenue operations should not depend on someone
                remembering every follow-up, forecast review or
                stalled deal. These workflows turn operating signals
                into management actions.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    automations = [
        (
            "Deal Stall Monitor",
            "ACTIVE",
            (
                "Detects inactivity, stage ageing "
                "and missing next steps."
            ),
            (
                f"{len(risky)} interventions "
                "currently surfaced"
            ),
        ),
        (
            "Forecast Truth Engine",
            "ACTIVE",
            (
                "Challenges rep-entered probability "
                "using qualification quality."
            ),
            (
                f"{money(optimism_gap)} optimism "
                "currently detected"
            ),
        ),
        (
            "Follow-up SLA Guard",
            "ACTIVE",
            (
                "Finds opportunities with no "
                "committed next action."
            ),
            "Runs after meaningful sales activity",
        ),
        (
            "Founder Escalation Engine",
            "ACTIVE",
            (
                "Routes high-value, high-risk deals "
                "for executive intervention."
            ),
            (
                f"{len(founder_deals)} opportunities "
                "currently founder-linked"
            ),
        ),
        (
            "Expansion Radar",
            "ACTIVE",
            (
                "Separates existing-account expansion "
                "from new-logo pipeline."
            ),
            (
                f"{money(expansion_pipeline)} expansion "
                "pipeline identified"
            ),
        ),
        (
            "AI Call Intelligence",
            "READY",
            (
                "Transcript → objections → stakeholders → "
                "qualification → CRM update."
            ),
            "API integration next",
        ),
        (
            "AI Follow-up Agent",
            "READY",
            (
                "Generates contextual follow-up from "
                "deal state and conversation history."
            ),
            "Human approval before send",
        ),
    ]

    for (
        title,
        status,
        description,
        result,
    ) in automations:

        status_class = (
            "active"
            if status == "ACTIVE"
            else "ready"
        )

        automation_html = dedent(
            f"""
            <div class="automation-card">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:16px;
                ">
                    <div class="automation-title">
                        {title}
                    </div>

                    <span class="pill {status_class}">
                        {status}
                    </span>
                </div>

                <div class="automation-copy">
                    {description}
                </div>

                <div style="
                    margin-top:10px;
                    font-size:0.82rem;
                    font-weight:650;
                    color:#3E3E3A;
                ">
                    {result}
                </div>

            </div>
            """
        )

        st.markdown(
            automation_html,
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader(
        "Operating Architecture"
    )

    st.code(
        """
Signal
  ↓
Detect
  ↓
Score / Diagnose
  ↓
Create Action
  ↓
Human Approval
  ↓
Execute
  ↓
CRM Updated
  ↓
Forecast Recalculated
        """,
        language="text",
    )


# ==========================================================
# REVENUE PLAN
# ==========================================================

elif page == "Revenue Plan":

    st.markdown(
        '<div class="eyebrow">Revenue Architecture</div>',
        unsafe_allow_html=True,
    )

    st.title(
        "What gets us to $3M?"
    )

    st.markdown(
        dedent(
            """
            <div class="hero-copy">
                Model the combination of average contract value,
                conversion, sales capacity, expansion and pipeline
                creation required to reach the next revenue stage.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Public Ambition",
            "$3M",
            "Directional context from the role description",
        )

    with c2:
        metric_card(
            "Illustrative Pipeline",
            money(
                forecast.raw_pipeline
            ),
            "Current synthetic opportunity portfolio",
        )

    with c3:
        metric_card(
            "Expansion Identified",
            money(
                expansion_pipeline
            ),
            "Synthetic existing-account opportunity",
        )

    st.write("")

    st.subheader(
        "Revenue Digital Twin"
    )

    sim1, sim2 = st.columns(2)

    with sim1:
        average_contract_value = st.slider(
            "Average contract value",
            min_value=20000,
            max_value=100000,
            value=50000,
            step=5000,
        )

        win_rate = st.slider(
            "Qualified win rate",
            min_value=10,
            max_value=60,
            value=30,
            step=1,
        )

        qualified_opportunities = st.slider(
            "Qualified opportunities / year",
            min_value=20,
            max_value=200,
            value=100,
            step=5,
        )

    with sim2:
        expansion_share = st.slider(
            "Expansion contribution (%)",
            min_value=0,
            max_value=40,
            value=15,
            step=1,
        )

        ae_count = st.slider(
            "AEs",
            min_value=1,
            max_value=10,
            value=4,
            step=1,
        )

        capacity_per_ae = st.slider(
            "Qualified opportunities per AE / year",
            min_value=10,
            max_value=50,
            value=25,
            step=1,
        )

    gross_new_revenue = (
        average_contract_value
        * qualified_opportunities
        * (
            win_rate
            / 100
        )
    )

    expansion_revenue = (
        gross_new_revenue
        * (
            expansion_share
            / 100
        )
    )

    modeled_revenue = (
        gross_new_revenue
        + expansion_revenue
    )

    ae_capacity = (
        ae_count
        * capacity_per_ae
    )

    required_wins = (
        3000000
        / average_contract_value
    )

    required_opportunities = (
        required_wins
        / (
            win_rate
            / 100
        )
        if win_rate > 0
        else 0
    )

    st.write("")
    st.divider()

    o1, o2, o3, o4 = st.columns(4)

    o1.metric(
        "Modeled Revenue",
        money(
            modeled_revenue
        ),
    )

    o2.metric(
        "Required Wins",
        f"{required_wins:.0f}",
    )

    o3.metric(
        "Required Qualified Opps",
        f"{required_opportunities:.0f}",
    )

    o4.metric(
        "AE Capacity",
        f"{ae_capacity}",
    )

    if modeled_revenue >= 3000000:
        st.success(
            "This operating model clears the $3M revenue ambition."
        )
    else:
        shortfall = (
            3000000
            - modeled_revenue
        )

        st.warning(
            f"This operating model is short by "
            f"{money(shortfall)}."
        )


# ==========================================================
# FOOTER
# ==========================================================

st.write("")
st.write("")

st.caption(
    "THUNDERCLAP REVENUE OS • Independent application prototype • "
    "All CRM-level data is synthetic."
)
  
