from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class ActivityType(str, Enum):
    EMAIL_INBOUND = "EMAIL_INBOUND"
    EMAIL_OUTBOUND = "EMAIL_OUTBOUND"
    MEETING = "MEETING"
    CRM_UPDATE = "CRM_UPDATE"
    AUTOMATION = "AUTOMATION"


class SignalType(str, Enum):
    POSITIVE = "POSITIVE"
    RISK = "RISK"
    NEUTRAL = "NEUTRAL"


@dataclass
class RevenueActivity:
    activity_id: str
    deal_id: str
    occurred_at: datetime

    activity_type: ActivityType
    title: str
    summary: str

    signal_type: SignalType

    sender: Optional[str] = None
    recipient: Optional[str] = None

    transcript: Optional[str] = None

    extracted_signals: Optional[List[str]] = None

    recommended_action: Optional[str] = None

    automation_name: Optional[str] = None


def load_synthetic_activity() -> List[RevenueActivity]:
    """
    Synthetic email, meeting, CRM and automation activity.

    These records demonstrate how the Revenue OS could ingest
    communications, derive commercial signals and update deal
    intelligence.

    No real ThunderClap CRM or customer data is represented.
    """

    return [
        RevenueActivity(
            activity_id="ACT-001",
            deal_id="TC-001",
            occurred_at=datetime(2026, 8, 25, 9, 15),
            activity_type=ActivityType.MEETING,
            title="Northstar AI — Proposal Review",
            summary=(
                "Proposal review completed with the marketing team. "
                "Internal alignment exists, but final executive approval "
                "has not yet been confirmed."
            ),
            signal_type=SignalType.RISK,
            transcript=(
                "The team likes the direction and agrees the website "
                "needs to change before the next growth phase. "
                "The CMO still wants to review scope and timing. "
                "Budget itself is not the main issue, but we need "
                "internal alignment before confirming the project."
            ),
            extracted_signals=[
                "Business need reconfirmed",
                "Budget resistance appears limited",
                "CMO approval still required",
                "Decision process remains incomplete",
            ],
            recommended_action=(
                "Secure a decision meeting including the CMO."
            ),
        ),

        RevenueActivity(
            activity_id="ACT-002",
            deal_id="TC-001",
            occurred_at=datetime(2026, 8, 25, 9, 17),
            activity_type=ActivityType.AUTOMATION,
            title="Meeting Intelligence processed transcript",
            summary=(
                "Qualification and stakeholder signals extracted "
                "from meeting transcript."
            ),
            signal_type=SignalType.NEUTRAL,
            automation_name="AI Call Intelligence",
            extracted_signals=[
                "Economic buyer coverage incomplete",
                "Need remains active",
                "Executive approval missing",
            ],
            recommended_action=(
                "Re-score qualification and create executive follow-up."
            ),
        ),

        RevenueActivity(
            activity_id="ACT-003",
            deal_id="TC-001",
            occurred_at=datetime(2026, 8, 25, 9, 18),
            activity_type=ActivityType.CRM_UPDATE,
            title="Northstar qualification updated",
            summary=(
                "Meeting signals were mapped into the synthetic "
                "deal intelligence layer."
            ),
            signal_type=SignalType.NEUTRAL,
            extracted_signals=[
                "Decision process unresolved",
                "Executive buyer not yet confirmed",
            ],
        ),

        RevenueActivity(
            activity_id="ACT-004",
            deal_id="TC-001",
            occurred_at=datetime(2026, 8, 25, 9, 19),
            activity_type=ActivityType.AUTOMATION,
            title="Founder escalation created",
            summary=(
                "High-value stalled opportunity routed for "
                "founder-assisted close."
            ),
            signal_type=SignalType.RISK,
            automation_name="Founder Escalation Engine",
            recommended_action="Founder intervention today.",
        ),

        RevenueActivity(
            activity_id="ACT-005",
            deal_id="TC-002",
            occurred_at=datetime(2026, 8, 25, 10, 2),
            activity_type=ActivityType.EMAIL_INBOUND,
            title="VectorCloud replied on commercial approval",
            summary=(
                "Customer indicated that budget approval is still "
                "being worked through internally."
            ),
            signal_type=SignalType.RISK,
            sender="buyer@vectorcloud.example",
            recipient="sales@thunderclap.example",
            extracted_signals=[
                "Budget approval still pending",
                "No rejection",
                "Decision timing remains uncertain",
            ],
            recommended_action=(
                "Clarify approval path and secure a dated next step."
            ),
        ),

        RevenueActivity(
            activity_id="ACT-006",
            deal_id="TC-002",
            occurred_at=datetime(2026, 8, 25, 10, 4),
            activity_type=ActivityType.AUTOMATION,
            title="Inbox Intelligence classified reply",
            summary=(
                "Inbound email classified as budget / decision delay."
            ),
            signal_type=SignalType.RISK,
            automation_name="Inbox Intelligence",
            extracted_signals=[
                "Budget",
                "Delay",
                "Next step missing",
            ],
            recommended_action="Draft targeted approval follow-up.",
        ),

        RevenueActivity(
            activity_id="ACT-007",
            deal_id="TC-005",
            occurred_at=datetime(2026, 8, 25, 11, 30),
            activity_type=ActivityType.MEETING,
            title="SignalForge — Commercial Alignment",
            summary=(
                "Commercial discussion advanced with the buyer team."
            ),
            signal_type=SignalType.POSITIVE,
            transcript=(
                "The team is comfortable with the scope. "
                "We want to move quickly and are aiming to make "
                "a final decision after the procurement review. "
                "The proposed timeline works for us."
            ),
            extracted_signals=[
                "Scope accepted",
                "Timeline accepted",
                "Procurement identified as final dependency",
                "Buying momentum strong",
            ],
            recommended_action=(
                "Support procurement and protect target close date."
            ),
        ),

        RevenueActivity(
            activity_id="ACT-008",
            deal_id="TC-005",
            occurred_at=datetime(2026, 8, 25, 11, 32),
            activity_type=ActivityType.AUTOMATION,
            title="Forecast confidence increased",
            summary=(
                "Meeting evidence supports current Commit positioning."
            ),
            signal_type=SignalType.POSITIVE,
            automation_name="Forecast Truth Engine",
            extracted_signals=[
                "Timeline validated",
                "Commercial scope validated",
                "Decision path clearer",
            ],
        ),

        RevenueActivity(
            activity_id="ACT-009",
            deal_id="TC-008",
            occurred_at=datetime(2026, 8, 25, 12, 8),
            activity_type=ActivityType.EMAIL_OUTBOUND,
            title="AtlasOps discovery follow-up sent",
            summary=(
                "Follow-up requested confirmation of buyer, "
                "budget and decision process."
            ),
            signal_type=SignalType.NEUTRAL,
            sender="ae02@thunderclap.example",
            recipient="buyer@atlasops.example",
        ),

        RevenueActivity(
            activity_id="ACT-010",
            deal_id="TC-008",
            occurred_at=datetime(2026, 8, 25, 16, 30),
            activity_type=ActivityType.AUTOMATION,
            title="Qualification guard triggered",
            summary=(
                "High rep probability conflicts with low qualification."
            ),
            signal_type=SignalType.RISK,
            automation_name="Forecast Truth Engine",
            extracted_signals=[
                "Rep probability 85%",
                "Qualification materially incomplete",
                "Commit classification unsupported",
            ],
            recommended_action=(
                "Requalify before maintaining Commit forecast."
            ),
        ),

        RevenueActivity(
            activity_id="ACT-011",
            deal_id="TC-011",
            occurred_at=datetime(2026, 8, 25, 14, 15),
            activity_type=ActivityType.EMAIL_INBOUND,
            title="BluePeak requested Phase II discussion",
            summary=(
                "Existing customer expressed interest in expanding "
                "the engagement."
            ),
            signal_type=SignalType.POSITIVE,
            sender="marketing@bluepeak.example",
            recipient="ae01@thunderclap.example",
            extracted_signals=[
                "Expansion intent",
                "Existing relationship",
                "New scope discussion requested",
            ],
            recommended_action=(
                "Schedule expansion discovery and quantify scope."
            ),
        ),

        RevenueActivity(
            activity_id="ACT-012",
            deal_id="TC-011",
            occurred_at=datetime(2026, 8, 25, 14, 17),
            activity_type=ActivityType.AUTOMATION,
            title="Expansion opportunity created",
            summary=(
                "Existing-account signal classified as expansion."
            ),
            signal_type=SignalType.POSITIVE,
            automation_name="Expansion Radar",
            recommended_action=(
                "Route opportunity to account owner."
            ),
        ),

        RevenueActivity(
            activity_id="ACT-013",
            deal_id="TC-027",
            occurred_at=datetime(2026, 8, 25, 15, 5),
            activity_type=ActivityType.AUTOMATION,
            title="Proposal stall detected",
            summary=(
                "Proposal remains open with no committed next meeting."
            ),
            signal_type=SignalType.RISK,
            automation_name="Deal Stall Monitor",
            extracted_signals=[
                "Proposal outstanding",
                "No next meeting",
                "Stage ageing elevated",
            ],
            recommended_action=(
                "Follow up and force a concrete next step."
            ),
        ),

        RevenueActivity(
            activity_id="ACT-014",
            deal_id="TC-027",
            occurred_at=datetime(2026, 8, 25, 15, 6),
            activity_type=ActivityType.AUTOMATION,
            title="Follow-up SLA created",
            summary=(
                "Opportunity added to AE-01 action queue."
            ),
            signal_type=SignalType.NEUTRAL,
            automation_name="Follow-up SLA Guard",
            recommended_action="Follow up within 24 hours.",
        ),

        RevenueActivity(
            activity_id="ACT-015",
            deal_id="TC-014",
            occurred_at=datetime(2026, 8, 25, 16, 10),
            activity_type=ActivityType.EMAIL_INBOUND,
            title="CoreLabs confirmed next discussion",
            summary=(
                "Existing customer confirmed continued interest "
                "and a next meeting."
            ),
            signal_type=SignalType.POSITIVE,
            sender="brand@corelabs.example",
            recipient="founder@thunderclap.example",
            extracted_signals=[
                "Next step confirmed",
                "Existing-account momentum",
                "Founder involvement active",
            ],
        ),
    ]


def activities_for_deal(
    deal_id: str,
) -> List[RevenueActivity]:
    activities = [
        activity
        for activity in load_synthetic_activity()
        if activity.deal_id == deal_id
    ]

    return sorted(
        activities,
        key=lambda activity: activity.occurred_at,
        reverse=True,
    )


def recent_activity(
    limit: int = 10,
) -> List[RevenueActivity]:
    activities = sorted(
        load_synthetic_activity(),
        key=lambda activity: activity.occurred_at,
        reverse=True,
    )

    return activities[:limit]
