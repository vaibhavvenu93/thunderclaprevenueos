from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

import streamlit as st

from data.synthetic_activity import (
    ActivityType,
    RevenueActivity,
    SignalType,
    activities_for_deal,
    load_synthetic_activity,
    recent_activity,
)
from data.synthetic_pipeline import load_synthetic_pipeline
from engines.deal_risk_engine import (
    RiskLevel,
    assess_deal_risk,
)
from engines.forecast_engine import build_forecast
from models.deal import Deal, DealSource


# ==========================================================
# CONFIG
# ==========================================================

TODAY = date(2026, 8, 26)
TARGET_REVENUE = 750000
LONG_TERM_REVENUE_TARGET = 3000000


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
    """
<style>

.stApp {
    background:
        radial-gradient(
            circle at 82% -10%,
            rgba(217,255,56,0.08),
            transparent 28%
        ),
        #F7F7F2;
    color: #171717;
}

.block-container {
    padding-top: 2.2rem;
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
    margin-bottom: 3px;
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

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.78);
    border: 1px solid #E0E0D8;
    padding: 18px;
    border-radius: 14px;
}

div[data-testid="stMetricLabel"] {
    font-weight: 650;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 700;
    border: 1px solid #191919;
    min-height: 42px;
}

.stButton > button[kind="primary"] {
    background: #171717;
    color: #D9FF38;
}

div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.64);
    border: 1px solid #E0E0D8;
    border-radius: 12px;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True,
)


# ==========================================================
# HELPERS
# ==========================================================

def money(value: float) -> str:
    return f"${value:,.0f}"


def clean_enum(value: str) -> str:
    return value.replace("_", " ").title()


def signal_icon(signal: SignalType) -> str:
    if signal == SignalType.POSITIVE:
        return "🟢"

    if signal == SignalType.RISK:
        return "🔴"

    return "⚪"


def activity_icon(activity_type: ActivityType) -> str:
    mapping = {
        ActivityType.EMAIL_INBOUND: "📥",
        ActivityType.EMAIL_OUTBOUND: "📤",
        ActivityType.MEETING: "🎙️",
        ActivityType.CRM_UPDATE: "🗂️",
        ActivityType.AUTOMATION: "⚡",
    }

    return mapping.get(
        activity_type,
        "•",
    )


def risk_label(risk_level: RiskLevel) -> str:
    if risk_level == RiskLevel.CRITICAL:
        return "🔴 CRITICAL"

    if risk_level == RiskLevel.HIGH:
        return "🟠 HIGH"

    return "🟢 HEALTHY"


def momentum_score(
    deal: Deal,
    risk_reason_count: int,
) -> int:
    score = 100

    if deal.days_in_stage >= 20:
        score -= 35
    elif deal.days_in_stage >= 12:
        score -= 20
    elif deal.days_in_stage >= 7:
        score -= 10

    if deal.next_meeting_date is None:
        score -= 25

    score -= min(
        30,
        risk_reason_count * 4,
    )

    return max(
        0,
        score,
    )


def render_page_intro(
    eyebrow: str,
    title: str,
    description: str,
) -> None:
    st.caption(
        eyebrow.upper()
    )

    st.title(
        title
    )

    st.write(
        description
    )

    st.write("")


def render_activity(
    activity: RevenueActivity,
    show_deal: bool = True,
) -> None:

    title = (
        f"{activity_icon(activity.activity_type)} "
        f"{activity.title}"
    )

    with st.container(
        border=True
    ):
        top1, top2 = st.columns(
            [4, 1]
        )

        with top1:
            st.markdown(
                f"**{title}**"
            )

        with top2:
            st.caption(
                activity.occurred_at.strftime(
                    "%d Aug • %H:%M"
                )
            )

        if show_deal:
            st.caption(
                f"Deal: {activity.deal_id}"
            )

        st.write(
            f"{signal_icon(activity.signal_type)} "
            f"{activity.summary}"
        )

        if activity.extracted_signals:
            with st.expander(
                "Signals extracted"
            ):
                for signal in activity.extracted_signals:
                    st.write(
                        f"• {signal}"
                    )

        if activity.recommended_action:
            st.info(
                "Recommended action: "
                + activity.recommended_action
            )


# ==========================================================
# LOAD DATA + ENGINES
# ==========================================================

deals = load_synthetic_pipeline()
activities = load_synthetic_activity()

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

deal_by_id = {
    deal.deal_id: deal
    for deal in deals
}


optimism_gap = max(
    0.0,
    forecast.rep_weighted_forecast
    - forecast.qualification_adjusted_forecast,
)


risky = [
    (
        deal,
        assessment,
    )
    for deal, assessment in assessments
    if assessment.risk_level
    in {
        RiskLevel.HIGH,
        RiskLevel.CRITICAL,
    }
]

risky.sort(
    key=lambda item: (
        item[1].risk_level
        == RiskLevel.CRITICAL,
        item[0].amount_usd,
    ),
    reverse=True,
)


founder_deals = [
    deal
    for deal in deals
    if (
        deal.founder_involved
        or deal.owner == "Founder"
    )
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
    if deal.source
    == DealSource.EXISTING_ACCOUNT
]

expansion_pipeline = sum(
    deal.amount_usd
    for deal in expansion_deals
)


inbox_activity = [
    activity
    for activity in activities
    if activity.activity_type
    in {
        ActivityType.EMAIL_INBOUND,
        ActivityType.EMAIL_OUTBOUND,
    }
]


meeting_activity = [
    activity
    for activity in activities
    if activity.activity_type
    == ActivityType.MEETING
]


automation_activity = [
    activity
    for activity in activities
    if activity.activity_type
    == ActivityType.AUTOMATION
]


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown(
        "## ⚡ THUNDERCLAP"
    )

    st.caption(
        "REVENUE OS // APPLICATION BUILD"
    )

    st.write("")

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Action Queue",
            "Pipeline Truth",
            "Deal Room",
            "Inbox Intelligence",
            "Meeting Intelligence",
            "Activity Feed",
            "Automations",
            "Revenue Plan",
            "Integrations",
        ],
        label_visibility="collapsed",
    )

    st.write("")
    st.write("")

    st.caption(
        "SYSTEM STATUS"
    )

    st.success(
        "● Intelligence Active"
    )

    st.caption(
        "Synthetic opportunity dataset"
    )

    st.write(
        f"**{len(deals)} opportunities**"
    )

    st.caption(
        "Synthetic activity events"
    )

    st.write(
        f"**{len(activities)} events**"
    )

    st.caption(
        "Last simulated refresh"
    )

    st.write(
        "**26 Aug • 00:15 IST**"
    )

    st.write("")

    st.caption(
        "Independent application exercise. "
        "No confidential ThunderClap information."
    )


# ==========================================================
# OVERVIEW
# ==========================================================

if page == "Overview":

    render_page_intro(
        "Executive Overview",
        "Good morning. Revenue needs attention.",
        (
            f"{len(risky)} opportunities require intervention. "
            f"{money(forecast.revenue_at_risk)} of synthetic pipeline "
            f"is exposed, while {money(optimism_gap)} of rep-weighted "
            "forecast is being challenged by qualification evidence."
        ),
    )

    action_col, copy_col = st.columns(
        [1, 4]
    )

    with action_col:
        st.button(
            "⚡ Run Revenue Brief",
            type="primary",
            use_container_width=True,
        )

    with copy_col:
        st.caption(
            "Re-runs qualification, risk, forecast and "
            "management intervention logic."
        )

    st.write("")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Open Pipeline",
        money(
            forecast.raw_pipeline
        ),
        f"{forecast.open_deals} deals",
    )

    c2.metric(
        "Believable Forecast",
        money(
            forecast.qualification_adjusted_forecast
        ),
        (
            f"{forecast.forecast_attainment_pct:.1f}% "
            "of illustrative target"
        ),
    )

    c3.metric(
        "Revenue Exposed",
        money(
            forecast.revenue_at_risk
        ),
        (
            f"{forecast.high_risk_deals + forecast.critical_risk_deals} "
            "urgent deals"
        ),
        delta_color="inverse",
    )

    c4.metric(
        "Optimism Gap",
        money(
            optimism_gap
        ),
        "Rep vs OS",
        delta_color="inverse",
    )

    c5.metric(
        "Coverage",
        f"{forecast.pipeline_coverage:.2f}x",
        f"{forecast.forecast_confidence:.0%} confidence",
    )

    st.divider()

    left, right = st.columns(
        [1.45, 0.8]
    )

    with left:

        st.subheader(
            "Priority Queue"
        )

        st.caption(
            "Highest-value interventions management should inspect first."
        )

        for rank, (
            deal,
            assessment,
        ) in enumerate(
            risky[:5],
            start=1,
        ):

            with st.container(
                border=True
            ):

                name_col, value_col = st.columns(
                    [4, 1]
                )

                with name_col:
                    st.markdown(
                        f"### {rank:02d}. {deal.deal_name}"
                    )

                    st.caption(
                        risk_label(
                            assessment.risk_level
                        )
                    )

                with value_col:
                    st.metric(
                        "Value",
                        money(
                            deal.amount_usd
                        ),
                    )

                st.write(
                    f"**Rep:** {deal.probability:.0%} "
                    f"→ **OS:** {assessment.adjusted_probability:.0%}"
                )

                st.write(
                    "**Next action:** "
                    + clean_enum(
                        assessment.recommended_action.value
                    )
                )

                st.caption(
                    f"Owner: {assessment.owner} • SLA: {assessment.sla}"
                )

    with right:

        st.subheader(
            "Today's Revenue Truth"
        )

        with st.container(
            border=True
        ):
            st.metric(
                "Forecast being challenged",
                money(
                    optimism_gap
                ),
            )

            st.write(
                "Qualification evidence does not support "
                "the full rep-weighted forecast."
            )

            st.divider()

            st.metric(
                "Founder-dependent pipeline",
                f"{founder_share:.1f}%",
            )

            st.caption(
                money(
                    founder_pipeline
                )
                + " has founder ownership or involvement."
            )

        st.subheader(
            "Expansion Radar"
        )

        st.metric(
            "Existing-account pipeline",
            money(
                expansion_pipeline
            ),
            f"{len(expansion_deals)} opportunities",
        )

    st.divider()

    st.subheader(
        "What changed?"
    )

    for activity in recent_activity(
        5
    ):
        render_activity(
            activity
        )


# ==========================================================
# ACTION QUEUE
# ==========================================================

elif page == "Action Queue":

    render_page_intro(
        "Revenue Execution",
        "Action Queue",
        (
            "A ranked operating queue generated from deal value, "
            "qualification, inactivity, stage ageing and forecast risk."
        ),
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
                or item[0].owner
                == "Founder"
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

            c1, c2, c3 = st.columns(
                [3, 1, 1]
            )

            with c1:
                st.subheader(
                    f"{rank:02d}. {deal.deal_name}"
                )

                st.caption(
                    risk_label(
                        assessment.risk_level
                    )
                )

            c2.metric(
                "Value",
                money(
                    deal.amount_usd
                ),
            )

            c3.metric(
                "Health",
                f"{assessment.health_score:.0f}/100",
            )

            q1, q2, q3, q4 = st.columns(
                4
            )

            q1.metric(
                "Qualification",
                f"{assessment.qualification_score:.0f}",
            )

            q2.metric(
                "Rep Probability",
                f"{deal.probability:.0%}",
            )

            q3.metric(
                "OS Probability",
                f"{assessment.adjusted_probability:.0%}",
            )

            q4.metric(
                "SLA",
                assessment.sla,
            )

            st.write(
                "**Why now:** "
                + assessment.primary_risk
            )

            st.write(
                "**Next best action:** "
                + clean_enum(
                    assessment.recommended_action.value
                )
            )

            b1, b2, b3 = st.columns(
                3
            )

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

    render_page_intro(
        "Forecast Intelligence",
        "What can we actually believe?",
        (
            "Rep-entered probabilities are compared with "
            "qualification-adjusted probabilities before "
            "management commits to a forecast."
        ),
    )

    c1, c2, c3 = st.columns(
        3
    )

    c1.metric(
        "Rep Forecast",
        money(
            forecast.rep_weighted_forecast
        ),
    )

    c2.metric(
        "OS Forecast",
        money(
            forecast.qualification_adjusted_forecast
        ),
    )

    c3.metric(
        "Optimism Gap",
        money(
            optimism_gap
        ),
    )

    st.write("")

    st.subheader(
        "Forecast Mix"
    )

    f1, f2, f3, f4 = st.columns(
        4
    )

    f1.metric(
        "Commit",
        money(
            forecast.commit_pipeline
        ),
    )

    f2.metric(
        "Likely",
        money(
            forecast.likely_pipeline
        ),
    )

    f3.metric(
        "Upside",
        money(
            forecast.upside_pipeline
        ),
    )

    f4.metric(
        "Coverage",
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

            d1, d2, d3, d4 = st.columns(
                [2.5, 1, 1, 1]
            )

            d1.markdown(
                f"**{deal.deal_name}**"
            )

            d2.metric(
                "Rep",
                f"{deal.probability:.0%}",
            )

            d3.metric(
                "OS",
                f"{assessment.adjusted_probability:.0%}",
            )

            d4.metric(
                "Forecast Gap",
                money(
                    value_gap
                ),
            )


# ==========================================================
# DEAL ROOM
# ==========================================================

elif page == "Deal Room":

    render_page_intro(
        "Deal Intelligence",
        "Deal Room",
        (
            "One workspace for deal state, risk, communications "
            "and next-best-action intelligence."
        ),
    )

    deal_lookup: Dict[
        str,
        Deal,
    ] = {
        (
            f"{deal.deal_id} — "
            f"{deal.deal_name} — "
            f"{money(deal.amount_usd)}"
        ): deal
        for deal in deals
    }

    selected_label = st.selectbox(
        "Select opportunity",
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

    deal_activity = activities_for_deal(
        selected.deal_id
    )

    momentum = momentum_score(
        selected,
        len(
            assessment.risk_reasons
        ),
    )

    st.write("")

    title_col, value_col = st.columns(
        [4, 1]
    )

    with title_col:
        st.subheader(
            selected.deal_name
        )

        st.caption(
            risk_label(
                assessment.risk_level
            )
        )

    value_col.metric(
        "Deal Value",
        money(
            selected.amount_usd
        ),
    )

    s1, s2, s3, s4 = st.columns(
        4
    )

    s1.metric(
        "Health",
        f"{assessment.health_score:.0f}",
    )

    s2.metric(
        "Momentum",
        f"{momentum}",
    )

    s3.metric(
        "Qualification",
        f"{assessment.qualification_score:.0f}",
    )

    s4.metric(
        "Forecast Confidence",
        f"{assessment.adjusted_probability:.0%}",
    )

    st.divider()

    left, right = st.columns(
        [1.25, 1]
    )

    with left:

        st.subheader(
            "Why the system is concerned"
        )

        if assessment.risk_reasons:

            for reason in assessment.risk_reasons:
                st.write(
                    f"• {reason}"
                )

        else:
            st.success(
                "No material risk signals detected."
            )

        st.subheader(
            "Current Deal State"
        )

        st.write(
            f"**Stage:** "
            f"{clean_enum(selected.stage.value)}"
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

    with right:

        st.subheader(
            "Next Best Action"
        )

        with st.container(
            border=True
        ):

            st.markdown(
                "### "
                + clean_enum(
                    assessment.recommended_action.value
                )
            )

            st.write(
                assessment.action_reason
            )

            st.divider()

            st.write(
                f"**Owner:** {assessment.owner}"
            )

            st.write(
                f"**SLA:** {assessment.sla}"
            )

        a1, a2 = st.columns(
            2
        )

        a1.button(
            "✨ Analyse with AI",
            type="primary",
            use_container_width=True,
        )

        a2.button(
            "Build Close Plan",
            use_container_width=True,
        )

        a3, a4 = st.columns(
            2
        )

        a3.button(
            "Draft Follow-up",
            use_container_width=True,
        )

        a4.button(
            "Escalate",
            use_container_width=True,
        )

    st.divider()

    st.subheader(
        "Deal Activity"
    )

    if not deal_activity:

        st.info(
            "No synthetic activity available for this deal."
        )

    else:

        for activity in deal_activity:
            render_activity(
                activity,
                show_deal=False,
            )


# ==========================================================
# INBOX INTELLIGENCE
# ==========================================================

elif page == "Inbox Intelligence":

    render_page_intro(
        "Communication Intelligence",
        "Inbox Intelligence",
        (
            "Turn customer email into revenue signals instead of "
            "letting important commercial context disappear inside inboxes."
        ),
    )

    inbound = [
        item
        for item in inbox_activity
        if item.activity_type
        == ActivityType.EMAIL_INBOUND
    ]

    risk_emails = [
        item
        for item in inbound
        if item.signal_type
        == SignalType.RISK
    ]

    positive_emails = [
        item
        for item in inbound
        if item.signal_type
        == SignalType.POSITIVE
    ]

    associated_pipeline = sum(
        deal_by_id[item.deal_id].amount_usd
        for item in inbound
        if item.deal_id
        in deal_by_id
    )

    c1, c2, c3, c4 = st.columns(
        4
    )

    c1.metric(
        "Deal-related conversations",
        len(
            inbox_activity
        ),
    )

    c2.metric(
        "Inbound requiring attention",
        len(
            risk_emails
        ),
    )

    c3.metric(
        "Positive buying signals",
        len(
            positive_emails
        ),
    )

    c4.metric(
        "Associated pipeline",
        money(
            associated_pipeline
        ),
    )

    st.divider()

    filter_signal = st.selectbox(
        "Signal filter",
        [
            "All",
            "Risk",
            "Positive",
            "Neutral",
        ],
    )

    filtered_inbox = inbox_activity

    if filter_signal == "Risk":

        filtered_inbox = [
            activity
            for activity in inbox_activity
            if activity.signal_type
            == SignalType.RISK
        ]

    elif filter_signal == "Positive":

        filtered_inbox = [
            activity
            for activity in inbox_activity
            if activity.signal_type
            == SignalType.POSITIVE
        ]

    elif filter_signal == "Neutral":

        filtered_inbox = [
            activity
            for activity in inbox_activity
            if activity.signal_type
            == SignalType.NEUTRAL
        ]

    for activity in sorted(
        filtered_inbox,
        key=lambda item: item.occurred_at,
        reverse=True,
    ):

        deal = deal_by_id.get(
            activity.deal_id
        )

        with st.container(
            border=True
        ):

            c1, c2 = st.columns(
                [4, 1]
            )

            with c1:
                st.subheader(
                    activity.title
                )

                st.caption(
                    f"{signal_icon(activity.signal_type)} "
                    f"{clean_enum(activity.signal_type.value)} signal"
                )

            with c2:
                if deal:
                    st.metric(
                        "Deal Value",
                        money(
                            deal.amount_usd
                        ),
                    )

            if activity.sender:
                st.write(
                    f"**From:** {activity.sender}"
                )

            if activity.recipient:
                st.write(
                    f"**To:** {activity.recipient}"
                )

            st.write(
                activity.summary
            )

            if activity.extracted_signals:

                st.markdown(
                    "**Commercial signals**"
                )

                for signal in activity.extracted_signals:
                    st.write(
                        f"• {signal}"
                    )

            if activity.recommended_action:
                st.info(
                    activity.recommended_action
                )

            b1, b2, b3 = st.columns(
                3
            )

            b1.button(
                "Summarise Thread",
                key=(
                    "summarise_"
                    + activity.activity_id
                ),
                use_container_width=True,
            )

            b2.button(
                "Draft Follow-up",
                key=(
                    "draft_email_"
                    + activity.activity_id
                ),
                use_container_width=True,
            )

            b3.button(
                "Update Deal",
                key=(
                    "update_email_"
                    + activity.activity_id
                ),
                use_container_width=True,
            )


# ==========================================================
# MEETING INTELLIGENCE
# ==========================================================

elif page == "Meeting Intelligence":

    render_page_intro(
        "Conversation Intelligence",
        "Meeting Intelligence",
        (
            "Transform meeting transcripts into qualification, "
            "stakeholder, risk and next-action intelligence."
        ),
    )

    st.caption(
        "Synthetic transcript workflow — no real customer conversations."
    )

    meeting_lookup = {
        (
            f"{activity.deal_id} — "
            f"{activity.title}"
        ): activity
        for activity in meeting_activity
    }

    if not meeting_lookup:

        st.info(
            "No meeting activity available."
        )

    else:

        selected_meeting_label = st.selectbox(
            "Choose meeting",
            list(
                meeting_lookup.keys()
            ),
        )

        meeting = meeting_lookup[
            selected_meeting_label
        ]

        deal = deal_by_id.get(
            meeting.deal_id
        )

        assessment = (
            assessment_by_id.get(
                meeting.deal_id
            )
        )

        st.write("")

        title_col, signal_col = st.columns(
            [4, 1]
        )

        with title_col:
            st.subheader(
                meeting.title
            )

            st.caption(
                meeting.occurred_at.strftime(
                    "%25 Aug 2026 • %H:%M"
                )
                if False
                else meeting.occurred_at.strftime(
                    "%d Aug 2026 • %H:%M"
                )
            )

        with signal_col:
            st.metric(
                "Signal",
                clean_enum(
                    meeting.signal_type.value
                ),
            )

        if deal and assessment:

            c1, c2, c3, c4 = st.columns(
                4
            )

            c1.metric(
                "Deal Value",
                money(
                    deal.amount_usd
                ),
            )

            c2.metric(
                "Qualification",
                f"{assessment.qualification_score:.0f}",
            )

            c3.metric(
                "Rep Probability",
                f"{deal.probability:.0%}",
            )

            c4.metric(
                "OS Probability",
                f"{assessment.adjusted_probability:.0%}",
            )

        st.divider()

        left, right = st.columns(
            [1.15, 1]
        )

        with left:

            st.subheader(
                "Transcript"
            )

            if meeting.transcript:

                st.text_area(
                    "Synthetic transcript",
                    value=meeting.transcript,
                    height=220,
                    disabled=True,
                    label_visibility="collapsed",
                )

            else:

                st.info(
                    "No transcript stored."
                )

        with right:

            st.subheader(
                "Signals Extracted"
            )

            if meeting.extracted_signals:

                for signal in meeting.extracted_signals:
                    st.write(
                        f"• {signal}"
                    )

            if meeting.recommended_action:

                st.info(
                    "Next action: "
                    + meeting.recommended_action
                )

            st.write("")

            b1, b2 = st.columns(
                2
            )

            b1.button(
                "Process Transcript",
                type="primary",
                use_container_width=True,
            )

            b2.button(
                "Update CRM",
                use_container_width=True,
            )

            b3, b4 = st.columns(
                2
            )

            b3.button(
                "Draft Recap",
                use_container_width=True,
            )

            b4.button(
                "Create Tasks",
                use_container_width=True,
            )

        st.divider()

        st.subheader(
            "Revenue OS Impact"
        )

        if assessment and deal:

            impact1, impact2, impact3 = st.columns(
                3
            )

            impact1.metric(
                "Current Qualification",
                f"{assessment.qualification_score:.0f}/100",
            )

            impact2.metric(
                "Current OS Forecast",
                f"{assessment.adjusted_probability:.0%}",
            )

            impact3.metric(
                "Current Risk",
                clean_enum(
                    assessment.risk_level.value
                ),
            )

        st.caption(
            "In a live implementation, extracted meeting signals "
            "would update CRM fields and automatically re-run the "
            "qualification, risk and forecast engines."
        )


# ==========================================================
# ACTIVITY FEED
# ==========================================================

elif page == "Activity Feed":

    render_page_intro(
        "Revenue Event Stream",
        "Activity Feed",
        (
            "A single operating timeline showing communication, "
            "CRM updates and machine-generated actions."
        ),
    )

    c1, c2, c3 = st.columns(
        3
    )

    c1.metric(
        "Total simulated events",
        len(
            activities
        ),
    )

    c2.metric(
        "Automation events",
        len(
            automation_activity
        ),
    )

    c3.metric(
        "Deals represented",
        len(
            set(
                activity.deal_id
                for activity in activities
            )
        ),
    )

    activity_filter = st.selectbox(
        "Activity type",
        [
            "All",
            "Email",
            "Meeting",
            "Automation",
            "CRM Update",
        ],
    )

    display_activity = activities

    if activity_filter == "Email":

        display_activity = [
            activity
            for activity in activities
            if activity.activity_type
            in {
                ActivityType.EMAIL_INBOUND,
                ActivityType.EMAIL_OUTBOUND,
            }
        ]

    elif activity_filter == "Meeting":

        display_activity = [
            activity
            for activity in activities
            if activity.activity_type
            == ActivityType.MEETING
        ]

    elif activity_filter == "Automation":

        display_activity = [
            activity
            for activity in activities
            if activity.activity_type
            == ActivityType.AUTOMATION
        ]

    elif activity_filter == "CRM Update":

        display_activity = [
            activity
            for activity in activities
            if activity.activity_type
            == ActivityType.CRM_UPDATE
        ]

    for activity in sorted(
        display_activity,
        key=lambda item: item.occurred_at,
        reverse=True,
    ):

        render_activity(
            activity
        )


# ==========================================================
# AUTOMATIONS
# ==========================================================

elif page == "Automations":

    render_page_intro(
        "Revenue Automation",
        "The machine behind the sales team",
        (
            "Turn commercial signals into actions without relying "
            "on somebody remembering every follow-up or forecast review."
        ),
    )

    automations = [
        {
            "name": "Deal Stall Monitor",
            "status": "ACTIVE",
            "description": (
                "Detect inactivity, stage ageing and missing next steps."
            ),
            "output": (
                f"{len(risky)} high / critical interventions surfaced"
            ),
        },
        {
            "name": "Forecast Truth Engine",
            "status": "ACTIVE",
            "description": (
                "Challenge rep probability against qualification evidence."
            ),
            "output": (
                f"{money(optimism_gap)} forecast optimism detected"
            ),
        },
        {
            "name": "Inbox Intelligence",
            "status": "SIMULATED",
            "description": (
                "Classify customer emails into commercial buying signals."
            ),
            "output": (
                f"{len(inbox_activity)} synthetic email events processed"
            ),
        },
        {
            "name": "Meeting Intelligence",
            "status": "SIMULATED",
            "description": (
                "Convert transcripts into qualification and deal updates."
            ),
            "output": (
                f"{len(meeting_activity)} synthetic meetings processed"
            ),
        },
        {
            "name": "Follow-up SLA Guard",
            "status": "ACTIVE",
            "description": (
                "Create action when an opportunity loses momentum."
            ),
            "output": (
                "AE follow-up actions routed into Action Queue"
            ),
        },
        {
            "name": "Founder Escalation Engine",
            "status": "ACTIVE",
            "description": (
                "Route high-value, high-risk deals for executive intervention."
            ),
            "output": (
                f"{len(founder_deals)} founder-linked opportunities"
            ),
        },
        {
            "name": "Expansion Radar",
            "status": "ACTIVE",
            "description": (
                "Surface growth opportunities inside existing accounts."
            ),
            "output": (
                f"{money(expansion_pipeline)} expansion pipeline"
            ),
        },
        {
            "name": "AI Deal Desk",
            "status": "READY",
            "description": (
                "Generate deal diagnosis, close plans and follow-up."
            ),
            "output": (
                "API connection intentionally deferred"
            ),
        },
    ]

    for automation in automations:

        with st.container(
            border=True
        ):

            c1, c2 = st.columns(
                [4, 1]
            )

            with c1:
                st.subheader(
                    automation[
                        "name"
                    ]
                )

            with c2:
                st.caption(
                    automation[
                        "status"
                    ]
                )

            st.write(
                automation[
                    "description"
                ]
            )

            st.info(
                automation[
                    "output"
                ]
            )

    st.divider()

    st.subheader(
        "Operating Architecture"
    )

    st.code(
        """
SIGNAL
  ↓
INGEST
  ↓
CLASSIFY
  ↓
UPDATE DEAL STATE
  ↓
QUALIFY
  ↓
RISK SCORE
  ↓
FORECAST
  ↓
CREATE ACTION
  ↓
HUMAN APPROVAL
  ↓
EXECUTE
  ↓
RE-MONITOR
        """,
        language="text",
    )


# ==========================================================
# REVENUE PLAN
# ==========================================================

elif page == "Revenue Plan":

    render_page_intro(
        "Revenue Architecture",
        "What gets us to $3M?",
        (
            "Model the combination of ACV, conversion, pipeline, "
            "sales capacity and expansion required to reach the next stage."
        ),
    )

    c1, c2, c3 = st.columns(
        3
    )

    c1.metric(
        "Revenue Ambition",
        "$3M",
    )

    c2.metric(
        "Illustrative Pipeline",
        money(
            forecast.raw_pipeline
        ),
    )

    c3.metric(
        "Expansion Identified",
        money(
            expansion_pipeline
        ),
    )

    st.divider()

    st.subheader(
        "Revenue Digital Twin"
    )

    left, right = st.columns(
        2
    )

    with left:

        average_contract_value = st.slider(
            "Average contract value",
            min_value=20000,
            max_value=120000,
            value=50000,
            step=5000,
        )

        win_rate = st.slider(
            "Qualified win rate (%)",
            min_value=10,
            max_value=70,
            value=30,
            step=1,
        )

        qualified_opportunities = st.slider(
            "Qualified opportunities / year",
            min_value=20,
            max_value=300,
            value=100,
            step=5,
        )

    with right:

        expansion_share = st.slider(
            "Expansion contribution (%)",
            min_value=0,
            max_value=50,
            value=15,
            step=1,
        )

        ae_count = st.slider(
            "Number of AEs",
            min_value=1,
            max_value=12,
            value=4,
            step=1,
        )

        capacity_per_ae = st.slider(
            "Qualified opportunities per AE / year",
            min_value=10,
            max_value=60,
            value=25,
            step=1,
        )

    new_logo_revenue = (
        average_contract_value
        * qualified_opportunities
        * (
            win_rate
            / 100
        )
    )

    expansion_revenue = (
        new_logo_revenue
        * (
            expansion_share
            / 100
        )
    )

    modeled_revenue = (
        new_logo_revenue
        + expansion_revenue
    )

    ae_capacity = (
        ae_count
        * capacity_per_ae
    )

    required_wins = (
        LONG_TERM_REVENUE_TARGET
        / average_contract_value
    )

    required_opportunities = (
        required_wins
        / (
            win_rate
            / 100
        )
        if win_rate
        else 0
    )

    st.divider()

    r1, r2, r3, r4 = st.columns(
        4
    )

    r1.metric(
        "Modeled Revenue",
        money(
            modeled_revenue
        ),
    )

    r2.metric(
        "Required Wins",
        f"{required_wins:.0f}",
    )

    r3.metric(
        "Required Qualified Opps",
        f"{required_opportunities:.0f}",
    )

    r4.metric(
        "AE Capacity",
        f"{ae_capacity}",
    )

    if modeled_revenue >= LONG_TERM_REVENUE_TARGET:

        st.success(
            "This operating model clears the $3M ambition."
        )

    else:

        shortfall = (
            LONG_TERM_REVENUE_TARGET
            - modeled_revenue
        )

        st.warning(
            "This operating model is short by "
            + money(
                shortfall
            )
            + "."
        )

    if required_opportunities > ae_capacity:

        st.error(
            "Current AE capacity cannot support the required "
            "qualified opportunity volume."
        )

    else:

        st.success(
            "AE capacity is sufficient for the modeled opportunity load."
        )


# ==========================================================
# INTEGRATIONS
# ==========================================================

elif page == "Integrations":

    render_page_intro(
        "System Architecture",
        "Integrations",
        (
            "How the prototype becomes a live Revenue OS connected "
            "to the tools the sales team already uses."
        ),
    )

    st.info(
        "These connectors are architecture-ready concepts. "
        "They are not currently authenticated to ThunderClap systems."
    )

    integrations = [
        {
            "name": "Gmail",
            "status": "READY TO CONNECT",
            "purpose": (
                "Ingest customer threads, classify buying signals, "
                "detect unanswered conversations and draft follow-up."
            ),
            "flow": (
                "Gmail → Inbox Intelligence → Deal State → Action Queue"
            ),
        },
        {
            "name": "Google Calendar",
            "status": "READY TO CONNECT",
            "purpose": (
                "Map meetings to opportunities and detect whether "
                "qualified deals have committed next steps."
            ),
            "flow": (
                "Calendar → Meeting Detection → Momentum Engine"
            ),
        },
        {
            "name": "Google Meet / Transcript",
            "status": "READY TO CONNECT",
            "purpose": (
                "Process transcript or meeting notes into qualification, "
                "stakeholders, objections and next actions."
            ),
            "flow": (
                "Transcript → Meeting Intelligence → CRM Update"
            ),
        },
        {
            "name": "HubSpot",
            "status": "ADAPTER READY",
            "purpose": (
                "Sync deals, stages, amounts, owners and activities."
            ),
            "flow": (
                "CRM → Revenue OS → CRM"
            ),
        },
        {
            "name": "Salesforce",
            "status": "AVAILABLE",
            "purpose": (
                "Alternative CRM adapter using the same canonical deal model."
            ),
            "flow": (
                "Salesforce → Canonical Deal Model → Engines"
            ),
        },
        {
            "name": "Slack",
            "status": "AVAILABLE",
            "purpose": (
                "Route founder escalations, deal alerts and daily briefs."
            ),
            "flow": (
                "Revenue Action → Slack → Human"
            ),
        },
        {
            "name": "OpenAI / Claude",
            "status": "DEFERRED",
            "purpose": (
                "Deal analysis, transcript extraction, close plans "
                "and contextual follow-up generation."
            ),
            "flow": (
                "Structured Deal Context → LLM → Human-reviewed Output"
            ),
        },
    ]

    for integration in integrations:

        with st.container(
            border=True
        ):

            c1, c2 = st.columns(
                [4, 1]
            )

            c1.subheader(
                integration[
                    "name"
                ]
            )

            c2.caption(
                integration[
                    "status"
                ]
            )

            st.write(
                integration[
                    "purpose"
                ]
            )

            st.code(
                integration[
                    "flow"
                ],
                language="text",
            )

    st.divider()

    st.subheader(
        "Live Architecture"
    )

    st.code(
        """
GMAIL ───────────────┐
                     │
GOOGLE CALENDAR ─────┤
                     │
MEETING TRANSCRIPT ──┤
                     ↓
               INGESTION LAYER
                     ↓
              CANONICAL DEAL MODEL
                     ↓
      ┌──────────────┼───────────────┐
      ↓              ↓               ↓
QUALIFICATION     DEAL RISK      FORECAST
      └──────────────┼───────────────┘
                     ↓
              ACTION ORCHESTRATOR
                     ↓
        ┌────────────┼────────────┐
        ↓            ↓            ↓
      CRM          GMAIL        SLACK
        """,
        language="text",
    )


# ==========================================================
# FOOTER
# ==========================================================

st.write("")
st.write("")

st.caption(
    "THUNDERCLAP REVENUE OS • Independent application prototype • "
    "All account, deal, communication and meeting data is synthetic."
)
